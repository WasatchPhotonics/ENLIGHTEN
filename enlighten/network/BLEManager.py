import time
import asyncio
import logging
from queue import Queue

from threading import Thread

from enlighten import common, util
from wasatch.DeviceFinderBLE import DeviceFinderBLE
from wasatch.BLEDevice       import BLEDevice # for get_run_loop

if common.use_pyside2():
    from PySide2 import QtCore, QtGui
    from PySide2.QtWidgets import QDialog, QPushButton, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QLabel
else:
    from PySide6 import QtCore, QtGui
    from PySide6.QtWidgets import QDialog, QPushButton, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QLabel

log = logging.getLogger(__name__)

class BLEManager:
    """
    Provides GUI allowing user to select a Wasatch BLE spectrometer for connection.

    @see detailed BLE architecture in wasatch.BLEDevice
    """

    def __init__(self, ctl):
        self.ctl = ctl
        cfu = ctl.form.ui

        self.discovered_device_queue = Queue() # holds wasatch.DeviceFinderBLE.DiscoveredBLEDevices

        self.ble_selector = BLESelector(ble_manager=self, parent=cfu.pushButton_show_ble_selector)
        cfu.pushButton_show_ble_selector.clicked.connect(self.show_selector_callback)

        # @todo move to AutoRaman
        cfu.readingProgressBar.hide()

        # grab an asyncio run_loop in which to call DeviceFinderBLE's async methods
        self.scan_loop = BLEDevice.get_run_loop()

    def show_selector_callback(self):
        self.ble_selector.show()
        self.ble_selector.reset()

        # we're starting a scan, so disable "Rescan" button
        self.ble_selector.set_rescan_enabled(False)

        # the table starts empty, so disable "Connect" button
        self.ble_selector.set_connect_enabled(False)

        self.device_finder = DeviceFinderBLE(self.discovered_device_queue)

        # Kick off the async search for BLE Devices. This is an async function, 
        # but we're not awaiting it -- let it run in its own time.
        log.debug("starting scan")
        asyncio.run_coroutine_threadsafe(
            self.device_finder.search_for_devices(),
            self.scan_loop)

    def poll_discovered_device_queue(self):
        """ 
        This is ticked by Controller.tick_bus_listener, meaning it runs inside a
        QTimer and can futz with GUI widgets.
        """
        while not self.discovered_device_queue.empty():
            discovered_device = self.discovered_device_queue.get_nowait()
            if discovered_device is None:
                log.debug(f"poll_discovered_device_queue: scan is complete")
                self.ble_selector.set_rescan_enabled(True)
            else:
                self.ble_selector.add_to_table(discovered_device)
                self.ble_selector.set_rescan_enabled(False)
                self.ble_selector.set_connect_enabled(True)

    def connect_callback(self):
        device_id = self.ble_selector.selected_device_id
        if device_id is None:
            return

        self.device_finder.stop_scanning()
        self.device_finder = None

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
    | ***  WP-01234         |
    | *    WP-01228         |
    | **   WP-01499         |
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
        """ 
        The user clicked a table cell, so highlight the whole row (and cache the
        DeviceID for BLEManager.connect_callback).
        """
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

    def add_to_table(self, discovered_device):
        """
        @param discovered_device: a wasatch.DeviceFinderBLE.DiscoveredBLEDevice
        """
        device_id = discovered_device.device_id
        rssi = discovered_device.rssi
        serial_number = device_id.serial_number

        rssi_str = f"{rssi:0.2f}"
        rssi_str = self.rssi_to_bars(rssi)

        try:
            if serial_number in self.serial_number_to_row:
                # we've seen this device before, so just update the previous RSSI
                row = self.serial_number_to_row[serial_number]
                self.table.setItem(row, 0, QTableWidgetItem(rssi_str))
            else:
                # new device, so insert new row
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(rssi_str))
                self.table.setItem(row, 1, QTableWidgetItem(serial_number))

                # update mappings
                self.serial_number_to_row[serial_number] = row
                self.row_to_device_id[row] = device_id
        except:
            log.error("exception updating QTableWidget", exc_info=1)

    def rssi_to_bars(self, rssi):
        cnt = 3 if rssi > -60 else 2 if rssi > -85 else 1
        bullet = util.get_bullet()
        return bullet * cnt # 🛜 📶

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
