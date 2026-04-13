import logging

from EnlightenPlugin import EnlightenPluginBase
from wasatch.BLEDevice import BLEDevice

log = logging.getLogger(__name__)

class BluetoothTester(EnlightenPluginBase):

    def get_configuration(self):
        self.name = "Bluetooth® LE Tester"
        self.streaming = False
        self.process_requests = False

        self.field(name="Power Watchdog Sec",    datatype=int,        callback=self.power_watchdog_sec, initial=0, minimum=0, maximum=600)
        self.field(name="Laser Warning Sec",     datatype=int,        callback=self.laser_warning_delay_sec, initial=2, minimum=0, maximum=10)
        self.field(name="Laser TEC Mode",        datatype="combobox", callback=self.laser_tec_mode, choices=list(BLEDevice.LASER_TEC_MODES.values()))
        self.field(name="Image Sensor State",    datatype="button",   callback=self.image_sensor_state)
        self.field(name="Update Status",         datatype="button",   callback=self.update_status)
        self.field(name="Reset",                 datatype="button",   callback=self.reset)
        self.field(name="Power Off",             datatype="button",   callback=self.power_off)

        self.change_setting("testing", True)

    def change_setting(self, setting, value):
        spec = self.ctl.current_spectrometer()
        if spec:
            spec.change_device_setting(setting, value)

    def laser_tec_mode          (self): self.change_setting("laser_tec_mode",           self.get_widget_from_name("Laser TEC Mode").currentIndex())
    def laser_warning_delay_sec (self): self.change_setting("laser_warning_delay_sec",  self.get_widget_from_name("Laser Warning Sec").value())
    def power_watchdog_sec      (self): self.change_setting("power_watchdog_sec",       self.get_widget_from_name("Power Watchdog Sec").value())
    def image_sensor_state      (self): self.change_setting("get_image_sensor_state")
    def update_status           (self): self.change_setting("update_status")
    def reset                   (self): self.change_setting("reset")
    def power_off               (self): self.change_setting("power_off")
