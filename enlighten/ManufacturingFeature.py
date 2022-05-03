import logging

log = logging.getLogger(__name__)

## A place to put manufacturing bits that don't fit elsewhere.
class ManufacturingFeature(object):

    def __init__(self,
            bt_dfu,
            multispec):

        self.bt_dfu     = bt_dfu
        self.multispec  = multispec

        self.bt_dfu.clicked.connect(self.dfu_enable)

    def dfu_enable(self):
        self.multispec.change_device_setting("dfu_enable")
