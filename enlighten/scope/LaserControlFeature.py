import time
from datetime import datetime, timedelta
import logging

from PySide6 import QtWidgets 

from enlighten import util
from enlighten.common import LaserStates

from wasatch.EEPROM                   import EEPROM

from enlighten.ScrollStealFilter import ScrollStealFilter
from enlighten.MouseWheelFilter import MouseWheelFilter

log = logging.getLogger(__name__)

##
# Encapsulate laser control from the application side.
class LaserControlFeature:

    MIN_BATTERY_PERC = 5
    BTN_OFF_TEXT = "Turn Laser Off"
    BTN_ON_TEXT = "Turn Laser On"

    def __init__(self, ctl):
        self.ctl = ctl

        self.ctl.battery_feature.register_observer(self.battery_callback)

        self.slider_stop_usb = False
        self.displayed_srm_tip = False
        self.locked = False

        sfu = self.ctl.form.ui

        sfu.pushButton_laser_power_dn   .clicked            .connect(self.dn_callback)
        sfu.pushButton_laser_power_up   .clicked            .connect(self.up_callback)
        sfu.pushButton_laser_toggle     .clicked            .connect(self.toggle_callback)
        sfu.verticalSlider_laser_power  .sliderPressed      .connect(self.slider_power_press_callback)
        sfu.verticalSlider_laser_power  .sliderMoved        .connect(sfu.doubleSpinBox_laser_power.setValue)
        sfu.verticalSlider_laser_power  .sliderReleased     .connect(self.slider_power_callback)
        sfu.doubleSpinBox_excitation_nm .valueChanged       .connect(self.excitation_callback)
        sfu.doubleSpinBox_laser_power   .valueChanged       .connect(sfu.verticalSlider_laser_power.setValue)
        sfu.doubleSpinBox_laser_power   .valueChanged       .connect(self.set_laser_power_callback)
        sfu.spinBox_laser_watchdog_sec  .valueChanged       .connect(self.set_watchdog_callback)
        sfu.checkBox_laser_watchdog     .clicked            .connect(self.set_watchdog_enable_callback)
        sfu.comboBox_laser_power_unit   .currentIndexChanged.connect(self.update_visibility)

        for widget in [ sfu.verticalSlider_laser_power ]:
            widget.installEventFilter(MouseWheelFilter(widget))

        for widget in [ sfu.doubleSpinBox_excitation_nm,
                        sfu.doubleSpinBox_laser_power,
                        sfu.spinBox_laser_watchdog_sec,
                        sfu.comboBox_laser_power_unit ]:
            widget.installEventFilter(ScrollStealFilter(widget))

    # ##########################################################################
    # Public Methods
    # ##########################################################################

    def set_locked(self, flag):
        self.locked = flag
        self.update_visibility()

    ##
    # Called by initialize_new_device when a new device has been connected:
    #
    # - default to 100% power (and max calibrated mW)
    # - default to "mW" if calibration found
    # - disable laser
    # - default to high-resolution laser power (1ms pulse period)
    def init_hotplug(self):
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return

        settings = spec.settings
        state = settings.state

        if not settings.eeprom.has_laser:
            return

        state.laser_power_perc = 100
        state.laser_power_mW = settings.eeprom.max_laser_power_mW
        state.use_mW = settings.eeprom.has_laser_power_calibration() and settings.is_mml()

        self.set_laser_enable(False)
        self.configure_watchdog(init=True)
        
        spec.change_device_setting("laser_power_high_resolution", True)

    ##
    # Called by initialize_new_device when the user selected one of several 
    # connected spectrometers.
    def update_visibility(self, init=False):
        log.debug(f"update_visibility(init={init})")
        spec = self.ctl.multispec.current_spectrometer()
        sfu = self.ctl.form.ui

        if spec is None:
            sfu.label_laser_watchdog_sec.setVisible(False)
            return

        settings = spec.settings
        has_laser = settings.eeprom.has_laser
        doing_expert = self.ctl.page_nav.doing_expert()
        is_ilc = any([component in settings.full_model().upper() for component in ["-ILC", "-IL-IC"]])
        combo_unit = sfu.comboBox_laser_power_unit

        sfu.frame_lightSourceControl.setVisible(has_laser)
        if not has_laser:
            return

        has_calibration = settings.eeprom.has_laser_power_calibration()
        log.debug("update_visibility: laser power calibration %s", has_calibration)

        combo_unit.setVisible(False)

        if not has_calibration:
            self.configure_laser_power_controls_percent()
        else:
            if is_ilc or doing_expert:
                combo_unit.setVisible(True)

            if combo_unit.isVisible():
                if combo_unit.currentIndex() == 0: 
                    self.configure_laser_power_controls_mW()
                else:
                    self.configure_laser_power_controls_percent()
            else:
                if settings.state.use_mW:
                    self.configure_laser_power_controls_mW()
                else:
                    self.configure_laser_power_controls_percent()

        sfu.doubleSpinBox_excitation_nm.setVisible(doing_expert)
        sfu.label_lightSourceWidget_excitation_nm.setVisible(doing_expert)

        self.configure_watchdog()

        if self.locked:
            # let them turn the laser on/off, nothing else
            for w in [ sfu.doubleSpinBox_excitation_nm,
                       sfu.pushButton_laser_power_dn,
                       sfu.pushButton_laser_power_up,
                       sfu.verticalSlider_laser_power,
                       sfu.doubleSpinBox_excitation_nm,
                       sfu.doubleSpinBox_laser_power,
                       sfu.spinBox_laser_watchdog_sec,
                       sfu.checkBox_laser_watchdog,
                       sfu.comboBox_laser_power_unit ]:
                w.setEnabled(False)

        self.refresh_laser_button()

    # expose this setter for BatchCollection and plugins
    def set_laser_enable(self, flag, spec=None, all=False):

        # BatchCollection doesn't use multispec.lock (it's not enforcing
        # synchronization in other commands), but it does manually send
        # an "all" to enable the lasers on all connected spectrometers.
        if all:
            for spec in self.ctl.multispec.get_spectrometers():
                self.set_laser_enable(flag, spec=spec)
            return

        # not all...

        if spec is None:
            # if we were NOT given a specific spectrometer (so this is
            # the default behavior, like clicking the GUI button), then
            # default to the current spectrometer, and obey multispec
            # locking if enabled
            spec = self.ctl.multispec.current_spectrometer()
            use_multispec = True
        else:
            # we were given a specific spectrometer (possibly via 'all',
            # possibly not), so don't do anything with multispec locking
            use_multispec = False

        if spec is None:
            return

        if not self.ctl.raman_intensity_correction.enabled and \
                self.ctl.raman_intensity_correction.is_supported() and \
                self.ctl.page_nav.doing_raman() and \
                not self.displayed_srm_tip and \
                flag:
            self.ctl.guide.suggest("Tip: Raman response is more consistent when using Raman Intensity Correction", token="enable_raman_intensity_correction")
            self.displayed_srm_tip = True

        if use_multispec:
            self.ctl.multispec.set_state("laser_enabled", flag)
            self.ctl.multispec.change_device_setting("laser_enable", flag)
        else:
            spec.settings.state.laser_enabled = flag
            spec.change_device_setting("laser_enable", flag)

        spec.app_state.laser_state = LaserStates.REQUESTED if flag else LaserStates.DISABLED
        log.debug(f"set_laser_enable: spec.settings.state.laser_enabled = {spec.settings.state.laser_enabled}, spec.app_state.laser_state = {spec.app_state.laser_state}")

        if self.ctl.multispec.is_current_spectrometer(spec):
            self.refresh_laser_button()

        self.ctl.status_indicators.update_visibility()

    def process_reading(self, reading):
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return

        if reading is None:
            return

        if reading.laser_enabled is None:
            log.debug("update_laser_status: reading.laser_enabled is None")
            return

        state = spec.app_state.laser_state

        if reading.laser_enabled:
            # reading says laser firing
            if state == LaserStates.DISABLED:
                log.critical("reading thinks laser firing when application thinks disabled?! Disabling...")
                self.set_laser_enable(False, spec)
            elif state == LaserStates.REQUESTED:
                log.debug("the laser has started firing")
                spec.app_state.laser_state = LaserStates.FIRING
            elif state == LaserStates.FIRING:
                log.debug("all agree laser firing")
        else:
            # reading says laser not firing
            if state == LaserStates.DISABLED:
                log.debug("all agree laser disabled")
                return
            elif state == LaserStates.REQUESTED:
                log.debug("awaiting laserDelaySec")
                return
            elif state == LaserStates.FIRING:
                log.info("laser stopped firing (watchdog or interlock?)")
                self.set_laser_enable(False, spec)

    ## So Controller etc don't call directly into internal callbacks
    def toggle_laser(self):
        log.debug("toggle_laser called")
        self.toggle_callback()

    def cant_fire_because_battery(self, spec=None):
        if spec is None:
            spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return False
        
        perc = self.ctl.battery_feature.get_perc(spec)
        if perc is None:
            return False

        return perc < self.MIN_BATTERY_PERC

    def disconnect(self):
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return

        if spec.settings.state.laser_enabled:
            spec.change_device_setting("laser_enable", False)

    def set_mW(self, mW):
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return
        if not spec.settings.state.use_mW:
            self.configure_laser_power_controls_mW()
        self.ctl.form.ui.doubleSpinBox_laser_power.setValue(mW)

    def set_perc(self, perc):
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return
        if spec.settings.state.use_mW:
            self.configure_laser_power_controls_percent()
        self.ctl.form.ui.doubleSpinBox_laser_power.setValue(perc)

    # ##########################################################################
    # Private Methods
    # ##########################################################################

    def refresh_laser_button(self):
        spec = self.ctl.multispec.current_spectrometer()
        enabled = spec.settings.state.laser_enabled if spec else False
        b = self.ctl.form.ui.pushButton_laser_toggle
        if enabled:
            b.setText(self.BTN_OFF_TEXT)
        else:
            b.setText(self.BTN_ON_TEXT)
        self.ctl.gui.colorize_button(b, enabled)

        self.refresh_watchdog_tooltip()

    def refresh_watchdog_tooltip(self):
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return

        watchdog_sec = spec.settings.state.laser_watchdog_sec
        sb = self.ctl.form.ui.spinBox_laser_watchdog_sec
        if self.ctl.form.ui.checkBox_laser_watchdog.isChecked():
            sb.setToolTip(f"Laser will automatically stop firing after {watchdog_sec} seconds")
        else:
            sb.setToolTip("Laser watchdog disabled")

    def configure_laser_power_controls_percent(self):
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return

        spinbox  = self.ctl.form.ui.doubleSpinBox_laser_power
        slider   = self.ctl.form.ui.verticalSlider_laser_power
        settings = spec.settings

        if settings.state.use_mW:
            # convert from mW -> %
            value = settings.eeprom.laser_power_mW_to_percent(settings.state.laser_power_mW)
        else:
            value = settings.state.laser_power_perc

        util.set_min_max(slider,  1, 100)
        util.set_min_max(spinbox, 1, 100, value)
        settings.state.use_mW = False

        spinbox.setSuffix("%")

        spinbox.setValue(value)

        spec.change_device_setting("laser_power_require_modulation", False)

        log.debug("configure_laser_power_controls_percent: value %s, suffix %s", value, spinbox.suffix())

    def configure_laser_power_controls_mW(self):
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return

        spinbox  = self.ctl.form.ui.doubleSpinBox_laser_power
        slider   = self.ctl.form.ui.verticalSlider_laser_power
        settings = spec.settings

        if settings.state.use_mW:
            value = settings.state.laser_power_mW
        else:
            # There is no quick way to convert the current laser power from
            # percent to mW (we don't store a calibration in that direction),
            # so just set it to maximum mW.
            #
            # TODO: If we really wanted, we could generate a LUT of (mW -> perc)
            # pairs from eeprom.laser_power_coeff, then dynamically make a
            # reverse calibration from (perc -> mW).  Would have error margin tho.
            value = settings.eeprom.max_laser_power_mW

        util.set_min_max(slider,  settings.eeprom.min_laser_power_mW,
                                  settings.eeprom.max_laser_power_mW)
        util.set_min_max(spinbox, settings.eeprom.min_laser_power_mW,
                                  settings.eeprom.max_laser_power_mW, value)
        settings.state.use_mW = True

        spinbox.setSuffix("mW")

        spec.change_device_setting("laser_power_require_modulation", True)
        spec.change_device_setting("laser_power_mW", value)

        log.debug("configure_laser_power_controls_mW: value %s, suffix %s", value, spinbox.suffix())

    def configure_watchdog(self, init=False):
        log.debug(f"configure_watchdog(init {init})")
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return

        has_laser = spec.settings.eeprom.has_laser
        is_xs = spec.settings.is_xs()
        lb_watchdog = self.ctl.form.ui.label_laser_watchdog_sec
        sb_watchdog = self.ctl.form.ui.spinBox_laser_watchdog_sec
        cb_watchdog = self.ctl.form.ui.checkBox_laser_watchdog

        if not (is_xs and has_laser):
            sb_watchdog.setVisible(False)
            lb_watchdog.setVisible(False)
            cb_watchdog.setVisible(False)
            return

        sb_watchdog.setVisible(True)
        lb_watchdog.setVisible(True)
        cb_watchdog.setVisible(True)
        
        sec = spec.settings.eeprom.laser_watchdog_sec

        if init and sec <= 0:
            # Acknowledge that the watchdog was disabled in the EEPROM.
            # We use this to disable annoying pop-up messages warning
            # the user about disabling the watchdog.  It's also possible
            # this is an older model that doesn't HAVE a watchdog.
            spec.app_state.laser_watchdog_disabled = True
            log.debug("watchdog was disabled in the EEPROM")

            # Nonetheless, ignore the disabled state and re-enable the
            # watchdog at runtime.  This is for safety and avoid product 
            # damage.  If the user wants to change it back to zero in 
            # ENLIGHTEN, they can (and we won't nag them about it), but
            # they have to explicitly choose "unsafe / destructive" every
            # session.
            sec = EEPROM.DEFAULT_LASER_WATCHDOG_SEC
            log.debug(f"declining to disable laser watchdog at connection, defaulting to {sec} sec")
            spec.settings.state.laser_watchdog_sec = sec
        
            # TODO: hide watchdog config and show "No watchdog msg"
        
        else:
            sb_watchdog.setValue(sec)

    # ##########################################################################
    # Callbacks
    # ##########################################################################

    def up_callback(self):
        util.incr_spinbox(self.ctl.form.ui.doubleSpinBox_laser_power)

    def dn_callback(self):
        util.decr_spinbox(self.ctl.form.ui.doubleSpinBox_laser_power)

    ##
    # This is going to give some weird results if some spectrometers have a laser
    # power calibration and others don't.
    #
    # What it does now is uses the CURRENT spectrometer to decide if the commanded
    # power was in percent or mW, then sends that command (mW or perc) downstream
    # to all spectrometers with the associated value.
    #
    # If some spectrometers don't support the command (either because they have no
    # laser or lack a power calibration), they'll do whatever Wasatch.PY tells them
    # to do (probably nothing).  If the power is out-of-range for some, same deal.
    #
    def set_laser_power_callback(self):
        if self.slider_stop_usb:
            return
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return

        if spec.settings.state.use_mW:
            setting = "laser_power_mW"
        else:
            setting = "laser_power_perc"

        value = self.ctl.form.ui.doubleSpinBox_laser_power.value()
        self.ctl.multispec.set_state("laser_power", value)
        self.ctl.multispec.change_device_setting(setting, value)

    def set_watchdog_time(self, sec):
        # maintain application state
        self.ctl.multispec.set_state("laser_watchdog_sec", sec)
        # set the spectrometer's watchdog time
        self.ctl.multispec.change_device_setting("laser_watchdog_sec", sec)

    # called when watchdog is checked ON or OFF
    def set_watchdog_enable_callback(self, state):
        lb_watchdog = self.ctl.form.ui.label_laser_watchdog_sec
        sb_watchdog = self.ctl.form.ui.spinBox_laser_watchdog_sec
        cb_watchdog = self.ctl.form.ui.checkBox_laser_watchdog
        if not state:

            log.debug("User initiated watchdog disable")

            if self.confirm_disable():

                log.debug("User confirmed watchdog disable")

                # disable the watchdog
                self.set_watchdog_time(0)
                sb_watchdog.setVisible(False)
                lb_watchdog.setVisible(False)
            else:

                log.debug("User cancelled watchdog disable")

                # undo unchecking
                cb_watchdog.setChecked(True)
        else:

            log.debug("User enabled watchdog")

            # set the watchdog to the spinbox value
            sb_watchdog.setVisible(True)
            lb_watchdog.setVisible(True)
            self.set_watchdog_callback()

    # called when watchdog interval (sec) is changed
    def set_watchdog_callback(self):
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return

        sec = self.ctl.form.ui.spinBox_laser_watchdog_sec.value()
        log.debug(f"set_watchdog_callback: asked to set watchdog to {sec} seconds")

        # not possible with spinbox min = 3
        if sec < 3:
            log.critical("Watchdog spinbox set below desired minimum (<3)")
            return

        self.set_watchdog_time(sec)

        if spec.settings.state.laser_enabled:
            self.set_laser_enable(False)

        self.refresh_watchdog_tooltip()

    ## @todo consider making this a generic utility method (compare with EEPROMWriter)
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

        label = spec.label

        log.debug("prompting user to confirm their decision to disable the laser watchdog")
        box = QtWidgets.QMessageBox()
        box.setIcon(QtWidgets.QMessageBox.Warning)
        box.setWindowTitle(label)
        box.setText("Are you sure you wish to disable the laser watchdog? " +
            "Running the laser without watchdog could damage the instrument, risk human injury " +
            "and may void your warranty.")
        box.setInformativeText("Disabling watchdog may void warranty.")
        box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Cancel)

        retval = box.exec_()

        if retval != QtWidgets.QMessageBox.Yes:
            log.debug("user declined to disable laser watchdog on %s", label)
            self.ctl.marquee.clear(token="laser_watchdog")
            return False
        return True

    ##
    # This is a little convoluted because "laser enabled" was implemented
    # as a button rather than a checkbox.
    def toggle_callback(self):
        log.debug("toggle_callback: start")
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            log.debug("toggle_callback: no spectrometer?")
            return

        # invert the previous state
        flag = not spec.settings.state.laser_enabled
        log.debug(f"toggle_callback: laser_enabled was {spec.settings.state.laser_enabled}, so setting {flag}")

        # safety check for developmental firmware: if the user was trying to turn
        # the laser off, turn it off regardless of previous "believed" state. The
        # problem is there is no Checked() method on a button to determine 
        # "previous state" (they're stateless), and it's possible that 
        # state.laser_enabled could be wrong if wasatch.get_laser_enabled() isn't
        # working right due to FW bugs, so go by our internal tracking of the
        # user's "last request".
        if flag:
            # by default, we would be turning the laser ON at this point, since
            # laser_enabled is apparently False

            if spec.app_state.laser_state != LaserStates.DISABLED:
                # however, laser_state implies that ENLIGHTEN thought the laser
                # was either firing, or had been requested to fire

                flag = False
                log.critical(f"toggle_callback: turning laser OFF even though previous spec.settings.state.laser_enabled was {spec.settings.state.laser_enabled}, as spec.app_state.laser_state is {spec.app_state.laser_state}")

        self.set_laser_enable(flag)
        token = "laser_init"

        if flag:
            self.ctl.marquee.info("laser is initializing and stabilizing for use", token=token, period_sec=10)
        else:
            self.ctl.marquee.clear(token=token)

    ## 
    # This gets called when the "front" (Scope) laser excitation value is changed.
    # Note this will happen when excitation is changed in EEPROMEditor, as that object
    # calls Controller.update_wavecal which syncs the two excitation spinboxen.
    def excitation_callback(self):
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return

        value = self.ctl.form.ui.doubleSpinBox_excitation_nm.value()
        log.debug("changing current spectrometer's excitation to %.2f", value)

        spec.settings.eeprom.excitation_nm_float = value
        self.ctl.eeprom_editor.widget_callback("excitation_nm_float", reset_from_eeprom=True)

    # gets called by BatteryFeature when a new battery reading is received
    def battery_callback(self, perc, charging):
        enough_for_laser = perc >= self.MIN_BATTERY_PERC
        log.debug("enough_for_laser = %s (%.2f%%)" % (enough_for_laser, perc))

        b = self.ctl.form.ui.pushButton_laser_toggle
        b.setEnabled(enough_for_laser)
        b.setToolTip("Toggle laser (ctrl-L)" if enough_for_laser else "battery low ({perc:.2f}%)")

    def slider_power_callback(self):
        self.slider_stop_usb = False
        position = self.ctl.form.ui.verticalSlider_laser_power.sliderPosition()
        self.ctl.form.ui.doubleSpinBox_laser_power.setValue(position)
        self.set_laser_power_callback()

    # set a flag to prevent sending a command to the spectrometer
    # This prevents flooding the spec with laser values while the slider is moving
    # When it releases, the flag will be cleared and then it will send one, final, laser value
    def slider_power_press_callback(self):
        self.slider_stop_usb = True
