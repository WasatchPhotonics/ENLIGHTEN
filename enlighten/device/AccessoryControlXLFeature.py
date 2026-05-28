import logging

from enlighten.ui.ScrollStealFilter import ScrollStealFilter
from enlighten.EnlightenFeature import EnlightenFeature

log = logging.getLogger(__name__)

class AccessoryControlXLFeature(EnlightenFeature):
    """
    Support for accessories on Andor / XL spectrometers.
    """
    def __init__(self, ctl):
        super().__init__(ctl)

        cfu = ctl.form.ui

        self.cb_fan                     = cfu.checkBox_acc_xl_fan
        self.cb_shutter_open            = cfu.checkBox_acc_xl_shutter
        self.frame_widget               = cfu.frame_acc_xl

        self.visible = False

        # bindings
        self.cb_fan                     .stateChanged   .connect(self.fan_callback)
        self.cb_shutter_open            .stateChanged   .connect(self.shutter_open_callback)

        # disable scroll stealing
        for widget in [ ]:
            widget.installEventFilter(ScrollStealFilter(widget))

        self.cb_shutter_open.setToolTip("Shutter is OPEN when this checkbox is checked (measuring sample), and shutter is CLOSED when this checkbox is unchecked (taking dark)")

        self.update_visibility()

    def init_hotplug(self):
        self.update_visibility()
        if not self.visible:
            return

        if spec.settings.eeprom.has_cooling:
            self.cb_fan.setChecked(True)
        if spec.settings.state.shutter_open:
            self.cb_shutter_open.setChecked(True)

    def disconnect(self):
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return
        
        spec.change_device_setting("fan_enable", False)

    def update_visibility(self):
        spec = self.ctl.multispec.current_spectrometer()
        self.visible = spec is not None and spec.settings.is_andor()

        self.frame_widget.setVisible(self.visible)

    def fan_callback(self):
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return

        spec.settings.state.fan_enabled = self.cb_fan.isChecked()
        spec.change_device_setting("fan_enable", spec.settings.state.fan_enabled)

    def shutter_open_callback(self):
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return

        spec.settings.state.shutter_open = self.cb_shutter_open.isChecked()
        spec.change_device_setting("shutter_open", spec.settings.state.shutter_open)
