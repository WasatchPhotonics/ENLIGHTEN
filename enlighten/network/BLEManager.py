import os
import time
import asyncio
import logging
from queue import Queue

from bleak import discover, BleakClient, BleakScanner
from bleak.exc import BleakError
from threading import Thread

from enlighten import common
from wasatch.DeviceID import DeviceID

if common.use_pyside2():
    from PySide2 import QtCore, QtWidgets, QtGui
    from PySide2.QtWidgets import QApplication, QDialog, QMainWindow, QPushButton, QVBoxLayout, QLabel
else:
    from PySide6 import QtCore, QtWidgets, QtGui
    from PySide6.QtWidgets import QApplication, QDialog, QMainWindow, QPushButton, QVBoxLayout, QLabel

log = logging.getLogger(__name__)

class BLEManager:
    """
    Special features required to support and interface with BLE-based spectrometers.

    @todo show progress indicator while reading EEPROM (~15sec)
    @todo show progress indicator while reading spectrum (~4sec)
    """

    def __init__(self, 
                 marquee,
                 ble_button, 
                 controller_connect,
                 controller_disconnect,
                 progress_bar,
                 multispec):
        self.scans_q = Queue()
        self.ble_present = False
        self.marquee = marquee
        self.multispec = multispec
        self.ble_button = ble_button
        self.progress_bar = progress_bar
        self.ble_btn_stlye = ble_button.styleSheet()
        self.controller_connect = controller_connect
        self.controller_disconnect = controller_disconnect
        self.selection_popup = BLESelector(parent=self.ble_button)
        self.ble_button.clicked.connect(self.ble_btn_click)
        self.ble_device_id = None
        self.loop = asyncio.new_event_loop()
        self.ble_device = None
        self.progress_bar.hide()
        self.thread = Thread(target=self.make_async_loop, args=(self.loop,), daemon=True)
        self.thread.start()

    def check_complete_scans(self):
        log.debug(f"checking for scans and queue is empty {self.scans_q.empty()}")
        if not self.scans_q.empty():
            wp_devices = self.scans_q.get_nowait()
            self.selection_popup.clear_plugin_layout(self.selection_popup.layout)
            if wp_devices != []:
                for d in wp_devices:
                    btn = QPushButton()
                    btn.setText(str(d.name))
                    log.debug(f"In complete scan found device {d}")
                    btn.clicked.connect(lambda: self.ble_discover_click(btn, d))
                    self.selection_popup.device_widgets.append(btn)
                    self.selection_popup.layout.addWidget(btn)
            else:
                label =  QLabel()
                label.setText("No WP Devices found.")
                label.setAlignment(QtCore.Qt.AlignCenter)
                self.selection_popup.layout.addWidget(label)

    def make_async_loop(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def stop(self):
        log.debug(f"calling stop of async loop")
        self.marquee.info("Closing BLE spectrometers...", immediate=True)
        time.sleep(0.05)
        if self.ble_device_id is not None:
            self.controller_disconnect(self.multispec.get_spectrometer(self.ble_device_id))
            self.multispec.set_disconnecting(self.ble_device_id, False)
            self.ble_device_id = None

    def ble_btn_click(self):
        log.debug("ble button clicked, creating task")
        if self.ble_present:
            log.debug("BLE btn clicked while device connected, disconnecting")
            self.ble_present = False
            self.progress_bar.hide()
            self.ble_button.setStyleSheet(self.ble_btn_stlye)
            self.stop()
            return
        # clear anything that might be in the pop up for available devices
        self.selection_popup.clear_plugin_layout(self.selection_popup.layout)
        self.selection_popup.device_widgets.clear()
        # add the throbber for UI/UX
        self.selection_popup.add_throbber()
        log.debug("calling soon perform discovery")
        # Kick of the async search for BLE Devices and show the pop up
        asyncio.run_coroutine_threadsafe(self.perform_discovery(), self.loop)
        self.selection_popup.show()

    def ble_discover_click(self, btn, device):
        log.debug(f"ble device button clicked device is {device}")
        self.device = device
        self.selection_popup.hide()
        self.perform_connect(btn, device)

    def perform_connect(self, btn, device):
        log.debug(f"called to perform connect on btn {btn} with text {btn.text()}")
        #self.ble_device = BLEDevice(device, self.loop)
        self.ble_device_id = DeviceID(label=f"BLE:{device.address}:{device.name}")
        ok = self.controller_connect(self.ble_device_id)
        self.ble_present = True
        if ok:
            self.ble_button.setStyleSheet("background-color: blue")

    async def perform_discovery(self):
        log.debug("starting discovery")
        devices = await discover()
        log.debug(f"found devices of {devices}")
        wp_devices = [dev for dev in devices if dev.name is not None and ("wp" in dev.name.lower())]
        log.debug(f"wp_devices is {wp_devices}")
        self.scans_q.put(wp_devices)

class BLESelector(QDialog):
    """
    A pop-up window listing all discovered BLE devices.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("BLE Devices")
        #self.setMinimumSize(300,100)
        self.device_widgets = []
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

    def add_throbber(self):
        self.label = QLabel(self)
        self.label.setObjectName("label")
        log.info(f"getting gif from path :gifs/images/throbbers/EnlightenIconGif.gif")
        self.movie = QtGui.QMovie(":gifs/images/throbbers/EnlightenIconGif.gif")
        self.label.setMovie(self.movie)
        self.movie.start()
        self.layout.addWidget(self.label)

    def clear_plugin_layout(self, layout):
        """
        Same as plugin Controller.
        Need to clear all depending the layout recursively.
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
