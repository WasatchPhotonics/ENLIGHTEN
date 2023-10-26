import logging

from enlighten import util
from enlighten.ScrollStealFilter import ScrollStealFilter

from wasatch import utils as wasatch_utils

log = logging.getLogger(__name__)

class BoxcarFeature(object):
    """ Encapsulate the high-frequency noise smoothing "boxcar" filter run at the end of post-processing. """
    def __init__(self, ctl):
        self.ctl = ctl

        sfu = ctl.form.ui
        self.bt_dn      = sfu.pushButton_boxcar_half_width_dn
        self.bt_up      = sfu.pushButton_boxcar_half_width_up
        self.spinbox    = sfu.spinBox_boxcar_half_width

        self.bt_dn      .clicked        .connect(self.dn_callback)
        self.bt_up      .clicked        .connect(self.up_callback)
        self.spinbox    .valueChanged   .connect(self.update_from_gui)
        self.spinbox                    .installEventFilter(ScrollStealFilter(self.spinbox))

        self.ctl.presets.register(self, ["boxcar_half_width"])

    def update_visibility(self):
        self.update_from_gui()

    def update_from_gui(self):
        value = self.spinbox.value()

        # save boxcar to application state
        self.ctl.multispec.set_state("boxcar_half_width", value)

        # persist boxcar in .ini
        self.ctl.config.set(self.ctl.multispec.current_spectrometer().settings.eeprom.serial_number, "boxcar_half_width", value)

        if value > 0:
            self.spinbox.setToolTip("boxcar half-width of %d pixels (%d-pixel moving average)" % (value, value * 2 + 1))
        else:
            self.spinbox.setToolTip("smoothing disabled (half-width)")

    def up_callback(self):
        util.incr_spinbox(self.spinbox)

    def dn_callback(self):
        util.decr_spinbox(self.spinbox)

    def process(self, pr, spec=None):
        """
        @param pr (In/Out) ProcessedReading
        @param spec (Input) Spectrometer
        @note supports cropped ProcessedReading
        """
        if pr is None:
            return

        if spec is None:
            spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return

        half_width = spec.settings.state.boxcar_half_width
        if half_width < 1:
            return

        pr.set_processed(wasatch_utils.apply_boxcar(pr.get_processed(), half_width))

        if not self.ctl.page_nav.using_reference():
            if pr.recordable_dark is not None:
                pr.recordable_dark = wasatch_utils.apply_boxcar(pr.recordable_dark, half_width)
            
            if pr.recordable_reference is not None:
                pr.recordable_reference = wasatch_utils.apply_boxcar(pr.recordable_reference, half_width)

    def get_preset(self, attr):
        if attr == "boxcar_half_width":
            return int(self.spinbox.value())

    def set_preset(self, attr, value):
        if attr == "boxcar_half_width":
            self.spinbox.setValue(int(value))
