import logging

log = logging.getLogger(__name__)

class ElectricalDarkCorrectionFeature:
    
    def __init__(self, ctl):
        self.ctl = ctl
        cfu = ctl.form.ui

        self.cb_enable = cfu.checkBox_edc_enabled

        self.cb_enable.stateChanged.connect(self.enable_callback)

    def enable_callback(self):
        enabled = self.cb_enable.isChecked()
        self.ctl.multispec.change_device_setting("edc_enable", enabled)

    def update_visibility(self):
        spec = self.ctl.multispec.current_spectrometer()
        visible = spec is not None and spec.settings.is_xs() and self.ctl.page_nav.doing_expert()
        self.cb_enable.setVisible(visible)
