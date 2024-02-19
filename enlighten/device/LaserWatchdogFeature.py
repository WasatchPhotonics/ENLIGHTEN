import logging

from enlighten.ui.ScrollStealFilter import ScrollStealFilter
from enlighten.util import unwrap

log = logging.getLogger(__name__)

class LaserWatchdogFeature:

    def __init__(self, ctl):
        self.ctl = ctl
        cfu = ctl.form.ui

        self.enabled = False
        self.sec = None

        self.lb_sec = cfu.label_laser_watchdog_sec
        self.sb_sec = cfu.spinBox_laser_watchdog_sec
        self.cb_enable = cfu.checkBox_laser_watchdog

        self.sb_sec      .valueChanged   .connect(self.sec_callback)
        self.cb_enable   .clicked        .connect(self.enable_callback)

        self.sb_sec.installEventFilter(ScrollStealFilter(self.sb_sec))

        for widget in [self.lb_sec, self.sb_sec, self.cb_enable]:
            widget.setWhatsThis(unwrap("""
                Control the hardware laser watchdog. This accepts a positive 
                integral number of seconds, after which the laser is automatically 
                turned off. The goal is partially laser safety, but also to avoid
                burning out laser diodes and running down battery on mobile units. 
                This feature is only available on XS series spectrometers. The 
                watchdog can be disabled by setting to zero seconds."""))

    def init_hotplug(self):
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return

        settings = spec.settings
        if not settings.eeprom.has_laser:
            return

        self.configure(init=True)

    def update_visibility(self, init=False):
        log.debug(f"update_visibility(init={init})")
        spec = self.ctl.multispec.current_spectrometer()

        if spec is None:
            self.lb_sec.setVisible(False)
            return

        self.configure()

    def refresh_tooltip(self):
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return

        sec = spec.settings.state.laser_watchdog_sec

        if self.cb_enable.isChecked():
            self.sb_sec.setToolTip(f"Laser will automatically stop firing after {sec} seconds")
        else:
            self.sb_sec.setToolTip("Laser watchdog disabled")

    def set_visible(self, flag):
        log.debug(f"set_visible: flag {flag}")
        for w in [ self.lb_sec,
                   self.sb_sec,
                   self.cb_enable ]:
            w.setVisible(flag)

    def configure(self, init=False):
        log.debug(f"configure({init}): start")
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return

        settings = spec.settings

        reason = None
        if not settings.eeprom.has_laser:
            reason = "requires laser"
        elif not settings.is_xs():
            reason = "only applies to XS"

        # The following are reasons why we don't NEED to use the laser watchdog,
        # but aren't necessarily reasons to hide / disable the feature.  For now,
        # let's "allow" the user to use the laser watchdog from such units, but 
        # just not REQUIRE it (they can default it to zero in the EEPROM without
        # scary warning messages).
        #
        # elif settings.eeprom.sig_laser_tec:
        #   reason = "isn't needed with a laser TEC"
        # elif settings.eeprom.has_mml():
        #     reason = "isn't needed for MML"

        if reason:
            log.debug(f"configure({init}): inapplicable because {reason}")
            self.set_visible(False)
            self.enabled = False
            return

        ########################################################################
        # apparently we've decided to show and use the feature
        ########################################################################

        self.cb_enable.setVisible(True)
        sec = spec.settings.eeprom.laser_watchdog_sec

        # has a new spectrometer just connected?
        if init:
            if sec <= 0:
                log.debug(f"configure({init}): EEPROM was configured to disable the watchdog")
                self.enabled = False
                spec.app_state.laser_watchdog_disabled = True
                self.cb_enable.setChecked(False)
                self.enable_callback(False)
            else:
                log.debug(f"configure({init}): initializing new spectrometer to {sec} sec")
                self.enabled = True
                self.cb_enable.setChecked(True)

        log.debug(f"configure({init}): sync settings to GUI")
        self.sb_sec.setValue(sec)

        log.debug(f"configure({init}): GUI to device")
        self.sec_callback()

    def enable_callback(self, state):
        """ called when watchdog is checked ON or OFF """
        log.debug(f"enable_callback({state}): start")

        if not state:
            log.debug(f"enable_callback({state}): disabling")
            if self.confirm_disable():
                log.debug(f"enable_callback({state}): user confirmed disable, so hiding widgets")

                self.enabled = False # must come before set_sec
                self.set_sec(0)
                self.sb_sec.setVisible(False)
                self.lb_sec.setVisible(False)
            else:
                log.debug(f"enable_callback({state}): user cancelled disable")
                self.enabled = True
                self.cb_enable.setChecked(True)
        else:
            log.debug(f"enable_callback({state}): enabling")
            self.enabled = True
            self.sb_sec.setVisible(True)
            self.lb_sec.setVisible(True)
            self.set_sec()

            # requirement: if enabling watchdog in the middle of a laser event, disable laser
            log.debug(f"enable_callback({state}): enabled watchdog, so disabling laser")
            self.ctl.laser_control.set_laser_enable(False)

    def sec_callback(self):
        """ called when spinbox value changes """
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return

        if self.enabled:
            sec = self.sb_sec.value()
            log.debug(f"sec_callback({sec}): syncing from spinbox to feature/device")

            # requirement: changing the watchdog disables the laser
            if sec != self.sec and spec.settings.state.laser_enabled:
                log.debug(f"watchdog changed from {self.sec} to {sec}, so disabling laser")
                self.ctl.laser_control.set_laser_enable(False)
        else:
            sec = 0
            log.debug(f"sec_callback({sec}): disabled, so {sec}sec")

        log.debug(f"sec_callback({sec}): calling set_sec to send downstream")
        self.set_sec(sec)

        self.refresh_tooltip()
        log.debug(f"sec_callback({sec}): done")

    def set_sec(self, sec=None):
        """ sets the spinbox value and sends value downstream """
        log.debug(f"set_sec({sec}): start")

        if sec is None:
            sec = self.sb_sec.value()
            log.debug(f"set_sec({sec}): asked to re-set existing seconds (possibly due to a re-enable), so syncing from GUI")
            self.ctl.multispec.set_state("laser_watchdog_sec", sec)
            self.ctl.multispec.change_device_setting("laser_watchdog_sec", sec)
        elif sec != self.sec:
            log.debug(f"set_sec({sec}): watchdog changed from previous {self.sec} so sending downstream")
            self.ctl.multispec.set_state("laser_watchdog_sec", sec)
            self.ctl.multispec.change_device_setting("laser_watchdog_sec", sec)
        else:
            log.debug(f"set_sec({sec}): not sending anything downstream, because sec was neither None nor different from current value")

        log.debug(f"set_sec({sec}): caching value internally")
        self.sec = sec

        if self.enabled:
            log.debug(f"set_sec({sec}): syncing value to GUI")
            self.sb_sec.setValue(sec)
        else:
            log.debug(f"set_sec({sec}): disabled, so NOT syncing value to GUI")

        log.debug(f"set_sec({sec}): done")

    def confirm_disable(self) -> bool:
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return False

        # If the user disabled the watchdog in the EEPROM, assume they
        # know what they're doing and don't nag them.  Also, it could be
        # an older spectrometer that didn't HAVE a watchdog and therefore
        # the value "defaults" to zero — we don't want to annoy those users
        # every connection either.
        if spec.app_state.laser_watchdog_disabled:
            return True

        # If this is an MML or has a laser TEC, then they don't really need
        # the watchdog, so let them disable it freely without annoying
        # confirmations.
        if spec.settings.eeprom.sig_laser_tec:
            log.debug("confirm_disable: skipping confirmation because have laser TEC")
            return True
        if spec.settings.eeprom.has_mml():
            log.debug("confirm_disable: skipping confirmation because have MML")
            return True

        log.debug("confirm_disable: prompting user to confirm their decision to disable the laser watchdog")

        msg = "Are you sure you wish to disable the laser watchdog? Running the " \
            + "laser without watchdog could damage the instrument, risk human " \
            + "injury and may void your warranty."
        response = common.msgbox(msg, title="Laser Watchdog Disable", buttons="yes|cancel", informative_text="Disabling watchdog may void warranty.")
        if response is None or response != "Yes":
            log.debug("confirm_disable: user reconsidered disabling laser watchdog")
            return False

        log.debug("confirm_disable: user explicitly confirmed they wish to disable the laser watchdog")
        return True
