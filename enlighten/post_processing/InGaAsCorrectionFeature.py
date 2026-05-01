import logging

from enlighten.EnlightenFeature import EnlightenFeature

log = logging.getLogger(__name__)

class InGaAsCorrectionFeature(EnlightenFeature):

    def __init__(self, ctl):
        super().__init__(ctl)

        cfu = ctl.form.ui

        self.cb_enable = cfu.checkBox_ingaas_correction
