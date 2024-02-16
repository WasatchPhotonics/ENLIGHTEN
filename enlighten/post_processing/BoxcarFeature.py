import logging

from enlighten.ui.ScrollStealFilter import ScrollStealFilter
from enlighten.util import unwrap, incr_spinbox, decr_spinbox
from wasatch.utils import apply_boxcar

log = logging.getLogger(__name__)

class BoxcarFeature:
    """ Encapsulate the high-frequency noise smoothing "boxcar" filter run at the end of post-processing. """
    def __init__(self, ctl):
        self.ctl = ctl

        cfu = ctl.form.ui
        self.bt_dn      = cfu.pushButton_boxcar_half_width_dn
        self.bt_up      = cfu.pushButton_boxcar_half_width_up
        self.spinbox    = cfu.spinBox_boxcar_half_width

        self.bt_dn      .clicked        .connect(self.dn_callback)
        self.bt_up      .clicked        .connect(self.up_callback)
        self.spinbox    .valueChanged   .connect(self.update_from_gui)
        self.spinbox                    .installEventFilter(ScrollStealFilter(self.spinbox))

        for widget in [ self.bt_dn, self.bt_up, self.spinbox ]:
            widget.setWhatsThis(unwrap("""
                Boxcar applies a lightweight smoothing (spatial averaging) convolution
                to remove high-frequency noise from your spectrum, at the cost of
                reduced peak intensity and optical resolution (i.e. increased FWHM).

                It can be useful to quickly make spectra "prettier" and improve 
                "apparent SNR" for human viewers, but is a lossy transformation 
                which rarely improves fundamental data quality.

                Boxcar is applied in pixel space, and does not account for the 
                non-linearity of wavelength or wavenumber axes.

                Typical values may be 1 or 2 for Raman, or up to 10 for non-Raman
                with broad spectral features."""))

        self.ctl.presets.register(self, "boxcar_half_width", getter=self.get_half_width, setter=self.set_half_width)

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
        incr_spinbox(self.spinbox)

    def dn_callback(self):
        decr_spinbox(self.spinbox)

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

        pr.set_processed(apply_boxcar(pr.get_processed(), half_width))

        if not self.ctl.page_nav.using_reference():
            if pr.recordable_dark is not None:
                pr.recordable_dark = apply_boxcar(pr.recordable_dark, half_width)
            
            if pr.recordable_reference is not None:
                pr.recordable_reference = apply_boxcar(pr.recordable_reference, half_width)

    def get_half_width(self):
        return int(self.spinbox.value())

    def set_half_width(self, value):
        self.spinbox.setValue(int(value))
