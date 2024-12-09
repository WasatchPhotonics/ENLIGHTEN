import time
import asyncio
import logging
from queue import Queue

from bleak import BleakScanner, BleakClient
from threading import Thread

from enlighten import common
from wasatch.DeviceID import DeviceID
# from wasatch.BLEScanner import BLEScanner

if common.use_pyside2():
    from PySide2 import QtCore, QtGui
    from PySide2.QtWidgets import QDialog, QPushButton, QVBoxLayout, QLabel
else:
    from PySide6 import QtCore, QtGui
    from PySide6.QtWidgets import QDialog, QPushButton, QVBoxLayout, QLabel

log = logging.getLogger(__name__)

class BLEManager:
    """
    Allows user to connect to nearby wasatch.BLEDevices.

    @par Connection

    +-----------------------+
    | BLE Spectrometers [x] |
    +-----------------------+
    | [Connect]    [Rescan] |
    |                       |
    | RSSI Serial Number    |
    | )))  WP-01234         |
    | )    WP-01228         |
    | ))   WP-01499         |
    +-----------------------+

    Goals:
    - provide a button that pops-up a dialog listing advertised localNames
    - scan should begin as soon as dialog opens
    - allow the background Bleak discovery scan to update the dialog roughly 1/sec (probably using Queue)
    - colorize the selected item when user clicks the row
    - when user clicks "Connect"
        - construct DeviceID with non-serializable .bleak_device populated 
          (as passed to detection_callback by BleakScanner, then to BLEManager 
          through Queue)
        - add new DeviceID to Controller.other_device_ids
        - close dialog
    - list should be sorted in "discovery" order -- don't "sort" list, as we 
      don't want rows to move while user is trying to click on them

    @par Architecture

    - wasatch.BLEDeviceFinder
        - runs 30sec scan, generating callback with (DeviceID, rssi) of new/updated devices
        - this is where BleakScanner lives

    - wasatch.BLEDevice
        - constructor takes DeviceID 
            - expects device_id.bleak_device to hold populated bleak.backends.device.BLEDevice
        - connect() returns SpectrometerResponse(True) after SpectrometerSettings.EEPROM parsed

    """

    def __init__(self, ctl):
        self.ctl = ctl
        cfu = ctl.form.ui

        # used to initiate a search, and to indicate whether one or more a BLE 
        # spectrometers are paired
        self.ble_button = cfu.pushButton_bleScan

        self.scans_q = Queue()

        self.ble_device = None
        self.ble_present = False
        self.ble_device_id = None

        self.original_button_style = self.ble_button.styleSheet()
        self.selection_popup = BLESelector(parent=self.ble_button)

        self.ble_button.clicked.connect(self.button_callback)

        self.ctl.reading_progress_bar.hide()

        # create a thread in which to run BleakScanner, so we're not blocking 
        # the GUI loop when the button is pressed
        self.scan_loop = asyncio.new_event_loop()
        self.scan_thread = Thread(target=self.make_scan_loop, daemon=True)
        self.scan_thread.start()

    def make_scan_loop(self):
        asyncio.set_event_loop(self.scan_loop)
        self.scan_loop.run_forever()

    def check_complete_scans(self):
        if not self.scans_q.empty():
            log.debug(f"scan queue non-empty...checking for wp_devices")
            wp_devices = self.scans_q.get_nowait()
            self.selection_popup.clear_plugin_layout(self.selection_popup.layout)
            if wp_devices != []:
                log.debug(f"found wp_devices {wp_devices}")
                for d in wp_devices:
                    btn = QPushButton()
                    btn.setText(str(d.name)) # YOU ARE HERE
                    log.debug(f"  found device {d}")
                    btn.clicked.connect(lambda: self.connect_callback(btn, d))
                    self.selection_popup.device_widgets.append(btn)
                    self.selection_popup.layout.addWidget(btn)
            else:
                label = QLabel()
                label.setText("no wp_devices found")
                label.setAlignment(QtCore.Qt.AlignCenter)
                self.selection_popup.layout.addWidget(label)

    def stop(self):
        self.ctl.marquee.info("Closing BLE spectrometers...", immediate=True)
        time.sleep(0.05)
        if self.ble_device_id is not None:
            self.ctl.disconnect_device(self.ctl.multispec.get_spectrometer(self.ble_device_id))
            self.ctl.multispec.set_disconnecting(self.ble_device_id, False)
            self.ble_device_id = None

    def button_callback(self):
        log.debug("BLE button clicked")
        if self.ble_present:
            log.debug("disconnecting from BLE device")
            self.ble_present = False
            self.ctl.reading_progress_bar.hide()
            self.ble_button.setStyleSheet(self.original_button_style)
            self.stop()
            return

        log.debug("Searching for BLE devices")

        # clear anything that might be in the pop up for available devices
        self.selection_popup.clear_plugin_layout(self.selection_popup.layout)
        self.selection_popup.device_widgets.clear()

        # Kick off the async search for BLE Devices and show the pop up
        log.debug("calling perform_discovery")
        asyncio.run_coroutine_threadsafe(self.perform_discovery(), self.scan_loop)
        self.selection_popup.show()

    async def perform_discovery(self):
        """ This method is explicitly run in a separate thread under asyncio via scan_loop """

        log.debug("starting discovery")
        devices = await discover()
        wp_devices = [dev for dev in devices if dev.name is not None and ("wp" in dev.name.lower())]
        log.debug(f"adding wp_devices to scans_q: {wp_devices}")
        self.scans_q.put(wp_devices)

    def connect_callback(self, btn, device):
        log.debug(f"Connecting to {device}")
        self.device = device
        self.selection_popup.hide()

        self.ble_device_id = DeviceID(label=f"BLE:{device.address}:{device.name}")

        log.debug(f"calling connect_new with DeviceID {self.ble_device_id}")
        ok = self.ctl.connect_new(self.ble_device_id)
        log.debug(f"connect_new returned ok {ok}")
        self.ble_present = True
        if ok:
            log.debug(f"updating button color")
            self.ble_button.setStyleSheet("background-color: #4a5da9")
            # '#6758c5', # the 'E' in ENLIGHTEN (violet)
            # '#4a5da9', # the 'N' in ENLIGHTEN (blue)
            # '#2994d3', # the 'L' in ENLIGHTEN (cyan)
            # '#27c0a1', # the 'I' in ENLIGHTEN (bluegreen)

class BLESelector(QDialog):
    """
    A pop-up window listing all discovered BLE devices.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("BLE Spectrometers")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # MZ: is this actually needed? All it stores are handles to QPushButtons,
        # which are already added to self.layout and so persisted there.
        self.device_widgets = []

    def clear_plugin_layout(self, layout):
        """
        Same as PluginController, clear all descending the layout recursively.
        @see https://stackoverflow.com/questions/4528347/clear-all-widgets-in-a-layout-in-pyqt
        """
        if layout is None:
            return

        log.debug("clearing plugin layout")
        for i in reversed(range(layout.count())):
            layout_item = layout.takeAt(i)
            widget = layout_item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                self.clear_plugin_layout(layout_item.layout())
