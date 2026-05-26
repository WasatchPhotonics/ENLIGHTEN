import logging
import datetime

from enlighten.ui.ScrollStealFilter import ScrollStealFilter
from enlighten.EnlightenFeature import EnlightenFeature

from enlighten import common

if common.use_pyside2():
    from PySide2 import QtCore 
else:
    from PySide6 import QtCore 

log = logging.getLogger(__name__)

class DetectorTemperatureFeature(EnlightenFeature):
    """ Encapsulate the monitoring and control of detector temperature. """

    def __init__(self, ctl):
        super().__init__(ctl)
        
        cfu = ctl.form.ui

        self.cb_enabled     = cfu.checkBox_detector_tec_enabled
        self.slider         = cfu.verticalSlider_detector_setpoint_degC
        self.spinbox        = cfu.spinBox_detector_setpoint_degC
        self.button_up      = cfu.temperatureWidget_pushButton_detector_setpoint_up
        self.button_dn      = cfu.temperatureWidget_pushButton_detector_setpoint_dn

        self.cb_enabled     .stateChanged       .connect(self.enabled_callback)
        self.spinbox        .valueChanged       .connect(self.slider.setValue)
        self.spinbox        .installEventFilter(ScrollStealFilter(self.spinbox))
        self.spinbox        .valueChanged       .connect(self.spinbox_callback)
        self.slider         .valueChanged       .connect(self.spinbox.setValue)
        self.button_up      .clicked            .connect(self.up_callback)
        self.button_dn      .clicked            .connect(self.dn_callback)

        self.detector_tec_control_widgets = [
            cfu.detectorControlWidget_label_detectorTemperature,
            self.cb_enabled,
            self.slider,
            self.spinbox,
            self.button_up,
            self.button_dn
        ]

        self.strip_chart = self.ctl.strip_charts.create_chart(
            name="Detector Temperature", 
            y_unit="Celsius (°C)", 
            format="{value:.2f}°C", 
            warn_hi=26,
            process_reading_callback=self.process_reading_callback)

        self.ctl.page_nav.register_observer(self.page_nav_mode_callback, "mode")

        self.page_nav_mode_callback()

    def page_nav_mode_callback(self):
        spec = self.ctl.multispec.current_spectrometer()
        doing_expert = self.ctl.page_nav.doing_expert()
        for widget in self.detector_tec_control_widgets:
            widget.setVisible(doing_expert and spec is not None and spec.settings.eeprom.has_cooling)

    # ##########################################################################
    # public methods
    # ##########################################################################

    def enable_widgets(self, flag):
        for w in [ self.cb_enabled,
                   self.spinbox,
                   self.slider,
                   self.button_up,
                   self.button_dn ]:
            w.setEnabled(flag)

        self.strip_chart.set_visible(flag)

    def init_hotplug(self):
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return

        if not spec.settings.eeprom.has_cooling:
            self.enable_widgets(False)
            return

        self.enable_widgets(True)
        self.update_limits()

        value = self.get_default_temp(spec)
        self.spinbox.setValue(value)
        spec.settings.state.tec_setpoint_degC = value
        # If a spec was previously connected or a current spec has the tec enabled,
        # The checkbox will already be checked so it won't auto enable the tec
        # This unchecks it so that it will auto enable the tec
        self.cb_enabled.setChecked(False)

        self.cb_enabled.setCheckState(QtCore.Qt.CheckState.Checked)
        self.enabled_callback()
        self.apply_setpoint()

    def update_visibility(self):
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            self.enable_widgets(False)
            return

        if not spec.settings.eeprom.has_cooling:
            self.enable_widgets(False)
            return

        self.enable_widgets(True)
        self.update_limits()

        # restore whatever had been previously in place for this spectrometer
        self.spinbox.setValue(spec.settings.state.tec_setpoint_degC)
        self.cb_enabled.setChecked(spec.settings.state.tec_enabled)

    def update_limits(self):
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return

        # Change the limits of the tec setpoint control
        log.debug("update_limits: blocking signals")

        # This is a little kludgy, but essentially required by the fact that we
        # expose both spinbox and slider to control the same model value.
        self.slider.blockSignals(True)
        self.spinbox.blockSignals(True)

        log.debug(f"update_limits: setting min/max slider to {spec.settings.eeprom.min_temp_degC}/{spec.settings.eeprom.max_temp_degC}")
        self.slider.setMinimum (spec.settings.eeprom.min_temp_degC)
        self.slider.setMaximum (spec.settings.eeprom.max_temp_degC)

        log.debug(f"update_limits: setting min/max spinner {spec.settings.eeprom.min_temp_degC}/{spec.settings.eeprom.max_temp_degC}")
        self.spinbox.setMinimum(spec.settings.eeprom.min_temp_degC)
        self.spinbox.setMaximum(spec.settings.eeprom.max_temp_degC)

        log.debug("update_limits: restoring signals")
        self.slider.blockSignals(False)
        self.spinbox.blockSignals(False)

    def process_reading_callback(self, spec, reading):
        """ Called by StripCharts """
        current_spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return

        if not spec.settings.eeprom.has_cooling:
            return

        app_state = spec.app_state
        if app_state is None or reading is None:
            return

        log.debug(f"process_reading: reading {reading}")
        if reading.detector_temperature_degC is None:
            return

        self.strip_chart.add_value(spec, reading.detector_temperature_degC)

        self.notify_observers_with_value(reading.detector_temperature_degC)

    def apply_setpoint(self, value=None):
        """ Send GUI value downstream (and turns on if it was off). """
        if value is not None:
            log.debug(f"apply_setpoint: updating GUI to {value}, trusting events to pass downstream")
            self.spinbox.setValue(value)
            return

        # shouldn't matter if we take from spinbox or slider
        value = self.spinbox.value() 
        log.debug(f"apply_setpoint: triggered by change to {value}")

        self.ctl.multispec.set_state("tec_setpoint_degC", value)
        self.ctl.multispec.change_device_setting("detector_tec_setpoint_degC", value)

        if self.cb_enabled.isChecked():
            self.ctl.status_indicators.update_visibility()
        else:
            log.debug("auto-enabling TEC")
            self.cb_enabled.setChecked(True)

    # ##########################################################################
    # private methods
    # ##########################################################################

    def get_default_temp(self, spec):
        """
        If a startup temperature has been configured and is in range, use that;
        otherwise default to minimum.
        """
        lo          = spec.settings.eeprom.min_temp_degC
        hi          = spec.settings.eeprom.max_temp_degC
        startup     = spec.settings.eeprom.startup_temp_degC
        by_detector = spec.settings.default_detector_setpoint_degC()

        if by_detector is not None:
            log.debug(f"get_default_temp: using configured detector value {by_detector}")
            return by_detector
        elif lo <= startup and startup <= hi:
            log.debug(f"get_default_temp: using in-range startup value {startup}")
            return startup
        else:
            log.debug(f"get_default_temp: using minimum value {lo}")
            return lo

    # ##########################################################################
    # callbacks
    # ##########################################################################

    def up_callback(self):
        self.slider.setValue(self.slider.value() + 1)

    def dn_callback(self):
        self.slider.setValue(self.slider.value() - 1)

    ## The user changed the desired setpoint, so send it downstream
    def spinbox_callback(self):
        self.apply_setpoint()

    def enabled_callback(self):
        """
        Apply the current "enabled" checkbox state downstream and to GUI elements.
        
        Note that if the DetectorTemperatureFeature is disabled, it does not let 
        you change the setpoint via spinner, slider or buttons.  This is deliberate.
        You can only adjust the setpoint when the TEC is enabled.
        """
        enabled = self.cb_enabled.isChecked()

        self.ctl.multispec.set_state("tec_enabled", enabled)
        self.ctl.multispec.change_device_setting("detector_tec_enable", enabled)

        for widget in [
                self.spinbox,
                self.slider,
                self.button_up,
                self.button_dn]:
            widget.setEnabled(enabled)

        self.ctl.status_indicators.update_visibility()
