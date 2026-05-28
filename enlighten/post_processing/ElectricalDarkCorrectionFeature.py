import logging

from enlighten.EnlightenFeature import EnlightenFeature

log = logging.getLogger(__name__)

class ElectricalDarkCorrectionFeature(EnlightenFeature):
    
    def __init__(self, ctl):
        super().__init__(ctl)

        cfu = ctl.form.ui

        self.cb_enable = cfu.checkBox_edc_enabled

        self.enabled = False
        self.visible = False

        self.cb_enable.stateChanged.connect(self.enable_callback)

    def enable_callback(self):
        self.enabled = self.cb_enable.isChecked()
        self.ctl.multispec.change_device_setting("edc_enable", self.enabled)
        self.update_visibility()

    def update_visibility(self):
        spec = self.ctl.multispec.current_spectrometer()
        self.visible = spec is not None and spec.settings.is_xs() and self.ctl.page_nav.doing_expert()
        self.cb_enable.setVisible(self.visible)
        self.notify_observers()
