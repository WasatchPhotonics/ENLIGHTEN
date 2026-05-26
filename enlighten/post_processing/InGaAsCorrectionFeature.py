import logging
import os

from enlighten.EnlightenFeature import EnlightenFeature

log = logging.getLogger(__name__)

class InGaAsCorrectionFeature(EnlightenFeature):
    """
    All processing is currently done in Wasatch.PY.
    """

    def __init__(self, ctl):
        super().__init__(ctl)

        cfu = ctl.form.ui

        self.cb_enable = cfu.checkBox_ingaas_correction
        self.bt_toggle = cfu.pushButton_ingaas_correction

        self.visible = False
        self.enabled = False

        self.cb_enable.stateChanged.connect(self.enable_callback)
        self.bt_toggle.clicked.connect(self.toggle_callback)

    def update_visibility(self):
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            self.visible = False
        else:
            # only display the feature at all if on a spectrometer with an 
            # InGaAs correction (very few of those at this time)
            self.visible = spec.settings.ingaas_correction is not None

        self.cb_enable.setVisible(self.visible)
        self.bt_toggle.setVisible(self.visible)
        self.ctl.gui.colorize_button(self.bt_toggle, self.enabled)

        self.notify_observers()

    def toggle_callback(self):
        self.cb_enable.setChecked(not self.enabled)
        self.update_visibility()

    def enable_callback(self):
        self.enabled = self.cb_enable.isChecked()

        spec = self.ctl.multispec.current_spectrometer()
        if spec:
            spec.change_device_settings("ingaas_correction_enable", self.enabled)

        self.update_visibility()

    def process(self, pr):
        if not pr.settings.ingaas_correction:
            return

        try:
            log.debug("applying InGaAs correction")
            spectrum = pr.get_processed()
            corrected = pr.settings.ingaas_correction.apply(spectrum)
            pr.set_processed(corrected)
        except:
            log.error("error applying InGaAs correction", exc_info=1)
            pass
