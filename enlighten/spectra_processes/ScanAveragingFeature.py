import logging

from enlighten import util
from enlighten.ui.ScrollStealFilter import ScrollStealFilter

log = logging.getLogger(__name__)

class ScanAveragingFeature(object):
    def __init__(self, ctl):
        self.ctl = ctl

        sfu = ctl.form.ui
        self.bt_dn      = sfu.pushButton_scan_averaging_dn
        self.bt_up      = sfu.pushButton_scan_averaging_up
        self.spinbox    = sfu.spinBox_scan_averaging
        self.label      = sfu.label_scan_averaging

        self.spinbox    .valueChanged   .connect(self.update_from_gui)
        self.spinbox                    .installEventFilter(ScrollStealFilter(self.spinbox))
        self.bt_dn      .clicked        .connect(self.down)
        self.bt_up      .clicked        .connect(self.up)

        self.ctl.presets.register(self, "scans_to_average", getter=self.get_scans_to_average, setter=self.set_scans_to_average)

        self.reset()

    def initialize(self, spec=None):
        if spec is None:
            spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return

        self.set(spec.settings.state.scans_to_average)

    def complete_registrations(self):
        self.ctl.vcr_controls.register_observer("pause", self.reset)

    ##
    # When VCRControls are paused or stopped, hide the label and reset the count
    def reset(self):
        self.show_label(False)
        self.ctl.multispec.change_device_setting("reset_scan_averaging", True)

    def set(self, value):
        self.spinbox.blockSignals(True)
        self.spinbox.setValue(value)
        self.spinbox.blockSignals(False)

        self.update_from_gui()

    def set_locked(self, flag):
        for w in [ self.bt_dn,
                   self.bt_up,
                   self.spinbox ]:
            w.setEnabled(not flag)

    def update_from_gui(self):
        value = int(self.spinbox.value())
        self.ctl.multispec.set_state("scans_to_average", value)
        self.ctl.multispec.change_device_setting("scans_to_average", value)

    def show_label(self, flag):
        self.label.setVisible(flag)

    def update_label(self, spec, count):
        log.debug("count %d" % count)
        if spec is None:
            return

        # don't do anything if we're not the current spectrometer
        if not self.ctl.multispec.is_selected(spec.device_id):
            return

        # if active spectrometer isn't averaging, hide label
        if not self.enabled(spec):
            self.label.setVisible(False)
            return

        if self.ctl.vcr_controls and self.ctl.vcr_controls.is_paused(spec):
            self.label.setVisible(False)
            return

        # update label
        count = max(1, min(count, spec.settings.state.scans_to_average))

        # patch #179
        if count == 1:
            self.label.setVisible(True)

        self.label.setText("Collected %d of %d" % (count, spec.settings.state.scans_to_average))

    def up(self):
        util.incr_spinbox(self.spinbox)

    def down(self):
        util.decr_spinbox(self.spinbox)

    ## moved from Controller.doing_averaging
    def enabled(self, spec=None):
        if spec is None:
            spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return False
        return spec.settings.state.scans_to_average > 1

    def set_scans_to_average(self, value):
        value = int(value)
        if value != self.get_scans_to_average():
            self.set(value)

    def get_scans_to_average(self):
        return int(self.spinbox.value())
