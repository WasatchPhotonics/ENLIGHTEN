import logging

from enlighten.EnlightenFeature import EnlightenFeature
from enlighten.util import unwrap

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

        self.bt_toggle.setWhatsThis(unwrap("""
            Etalon correction is a per-pixel correction offered on certain spectrometer 
            models that corrects for a faint "ripple" (standing wave) in intensity values, 
            visible in broadband spectra. This etaloning effect comes from reflections 
            that can occur in a detector between the sensor substrate and the underside
            of the protective glass window.

            This calibration is available on the EEPROM of XS spectrometers, and can be
            provided in an external JSON file on X / XM / XL series spectrometers."""))
            
    def update_visibility(self):
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            self.visible = False
        else:
            self.visible = spec.settings.etalon_correction is not None
            log.debug(f"update_visibility: visible = {self.visible}")

        self.cb_enable.setVisible(self.visible)
        self.bt_toggle.setVisible(self.visible)

        self.ctl.gui.colorize_button(self.bt_toggle, self.enabled)

        self.notify_observers()

    def toggle_callback(self):
        self.cb_enable.setChecked(not self.enabled)
        self.update_visibility()

    def enable_callback(self):
        self.enabled = self.cb_enable.isChecked()
        self.update_visibility()

    def process(self, pr):
        if not self.enabled or not pr.settings.etalon_correction:
            return

        try:
            log.debug("applying etalon correction")
            spectrum = pr.get_processed()
            corrected = pr.settings.etalon_correction.apply(spectrum)
            pr.set_processed(corrected)
            pr.etalon_corrected = True
        except:
            log.error("error applying etalon correction", exc_info=1)
            pass
