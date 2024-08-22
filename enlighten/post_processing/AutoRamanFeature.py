import logging
from datetime import datetime, timedelta

from wasatch.TakeOneRequest import TakeOneRequest
from enlighten.util import unwrap

log = logging.getLogger(__name__)

class AutoRamanFeature:
    """
    This feature adds a checkbox on the Laser Control widget called "Auto-Raman"
    which exposes the "Auto-Raman Measurement" button (also on Laser Control).

    Old: turns the standard VCRControls Step and StepAndSave buttons into auto-
    nomous atomic Raman collections (averaged dark, laser warmup, averaged sample,
    laser disable).
    """

    LASER_WARMUP_MS = 5000
    SECTION = "Auto-Raman"
    LASER_CONTROL_DISABLE_REASON = "Auto-Raman enabled"

    def __init__(self, ctl):
        self.ctl = ctl
        cfu = self.ctl.form.ui

        self.bt_laser   = cfu.pushButton_laser_toggle
        self.cb_enable  = cfu.checkBox_auto_raman_enable
        self.bt_measure = cfu.pushButton_auto_raman_measurement

        self.enabled = False
        self.visible_cb = False
        self.visible_bt = False

        self.bt_measure.clicked.connect(self.measure_callback)
        self.cb_enable.clicked.connect(self.enable_callback)
        self.cb_enable.setWhatsThis(unwrap("""
            Auto-Raman provides one-click collection of an averaged, dark-corrected
            Raman measurement with automatically optimized integration time and
            gain.

            This feature is potentially hazardous as it involves automonously enabling
            the laser, so please read the ENLIGHTEN documentation before enabling it.

            The feature is currently only available on XS spectrometers with analog 
            gain control.

            Clicking the button will clear the current dark, then enable the laser, 
            wait a configured "warmup" time for the laser to stabilize, then attempt
            to optimize acquisition parameters by first tuning integration time, then
            when necessary gain. 

            After acquisition parameters have been optimized, ENLIGHTEN will determine
            how many averaged measurements can be acquired within the configured
            "measurement" period.  It will then complete the computed number of Raman
            sample spectra, disable the laser, take the same number of averaged 
            dark spectra (storing the averaged dark), and perform dark correction.

            The final processed measurement will then be graphed and sent to any 
            connected plug-ins for additional processing.
            """))

        self.update_visibility()

        # self.ctl.vcr_controls.register_observer("pause", self.update_visibility)
        # self.ctl.vcr_controls.register_observer("play",  self.update_visibility)

        # self.ctl.take_one.register_observer("start", self.take_one_start)
        # self.ctl.take_one.register_observer("complete", self.take_one_complete)

    ##
    # called by Controller.disconnect_device to ensure we turn this off between
    # connections
    def disconnect(self):
        self.cb_enable.setChecked(False)
        self.update_visibility()

    ############################################################################
    # Methods
    ############################################################################

    def update_visibility(self):
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            self.visible_cb = False
            self.visible_bt = False
            is_micro = False
        else:
            is_micro = spec.settings.is_micro()
            self.visible_cb = is_micro and \
                              self.ctl.page_nav.doing_raman() and \
                              self.ctl.vcr_controls.is_paused() and \
                              spec.settings.eeprom.has_laser

        self.cb_enable.setVisible(self.visible_cb)

        if not self.visible_cb:
            self.bt_measure.setVisible(False)
            self.cb_enable.setChecked(False)
            self.ctl.laser_control.clear_restriction(self.LASER_CONTROL_DISABLE_REASON)
        else:
            self.enable_callback()

    def generate_take_one_request(self):
        spec = self.ctl.multispec.current_spectrometer()
        avg = 1 if spec is None else spec.settings.state.scans_to_average

        return TakeOneRequest(take_dark=True, 
                              enable_laser_before=True, 
                              disable_laser_after=True, 
                              laser_warmup_ms=3000, 
                              scans_to_average=avg)

    ############################################################################
    # Callbacks
    ############################################################################

    def take_one_start(self):
        log.debug(f"take_one_start: enabled {self.enabled}")
        if self.enabled:
            self.ctl.dark_feature.clear(quiet=True)
            buffer_ms = 2000
            scans_to_average = self.ctl.scan_averaging.get_scans_to_average()
            for spec in self.ctl.multispec.get_spectrometers():
                timeout_ms = buffer_ms + self.LASER_WARMUP_MS + 2 * spec.settings.state.integration_time_ms * scans_to_average
                ignore_until = datetime.now() + timedelta(milliseconds=timeout_ms)
                log.debug(f"take_one_start: setting {spec} ignore_timeouts_util = {ignore_until} ({timeout_ms} ms)")
                spec.settings.state.ignore_timeouts_until = ignore_until

            log.debug("take_one_start: forcing laser button")
            self.ctl.laser_control.refresh_laser_buttons(force_on=True)

    def take_one_complete(self):
        log.debug("take_one_complete: refreshing laser button")
        self.ctl.laser_control.refresh_laser_buttons()

    def enable_callback(self):
        self.bt_measure.setVisible(False)
        enabled = self.visible and self.cb_enable.isChecked()
        log.debug("enable_callback: enable = %s", enabled)

        if enabled and not self.confirm():
            self.cb_enable.setChecked(False)
            log.debug("enable_callback: user declined (returning)")
            return

        log.debug(f"enable_callback: either we're disabling the feature (enabled {enabled}) or user confirmed okay")
        self.enabled = enabled
        if enabled:
            self.ctl.laser_control.set_restriction(self.LASER_CONTROL_DISABLE_REASON)
            self.bt_measure.setVisible(True)
        else:
            self.ctl.laser_control.clear_restriction(self.LASER_CONTROL_DISABLE_REASON)
        log.debug("enable_callback: done")

    def confirm(self):
        log.debug("confirm: start")
        option = "suppress_auto_raman_warning"

        if self.ctl.config.get(self.SECTION, option, default=False):
            log.debug("confirm: user already confirmed and disabled future warnings")
            return True

        # Prompt the user. Make it scary.
        result = self.ctl.gui.msgbox_with_checkbox(
            title="Auto-Raman Warning", 
            text="Auto-Raman will AUTOMATICALLY FIRE THE LASER when taking measurements " + 
                 "using the ⏯ button. Be aware that the laser will automtically enable " + 
                 "and disable when taking spectra while this mode is enabled.",
            checkbox_text="Don't show again")

        if not result["ok"]:
            log.debug("confirm: user declined")
            return False

        if result["checked"]:
            log.debug("confirm: saving approval")
            self.ctl.config.set(self.SECTION, option, True)
        log.debug("confirm: returning True")
        return True

    def measure_callback(self):
        self.ctl.gui.colorize_button(self.bt_measure, True)

    def from_db_to_linear(self, x):
        return 10 ** (x / 20.0)

    def from_linear_to_db(self, x):
        return 20 * math.log(x, 10)

    def inter_spectrum_delay(self):
        # time.sleep(inter_spectra_delay_ms / msPerSecond)
        pass

    def get_spectrum_with_dummies(self, int_time, num_dummies):
        # add a few dummy calls before the actual spectrum call
        # assumes the int time and gain is already set correctly

        for dummy in range(num_dummies):
            spectro.get_spectrum(integration_time_ms=int_time)
            self.inter_spectrum_delay()

        # take spectrum
        spectrum = spectro.get_spectrum(integration_time_ms=int_time)
        time.sleep(inter_spectra_delay_ms / msPerSecond)

        return np.array(spectrum)

    def get_avg_spectrum_with_dummy(self, int_time, gain_db, num_avg):
        """ Takes a single throwaway, then averages num_avg spectra """
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return

        num_dummies = 0 # as we call the get spectrum function with dummies, this leads to actually 1 dummies

        spec.set_integration_time_ms(int_time)
        spec.set_gain_db(gain_db)
        self.inter_spectrum_delay()

        # perform one throwaway
        _ = get_spectrum_with_dummies(spectro, int_time, num_dummies)

        sum_spectrum = np.zeros(num_pixels)
        for _ in range(num_avg):
            spectrum = np.array(spectro.get_spectrum(int_time))
            self.inter_spectrum_delay()
            sum_spectrum = sum_spectrum + spectrum

        return sum_spectrum / num_avg

    def get_auto_spectrum(, start_int_time, start_gain_db, start_laser_power, max_time, save_spectra=True):

        max_gain_db = 32.0	
        min_gain_db = 0.0

        max_int_time = 2000  
        min_int_time = 10

        target_level = 45000  # counts
        upper_limit = 50000
        lower_limit = 40000

        max_factor = 5
        drop_factor = 0.5
        saturation = 65000

        int_time = start_int_time
        gain_db = start_gain_db

        gain_linear = from_db_to_linear(gain_db)
        min_gain_linear = from_db_to_linear(min_gain_db)
        max_gain_linear = from_db_to_linear(max_gain_db)

        num_avg = 1
        max_total_time = max_time 

        # get one Raman spectrum to start (no dark)
        log.debug("Test Spectrum")
        turn_laser_on(spectro)
        spectrum = get_avg_spectrum_with_dummy(spectro, int_time, gain_db, num_avg=1)

        max_signal = spectrum.max()

        # integration/gain scaling
        quit_loop = False
        while not quit_loop:

            scale_factor = target_level / max_signal

            # We distribute scaling among integration time and linear gain
            #
            # mode: int time first
            #
            # if too small:
            # 1. increase int time from start to max
            # 2. increase gain from start to max
            #
            # if too large:
            # 1. decrease gain to min
            # 2. decrease int time

            # in mode 'int time first':
            # - we will first increase integration time - this will give best quality spectrum
            # - if the integration time is at the maximum, we will increase gain to reach expected
            #   signal levels

            prev_integration_time = int_time
            prev_gain_db = gain_db

            if scale_factor > 1.0:

                # do not grow too fast
                if scale_factor > max_factor:
                    scale_factor = max_factor
                
                # increase int time first
                int_time *= scale_factor

                # check int time does not exceed maximum
                if int_time > max_int_time:
                    # however much int time exceeds the max, transfer scaling to gain
                    gain_linear *= int_time / max_int_time
                    int_time = max_int_time

            elif scale_factor < 1.0:

                # if saturating, accelerate drop. do not use signal factor
                if max_signal >= saturation:
                    scale_factor = drop_factor

                # decrease gain first (INCREASE int time first implies DECREASE int time last)
                gain_linear *= scale_factor

                # check we did not drop below min gain
                if gain_linear < min_gain_linear:
                    # dump the overshoot into decreasing int time
                    int_time *= gain_linear / min_gain_linear
                    gain_linear = min_gain_linear

            # gain is rounded to 0.1 dB
            gain_db = round(from_linear_to_db(gain_linear), 1)
            gain_db = min(max_gain_db, max(gain_db, min_gain_db))

            # integration time is integral (ms)
            int_time = round(int_time)

            if (int_time == prev_integration_time) and (gain_db == prev_gain_db):
                # nothing has changed - rounding problem?
                # Here we do not distinguish between int time forst and gain first, the changes are very small
                if scale_factor > 1.0:
                    # was supposed to increase

                    # prefer to increase integration time
                    if int_time < max_int_time:
                        int_time += 1 
                    else:
                        # failover to increasing gain
                        if gain_db < max_gain_db:
                            gain_db += 0.1 
                        else: 
                            quit_loop = True
                else:
                    # was supposed to shrink

                    # prefer to shrink gain
                    if gain_db > min_gain_db:
                        gain_db -= 0.1 
                    else:
                        # fail-over to shrinking integration
                        if int_time > min_int_time:
                            int_time -= 1
                        else:
                            quit_loop = True

            log.debug("Test Spectrum")
            spectrum = get_avg_spectrum_with_dummy(spectro, int_time, gain_db, num_avg=1)
            max_signal = spectrum.max()

            if max_signal < upper_limit and max_signal > lower_limit:
                log.debug("achieved window")
                quit_loop = True
            elif max_signal < lower_limit and int_time >= max_int_time and gain_db >= max_gain_db:
                log.debug("can't achieve window within acquisition parameter limits")
                quit_loop = True

        # decide on number of averages - all times in ms
        # include dark + signal + laser warm up
        # note: also include one dummy scan each (dark and signal)...

        num_avg = round((max_total_time - laser_delay_ms) / (2 * int_time)) - 1
        num_avg = max(1, num_avg)

        # now get the spectrum with the chosen parameters
        # take two averaged spectra here: avg signal first, then turn laser off, then take dark
        # (this saves the laser warm up)

        # 1. signal - laser is still on
        log.debug("taking averaged Raman spectrum")
        new_spectrum = get_avg_spectrum_with_dummy(spectro, int_time, gain_db, num_avg)

        # 2. turn laser off
        self.ctl.laser_control.set_laser_enable(False)

        # 3. take dark
        log.debug("taking averaged dark")
        new_dark = get_avg_spectrum_with_dummy(spectro, int_time, gain_db, num_avg)
        self.ctl.dark_feature.save(new_dark)

        # correct signal minus dark
        log.debug("done")
        spectrum = new_spectrum - new_dark

        return spectrum
