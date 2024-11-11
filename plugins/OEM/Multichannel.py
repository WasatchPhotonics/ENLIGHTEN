import re
import time
import logging

from EnlightenPlugin import EnlightenPluginBase

log = logging.getLogger(__name__)

class Multichannel(EnlightenPluginBase):

    def get_configuration(self):
        self.name = "Multichannel"
        self.auto_enable = True

        self.field(name="Trigger Spec", datatype=str, direction="output")
        self.field(name="Fan Spec", datatype=str, direction="output")
        self.field(name="Trigger", datatype="button", callback=self.trigger_callback)

        self.trigger_spec = None
        self.trigger_name = None
        self.fan_spec = None
        self.fan_name = None

    def disconnect(self):
        log.critical("closing, so disabling fan")
        if self.fan_spec:
            self.fan_spec.change_device_setting("laser_enable", False)

    def process_request(self, request):

        if self.trigger_spec is None or self.fan_spec is None:
            for spec in self.ctl.multispec.get_spectrometers():
                m = re.match("pos=(\d+);\s*feature=(\S+)", spec.settings.eeprom.user_text)
                if m:
                    pos = int(m.group(1))
                    feature = m.group(2).lower()

                    if feature == "trigger":
                        self.trigger_spec = spec
                        self.trigger_name = f"{spec.settings.eeprom.serial_number} (pos {pos})"
                        log.info(f"found trigger_spec {self.trigger_name}")
                    elif feature == "fan":
                        self.fan_spec = spec
                        self.fan_name = f"{spec.settings.eeprom.serial_number} (pos {pos})"
                        log.info(f"found fan_spec {self.fan_name}")
                        spec.change_device_setting("laser_enable", True)

        self.outputs["Trigger Spec"] = self.trigger_name
        self.outputs["Fan Spec"] = self.fan_name

    def trigger_callback(self):
        if self.trigger_spec is None:
            return

        fid = self.trigger_spec.device.wrapper_worker.connected_device.hardware
        fid.set_laser_enable(True)
        time.sleep(0.005)
        fid.set_laser_enable(False)
