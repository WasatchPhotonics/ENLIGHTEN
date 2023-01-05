import time
from datetime import datetime, timedelta
import logging

from PySide2 import QtWidgets 

from . import util
from .common import LaserStates

from wasatch.EEPROM                   import EEPROM

from .ScrollStealFilter import ScrollStealFilter
from .MouseWheelFilter import MouseWheelFilter

log = logging.getLogger(__name__)

##
# Encapsulate laser control from the application side.
class LaserControlFeature:

    def __init__(self,
                 battery_feature,
                 eeprom_editor,     # because of spinbox_excitation
                 gui,
                 marquee,
                 multispec,
                 page_nav,
                 status_indicators,
                 raman_intensity_correction,

                 button_dn,
                 button_up,
                 button_toggle,
                 frame,
                 lb_watchdog,
                 spinbox_excitation,    # doubleSpinBox on Laser Control widget, not EEPROMEditor
                 spinbox_power,         # doubleSpinBox
                 slider_power,
                 spinbox_watchdog,
                 guide):

        self.eeprom_editor      = eeprom_editor
        self.gui                = gui
        self.marquee            = marquee
        self.multispec          = multispec
        self.page_nav           = page_nav
        self.status_indicators  = status_indicators
        self.guide              = guide

        self.button_dn          = button_dn
        self.button_up          = button_up
        self.button_toggle      = button_toggle
        self.frame              = frame
        self.lb_watchdog        = lb_watchdog
        self.spinbox_excitation = spinbox_excitation
        self.spinbox_power      = spinbox_power
        self.slider_power       = slider_power
        self.spinbox_watchdog   = spinbox_watchdog
        self.raman_intensity_correction = raman_intensity_correction

        battery_feature.register_observer(self.battery_callback)

        self.slider_stop_usb    = False
        self.displayed_srm_tip  = False

        self.button_dn          .clicked            .connect(self.dn_callback)
        self.button_up          .clicked            .connect(self.up_callback)
        self.button_toggle      .clicked            .connect(self.toggle_callback)
        self.slider_power       .sliderPressed      .connect(self.slider_power_press_callback)
        self.slider_power       .sliderMoved        .connect(self.spinbox_power.setValue)
        self.slider_power       .sliderReleased     .connect(self.slider_power_callback)
        self.slider_power                           .installEventFilter(MouseWheelFilter(self.slider_power))
        self.spinbox_excitation .valueChanged       .connect(self.excitation_callback)
        self.spinbox_power      .valueChanged       .connect(self.slider_power.setValue)
        self.spinbox_power      .valueChanged       .connect(self.set_laser_power_callback)
        self.spinbox_watchdog   .valueChanged       .connect(self.set_watchdog_callback)

        for key, item in self.__dict__.items():
            if key.startswith("spinbox_") or key.startswith("combo_"):
                item.installEventFilter(ScrollStealFilter(item))

    # ##########################################################################
    # Public Methods
    # ##########################################################################

    ##
    # Called by initialize_new_device when a new device has been connected:
    #
    # - default to 100% power (and max calibrated mW)
    # - default to "mW" if calibration found
    # - disable laser
    # - default to high-resolution laser power (1ms pulse period)
    def init_hotplug(self):
        spec = self.multispec.current_spectrometer()
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
        spec = self.multispec.current_spectrometer()
        if spec is None:
            self.lb_watchdog.setVisible(False)
            return

        settings = spec.settings
        has_laser = settings.eeprom.has_laser

        self.frame.setVisible(has_laser)
        if not has_laser:
            return

        has_calibration = settings.eeprom.has_laser_power_calibration()
        log.debug("update_visibility: laser power calibration %s", has_calibration)

        if not has_calibration:
            self.configure_laser_power_controls_percent()
        else:
            if settings.state.use_mW:
                self.configure_laser_power_controls_mW()
            else:
                self.configure_laser_power_controls_percent()

        self.configure_watchdog()

        self.refresh_laser_button()

    # expose this setter for BatchCollection
    def set_laser_enable(self, flag, spec=None, all=False):

        # BatchCollection doesn't use multispec.lock (it's not enforcing
        # synchronization in other commands), but it does manually send
        # an "all" to enable the lasers on all connected spectrometers.
        if all:
            for spec in self.multispec.get_spectrometers():
                self.set_laser_enable(flag, spec=spec)
            return

        # not all...

        if spec is None:
            # if we were NOT given a specific spectrometer (so this is
            # the default behavior, like clicking the GUI button), then
            # default to the current spectrometer, and obey multispec
            # locking if enabled
            spec = self.multispec.current_spectrometer()
            use_multispec = True
        else:
            # we were given a specific spectrometer (possibly via 'all',
            # possibly not), so don't do anything with multispec locking
            use_multispec = False

        if spec is None:
            return

        if not self.raman_intensity_correction.enabled and \
                self.raman_intensity_correction.is_supported() and \
                self.page_nav.doing_raman() and \
                not self.displayed_srm_tip and \
                flag:
            self.guide.suggest("Tip: Raman response is more consistent when using Raman Intensity Correction", token="enable_raman_intensity_correction")
            self.displayed_srm_tip = True

        if use_multispec:
            self.multispec.set_state("laser_enabled", flag)
            self.multispec.change_device_setting("laser_enable", flag)
        else:
            spec.settings.state.laser_enabled = flag
            spec.change_device_setting("laser_enable", flag)

        spec.app_state.laser_state = LaserStates.REQUESTED if flag else LaserStates.DISABLED

        if self.multispec.is_current_spectrometer(spec):
            self.refresh_laser_button()

        self.status_indicators.update_visibility()

    def process_reading(self, reading):
        spec = self.multispec.current_spectrometer()
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

    def disconnect(self):
        spec = self.multispec.current_spectrometer()
        if spec is None:
            return

        if spec.settings.state.laser_enabled:
            spec.change_device_setting("laser_enable", False)

    # ##########################################################################
    # Private Methods
    # ##########################################################################

    def refresh_laser_button(self):
        spec = self.multispec.current_spectrometer()
        enabled = spec.settings.state.laser_enabled if spec else False
        if enabled:
            self.button_toggle.setText("Turn Laser Off")
        else:
            self.button_toggle.setText("Turn Laser On")
        self.gui.colorize_button(self.button_toggle, enabled)

        self.refresh_watchdog_tooltip()

    def refresh_watchdog_tooltip(self):
        spec = self.multispec.current_spectrometer()
        if spec is None:
            return

        watchdog_sec = spec.settings.state.laser_watchdog_sec
        if watchdog_sec > 0:
            self.spinbox_watchdog.setToolTip(f"Laser will automatically stop firing after {watchdog_sec} seconds")
        else:
            self.spinbox_watchdog.setToolTip("Laser watchdog disabled")

    def configure_laser_power_controls_percent(self):
        spec = self.multispec.current_spectrometer()
        if spec is None:
            return

        spinbox  = self.spinbox_power
        slider   = self.slider_power
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
        spec = self.multispec.current_spectrometer()
        if spec is None:
            return

        spinbox  = self.spinbox_power
        slider   = self.slider_power
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
        spec = self.multispec.current_spectrometer()
        if spec is None:
            return

        has_laser = spec.settings.eeprom.has_laser
        is_xs = spec.settings.is_xs()

        if not (is_xs and has_laser):
            self.spinbox_watchdog.setVisible(False)
            self.lb_watchdog.setVisible(False)
            return

        self.spinbox_watchdog.setVisible(True)
        self.lb_watchdog.setVisible(True)
        
        sec = spec.settings.eeprom.laser_watchdog_sec

        if init and sec <= 0:
            sec = EEPROM.DEFAULT_LASER_WATCHDOG_SEC
            log.debug(f"declining to disable laser watchdog at connection, defaulting to {sec} sec")
            spec.settings.state.laser_watchdog_sec = sec

        self.spinbox_watchdog.setValue(sec)

    # ##########################################################################
    # Callbacks
    # ##########################################################################

    def up_callback(self):
        util.incr_spinbox(self.spinbox_power)

    def dn_callback(self):
        util.decr_spinbox(self.spinbox_power)

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
        spec = self.multispec.current_spectrometer()
        if spec is None:
            return

        if spec.settings.state.use_mW:
            setting = "laser_power_mW"
        else:
            setting = "laser_power_perc"

        value = self.spinbox_power.value()
        self.multispec.set_state("laser_power", value)
        self.multispec.change_device_setting(setting, value)

    def set_watchdog_callback(self):
        spec = self.multispec.current_spectrometer()
        if spec is None:
            return

        sec = self.spinbox_watchdog.value()
        log.debug(f"set_watchdog_callback: asked to set watchdog to {sec} seconds")

        if sec <= 0 and not self.confirm_disable():
            return

        self.multispec.set_state("laser_watchdog_sec", sec)
        self.multispec.change_device_setting("laser_watchdog_sec", sec)

        if spec.settings.state.laser_enabled:
            self.set_laser_enable(False)

        self.refresh_watchdog_tooltip()

    ## @todo consider making this a generic utility method (compare with EEPROMWriter)
    def confirm_disable(self) -> bool:
        spec = self.multispec.current_spectrometer()
        if spec is None:
            return
        label = spec.label

        log.debug("prompting user to confirm their decision to disable the laser watchdog")
        box = QtWidgets.QMessageBox()
        box.setIcon(QtWidgets.QMessageBox.Warning)
        box.setWindowTitle(label)
        box.setText("Are you sure you wish to disable the laser watchdog? " +
            "Running the laser without watchdog could damage the instrument, risk human injury " +
            "and void your warranty.")
        box.setInformativeText("Disabling watchdog voids warranty.")
        box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Cancel)

        retval = box.exec_()

        if retval != QtWidgets.QMessageBox.Yes:
            log.debug("user declined to disable laser watchdog on %s", label)
            self.marquee.clear(token="laser_watchdog")
            self.spinbox_watchdog.setValue(spec.settings.state.laser_watchdog_sec)
            return False
        return True

    ##
    # This is a little convoluted because "laser enabled" was implemented
    # as a button rather than a checkbox.
    def toggle_callback(self):
        log.debug("toggle_callback: start")
        spec = self.multispec.current_spectrometer()
        if spec is None:
            log.debug("toggle_callback: no spectrometer?")
            return

        # invert the previous state
        flag = not spec.settings.state.laser_enabled
        log.debug(f"toggle_callback: laser_enabled was {spec.settings.state.laser_enabled}, so setting {flag}")
        self.set_laser_enable(flag)

        token = "laser_init"

        if flag:
            self.marquee.info("laser is initializing and stabilizing for use", token=token, period_sec=10)
        else:
            self.marquee.clear(token=token)

    ## 
    # This gets called when the "front" (Scope) laser excitation value is changed.
    # Note this will happen when excitation is changed in EEPROMEditor, as that object
    # calls Controller.update_wavecal which syncs the two excitation spinboxen.
    def excitation_callback(self):
        spec = self.multispec.current_spectrometer()
        if spec is None:
            return

        value = self.spinbox_excitation.value()
        log.debug("changing current spectrometer's excitation to %.2f", value)

        spec.settings.eeprom.excitation_nm_float = value
        self.eeprom_editor.widget_callback("excitation_nm_float", reset_from_eeprom=True)

    # gets called by BatteryFeature when a new battery reading is received
    def battery_callback(self, perc, charging):
        enough_for_laser = perc >= 5.0
        log.debug("enough_for_laser = %s (%.2f%%)" % (enough_for_laser, perc))

        self.button_toggle.setEnabled(enough_for_laser)
        self.button_toggle.setToolTip("Toggle laser (ctrl-L)" if enough_for_laser else "battery low")

    def slider_power_callback(self):
        self.slider_stop_usb = False
        position = self.slider_power.sliderPosition()
        self.spinbox_power.setValue(position)
        self.set_laser_power_callback()

    # set a flag to prevent sending a command to the spectrometer
    # This prevents flooding the spec with laser values while the slider is moving
    # When it releases, the flag will be cleared and then it will send one, final, laser value
    def slider_power_press_callback(self):
        self.slider_stop_usb = True
