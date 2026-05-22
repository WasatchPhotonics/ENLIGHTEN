import logging
import os

from enlighten.EnlightenFeature import EnlightenFeature

log = logging.getLogger(__name__)

class EtalonCorrectionFeature(EnlightenFeature):
    """
    All processing is currently done in Wasatch.PY.
    """

    def __init__(self, ctl):
        super().__init__(ctl)
        
        cfu = ctl.form.ui

        self.cb_enable = cfu.checkBox_etalon_correction
        self.bt_toggle = cfu.pushButton_etalon_correction
        
        self.visible = False
        self.enabled = False

        self.cb_enable.stateChanged.connect(self.enable_callback)
        self.bt_toggle.clicked.connect(self.toggle_callback)

    def update_visibility(self):
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            self.visible = False
        else:
            self.visible = spec.settings.etalon_correction is not None

        self.cb_enable.setVisible(self.visible)
        self.bt_toggle.setVisible(self.visible)

        self.notify_observers()

    def toggle_callback(self):
        self.cb_enable.setChecked(not self.enabled)
        self.update_visibility()

    def enable_callback(self):
        self.enabled = self.cb_enable.isChecked()

        spec = self.ctl.multispec.current_spectrometer()
        if spec:
            spec.change_device_settings("etalon_correction_enable", self.enabled)

        self.update_visibility()
