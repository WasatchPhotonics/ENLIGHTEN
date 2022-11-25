import os
import json
import logging
from typing import Optional

from PySide2.QtWidgets import QFileDialog

from .Spectrometer import Spectrometer
from wasatch.WasatchDeviceWrapper import WasatchDeviceWrapper
from wasatch.MockUSBDevice import MockUSBDevice
from wasatch.DeviceID import DeviceID

log = logging.getLogger(__name__)

class MockManager:

    # mock_defaults will be available for generated spectra option
    mock_defaults = {"WP-785-ER": ("WP_785_ER", "WP_785_ER.json"),
                     "NIR1": ("WP_00998_NIR1", "WP_00998.json")}

    def __init__(self,
                 cb_via_file,
                 combo_compound,
                 combo_virtual,
                 connect_btn,
                 connect_new,
                 lamp_btn,
                 disconnect,
                 label_or,
                 label_sample,
                 gui,
                 multispec) -> None:

        self.connected = False

        # Functions and Classes
        self.connect_new = connect_new
        self.multispec = multispec
        self.disconnect = disconnect
        self.combo_virtual = combo_virtual
        self.gui = gui

        # UI
        self.combo_compound = combo_compound
        self.cb_file = cb_via_file
        self.connect_btn = connect_btn
        self.lamp_btn = lamp_btn
        self.lamp_enabled = False

        self.connect_btn.clicked.connect(self.connect)
        self.lamp_btn.clicked.connect(self.toggle_lamp)
        self.combo_compound.currentIndexChanged.connect(self.update_reading)

        # Not satisfied with the current generated spectra
        # For version one only doing files but not throwing
        # away what I have, hiding for now
        self.combo_virtual.hide()
        self.lamp_btn.hide()
        label_or.hide()
        label_sample.hide()
        self.cb_file.setChecked(True)
        self.cb_file.setEnabled(False)

    def connect(self) -> None:
        if self.connected:
            log.debug(f"MOCK MGR DISCONNECT CALLED")
            self.connected = False
            spec = self.get_mock_spec()
            self.disconnect(spec)
            self.lamp_btn.hide()
            self.connect_btn.setText("Connect")
            return

        if self.cb_file.isChecked():
            mock_id_str = self.obtain_mock_id()
            if mock_id_str is None:
                return
            log.debug(f"mock connect got id str of {mock_id_str}")
            sim_spec = DeviceID(label=mock_id_str)
        else:
            selected_default = self.combo_virtual.currentText()
            folder, eeprom = self.mock_defaults.get(selected_default, (None,None))
            if folder != None and eeprom != None:
                sim_spec = DeviceID(label=f"MOCK:{folder}:{eeprom}")
            else:
                return

        self.connect_new(sim_spec)
        self.connected = True
        self.connect_btn.setText("Disconnect")

    def initialize_mock(self, device: WasatchDeviceWrapper):
        self.combo_compound.clear()
        mock_device = device.wrapper_worker.connected_device.hardware.device_type
        with open(os.path.join(os.getcwd(), "enlighten", "assets", "example_data", "mock_raman", "mocks.json")) as f:
            mock_spectra_info = json.load(f)
            log.debug(f"generating readings for mock spectrometer")
            mock_device.generate_readings(mock_spectra_info)
        if not device.settings.eeprom.has_laser:
            self.lamp_btn.show()
        else:
            self.lamp_btn.hide()
        spectra = mock_device.get_available_spectra()
        for s in spectra:
            self.combo_compound.addItem(s.capitalize())


    def obtain_mock_id(self) -> Optional[str]:
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.Directory)
        if dialog.exec_():
            abs_folder_name = dialog.selectedUrls()[0].toLocalFile()
            spec_name = os.path.basename(abs_folder_name)
            eeprom_folder = os.path.join(abs_folder_name, "eeprom")
            eeprom_file = [f for f in os.listdir(eeprom_folder) if os.path.isfile(os.path.join(eeprom_folder, f)) and f.endswith(".json")]
            if len(eeprom_file) == 1:
                return f"MOCK:{spec_name}:{eeprom_file[0]}"
            else:
                log.error("Error with eeprom file or eeprom directory. Got results of {eeprom_file}")
                return None

    def get_mock_spec(self) -> Optional[Spectrometer]:
        if not self.connected:
            return None

        specs = self.multispec.get_spectrometers()

        for spec in specs:
            if spec.device.mock:
                return spec

        return None

    def get_mock_device(self) -> Optional[MockUSBDevice]:
        mock_spec = self.get_mock_spec()

        if mock_spec is None:
            return None
        else:
            return mock_spec.device.wrapper_worker.connected_device.hardware.device_type

    def toggle_lamp(self):
        mock_dev = self.get_mock_device()
        if mock_dev:
            mock_dev.toggle_lamp()
        # lamp enabled is duplicated here for later decision of will a virtual lamp be
        # per spectrometer or if there is a virtual light source should it be shared between specs
        self.lamp_enabled = not self.lamp_enabled
        self.color_lamp_btn(self.lamp_enabled)

    def color_lamp_btn(self, enabled):
        self.gui.colorize_button(self.lamp_btn, enabled)

    def update_reading(self) -> None:
        reading = self.combo_compound.currentText().lower()
        mock_dev = self.get_mock_device()
        mock_dev.set_active_readings(reading)
