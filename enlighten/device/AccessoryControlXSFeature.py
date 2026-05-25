import logging

from enlighten.ui.ScrollStealFilter import ScrollStealFilter
from enlighten.EnlightenFeature import EnlightenFeature

log = logging.getLogger(__name__)

class AccessoryControlXSFeature(EnlightenFeature):
    """
    Support for OEM Accessory Connector on XS V2 spectrometers.

     XS V2 Accessory Connector
     ______________________________
    |                              |
    | [x] GPIO Enable              |
    | [x] 5V Enable                |
    |                              |
    | .-[ GPIO1 ]----------------. |
    | | Mode:      [_FUNCTION_v] | |
    | | Direction: [_INPUT____v] | |
    | | Function:  [_DISABLED_v] | | (..., EXT_TRIGGER_RISING_EDGE, LASER_OVERRIDE)
    | | Value:     1 (HIGH)      | |
    | |__________________________| |
    |                              |
    | .-[ GPIO2 ]----------------. |
    | | Mode:      [_MANUAL___v] | |
    | | Direction: [_OUTPUT___v] | |
    | | Function:  [_DISABLED_v] | | (..., CONT_STROBE, DATA_READY, LASER_MIRROR, LASER_ERROR)
    | | Value:     0 (LOW)       | |
    | |__________________________| |
    |                              |
    | .-[ Cont Strobe ]----------. |
    | | Period:    [v 1000µs  v] | |
    | | Width:     [v  500µs  v] | |
    | | Delay:     [v   0µs   ^] | |
    | | Count:     [v    1    ^] | |
    | |__________________________| |
    |______________________________|
    """
    def __init__(self, ctl):
        super().__init__(ctl)

        cfu = ctl.form.ui

        self.frame_widget           = cfu.frame_xs_acc
        self.lb_gpio1               = cfu.label_xs_acc_gpio1
        self.lb_gpio2               = cfu.label_xs_acc_gpio2
        self.lb_cont_strobe         = cfu.label_xs_acc_cont_strobe
        self.frame_cont_strobe      = cfu.frame_xs_acc_cont_strobe
        self.frame_gpio1            = cfu.frame_xs_acc_gpio1
        self.frame_gpio2            = cfu.frame_xs_acc_gpio2

        self.cb_gpio_enable         = cfu.checkBox_xs_acc_gpio_enable
        self.cb_acc_5v_enable       = cfu.checkBox_xs_acc_5V_enable
        self.combo_gpio1_mode       = cfu.comboBox_xs_acc_gpio1_mode
        self.combo_gpio1_dir        = cfu.comboBox_xs_acc_gpio1_dir
        self.combo_gpio1_func       = cfu.comboBox_xs_acc_gpio1_function
        self.combo_gpio1_value      = cfu.comboBox_xs_acc_gpio1_value
        self.combo_gpio2_mode       = cfu.comboBox_xs_acc_gpio2_mode
        self.combo_gpio2_dir        = cfu.comboBox_xs_acc_gpio2_dir
        self.combo_gpio2_func       = cfu.comboBox_xs_acc_gpio2_function
        self.combo_gpio2_value      = cfu.comboBox_xs_acc_gpio2_value
        self.sb_strobe_period_us    = cfu.spinBox_xs_acc_cont_strobe_period_us
        self.sb_strobe_width_us     = cfu.spinBox_xs_acc_cont_strobe_width_us
        self.sb_strobe_delay_us     = cfu.spinBox_xs_acc_cont_strobe_delay_us
        self.sb_strobe_count        = cfu.spinBox_xs_acc_cont_strobe_count


        self.visible = False
        self.gpio_enabled = False
        self.acc_5v_enabled = False
        self.cont_strobe_enabled = False

        self.cb_gpio_enable.stateChanged.connect(self.update_settings)
        self.cb_acc_5v_enable.stateChanged.connect(self.update_settings)
        for widget in [ self.combo_gpio1_mode, self.combo_gpio1_dir, self.combo_gpio1_func, self.combo_gpio1_value,
                        self.combo_gpio2_mode, self.combo_gpio2_dir, self.combo_gpio2_func, self.combo_gpio2_value ]:
            widget.currentIndexChanged.connect(self.update_settings)
            widget.installEventFilter(ScrollStealFilter(widget))

        for widget in [ self.sb_strobe_period_us, self.sb_strobe_width_us, self.sb_strobe_delay_us, self.sb_strobe_count ]:
            widget.valueChanged.connect(self.update_settings)
            widget.installEventFilter(ScrollStealFilter(widget))

        self.update_visibility()

    def update_settings(self):
        self.gpio_enabled = self.cb_gpio_enable.isChecked()
        self.acc_5v_enabled = self.cb_acc_5v_enable.isChecked()
        self.cont_strobe_enabled = self.gpio_enabled and self.combo_gpio2_func.currentText() == "Cont Strobe"

        self.update_visibility()

    def disconnect(self):
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return
        
        spec.change_device_setting("acc_5v_enable", False)
        spec.change_device_setting("acc_gpio_enable", False)

    def update_visibility(self):
        spec = self.ctl.multispec.current_spectrometer()
        self.visible = spec is not None and (spec.settings.is_xs() and spec.settings.eeprom.is_oem)
        self.visible = True
        self.frame_widget.setVisible(self.visible)

        for w in [ self.lb_gpio1, self.frame_gpio1,
                   self.lb_gpio2, self.frame_gpio2 ]:
            w.setVisible(self.gpio_enabled)

        for w in [ self.lb_cont_strobe, self.frame_cont_strobe ]:
            w.setVisible(self.cont_strobe_enabled)
