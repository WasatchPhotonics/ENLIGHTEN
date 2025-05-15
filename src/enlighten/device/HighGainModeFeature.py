import logging

log = logging.getLogger(__name__)

class HighGainModeFeature:
    """
    Control the "high gain" mode on Hamamatsu InGaAs detectors (on or off).
    
    Note this completely unrelated to normal "detector gain" on Hamamatsu silicon 
    detectors (a FunkyFloat above 1.0), and likewise unrelated to the "gain dB" on
    Sony IMX detectors (a float from 0.0 - 32.0 or so).
    """

    CONFIG_KEY = "high_gain_mode_enabled"

    def __init__(self, ctl):
        self.ctl = ctl
        cfu = ctl.form.ui

        self.cb_enabled = cfu.checkBox_high_gain_mode_enabled

        self.cb_enabled.toggled.connect(self.enable_callback)
        self.cb_enabled.setWhatsThis("Toggles between analog gain modes on Hamamatsu InGaAs detectors.")
        self.cb_enabled.setVisible(False)

    def init_hotplug(self):
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return

        if not self.is_supported(spec):
            return

        sn = spec.settings.eeprom.serial_number
        if self.ctl.config.has_option(sn, self.CONFIG_KEY):
            flag = self.ctl.config.get_bool(sn, self.CONFIG_KEY)
            log.debug(f"restoring previously-saved high-gain mode {flag}")
        else:
            flag = self.recommended_default(spec)
            log.debug(f"defaulting high-gain mode to {flag}")
        
        self.cb_enabled.setChecked(flag)

    def update_visibility(self):
        spec = self.ctl.multispec.current_spectrometer()
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
        return spec.settings.is_ingaas() or spec.settings.is_andor()

    def recommended_default(self, spec):
        """ Default on for all InGaAs (Raman and otherwise), but not [yet] on by default for silicon Andor. """
        if spec is None:
            return False
        return spec.settings.is_ingaas()

    def enable_callback(self):
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None or not self.is_supported(spec):
            return

        enabled = self.cb_enabled.isChecked()
        self.ctl.multispec.set_state("high_gain_mode_enabled", enabled)
        self.ctl.multispec.change_device_setting("high_gain_mode_enable", enabled)

        sn = spec.settings.eeprom.serial_number
        self.ctl.config.set(sn, "high_gain_mode_enabled", enabled)

