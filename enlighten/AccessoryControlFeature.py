import logging

from .ScrollStealFilter import ScrollStealFilter

log = logging.getLogger(__name__)

class AccessoryControlFeature(object):
    """
    Support for the Gen 1.5 OEM External Accessory Connector.
    
    @par Nomenclature
    
    There are some differences in nomenclature here, and I'm not sure this is the 
    final or perfect version, but the differences are there for a reason.
    
    In ENLIGHTEN's GUI, "continuous strobe" is very different from "laser".  The
    controls are on different parts of the GUI, they're labeled differently, they
    are colored differently, and basically exposed as different and unrelated
    features.
    
    That said, inside the electronics and firmware, they're currently the same
    feature, they're just hooked to different hardware pins.  Both use the 
    "mod_*_us" attributes, and both are ultimately dis/enabled by the laser_enable
    USB opcode (there is no such thing as "strobe_enable").  (Not quite true:
    there is a Wasatch.PY "setting" called "strobe_enable," which MERELY sets
    the laser_enable opcode without other historical "laser management" behavior.)
    
    The bridging between nomenclatures is deliberately encapsulated here, within
    this Feature class.
    """
    def __init__(self,
            cb_display,
            cb_enable,
            cb_fan,
            cb_lamp,
            cb_shutter,
            frame_cont_strobe,
            frame_widget,
            multispec,
            sb_freq_hz,
            sb_width_us):

        self.cb_display                 = cb_display
        self.cb_enable                  = cb_enable
        self.cb_fan                     = cb_fan
        self.cb_lamp                    = cb_lamp
        self.cb_shutter                 = cb_shutter
        self.frame_cont_strobe          = frame_cont_strobe
        self.frame_widget               = frame_widget
        self.multispec                  = multispec
        self.sb_freq_hz                 = sb_freq_hz
        self.sb_width_us                = sb_width_us

        self.visible = False
        self.cont_strobe_visible = False

        # bindings
        self.cb_fan                     .stateChanged   .connect(self.fan_callback)
        self.cb_lamp                    .stateChanged   .connect(self.lamp_callback)
        self.cb_shutter                 .stateChanged   .connect(self.shutter_callback)
        self.cb_display                 .stateChanged   .connect(self.display_callback)
        self.cb_enable                  .stateChanged   .connect(self.enable_callback)
        self.sb_freq_hz                 .valueChanged   .connect(self.freq_callback)
        self.sb_width_us                .valueChanged   .connect(self.width_callback)

        # disable scroll stealing
        for key, item in self.__dict__.items():
            if key.startswith("cb_") or key.startswith("sb_"):
                item.installEventFilter(ScrollStealFilter(item))

        self.update_visibility()

    def init_hotplug(self):
        if not self.update_visibility():
            return

        spec = self.multispec.current_spectrometer()
        if spec is None:
            return

        if spec.settings.eeprom.has_cooling:
            self.cb_fan.setChecked(True)
        if spec.settings.state.shutter_enabled:
            self.cb_shutter.setChecked(True)

        self.freq_callback()
        self.width_callback()

    def disconnect(self):
        spec = self.multispec.current_spectrometer()
        if spec is None:
            return
        
        for setting in [ "fan_enable",
                         "strobe_enable",
                         "mod_enable",
                         "lamp_enable",
                         "shutter_enable" ]:
            spec.change_device_setting(setting, False)

    def update_visibility(self):
        spec = self.multispec.current_spectrometer()
        if spec is None:
            self.visible = False
        else:
            self.visible = spec.settings.is_gen15() or spec.settings.is_andor()

        self.frame_widget.setVisible(self.visible)
        self.frame_cont_strobe.setVisible(self.cont_strobe_visible)

        # usability decision...if user closes the Continuous Strobe feature, they
        # probably expect the strobe to turn off
        if not self.cont_strobe_visible:
            self.cb_enable      .setChecked (False)
        else:
            self.cb_enable      .setChecked (spec.settings.state.laser_enabled)
            self.sb_freq_hz     .setValue   (self.us_to_hz(spec.settings.state.mod_period_us))
            self.sb_width_us    .setValue   (spec.settings.state.mod_width_us)

        return self.visible

    def hz_to_us(self, hz) -> int:
        return int(round(1e6 / hz))

    def us_to_hz(self, us) -> int:
        return int(round(1e6 / us))

    def fan_callback(self):
        spec = self.multispec.current_spectrometer()
        if spec is None:
            return

        spec.settings.state.fan_enabled = self.cb_fan.isChecked()
        spec.change_device_setting("fan_enable", spec.settings.state.fan_enabled)

    def lamp_callback(self):
        spec = self.multispec.current_spectrometer()
        if spec is None:
            return

        spec.settings.state.lamp_enabled = self.cb_lamp.isChecked()
        spec.change_device_setting("lamp_enable", spec.settings.state.lamp_enabled)

    def shutter_callback(self):
        spec = self.multispec.current_spectrometer()
        if spec is None:
            return

        spec.settings.state.shutter_enabled = self.cb_shutter.isChecked()
        spec.change_device_setting("shutter_enable", spec.settings.state.shutter_enabled)

    def display_callback(self):
        self.cont_strobe_visible = self.cb_display.isChecked()
        self.update_visibility()

    def enable_callback(self):
        spec = self.multispec.current_spectrometer()
        if spec is None:
            return

        enabled = self.cb_enable.isChecked()
        spec.settings.state.laser_enabled = enabled
        spec.settings.state.mod_enabled   = enabled
        spec.change_device_setting("strobe_enable", enabled)
        spec.change_device_setting("mod_enable",    enabled)

    def freq_callback(self):
        spec = self.multispec.current_spectrometer()
        if spec is None:
            return

        spec.settings.state.mod_period_us = self.hz_to_us(self.sb_freq_hz.value())
        spec.change_device_setting("mod_period_us", spec.settings.state.mod_period_us)

    def width_callback(self):
        spec = self.multispec.current_spectrometer()
        if spec is None:
            return

        spec.settings.state.mod_width_us = int(self.sb_width_us.value())
        spec.change_device_setting("mod_width_us", spec.settings.state.mod_width_us)
