import logging

log = logging.getLogger(__name__)

class EtalonCorrectionFeature:

    def __init__(self, ctl):
        self.ctl = ctl
        
        cfu = ctl.form.ui

        self.cb_enable = cfu.checkBox_etalon_correction
