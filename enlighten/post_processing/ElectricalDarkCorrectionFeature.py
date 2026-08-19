import logging

from enlighten.EnlightenFeature import EnlightenFeature
from enlighten.util import unwrap

log = logging.getLogger(__name__)

class ElectricalDarkCorrectionFeature(EnlightenFeature):
    
    def __init__(self, ctl):
        super().__init__(ctl)

        cfu = ctl.form.ui

        self.cb_enable = cfu.checkBox_edc_enabled

        self.enabled = False
        self.visible = False

        self.cb_enable.stateChanged.connect(self.enable_callback)

        self.cb_enable.setWhatsThis(unwrap("""
            Some detectors include "optically-black" pixels to the left or right edges
            of the active sensor area, which are not exposed to incoming light from
            the collection optics, but which are affected by thermal noise and electrical
            readout noise (similar to other detector pixels). Therefore, these 
            optically-dark pixels can be read-out alongside the rest of the image frame,
            averaged together, and then subtracted from the "optically-active" pixels.

            This represents a simple form of Electrical Dark Correction, which while
            not as good as a regularly updated "dark" measurement, can be used as a 
            quick means of removing electrical aspects of a spectral baseline."""))

    def enable_callback(self):
        self.enabled = self.cb_enable.isChecked()
        self.ctl.multispec.change_device_setting("edc_enable", self.enabled)
        self.update_visibility()

    def update_visibility(self):
        spec = self.ctl.multispec.current_spectrometer()
        self.visible = spec is not None and spec.settings.is_xs() and self.ctl.page_nav.doing_expert()
        self.cb_enable.setVisible(self.visible)
        self.notify_observers()
