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

    def __init__(self,
            cb_enabled,
            multispec):

        self.cb_enabled = cb_enabled
        self.multispec  = multispec

        self.cb_enabled.toggled.connect(self.enable_callback)

    def update(self):
        spec = self.multispec.current_spectrometer()
        if spec is None or spec.wp_model_info is None:
            return

        is_ingaas = spec.settings.is_ingaas()
        is_andor = spec.device.is_andor
        self.cb_enabled.setVisible(is_ingaas or is_andor)
        if not is_ingaas and not is_andor:
            return

        self.cb_enabled.setChecked(spec.settings.state.high_gain_mode_enabled)

    def enable_callback(self):
        enabled = self.cb_enabled.isChecked()

        self.multispec.set_state("high_gain_mode_enabled", enabled)
        self.multispec.change_device_setting("high_gain_mode_enable", enabled)
