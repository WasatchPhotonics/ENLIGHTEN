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

    default_compounds = ["Dark", "Cyclohexane"]

    def __init__(self,
                 cb_via_file,
                 combo_compound,
                 connect_btn,
                 connect_new,
                 disconnect,
                 multispec) -> None:

        self.connected = False

        # Functions and Classes
        self.connect_new = connect_new
        self.multispec = multispec
        self.disconnect = disconnect

        # UI
        self.combo_compound = combo_compound
        self.cb_file = cb_via_file
        self.connect_btn = connect_btn

        self.connect_btn.clicked.connect(self.connect)
        self.combo_compound.currentIndexChanged.connect(self.update_reading)

    def connect(self) -> None:
        if self.connected:
            log.debug(f"MOCK MGR DISCONNECT CALLED")
            self.connected = False
            spec = self.get_mock_spec()
            self.disconnect(spec)
            self.connect_btn.setText("Connect")
            return

        if self.cb_file.isChecked():
            mock_id_str = self.obtain_mock_id()
            if mock_id_str is None:
                return
            log.debug(f"mock connect got id str of {mock_id_str}")
            sim_spec = DeviceID(label=mock_id_str)
        else:
            sim_spec = DeviceID(label="MOCK::")

        self.connect_new(sim_spec)
        self.connected = True
        self.connect_btn.setText("Disconnect")

    def initialize_mock(self, device: WasatchDeviceWrapper):
        mock_device = device.wrapper_worker.connected_device.hardware.device_type
        spectra = mock_device.get_available_spectra()
        self.combo_compound.clear()
        if mock_device.rasa_virtual:
            with open(os.path.join(os.getcwd(), "enlighten", "assets", "example_data", "mock_raman", "mocks.json")) as f:
                mock_spectra_info = json.load(f)
                log.debug(f"generating readings for mock spectrometer")
                mock_device.generate_readings(mock_spectra_info)
                for default in self.default_compounds:
                    self.combo_compound.addItem(default)
        else:
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

    def update_reading(self) -> None:
        reading = self.combo_compound.currentText().lower()
        mock_dev = self.get_mock_device()
        mock_dev.set_active_readings(reading)
