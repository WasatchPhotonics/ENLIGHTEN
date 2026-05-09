from enlighten.EnlightenFeature import EnlightenFeature
import logging

log = logging.getLogger(__name__)

class DalaiRamanFeature(EnlightenFeature):

    def __init__(self, ctl):
        super().__init__(ctl)

        cfu = ctl.form.ui
