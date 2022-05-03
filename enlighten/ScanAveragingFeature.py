import logging

from . import util
from .ScrollStealFilter import ScrollStealFilter

log = logging.getLogger(__name__)

class ScanAveragingFeature(object):
    def __init__(self,
            bt_dn,
            bt_up,
            label,
            multispec,
            spinbox):

        self.bt_dn      = bt_dn
        self.bt_up      = bt_up
        self.label      = label
        self.multispec  = multispec
        self.spinbox    = spinbox

        self.vcr_controls = None # will populate after initialization

        self.spinbox    .valueChanged   .connect(self.update_from_gui)
        self.spinbox                    .installEventFilter(ScrollStealFilter(self.spinbox))
        self.bt_dn      .clicked        .connect(self.down)
        self.bt_up      .clicked        .connect(self.up)

        self.reset()

    def initialize(self, spec=None):
        if spec is None:
            spec = self.multispec.current_spectrometer()
        if spec is None:
            return

        self.set(spec.settings.state.scans_to_average)

    def set_vcr_controls(self, obj):
        self.vcr_controls = obj
        self.vcr_controls.register_observer("pause", self.reset)

    ##
    # When VCRControls are paused or stopped, hide the label and reset the count
    def reset(self):
        self.show_label(False)
        self.multispec.change_device_setting("reset_scan_averaging", True)

    def set(self, value):
        self.spinbox.blockSignals(True)
        self.spinbox.setValue(value)
        self.spinbox.blockSignals(False)

        self.update_from_gui()

    def update_from_gui(self):
        value = int(self.spinbox.value())
        self.multispec.set_state("scans_to_average", value)
        self.multispec.change_device_setting("scans_to_average", value)

    def show_label(self, flag):
        self.label.setVisible(flag)

    def update_label(self, spec, count):
        log.debug("update_label: count %d" % count)
        if spec is None:
            return

        # don't do anything if we're not the current spectrometer
        if not self.multispec.is_selected(spec.device_id):
            return

        # if active spectrometer isn't averaging, hide label
        if not self.enabled(spec):
            self.label.setVisible(False)
            return

        if self.vcr_controls and self.vcr_controls.is_paused(spec):
            self.label.setVisible(False)
            return

        # update label
        log.debug("update_label: displaying")
        count = max(1, min(count, spec.settings.state.scans_to_average))
        self.label.setVisible(True)
        self.label.setText("Collected %d of %d" % (count, spec.settings.state.scans_to_average))

    def up(self):
        util.incr_spinbox(self.spinbox)

    def down(self):
        util.decr_spinbox(self.spinbox)

    ## moved from Controller.doing_averaging
    def enabled(self, spec=None):
        if spec is None:
            spec = self.multispec.current_spectrometer()
        if spec is None:
            return False
        return spec.settings.state.scans_to_average > 1
