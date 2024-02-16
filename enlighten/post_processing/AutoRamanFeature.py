import logging
from datetime import datetime, timedelta

from wasatch.TakeOneRequest import TakeOneRequest
from enlighten.util import unwrap

log = logging.getLogger(__name__)

class AutoRamanFeature:
    """
    This feature adds a checkbox on the Laser Control widget called "Auto-Raman"
    which turns the standard VCRControls Step and StepAndSave buttons into auto-
    nomous atomic Raman collections (averaged dark, laser warmup, averaged sample,
    laser disable).
    """

    LASER_WARMUP_MS = 5000
    SECTION = "Auto-Raman"
    LASER_CONTROL_DISABLE_REASON = "Auto-Raman enabled"

    def __init__(self, ctl):
        self.ctl = ctl
        cfu = self.ctl.form.ui

        self.bt_laser  = cfu.pushButton_laser_toggle
        self.cb_enable = cfu.checkBox_auto_raman_enable

        self.enabled = False
        self.visible = False

        self.ctl.vcr_controls.register_observer("pause", self.update_visibility)
        self.ctl.vcr_controls.register_observer("play",  self.update_visibility)

        self.cb_enable.clicked.connect(self.enable_callback)
        self.cb_enable.setWhatsThis(unwrap("""
            Auto-Raman provides one-click collection of an averaged, dark-corrected
            Raman measurement.

            This feature is somewhat hazardous as it involves automonously enabling
            the laser, so please read the ENLIGHTEN documentation before enabling it.

            The feature is only available when the spectrometer is "paused" in the
            VCR controls.

            Clicking the button will store an averaged dark (first clearing any
            existing dark measurement), then enable the laser, wait a configured
            "warmup" time for the laser to stabilize, take an averaged Raman 
            sample measurement, disable the laser, and perform dark correction.

            Auto-Raman measurements are taken using the "Step" and "Step-and-Save"
            buttons on the VCR toolbar.
            """))

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

        self.cb_enable.setVisible(self.visible)

        if not self.visible:
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
            text="Auto-Raman will AUTOMATICALLY FIRE THE LASER when taking measurements " + \
                 "using the ⏯ button. Be aware that the laser will automtically enable " + \
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
