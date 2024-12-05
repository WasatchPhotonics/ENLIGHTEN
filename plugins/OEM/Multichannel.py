import re
import time
import logging

from EnlightenPlugin import EnlightenPluginBase

log = logging.getLogger(__name__)

class Multichannel(EnlightenPluginBase):
    """
    This plugin is provided to control so-called "multichannel" spectrometer 
    systems where two or more spectrometers (at least eight have been tested) are
    wired together for simultaneous measurements using "external hardware 
    triggering."

    Although most Wasatch spectrometers have an "external_trigger_in" pin to 
    *receive* external triggers, many do not have an available output GPIO
    discrete for use in *generating* trigger signals. Therefore, when using
    X/XM series FX2-based spectrometers (R0 and R2 detectors tested), we can
    use the laser_enable pin on one spectrometer as a "controllable output 
    discrete". 

    That pin can then be multiplexed into the "external_hardware_in" pins on 
    several spectrometers -- including the "trigger master" unit! -- to cause the
    entire set of spectrometers to start a new acquisition at nearly the same time.

    ("Nearly" due to the necessarily free-running function of CCDs which keeps 
    each detector "empty" and ready to start a new acquisition with minimal 
    latency -- literally the minimum integration time of a given model, irrespect-
    ive of the currently configured integration time.)

    Obviously, if the laser_enable signal is being re-used in this manner, then
    the signal cannot easily be used for Raman operation, so this multichannel
    architecture is essentially limited to non-Raman applications.

    @par EEPROM Configuration

    This plugin assumes that the connected units each have Page 4 (User Data)
    populated with a string matching one of the following patterns:

    - "pos=n" (where n is an integer in the range 0-127)
    - "pos=n;feature=FEATURE" (where FEATURE is either "trigger" or "fan")

    Examples:

    - pos=1;feature=trigger
    - pos=2;feature=fan
    - pos=3
    - ...
    - pos=8

    """

    def get_configuration(self):
        self.name = "Multichannel"

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
        super().disconnect()

    def process_request(self, request):
        """
        This plugin doesn't actually do anything with spectra, but this is a 
        convenient place to update the outputs for the Trigger and Fan fields.
        """

        # If we have not yet identified the connected spectrometers whose "User 
        # Data" EEPROM page indicates that they are the "master" for acquisition
        # triggering and fan control, then perform that scan now.
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

                        # having found the fan controller, enable it
                        spec.change_device_setting("laser_enable", True)

        self.outputs["Trigger Spec"] = self.trigger_name
        self.outputs["Fan Spec"] = self.fan_name

    def trigger_callback(self):
        """
        The user has clicked the "Trigger" button on the plugin GUI, so briefly 
        pulse laser_enable on the spectrometer configured as the "trigger master"
        """
        if self.trigger_spec is None:
            return

        # This is a cross-thread direct handle to the wasatch.FeatureInterfaceDevice
        # of the spectrometer providing the trigger "master" through its laser_enable
        # output. 
        #
        # Normally we "queue" commands to a spectrometer through 
        # enlighten.Spectrometer.change_device_setting, but in this case most of the
        # spectrometers will likely be in external triggering mode, and therefore
        # blocking on attempted spectral reads, and so wouldn't be "checking" for
        # newly queued commands. 
        #
        # This short-circuits the entire Wasatch.PY architecture and allows the 
        # application to emit an EP0 control packet from one thread even while 
        # the WrapperWorker thread is blocking on a read of a bulk endpoint.
        fid = self.trigger_spec.device.wrapper_worker.connected_device.hardware
        
        # We haven't characterized trigger pulse width requirements, but empirical
        # testing indicates that 5ms seems to work.
        fid.set_laser_enable(True)
        time.sleep(0.005)
        fid.set_laser_enable(False)
