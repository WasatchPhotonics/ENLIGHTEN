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

    def update_visibility(self):
        return

    def stop(self):
        """ 
        Called by Controller at application shutdown.

        There is currently no way to tell self.scan_thread or self.scan_loop to
        stop, but I'm not sure this is a problem.
        """
        return

    def poll_device_id_queue(self):
        """ 
        This is ticked by Controller.tick_bus_listener, meaning it runs inside a
        QTimer and can futz with GUI widgets.
        """
        while not self.device_id_queue.empty():
            device_id = self.device_id_queue.get_nowait()
            if device_id is None:
                log.debug(f"poll_device_id_queue: scan is complete")
                self.ble_selector.set_rescan_enabled(True)
            else:
                self.ble_selector.add_to_table(device_id)
                self.ble_selector.set_rescan_enabled(False)
                self.ble_selector.set_connect_enabled(True)

    def show_selector_callback(self):
        self.ble_selector.show()
        self.ble_selector.reset()

        # we're starting a scan, so disable "Rescan" button
        self.ble_selector.set_rescan_enabled(False)

        # the table starts empty, so disable "Connect" button
        self.ble_selector.set_connect_enabled(False)

        # Kick off the async search for BLE Devices. This is an async function, 
        # but we're not awaiting it -- let it run in its own time.
        device_finder = DeviceFinderBLE(self.device_id_queue)

        log.debug("starting scan")
        asyncio.run_coroutine_threadsafe(
            device_finder.search_for_devices(),
            self.scan_loop)

    def connect_callback(self):
        device_id = self.ble_selector.selected_device_id
        if device_id is None:
            return

        self.ble_selector.reset()
        self.ble_selector.hide()

        # add this DeviceID to the Controller's list of "external" (non-USB) 
        # device IDs to check
        self.ctl.other_device_ids.add(device_id)

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

        try:
            # add horizontal layout with [Connect] and [Rescan] buttons
            button_layout = QHBoxLayout()
            self.bt_connect = QPushButton(text="Connect", parent=self)
            self.bt_rescan = QPushButton(text="Rescan", parent=self)
            button_layout.addWidget(self.bt_connect)
            button_layout.addWidget(self.bt_rescan)
            self.layout.addLayout(button_layout)

            # add QTableWidget with RSSI and Serial Number columns
            self.table = QTableWidget(1, 2, self)
            self.table.horizontalHeader().setStretchLastSection(True)
            self.layout.addWidget(self.table)
            self.table.cellClicked.connect(self.cellClicked_callback)

            self.bt_connect.clicked.connect(ble_manager.connect_callback)
            self.bt_rescan.clicked.connect(ble_manager.show_selector_callback)

            self.table.verticalHeader().hide()
            self.table.horizontalHeader().hide()
        except:
            log.error("exception constructing table", exc_info=1)

        self.init_stylesheet()
        self.reset()

    def set_rescan_enabled(self, flag):
        self.bt_rescan.setEnabled(flag)

    def set_connect_enabled(self, flag):
        self.bt_connect.setEnabled(flag)

    def reset(self):
        self.table.clear()
        self.table.setRowCount(1)

        self.table.setItem(0, 0, QTableWidgetItem("RSSI"))
        self.table.setItem(0, 1, QTableWidgetItem("Serial Number"))

        self.serial_number_to_row = {}
        self.row_to_device_id = {}
        self.selected_device_id = None

    def cellClicked_callback(self, row, column):
        """ The user clicked a table cell, so highlight the whole row (and capture the DeviceID) """
        self.selected_device_id = None

        if row == 0:
            self.table.clearSelection()
            return

        self.table.selectRow(row)
        device_id = self.row_to_device_id.get(row, None)
        if device_id is None:
            log.error(f"row {row} has no DeviceID?!")

        self.selected_device_id = device_id
        log.debug("user selected {device_id}")

    def add_to_table(self, device_id):
        sn = device_id.serial_number

        try:
            if sn in self.serial_number_to_row:
                row = self.serial_number_to_row[sn]
                self.table.setItem(row, 0, QTableWidgetItem(f"{device_id.rssi:0.2f}"))
            else:
                # insert new row
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(f"{device_id.rssi:0.2f}"))
                self.table.setItem(row, 1, QTableWidgetItem(sn))

                # update mappings
                self.serial_number_to_row[sn] = row
                self.row_to_device_id[row] = device_id
        except:
            log.error("exception updating QTableWidget", exc_info=1)

    def init_stylesheet(self):
        """ I tried to apply these through enlighten.css, but couldn't figure it out """
        self.setStyleSheet("""
            QTableView::hover,
            QTableView::item::hover 
            {
                background-color: hsl(0, 0%, 13%);
                border: none;
                color: #F0F0F0;
                gridline-color: #ccc;
            }

            QTableView:selected,
            QTableView::item::selected:hover 
            {
                background: hsl(0, 0%, 36%);
                border: none;
            }

            QTableView::item:pressed
            {
                background-color: hsl(0, 0%, 70%);
                border: none;
            }
        """)
