import logging
import datetime
import pyqtgraph

from enlighten.ScrollStealFilter import ScrollStealFilter

from enlighten import common

if common.use_pyside2():
    from PySide2 import QtGui, QtCore 
else:
    from PySide6 import QtGui, QtCore 

log = logging.getLogger(__name__)

class DetectorTemperatureFeature:
    """
    Encapsulate the monitoring of detector temperature.
    """

    def __init__(self,
            graph,
            multispec,
            status_indicators,
            cb_enabled,
            lb_degC,
            lb_raw,
            slider,
            spinbox,
            button_up,
            button_dn,
            clear_btn,
            sfu,
            gui,
            clipboard,
            hardware_file_manager):

        self.curve                 = None
        self.name                  = "Detector_TEC_Temperature"
        self.graph                 = graph
        self.multispec             = multispec
        self.status_indicators     = status_indicators
        self.sfu                   = sfu
        self.gui                   = gui
        self.clipboard             = clipboard
        self.output_to_file        = False
        self.hardware_file_manager = hardware_file_manager

        self.cb_enabled         = cb_enabled
        self.lb_degC            = lb_degC
        self.lb_raw             = lb_raw
        self.slider             = slider
        self.spinbox            = spinbox
        self.button_up          = button_up
        self.button_dn          = button_dn
        self.clear_btn          = clear_btn

        self.cb_enabled             	    	.stateChanged       .connect(self.enabled_callback)
        self.spinbox            	        	.valueChanged       .connect(self.slider.setValue)
        self.spinbox                                                .installEventFilter(ScrollStealFilter(self.spinbox))
        self.spinbox                		    .valueChanged       .connect(self.spinbox_callback)
        self.slider                 			.valueChanged       .connect(self.spinbox.setValue)
        self.button_up              			.clicked            .connect(self.up_callback)
        self.button_dn                          .clicked            .connect(self.dn_callback)
        self.clear_btn                          .clicked            .connect(self.clear_data)
        self.sfu.pushButton_detector_tec_copy   .clicked            .connect(self.copy_data)

        self.observers = []
        self.populate_placeholder()
        self.multispec.register_strip_feature(self)
        self.hardware_file_manager.register_feature(self)

    # ##########################################################################
    # public methods
    # ##########################################################################

    def register_observer(self, callback):
        if callback not in self.observers:
            self.observers.append(callback)

    def unregister_observer(self, callback):
        self.observers.pop(callback, None)

    def enable_widgets(self, flag):
        for w in [ self.cb_enabled,
                   self.spinbox,
                   self.slider,
                   self.button_up,
                   self.button_dn,
                   self.clear_btn,
                   self.sfu.pushButton_detector_tec_copy ]:
            w.setEnabled(flag)

    def init_hotplug(self):
        spec = self.multispec.current_spectrometer()
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
        """ The user just selected a different spectrometer (but it isn't a hotplug). """
        spec = self.multispec.current_spectrometer()
        if spec is None:
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
        spec = self.multispec.current_spectrometer()
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

    def process_reading(self, spec, reading):
        current_spec = self.multispec.current_spectrometer()
        if spec is None:
            return

        if not spec.settings.eeprom.has_cooling:
            self.lb_degC.setText("Ambient")
            self.lb_raw.setText("Ambient")
            return

        app_state = spec.app_state
        if app_state is None or reading is None:
            log.error(f"Either app_state: {app_state} or reading: {reading} was None, returning")
            return

        # add the measurement to the moving window
        app_state.detector_temperatures_degC.add(reading.detector_temperature_degC)
        app_state.detector_temperature_degC_latest = reading.detector_temperature_degC

        log.debug("detector_temperature_degC = %s", reading.detector_temperature_degC)

        # update the primary label
        if spec == current_spec:
            self.lb_degC.setText("%-5.2f °C" % reading.detector_temperature_degC)
        curve = self.multispec.get_hardware_feature_curve(self.name, spec.device_id)
        if curve is None:
            log.error(f"curve was none for spec that had cooling, returning")
            return

        current_time = datetime.datetime.now()
        app_state.detector_temperatures_degC_averaged_display.add(reading.detector_temperature_degC)
        if self.output_to_file:
            self.hardware_file_manager.write_line(self.name,f"{self.name},{spec.label},{current_time},{reading.detector_temperature_degC}")
        x_time = [(current_time-x).total_seconds() for x,y in app_state.detector_temperatures_degC_averaged_display.data]
        self.graph.set_data(
            curve = curve,
            y     = app_state.detector_temperatures_degC_averaged_display.get_values(),
            x     = x_time)

        if spec == current_spec:
            self.lb_raw.setText("0x%03x" % int(reading.detector_temperature_degC))

        # notify observers
        for callback in self.observers:
            callback(reading.detector_temperature_degC)

    def apply_setpoint(self, value=None):
        """ Send GUI value downstream (and turns on if it was off). """
        if value is not None:
            log.debug(f"apply_setpoint: updating GUI to {value}, trusting events to pass downstream")
            self.spinbox.setValue(value)
            return

        # shouldn't matter if we take from spinbox or slider
        value = self.spinbox.value() 
        log.debug(f"apply_setpoint: triggered by change to {value}")

        self.multispec.set_state("tec_setpoint_degC", value)
        self.multispec.change_device_setting("detector_tec_setpoint_degC", value)

        if self.cb_enabled.isChecked():
            self.status_indicators.update_visibility()
        else:
            log.debug("auto-enabling TEC")
            self.cb_enabled.setChecked(True)

    # ##########################################################################
    # private methods
    # ##########################################################################

    def populate_placeholder(self):
        self.sfu.tec_temperature_graph = pyqtgraph.PlotWidget(name="TEC Temperature")
        self.sfu.tec_temperature_graph.setLabel(axis="bottom", text="seconds ago")
        self.sfu.tec_temperature_graph.setLabel(axis="left", text="Celsius")
        self.sfu.tec_temperature_graph.invertX(True)
        self.sfu.stackedWidget_detector_temperature.addWidget(self.sfu.tec_temperature_graph)
        self.sfu.stackedWidget_detector_temperature.setCurrentIndex(1)

    def add_spec_curve(self, spec):
        if self.multispec.check_hardware_curve_present(self.name, spec.device_id):
            log.info(f"Called add_spec_curve for spec {spec.label} with curve already present, returning")
            return
        curve = self.sfu.tec_temperature_graph.plot([], pen=spec.curve.opts['pen'],name=str(spec.label))
        self.multispec.register_hardware_feature_curve(self.name, spec.device_id, curve)

    def remove_spec_curve(self, spec):
        cur_curve = self.multispec.get_hardware_feature_curve(self.name, spec.device_id)
        if cur_curve == None:
            log.info(f"attempted to delete curve for spec {spec.label} that doesn't exist. Returning")
            return
        # remove current curve from graph
        for curve in self.sfu.tec_temperature_graph.listDataItems():
            if curve.name() == cur_curve.name():
                self.sfu.tec_temperature_graph.removeItem(curve)
        # remove current curve from multispec record
        self.multispec.remove_hardware_curve(self.name, spec.device_id)
    
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

        self.multispec.set_state("tec_enabled", enabled)
        self.multispec.change_device_setting("detector_tec_enable", enabled)

        for widget in [
                self.spinbox,
                self.slider,
                self.button_up,
                self.button_dn]:
            widget.setEnabled(enabled)

        self.status_indicators.update_visibility()

    def clear_data(self):
        for spec in self.multispec.get_spectrometers():
            if spec is None:
                continue

            app_state = spec.app_state
            if app_state is None:
                return

            app_state.detector_temperatures_degC_averaged.clear()
            app_state.detector_temperatures_degC_averaged_display.clear()

    def update_curve_color(self, spec):
        curve = self.multispec.get_hardware_feature_curve(self.name, spec.device_id)
        if curve == None:
            return
        curve.opts["pen"] = spec.color

    def copy_data(self):
        copy_str = []
        for spec in self.multispec.get_spectrometers():
            if not self.multispec.check_hardware_curve_present(self.name, spec.device_id):
                continue

            app_state = spec.app_state
            if app_state is None:
                continue
            rds = app_state.detector_temperatures_degC_averaged_display
            copy_str.append(rds.get_csv_data("Detector Tec Temperature",spec.label))
        self.clipboard.raw_set_text('\n'.join(copy_str))
