import logging

log = logging.getLogger(__name__)

##
# Control the "high gain" mode on Hamamatsu InGaAs detectors (on or off).
#
# Note this completely unrelated to normal "detector gain" on Hamamatsu silicon 
# detectors (a FunkyFloat above 1.0), and likewise unrelated to the "gain dB" on
# Sony IMX detectors (a float from 0.0 - 31.9 or so).
#
# Note this feature supports "locking" via Multispec.
class HighGainModeFeature:

    CONFIG_KEY = "high_gain_mode_enabled"

    def __init__(self,
            cb_enabled,
            config,
            multispec):

        self.cb_enabled = cb_enabled
        self.multispec  = multispec

        self.cb_enabled.toggled.connect(self.enable_callback)
        self.cb_enabled.setVisible(False)

    def init_hotplug(self):
        spec = self.multispec.current_spectrometer()
        if spec is None:
            return

        if not self.is_supported(spec):
            return

        sn = spec.settings.eeprom.serial_number
        if self.config.has_option(sn, self.CONFIG_KEY):
            flag = self.config.get_bool(sn, self.CONFIG_KEY)
            log.debug(f"restoring previously-saved high-gain mode {flag}")
        else:
            flag = self.recommended_default(spec)
            log.debug(f"defaulting high-gain mode to {flag}")
        
        self.cb_enabled.setChecked(flag)

    def update_visibility(self):
        spec = self.multispec.current_spectrometer()
        if spec is None:
            return

        supported = self.is_supported(spec)
        self.cb_enabled.setVisible(supported)
        if not supported:
            return

        self.cb_enabled.setChecked(spec.settings.state.high_gain_mode_enabled)

    def is_supported(self, spec):
        """ I believe that all Andor iDus detectors (incl DV416 and DU490) support multiple gain modes. """
        if spec is None:
            return False
        return spec.settings.is_ingaas() or spec.device.is_andor()

    def recommended_default(self, spec):
        """ Default high for Raman models, low for referenced-based techniques """
        if spec is None:
            return False
        return spec.settings.eeprom.has_excitation() 

    def enable_callback(self):
        spec = self.multispec.current_spectrometer()
        if spec is None or not self.is_supported(spec):
            return

        enabled = self.cb_enabled.isChecked()
        self.multispec.set_state("high_gain_mode_enabled", enabled)
        self.multispec.change_device_setting("high_gain_mode_enable", enabled)

        sn = spec.settings.eeprom.serial_number
        self.config.set(sn, "high_gain_mode_enabled", enabled)

