import logging

log = logging.getLogger(__name__)

class DFUFeature:

    def __init__(self, ctl):
        self.ctl = ctl
        cfu = ctl.form.ui

        cfu.pushButton_mfg_dfu.clicked.connect(self.dfu_enable)

    def dfu_enable(self):
        self.ctl.multispec.change_device_setting("dfu_enable")
