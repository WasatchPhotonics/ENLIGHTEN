import time
import datetime
import logging

from . import util
from . import common
from .ScrollStealFilter import ScrollStealFilter
from .MouseWheelFilter import MouseWheelFilter

log = logging.getLogger(__name__)

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
                 spinbox_excitation,    # doubleSpinBox on Laser Control widget, not EEPROMEditor
                 spinbox_power,         # doubleSpinBox
                 slider_power,
                 guide):         # verticalSlider

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
        self.spinbox_excitation = spinbox_excitation
        self.spinbox_power      = spinbox_power
        self.slider_power       = slider_power
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

        state.laser_power_perc = 100
        state.laser_power_mW = settings.eeprom.max_laser_power_mW
        state.use_mW = settings.eeprom.has_laser_power_calibration() and settings.is_mml()
        log.debug(f"For spec has cali {settings.eeprom.has_laser_power_calibration()} and is mml {settings.is_mml()} thus use milli is {state.use_mW}")

        self.set_laser_enable(False)
        
        spec.change_device_setting("laser_power_high_resolution", True)

        self.update_visibility()

    ##
    # Called by initialize_new_device when the user selected one of several 
    # connected spectrometers.
    def update_visibility(self):
        spec = self.multispec.current_spectrometer()
        if spec is None:
            return

        settings = spec.settings

        has_calibration = settings.eeprom.has_laser_power_calibration()
        log.debug("update_visibility: laser power calibration %s", has_calibration)

        if not has_calibration:
            self.configure_laser_power_controls_percent()
        else:
            if settings.state.use_mW:
                self.configure_laser_power_controls_mW()
            else:
                self.configure_laser_power_controls_percent()

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

        if self.multispec.is_current_spectrometer(spec):
            self.refresh_laser_button()

        self.status_indicators.update_visibility()

    ## So Controller etc don't call directly into internal callbacks
    def toggle_laser(self):
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
            self.button_toggle.setText("Laser Off")
        else:
            self.button_toggle.setText("Laser On")
        self.gui.colorize_button(self.button_toggle, enabled)

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

    ##
    # This is a little convoluted because "laser enabled" was implemented
    # as a button rather than a checkbox.
    def toggle_callback(self):
        spec = self.multispec.current_spectrometer()
        if spec is None:
            return

        # invert the previous state
        flag = not spec.settings.state.laser_enabled
        self.set_laser_enable(flag)

        token = "laser_init"

        if flag:
            self.marquee.info("laser is initializing and stabilizing for use", token=token, period_sec=10)
        else:
            self.marquee.clear(token=token)

    ## 
    # This gets called when the "front" (Scope) laser excitation value is changed.
    # Note this will happen when excitation is changed in EEPROMEditor, as that object
    # calls Controller.update_wavecal which syncs the two excitation spinners.
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
