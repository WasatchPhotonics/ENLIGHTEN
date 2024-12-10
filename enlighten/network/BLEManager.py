import time
import asyncio
import logging
from queue import Queue

from threading import Thread

from enlighten import common
from wasatch.DeviceFinderBLE import DeviceFinderBLE

if common.use_pyside2():
    from PySide2 import QtCore, QtGui
    from PySide2.QtWidgets import QDialog, QPushButton, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QLabel
else:
    from PySide6 import QtCore, QtGui
    from PySide6.QtWidgets import QDialog, QPushButton, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QLabel

log = logging.getLogger(__name__)

class BLEManager:
    """
    Allows user to connect to nearby wasatch.BLEDevices.

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

    @par Threading

    self.scan_loop runs forever inside self.scan_thread. They are created when ENLIGHTEN is 
    launched and exit at shutdown.

     _self.scan_thread__
    | self.scan_loop    |
    |___________________|

    self.scan_loop is passed in the call to perform_discovery (kick-off a scan), as the 
    loop in which perform_discovery runs:

        asyncio.run_coroutine_threadsafe(self.perform_discovery(), self.scan_loop)

    """

    def __init__(self, ctl):
        self.ctl = ctl
        cfu = ctl.form.ui

        # this is the button above the main graph stating "BLE", used to display
        # the BLESelector dialog
        self.bt_show_selector = cfu.pushButton_show_ble_selector
        self.progress_bar = cfu.readingProgressBar

        self.device_id_queue = Queue() # queue of wasatch.DeviceID

        self.ble_device = None
        self.connected = False
        self.ble_device_id = None

        self.original_button_style = self.bt_show_selector.styleSheet()
        self.ble_selector = BLESelector(ble_manager=self, parent=self.bt_show_selector)

        self.bt_show_selector.clicked.connect(self.show_selector_callback)

        # @todo move to AutoRaman
        self.progress_bar.hide()

        # create a persistent thread in which to run BleakScanner, so we're not 
        # blocking the GUI loop when the button is pressed

        self.scan_loop = asyncio.new_event_loop()
        self.scan_thread = Thread(target=self.make_scan_loop, daemon=True)
        self.scan_thread.start()

    def make_scan_loop(self):
        asyncio.set_event_loop(self.scan_loop)
        self.scan_loop.run_forever()

    def poll_device_id_queue(self):
        """ 
        This is ticked by Controller.tick_bus_listener, meaning it runs inside a
        QTimer and can futz with GUI widgets.
        """
        while not self.device_id_queue.empty():
            device_id = self.device_id_queue.get_nowait()
            log.debug(f"poll_device_id_queue: add_to_table {device_id}")
            self.ble_selector.add_to_table(device_id)

    def stop(self):
        """ Called by Controller at application shutdown """
        self.ctl.marquee.info("Closing BLE spectrometers...", immediate=True)
        time.sleep(0.05)
        if self.ble_device_id is not None:
            self.ctl.disconnect_device(self.ctl.multispec.get_spectrometer(self.ble_device_id))
            self.ctl.multispec.set_disconnecting(self.ble_device_id, False)
            self.ble_device_id = None

    def show_selector_callback(self):
        log.debug("BLE button clicked")
        if self.connected:
            log.debug("disconnecting from BLE device")
            self.connected = False
            self.bt_show_selector.setStyleSheet(self.original_button_style)
            self.stop()
            return

        log.debug("showing BLESelector")
        self.ble_selector.reset()
        self.ble_selector.show()

        # Kick off the async search for BLE Devices. This is an async function, 
        # but we're not awaiting it -- let it run in its own time.
        log.debug("calling perform_discovery")
        self.perform_discovery()

    def perform_discovery(self):
        log.debug("perform_discovery: start")
        device_finder = DeviceFinderBLE(self.device_id_queue)

        asyncio.run_coroutine_threadsafe(
            device_finder.search_for_devices(),
            self.scan_loop)

        log.debug("perform_discovery: done")

    def rescan_callback(self):
        log.debug("user clicked [rescan]")
        self.start_scan()

    def connect_callback(self):
        self.ble_device_id = self.ble_selector.selected_device_id
        if self.ble_device_id is None:
            return

        log.debug(f"Connecting to {self.ble_device_id}")
        self.ble_selector.hide()
        self.ble_selector.reset()

        # add this DeviceID to the Controller's list of "external" (non-USB) 
        # device IDs to check
        self.ctl.other_device_ids.append(self.ble_device_id)

        ok = self.ctl.connect_new(self.ble_device_id)
        self.connected = True

    def update_visibility(self):
        if self.connected:
            self.bt_show_selector.setStyleSheet("background-color: #4a5da9")
        else:
            self.bt_show_selector.setStyleSheet(self.original_button_style)

class BLESelector(QDialog):
    """
    A pop-up window listing all discovered BLE devices.

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
    """
    def __init__(self, ble_manager, parent=None):
        super().__init__(parent)

        self.ble_manager = ble_manager

        self.setWindowTitle("BLE Spectrometers")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # add horizontal layout with [Connect] and [Rescan] buttons
        button_layout = QHBoxLayout()
        self.bt_connect = QPushButton(text="Connect", parent=self)
        self.bt_rescan = QPushButton(text="Rescan", parent=self)
        button_layout.addWidget(self.bt_connect)
        button_layout.addWidget(self.bt_rescan)
        self.layout.addLayout(button_layout)

        # add QTableWidget with RSSI and Serial Number columns
        self.table = QTableWidget(0, 2, self)
        self.table.setHorizontalHeaderLabels(["RSSI", "Serial Number"])
        self.layout.addWidget(self.table)
        self.table.cellClicked.connect(self.cellClicked_callback)

        self.bt_connect.clicked.connect(ble_manager.connect_callback)
        self.bt_rescan.clicked.connect(ble_manager.rescan_callback)

        self.reset()

    def reset(self):
        self.table.clear()
        self.serial_number_to_row = {}
        self.selected_serial_number = None

    def cellClicked_callback(self, row, column):
        log.debug(f"user clicked row {row}, column {column}")
        item = self.table.item(row, 1)
        self.selected_serial_number = item.text()
        log.debug(f"user selected {self.selected_serial_number}")

    def add_to_table(self, device_id):
        log.debug("add_to_table: start")
        sn = device_id.serial_number

        try:
            log.debug(f"add_to_table: sn {sn}")
            if sn in self.serial_number_to_row:
                row = self.serial_number_to_row.get(sn)
                self.table.setItem(row, 0, item=QTableWidgetItem(f"{device_id.rssi:0.2f}"))
            else:
                row = self.table.rowCount()
                self.serial_number_to_row[sn] = row

                log.debug(f"inserting row {row}")
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(f"{device_id.rssi:0.2f}"))
                self.table.setItem(row, 1, QTableWidgetItem(sn))
        except:
            log.error("exception updating QTableWidget", exc_info=1)

        log.debug("add_to_table: done")
