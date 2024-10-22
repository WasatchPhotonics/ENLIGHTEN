import time
import asyncio
import logging
from queue import Queue

from bleak import discover
from threading import Thread

from enlighten import common
from wasatch.DeviceID import DeviceID

if common.use_pyside2():
    from PySide2 import QtCore, QtGui
    from PySide2.QtWidgets import QDialog, QPushButton, QVBoxLayout, QLabel
else:
    from PySide6 import QtCore, QtGui
    from PySide6.QtWidgets import QDialog, QPushButton, QVBoxLayout, QLabel

log = logging.getLogger(__name__)

class BLEManager:
    """
    Special features required to support and interface with BLE-based spectrometers.

    @todo show progress indicator while reading EEPROM (~15sec)
    @todo show progress indicator while reading spectrum (~4sec)
    """

    def __init__(self, ctl):
        self.ctl = ctl

        self.ble_button = ctl.form.ui.pushButton_bleScan

        self.scans_q = Queue()
        self.loop = asyncio.new_event_loop()

        self.ble_device = None
        self.ble_present = False
        self.ble_device_id = None

        self.original_button_style = self.ble_button.styleSheet()
        self.selection_popup = BLESelector(parent=self.ble_button)

        self.ble_button.clicked.connect(self.search_callback)

        self.ctl.reading_progress_bar.hide()

        self.thread = Thread(target=self.make_async_loop, args=(self.loop,), daemon=True)
        self.thread.start()

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

    def make_async_loop(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def stop(self):
        log.debug(f"calling stop of async loop")
        self.ctl.marquee.info("Closing BLE spectrometers...", immediate=True)
        time.sleep(0.05)
        if self.ble_device_id is not None:
            self.ctl.disconnect_device(self.ctl.multispec.get_spectrometer(self.ble_device_id))
            self.ctl.multispec.set_disconnecting(self.ble_device_id, False)
            self.ble_device_id = None

    def search_callback(self):
        log.debug("Searching for BLE devices")
        if self.ble_present:
            log.debug("BLE clicked while device connected, disconnecting")
            self.ble_present = False
            self.ctl.reading_progress_bar.hide()
            self.ble_button.setStyleSheet(self.original_button_style)
            self.stop()
            return

        # clear anything that might be in the pop up for available devices
        self.selection_popup.clear_plugin_layout(self.selection_popup.layout)
        self.selection_popup.device_widgets.clear()

        # add the throbber for UI/UX
        self.selection_popup.add_throbber()

        # Kick of the async search for BLE Devices and show the pop up
        log.debug("calling perform_discovery")
        asyncio.run_coroutine_threadsafe(self.perform_discovery(), self.loop)
        self.selection_popup.show()

    def connect_callback(self, btn, device):
        log.debug(f"Connecting to {device}")
        self.device = device
        self.selection_popup.hide()

        #self.ble_device = BLEDevice(device, self.loop)
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

    async def perform_discovery(self):
        log.debug("starting discovery")
        devices = await discover()
        # log.debug(f"found devices {devices}")
        wp_devices = [dev for dev in devices if dev.name is not None and ("wp" in dev.name.lower())]
        log.debug(f"adding wp_devices to scans_q: {wp_devices}")
        self.scans_q.put(wp_devices)

class BLESelector(QDialog):
    """
    A pop-up window listing all discovered BLE devices.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("BLE Devices")
        # self.setMinimumSize(300,100)
        self.device_widgets = []
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

    def add_throbber(self):
        self.label = QLabel(self)
        self.label.setObjectName("label")
        self.movie = QtGui.QMovie(":gifs/images/throbbers/EnlightenIconGif.gif")
        self.label.setMovie(self.movie)
        self.movie.start()
        self.layout.addWidget(self.label)

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
