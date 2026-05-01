import time
import asyncio
import logging
from queue import Queue

from threading import Thread

from enlighten import common, util
from enlighten.EnlightenFeature import EnlightenFeature
from wasatch.DeviceFinderBLE import DeviceFinderBLE
from wasatch.BLEDevice       import BLEDevice # for get_run_loop

if common.use_pyside2():
    from PySide2 import QtCore, QtGui
    from PySide2.QtWidgets import QDialog, QPushButton, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QLabel, QAbstractItemView
else:
    from PySide6 import QtCore, QtGui
    from PySide6.QtWidgets import QDialog, QPushButton, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QLabel, QAbstractItemView

log = logging.getLogger(__name__)

class BLEManagerFeature(EnlightenFeature):
    """
    Provides GUI allowing user to select a Wasatch Bluetooth® LE spectrometer for
    connection.

    Note that all displayed strings, labels etc referencing BLE should utilize the
    full "Bluetooth® LE" registered trademark. Internal variables, class names, 
    methods etc may using the BLE abbreviation as long as those are not exposed 
    in the public GUI.

    @see detailed Bluetooth® LE architecture in wasatch.BLEDevice
    """

    def __init__(self, ctl):
        super().__init__(ctl)

        cfu = ctl.form.ui

        self.bt_ble = cfu.pushButton_show_ble_selector

        self.discovered_device_queue = Queue() # holds wasatch.DeviceFinderBLE.DiscoveredBLEDevices
        self.connected = False

        self.ble_selector = BLESelector(ble_manager=self, parent=self.bt_ble)
        self.bt_ble.clicked.connect(self.button_callback)

        # @todo move to AutoRaman
        cfu.readingProgressBar.hide()

        # grab an asyncio run_loop in which to call DeviceFinderBLE's async methods
        self.scan_loop = BLEDevice.get_run_loop()

    def init_hotplug(self):
        self.refresh_connected()

    def disconnect(self):
        """ 
        Try to disconnect the currently-connected spectrometer, but ENLIGHTEN is
        staying up and may reconnect later.
        """
        log.debug("disconnect: start")
        spec = self.get_connected_ble_spectrometer()
        if spec:
            spec.device.disconnect()
        self.refresh_connected()
        log.debug("disconnect: done")

    def stop(self):
        """ ENLIGHTEN is shutting down, so disconnect everything ASAP """
        log.debug("stop: start")
        spec = self.get_connected_ble_spectrometer(include_disconnecting=True)
        if spec:
            spec.device.disconnect()
        log.debug("stop: done")

    def refresh_connected(self):
        spec = self.get_connected_ble_spectrometer()
        self.connected = spec is not None
        self.ctl.gui.colorize_button(self.bt_ble, self.connected, active_color="blue")

        if self.connected:
            tt = "Disconnect Bluetooth® LE spectrometer"
        else:
            tt = "Scan for Bluetooth® LE spectrometers"
        self.bt_ble.setToolTip(tt)

    def get_connected_ble_spectrometer(self, include_disconnecting=False):
        for spec in self.ctl.multispec.get_spectrometers():
            if spec.device_id.is_ble() and (include_disconnecting or not self.ctl.multispec.is_disconnecting(spec.device_id)):
                return spec

    def button_callback(self):
        spec = self.get_connected_ble_spectrometer()
        if spec:
            # un-pair
            spec.device.disconnect()

            # remove from ENLIGHTEN GUI
            self.ctl.disconnect_device(spec)
            return

        # apparently we weren't connected, so prompt to select
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
        log.debug(f"adding {device_id} to Controller external search list")
        self.ctl.other_device_ids.add(device_id)

class BLESelector(QDialog):
    """
    A pop-up window listing all discovered Bluetooth® LE devices.

    +-----------------------+
    | BLE Spectrometers [x] |
    +-----------------------+
    | [Connect]    [Rescan] |
    |                       |
    | Signal Serial Number  |
    | ***    WP-01234       |
    | *      WP-01228       |
    | **     WP-01499       |
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

            self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
            self.table.cellClicked.connect(self.cellClicked_callback)
            self.table.selectionModel().selectionChanged.connect(self.selectionChanged_callback)

            self.bt_connect.clicked.connect(ble_manager.connect_callback)
            self.bt_rescan.clicked.connect(ble_manager.button_callback)

            self.table.verticalHeader().setVisible(False)
            self.table.horizontalHeader().setVisible(False)
        except:
            log.error("exception constructing table", exc_info=1)

        # @todo move to enlighten.css 
        self.setStyleSheet("""QTableView::item::selected, QTableView::item::selected:hover { background: darkblue; color: silver }""")

        self.reset()

    def set_rescan_enabled(self, flag):
        self.bt_rescan.setEnabled(flag)

    def set_connect_enabled(self, flag):
        self.bt_connect.setEnabled(flag)

    def reset(self):
        self.table.clear()
        self.table.setRowCount(1)

        self.table.setItem(0, 0, QTableWidgetItem("Signal"))
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
        log.debug(f"user selected {device_id}")

    def selectionChanged_callback(self):
        items = self.table.selectedItems()
        for item in items:
            row = item.row()

            device_id = self.row_to_device_id.get(row, None)
            if device_id is None:
                log.error(f"row {row} has no DeviceID?!")

            self.selected_device_id = device_id
            log.debug(f"user selected {device_id}")

    def add_to_table(self, discovered_device):
        """
        @param discovered_device: a wasatch.DeviceFinderBLE.DiscoveredBLEDevice
        """
        device_id = discovered_device.device_id
        rssi = discovered_device.rssi
        serial_number = device_id.serial_number

        rssi_num_str = f"RSSI {rssi:0.2f}"
        rssi_bar_str = self.rssi_to_bars(rssi)
        rssi_item = QTableWidgetItem(rssi_bar_str)
        rssi_item.setToolTip(rssi_num_str)

        try:
            if serial_number in self.serial_number_to_row:
                # we've seen this device before, so just update the previous RSSI
                row = self.serial_number_to_row[serial_number]
                self.table.setItem(row, 0, rssi_item)
            else:
                # new device, so insert new row
                row = self.table.rowCount()
                self.table.insertRow(row)

                self.table.setItem(row, 0, rssi_item)
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
