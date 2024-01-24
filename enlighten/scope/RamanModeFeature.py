import logging
from datetime import datetime, timedelta

from wasatch.TakeOneRequest import TakeOneRequest

log = logging.getLogger(__name__)

##
# This class encapsulates the "Raman Mode" features intended for the new 
# ramanMicro (SiG) spectrometers.  Note that HW features are developmental, so
# some are currently implemented in software; this may change as FW develops.
#
# If and when other spectrometers receive a Laser Watchdog feature, we may break
# that and other portions out into other classes.
#
# This feature cannot be enabled at startup for safety reasons.
#
# @todo consider if and where we should disable the laser if battery too low
class RamanModeFeature(object):

    LASER_WARMUP_MS = 5000

    def __init__(self, ctl):
        self.ctl = ctl
        sfu = self.ctl.form.ui

        self.bt_laser  = sfu.pushButton_laser_toggle
        self.cb_enable = sfu.checkBox_raman_mode_enable

        self.enabled = False
        self.visible = False

        self.ctl.vcr_controls.register_observer("pause", self.update_visibility)
        self.ctl.vcr_controls.register_observer("play",  self.update_visibility)

        self.cb_enable.stateChanged.connect(self.enable_callback)

        self.update_visibility()

        self.ctl.take_one.register_observer("start", self.take_one_start)
        self.ctl.take_one.register_observer("complete", self.take_one_complete)

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
            self.visible = False
            is_micro = False
        else:
            is_micro = spec.settings.is_micro()
            self.visible = is_micro and \
                           self.ctl.page_nav.doing_raman() and \
                           self.ctl.vcr_controls.is_paused() and \
                           spec.settings.eeprom.has_laser

        # log.debug("visible = %s", self.visible)
        self.cb_enable.setVisible(self.visible)

        if not self.visible:
            self.cb_enable.setChecked(False)
        else:
            self.enable_callback()

    def generate_take_one_request(self):
        return TakeOneRequest(take_dark=True, enable_laser_before=True, disable_laser_after=True, laser_warmup_ms=3000)

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
            self.ctl.laser_control.refresh_laser_button(force_on=True)

    def take_one_complete(self):
        log.debug("take_one_complete: refreshing laser button")
        self.ctl.laser_control.refresh_laser_button()

    def enable_callback(self):
        self.enabled = self.visible and self.cb_enable.isChecked()

        log.debug("enable = %s", self.enabled)

        self.ctl.laser_control.set_allowed(not self.enabled, reason_why_not="Raman Mode enabled")
