import logging

from enlighten.util import incr_spinbox, decr_spinbox, unwrap
from enlighten.ui.ScrollStealFilter import ScrollStealFilter

log = logging.getLogger(__name__)

class ScanAveragingFeature:
    def __init__(self, ctl):
        self.ctl = ctl

        cfu = ctl.form.ui
        self.bt_dn      = cfu.pushButton_scan_averaging_dn
        self.bt_up      = cfu.pushButton_scan_averaging_up
        self.spinbox    = cfu.spinBox_scan_averaging
        self.label      = cfu.label_scan_averaging

        self.spinbox    .valueChanged   .connect(self.update_from_gui)
        self.spinbox                    .installEventFilter(ScrollStealFilter(self.spinbox))
        self.bt_dn      .clicked        .connect(self.down)
        self.bt_up      .clicked        .connect(self.up)

        self.ctl.presets.register(self, "scans_to_average", getter=self.get_scans_to_average, setter=self.set_scans_to_average)

        for widget in [ self.spinbox, self.bt_dn, self.bt_up ]:
            widget.setWhatsThis(unwrap("""
                Scan averaging is one of the simplest yet most effective things 
                you can do to increase Signal-to-Noise Ratio (SNR).

                As boxcar averages over space, scan averaging averages over time,
                averaging several samples together to reduce high-frequency noise
                and generate authentically smoothed spectra without compromising peak 
                intensity or optical resolution.

                Setting averaging to 5 is a quick way to get a measurable boost in
                effective signal. However, as signal is measured on a logarithmic
                scale, you basically need to jump to 25 spectra to get the next 
                noticable improvement in quality."""))

        self.reset()

    def initialize(self, spec=None):
        if spec is None:
            spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return

        self.set_scans_to_average(spec.settings.state.scans_to_average)

    def complete_registrations(self):
        self.ctl.vcr_controls.register_observer("pause", self.reset)

    ##
    # When VCRControls are paused or stopped, hide the label and reset the count
    def reset(self):
        self.show_label(False)
        self.ctl.multispec.change_device_setting("reset_scan_averaging", True)

    def set_locked(self, flag):
        for w in [ self.bt_dn,
                   self.bt_up,
                   self.spinbox ]:
            w.setEnabled(not flag)

    def update_from_gui(self):
        value = int(self.spinbox.value())
        self.ctl.multispec.set_state("scans_to_average", value)
        self.ctl.multispec.change_device_setting("scans_to_average", value)

        spec = self.ctl.multispec.current_spectrometer()
        if spec:
            self.ctl.config.set(spec.settings.eeprom.serial_number, "scans_to_average", value)
            spec.app_state.check_refs()

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
        incr_spinbox(self.spinbox)

    def down(self):
        decr_spinbox(self.spinbox)

    ## moved from Controller.doing_averaging
    def enabled(self, spec=None):
        if spec is None:
            spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return False
        return spec.settings.state.scans_to_average > 1

    def set_scans_to_average(self, value):
        value = int(round(float(value)))
        log.debug(f"set_scans_to_average({value})")

        if value != self.get_scans_to_average():
            log.debug(f"apply {value}")
            self.spinbox.blockSignals(True)
            self.spinbox.setValue(value)
            self.spinbox.blockSignals(False)

        self.update_from_gui()

    def get_scans_to_average(self):
        return int(self.spinbox.value())
