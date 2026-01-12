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

        # note: ORDER MATTERS in these two, because they BOTH will set SpectrometerState.scans_to_average
        log.debug("MZ: kludge, disabling onboard scan averaging")
        # self.ctl.multispec.change_device_setting("onboard_scans_to_average", 1)
        self.ctl.multispec.change_device_setting("scans_to_average", value)

        spec = self.ctl.multispec.current_spectrometer()
        if spec:
            self.ctl.config.set(spec.settings.eeprom.serial_number, "scans_to_average", value)
            spec.app_state.check_refs()

    def show_label(self, flag):
        self.label.setVisible(flag)

    def process_status_message(self, msg, spec):
        # ignore "floated-up" averaging updates if we're doing BatchCollection 
        # and we're between measurements. In this state, the scope is paused, and
        # it doesn't make sense to update the background averaging count if we're
        # not updating the spectrum. That said, we don't hide the display simply 
        # because VCRControls.paused, because many BatchCollections run entirely
        # while the scope is "paused," and we DO want to show active averaging when
        # for scheduled BatchCollection measurements.
        if self.ctl.batch_collection.running and spec.app_state.take_one_request is None:
            log.debug("squelching scan averaging update during gap in BatchCollection")
            return

        try:
            count = int(msg[1])
            self.update_label(spec, count)
        except:
            log.error("received invalid status msg {msg}", exc_info=1)

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

        if self.ctl.vcr_controls and self.ctl.vcr_controls.is_paused(spec) and not self.ctl.batch_collection.running:
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

    def get_scans_to_average(self, spec=None):
        if spec is None:
            spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return 1
        return int(spec.settings.state.scans_to_average)
