import logging

from enlighten.EnlightenFeature import EnlightenFeature
from enlighten.util import unwrap

log = logging.getLogger(__name__)

class DFUFeature(EnlightenFeature):

    def __init__(self, ctl):
        super().__init__(ctl)

        cfu = ctl.form.ui
        self.bt_enable = cfu.pushButton_mfg_dfu

        self.bt_enable.clicked.connect(self.dfu_enable)

        self.bt_enable.setWhatsThis(unwrap("""
            ARM-based Wasatch spectrometers (XS series) support Device Firmware 
            Update (DFU) mode, allowing new firmware to be flashed to the 
            microcontrollers and FPGA. This button will immediately set any 
            connected spectrometer into DFU mode, allowing tools such as
            STM32CubeIDE to be used to upload a new image over USB.

            Note that as soon as a device enables DFU mode, it is no longer
            visible to the computer as a Wasatch spectrometer, so the device
            will immediately disconnect from ENLIGHTEN.
        """))

    def dfu_enable(self):
        self.ctl.multispec.change_device_setting("dfu_enable")
