import logging

from enlighten.ui.ScrollStealFilter import ScrollStealFilter
from enlighten.util import unwrap

log = logging.getLogger(__name__)

##
# @todo redo process() math with numpy
class TransmissionFeature:
    
    def __init__(self, ctl):
        self.ctl = ctl
        cfu = ctl.form.ui

        self.cb_max_enable  = cfu.checkBox_enable_max_transmission
        self.sb_max_perc    = cfu.spinBox_max_transmission_perc

        self.update_from_gui()

        self.cb_max_enable  .stateChanged       .connect(self.update_from_gui)
        self.sb_max_perc    .valueChanged       .connect(self.update_from_gui)
        self.sb_max_perc                        .installEventFilter(ScrollStealFilter(self.sb_max_perc))

    ## transmission processing is: 100 * (sample - dark) / (reference - dark)
    # (if no dark is available, just use sample / reference)
    #
    # @returns True if ProcessedReading.processed successfully updated
    def process(self, processed_reading, settings, app_state):
        pr = processed_reading

        if pr.dark is None:
            self.ctl.marquee.error("Please take dark")
            return False

        ref = pr.reference
        if ref is None:
            self.ctl.marquee.error("Please take reference")
            return False

        # dark-correct reference if not already done
        if not app_state.reference_is_dark_corrected:
            ref = ref.copy()
            ref -= pr.dark

        sample = pr.get_processed()
        if sample is None:
            log.error("can't compute transmission without a sample")
            return False

        if pr.is_cropped() and settings is not None:
            roi = settings.eeprom.get_horizontal_roi()
            ref = self.ctl.horiz_roi.crop(ref, roi=roi)

        if len(ref) != len(sample):
            self.ctl.marquee.error("reference and sample must be same size")
            return False

        transmission = []
        has_neg = False
        for i in range(len(sample)):
            value = 0
            if ref[i] != 0:
                try:
                    value = 100.0 * float(sample[i]) / float(ref[i])
                except:
                    pass
            if self.max_enabled:
                value = min(value, self.max_perc)
            transmission.append(value)

            if value < 0:
                has_neg = True

        if has_neg:
            self.ctl.marquee.error("measurement out-of-range")

        pr.set_processed(transmission)
        log.debug("trans = %s", transmission[0:10])
        return True

    def update_from_gui(self):
        self.max_enabled = self.cb_max_enable.isChecked()
        self.max_perc = self.sb_max_perc.value()
