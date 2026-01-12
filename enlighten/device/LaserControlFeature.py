import logging

from enlighten import util
from enlighten.common import LaserStates

from enlighten.ui.ScrollStealFilter import ScrollStealFilter
from enlighten.ui.MouseWheelFilter import MouseWheelFilter

log = logging.getLogger(__name__)

class LaserControlFeature:
    """
    Encapsulate laser control from the application side.
    """

    MIN_BATTERY_PERC = 5
    BTN_OFF_TEXT = "Turn Laser Off"
    BTN_ON_TEXT = "Turn Laser On"

    MIN_INITIALIZATION_RATIO = 1.20 # 20% increase

    LASER_INIT_TOKEN = "laser_init"

    SECTION = "LaserControlFeature"

    def __init__(self, ctl):
        self.ctl = ctl

        self.ctl.battery_feature.register_observer(self.battery_callback)

        self.slider_stop_usb = False
        self.locked = False
        self.restrictions = set()
        self.observers = { "enabled": set(), "disabled": set() }

        self.initializing = False
        self.area_at_start = None
        self.min_at_start = None
        self.xs_password_provided = False
        self.current_spectrometer_callback = None # override callback to ctl.multispec.current_spectrometer()

        cfu = self.ctl.form.ui

        cfu.pushButton_laser_power_dn   .clicked            .connect(self.dn_callback)
        cfu.pushButton_laser_power_up   .clicked            .connect(self.up_callback)
        cfu.pushButton_laser_toggle     .clicked            .connect(self.toggle_callback)
        cfu.pushButton_laser_convenience.clicked            .connect(self.toggle_callback)
        cfu.verticalSlider_laser_power  .sliderPressed      .connect(self.slider_power_press_callback)
        cfu.verticalSlider_laser_power  .sliderMoved        .connect(cfu.doubleSpinBox_laser_power.setValue)
        cfu.verticalSlider_laser_power  .sliderReleased     .connect(self.slider_power_callback)
        cfu.doubleSpinBox_excitation_nm .valueChanged       .connect(self.excitation_callback)
        cfu.doubleSpinBox_laser_power   .valueChanged       .connect(cfu.verticalSlider_laser_power.setValue)
        cfu.doubleSpinBox_laser_power   .valueChanged       .connect(self.set_laser_power_callback)
        cfu.comboBox_laser_power_unit   .currentIndexChanged.connect(self.update_visibility)

        cfu.pushButton_laser_toggle     .setWhatsThis("Primary means to turn the laser on or off. Also available through a 'convenience' button at the screen top-right.")
        cfu.pushButton_laser_convenience.setWhatsThis("This is a 'convenience' shortcut for the Fire Laser button on the main Control Palette, positioned to ensure it's always accessible and visible")
        cfu.doubleSpinBox_excitation_nm .setWhatsThis("If you know the exact wavelength of your laser in nanometers, enter it here to improve wavenumber axis accuracy")
        cfu.comboBox_laser_power_unit   .setWhatsThis("Switch laser power units between duty-cycle percentage and calibrated milliWatts")

        self.expert_widgets = [
            cfu.label_lightSourceWidget_excitation_nm,
            cfu.doubleSpinBox_excitation_nm
        ]

        for widget in [ cfu.verticalSlider_laser_power ]:
            widget.installEventFilter(MouseWheelFilter(widget))

        for widget in [ cfu.doubleSpinBox_excitation_nm,
                        cfu.doubleSpinBox_laser_power,
                        cfu.comboBox_laser_power_unit ]:
            widget.installEventFilter(ScrollStealFilter(widget))

        self.ctl.page_nav.register_observer("mode", self.page_nav_mode_callback)

    def page_nav_mode_callback(self):
        cfu = self.ctl.form.ui

        doing_expert = self.ctl.page_nav.doing_expert()
        for widget in self.expert_widgets:
            widget.setVisible(doing_expert)

        spec = self.current_spectrometer()

        has_laser_power_calibration = spec is not None and spec.settings.eeprom.has_laser_power_calibration()
        cfu.comboBox_laser_power_unit.setVisible(has_laser_power_calibration and doing_expert)

    def set_current_spectrometer_callback(self, callback):
        self.current_spectrometer_callback = callback

    def current_spectrometer(self):
        """ 
        Allow ctl.multispec.current_spectrometer to be overridden by an external
        callback. This is provided for plugins.network.IDSPeak.
        """
        if self.current_spectrometer_callback:
            return self.current_spectrometer_callback()
        return self.ctl.multispec.current_spectrometer()

    # ##########################################################################
    # Public Methods
    # ##########################################################################

    def register_observer(self, event, callback):
        if event not in self.observers:
            log.error(f"register_observer: unsupported event {event}")
            return
        self.observers[event].add(callback)

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
        spec = self.current_spectrometer()
        if spec is None:
            return

        settings = spec.settings
        state = settings.state

        if not settings.eeprom.has_laser:
            return

        state.laser_power_perc = 100
        state.laser_power_mW = settings.eeprom.max_laser_power_mW
        state.use_mW = settings.eeprom.has_laser_power_calibration() and settings.is_mml()
        log.debug(f"init_hotplug: laser_power_perc {state.laser_power_perc}, laser_power_mW {state.laser_power_mW}, use_mW {state.use_mW}")

        self.set_laser_enable(False)
        
        spec.change_device_setting("laser_power_high_resolution", True)

    ##
    # Called by initialize_new_device when the user selected one of several 
    # connected spectrometers.
    def update_visibility(self, init=False):
        log.debug(f"update_visibility(init={init})")
        spec = self.current_spectrometer()
        cfu = self.ctl.form.ui
        
        if spec is None:
            log.debug(f"update_visibility: returning because spec {spec}")
            return

        settings = spec.settings
        has_laser = settings.eeprom.has_laser
        doing_expert = self.ctl.page_nav.doing_expert()
        is_ilc = any([component in settings.full_model().upper() for component in ["-ILC", "-IL-IC"]])
        combo_unit = cfu.comboBox_laser_power_unit

        for widget in [ cfu.frame_lightSourceControl,
                        cfu.pushButton_laser_convenience ]:
            widget.setVisible(has_laser)
        if not has_laser:
            log.debug(f"update_visibility: returning because has_laser {has_laser}")
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

        # let them turn the laser on/off, nothing else (including watchdog)
        for w in [ cfu.checkBox_laser_watchdog,
                   cfu.comboBox_laser_power_unit,
                   cfu.comboBox_laser_tec_mode,
                   cfu.doubleSpinBox_excitation_nm,
                   cfu.doubleSpinBox_laser_power,
                   cfu.pushButton_laser_power_dn,
                   cfu.pushButton_laser_power_up,
                   cfu.spinBox_laser_watchdog_sec,
                   cfu.verticalSlider_laser_power ]:
            w.setEnabled(not self.locked)

        self.refresh_laser_buttons()

    # expose this setter for BatchCollection and plugins
    def set_laser_enable(self, flag, spec=None, all_=False):

        # BatchCollection doesn't use multispec.lock (it's not enforcing
        # synchronization in other commands), but it does manually send
        # an "all" to enable the lasers on all connected spectrometers.
        if all_:
            for spec in self.ctl.multispec.get_spectrometers():
                self.set_laser_enable(flag, spec=spec)
            return

        # not all...

        if self.current_spectrometer_callback:
            spec = self.current_spectrometer()
        if spec is None:
            # if we were NOT given a specific spectrometer (so this is
            # the default behavior, like clicking the GUI button), then
            # default to the current spectrometer, and obey multispec
            # locking if enabled
            spec = self.current_spectrometer()
            use_multispec = True
        else:
            # we were given a specific spectrometer (possibly via 'all',
            # possibly not), so don't do anything with multispec locking
            use_multispec = False

        if spec is None:
            return

        log.debug(f"set_laser_enable: sending flag {flag} to spec {spec} (use_multispec {use_multispec})")

        if use_multispec:
            self.ctl.multispec.set_state("laser_enabled", flag)
            self.ctl.multispec.change_device_setting("laser_enable", flag)
        else:
            spec.settings.state.laser_enabled = flag
            spec.change_device_setting("laser_enable", flag)

        spec.app_state.laser_state = LaserStates.REQUESTED if flag else LaserStates.DISABLED

        if self.ctl.multispec.is_current_spectrometer(spec) or self.current_spectrometer_callback:
            self.refresh_laser_buttons()

        self.ctl.status_indicators.update_visibility()

        event = "enabled" if flag else "disabled"
        for callback in self.observers[event]:
            log.debug(f"set_laser_enable: calling {event} callback {callback}")
            callback()

        self.ctl.sounds.play("laser_on" if flag else "laser_off")

    def tick_status(self):
        """ Called from Controller.tick_status """
        spec = self.current_spectrometer()
        if spec is None:
            return

        if spec.settings.state.laser_enabled:
            self.ctl.sounds.play("laser_steady", repeat=True)

    def process_reading(self, reading):
        spec = self.current_spectrometer()
        if spec is None:
            return

        if reading is None:
            return

        if reading.laser_enabled is None:
            log.debug("update_laser_status: reading.laser_enabled is None")
            return

        if spec.settings.eeprom.has_interlock_feedback:
            # we have interlock feedback (and by implication, laser firing 
            # feedback) so use that

            definitely_on = False
            if not reading.laser_can_fire:
                if spec.app_state.laser_state != LaserStates.DISABLED:
                    self.set_laser_enable(False, spec)
                self.set_restriction("Interlock open")
            else:
                self.clear_restriction("Interlock open")
                if reading.laser_is_firing:
                    definitely_on = True
            self.refresh_laser_buttons(force_on=definitely_on)
        else:
            # we DON'T have interlock feedback (or laser firing feedback) so use
            # looser rules
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
                    # log.debug("all agree laser firing")
                    pass
            else:
                # reading says laser not firing
                if state == LaserStates.DISABLED:
                    # log.debug("all agree laser disabled")
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
            spec = self.current_spectrometer()
        if spec is None:
            return False
        
        perc = self.ctl.battery_feature.get_perc(spec)
        if perc is None:
            return False

        return perc < self.MIN_BATTERY_PERC

    def disconnect(self):
        log.debug("disconnect: start")
        spec = self.current_spectrometer()
        if spec and spec.settings.state.laser_enabled:
            spec.change_device_setting("laser_enable", False)
        self.refresh_laser_buttons(force_off=True)

    def set_mW(self, mW):
        spec = self.current_spectrometer()
        if spec is None:
            return
        if not spec.settings.state.use_mW:
            self.configure_laser_power_controls_mW()
        self.ctl.form.ui.doubleSpinBox_laser_power.setValue(mW)

    def set_perc(self, perc):
        spec = self.current_spectrometer()
        if spec is None:
            return
        if spec.settings.state.use_mW:
            self.configure_laser_power_controls_percent()
        self.ctl.form.ui.doubleSpinBox_laser_power.setValue(perc)

    def update_laser_firing_indicators(self, flag):
        self.refresh_laser_buttons(force_on=flag)
        self.ctl.status_indicators.force_laser_on = flag

    # ##########################################################################
    # Private Methods
    # ##########################################################################

    def refresh_laser_buttons(self, force_on=False, force_off=False):
        """ 
        force_on means whether the button is red (indicate laser is enabled and 
        firing) or grey (imply laser is not enabled and not firing). This doesn't
        actually affect whether the button is clickable -- that is determined by
        'allowed'.
        """
        log.debug("refresh_laser_buttons: start")
        spec = self.current_spectrometer()
        cfu = self.ctl.form.ui

        enabled = not force_off and (force_on or (spec and spec.settings.state.laser_enabled))
        allowed = 0 == len(self.restrictions)
        why_not = ", ".join(self.restrictions)

        log.debug(f"refresh_laser_buttons: enabled {enabled}, allowed {allowed}, why_not {why_not}")

        if enabled:
            cfu.pushButton_laser_toggle.setText(self.BTN_OFF_TEXT)
        else:
            cfu.pushButton_laser_toggle.setText(self.BTN_ON_TEXT)

        for b in [ cfu.pushButton_laser_toggle, cfu.pushButton_laser_convenience ]:
            b.setEnabled(allowed)
            b.setToolTip("Toggle laser (ctrl-L)" if allowed else f"Disabled ({why_not})")
            self.ctl.gui.colorize_button(b, enabled)
            log.debug(f"refresh_laser_buttons: updated button {b} with enabled {enabled}, allowed {allowed}, why_not {why_not}")

    def configure_laser_power_controls_percent(self):
        spec = self.current_spectrometer()
        if spec is None:
            return

        spinbox  = self.ctl.form.ui.doubleSpinBox_laser_power
        slider   = self.ctl.form.ui.verticalSlider_laser_power
        settings = spec.settings

        if settings.state.use_mW:
            # convert from mW -> %
            current_mW = settings.state.laser_power_mW
            log.debug(f"configure_laser_power_controls_percent: use_mW True, so converting {current_mW}mW to percent")
            value = settings.eeprom.laser_power_mW_to_percent(current_mW)
        else:
            value = settings.state.laser_power_perc

        log.debug(f"configure_laser_power_controls_percent: setting slider to {value}%, and use_mW False")
        util.set_min_max(slider,  1, 100)
        util.set_min_max(spinbox, 1, 100, value)
        settings.state.use_mW = False

        spinbox.setSuffix("%")

        spinbox.setValue(value)

        spec.change_device_setting("laser_power_require_modulation", False)

        log.debug("configure_laser_power_controls_percent: value %s, suffix %s", value, spinbox.suffix())

    def configure_laser_power_controls_mW(self):
        spec = self.current_spectrometer()
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

    # ##########################################################################
    # Callbacks
    # ##########################################################################

    def up_callback(self):
        util.incr_spinbox(self.ctl.form.ui.doubleSpinBox_laser_power)

    def dn_callback(self):
        util.decr_spinbox(self.ctl.form.ui.doubleSpinBox_laser_power)

    def set_laser_power_callback(self):
        if self.slider_stop_usb:
            return
        spec = self.current_spectrometer()
        if spec is None:
            return

        if spec.settings.state.use_mW:
            setting = "laser_power_mW"
        else:
            setting = "laser_power_perc"

        value = self.ctl.form.ui.doubleSpinBox_laser_power.value()
        spec.settings.state.laser_power = value
        spec.change_device_setting(setting, value)

    ##
    # This is a little convoluted because "laser enabled" was implemented
    # as a button rather than a checkbox.
    def toggle_callback(self):
        log.debug("toggle_callback: start")
        spec = self.current_spectrometer()
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
        
        if flag:
            self.ctl.marquee.info("laser preparing to fire", token=self.LASER_INIT_TOKEN, period_sec=10) # consider persist=True
        else:
            self.ctl.marquee.clear(token=self.LASER_INIT_TOKEN)

        self.initializing = flag

    ## 
    # This gets called when the "front" (Scope) laser excitation value is changed.
    # Note this will happen when excitation is changed in EEPROMEditor, as that object
    # calls Controller.update_wavecal which syncs the two excitation spinboxen.
    def excitation_callback(self):
        spec = self.current_spectrometer()
        if spec is None:
            return

        cfu = self.ctl.form.ui

        value = cfu.doubleSpinBox_excitation_nm.value()
        log.debug("changing current spectrometer's excitation to %.2f", value)

        spec.settings.eeprom.multi_wavelength_calibration.set("excitation_nm_float", value)

        log.debug("calling Settings.update_wavecal")
        spec.settings.update_wavecal()

    # gets called by BatteryFeature when a new battery reading is received
    def battery_callback(self, perc, charging):
        enough_for_laser = perc >= self.MIN_BATTERY_PERC
        log.debug("enough_for_laser = %s (%.2f%%)" % (enough_for_laser, perc))

        if enough_for_laser:
            self.clear_restriction("low battery")
        else:
            self.set_restriction("low battery")
            log.debug("since battery is low, make sure laser is OFF")
            self.set_laser_enable(False)

    def clear_restriction(self, reason):
        if reason in self.restrictions:
            self.restrictions.remove(reason)
        self.refresh_laser_buttons()

    def set_restriction(self, reason):
        self.restrictions.add(reason)
        self.refresh_laser_buttons()

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

    def laser_can_fire_per_password(self):
        spec = self.current_spectrometer()
        if spec is None:
            return False
        if self.xs_password_provided:
            return True
        if not spec.settings.is_xs():
            return True

        title = "XS Laser Safety PIN"
        label_text = "Enter password to allow XS laser to fire"
        result = self.ctl.gui.msgbox_with_lineedit(self, title=title, label_text=label_text, lineedit_text=None)
        self.xs_password_provided = result and result["ok"]

        return self.xs_password_provided
