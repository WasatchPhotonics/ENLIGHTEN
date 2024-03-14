import logging
import datetime
import pyqtgraph

log = logging.getLogger(__name__)

class LaserTemperatureFeature:

    def __init__(self, ctl):
        self.ctl = ctl
        cfu = ctl.form.ui

        self.lb_degC        = cfu.label_hardware_capture_details_laser_temperature
        self.lb_widget      = cfu.label_laser_tec_mode
        self.combo_mode     = cfu.comboBox_laser_tec_mode
        self.bt_clear       = cfu.pushButton_clear_laser_temperature_data
        self.bt_copy        = cfu.pushButton_copy_laser_temperature_data

        self.curve          = None
        self.name           = "Laser_TEC_Temperature"
        self.output_to_file = False
        self.observers      = set()

        self.populate_placeholder()

        self.ctl.multispec.register_strip_feature(self)
        self.ctl.hardware_file_manager.register_feature(self)
        self.ctl.page_nav.register_observer("mode", self.update_visibility)

        self.bt_clear    .clicked             .connect(self.clear_data)
        self.bt_copy     .clicked             .connect(self.copy_data)
        self.combo_mode  .currentIndexChanged .connect(self.combo_callback)

        self.update_visibility()

    def update_visibility(self):
        spec = self.ctl.multispec.current_spectrometer()
        visible = spec is not None and spec.settings.eeprom.sig_laser_tec and self.ctl.page_nav.doing_expert()

        for widget in [ self.combo_mode, self.lb_widget ]:
            widget.setVisible(visible)

    def combo_callback(self):
        spec = self.ctl.multispec.current_spectrometer()
        if spec and spec.settings.is_xs() and spec.settings.eeprom.sig_laser_tec:
            index = self.combo_mode.currentIndex()
            text  = self.combo_mode.currentText()
            log.debug("combo_callback: index {index}, text {text}")
            self.ctl.multispec.change_device_setting("set_laser_tec_mode", index)

    def register_observer(self, callback):
        self.observers.add(callback)

    def process_reading(self, spec, reading):
        current_spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return

        if spec.settings.eeprom.format <= 12:
            self.lb_degC.setText("Ambient")
            return

        if not spec.settings.eeprom.sig_laser_tec:
            self.lb_degC.setText("Ambient")
            return

        app_state = spec.app_state
        degC = reading.laser_temperature_degC
        if degC is None:
            return

        active_curve = self.ctl.multispec.get_hardware_feature_curve(self.name, spec.device_id)
        if active_curve == None:
            return

        rds = app_state.laser_temperature_data
        rds.add(degC)
        current_time = datetime.datetime.now()
        if self.output_to_file:
            self.ctl.hardware_file_manager.write_line(self.name,f"{self.name},{spec.label},{current_time},{degC}")

        x_time = [(current_time-x).total_seconds() for x,y in rds.data]
        y = rds.get_values()

        try:
            self.ctl.graph.set_data(curve=active_curve, y=y, x=x_time)
        except:
            log.error("error plotting laser temperature", exc_info=1)

        if spec == current_spec:
            self.lb_degC.setText("%.2f °C" % degC)

            # only doing callback for the selected spectrometer
            for callback in self.observers:
                callback(degC)

    def populate_placeholder(self):
        cfu = self.ctl.form.ui
        cfu.laser_temperature_graph = pyqtgraph.PlotWidget(name="Laser temperature")
        cfu.laser_temperature_graph.invertX(True)
        cfu.stackedWidget_laser_temperature.addWidget(cfu.laser_temperature_graph)
        cfu.stackedWidget_laser_temperature.setCurrentIndex(1)

    def add_spec_curve(self, spec):
        cfu = self.ctl.form.ui
        if self.ctl.multispec.check_hardware_curve_present(self.name, spec.device_id):
            return
        curve = cfu.laser_temperature_graph.plot([], pen=spec.curve.opts['pen'],name=str(spec.label))
        self.ctl.multispec.register_hardware_feature_curve(self.name, spec.device_id, curve) 
    
    def remove_spec_curve(self, spec):
        cfu = self.ctl.form.ui
        cur_curve = self.ctl.multispec.get_hardware_feature_curve(self.name, spec.device_id)
        if cur_curve is None:
            return
        # remove current curve from graph
        for curve in cfu.laser_temperature_graph.listDataItems():
            if curve.name() == cur_curve.name():
                cfu.laser_temperature_graph.removeItem(curve)
        self.ctl.multispec.remove_hardware_curve(self.name, spec.device_id)
        if self.ctl.multispec.get_spectrometers() == []:
            self.lb_degC.setText("0.0 °C")

    def clear_data(self):
        for spec in self.ctl.multispec.get_spectrometers():
            if spec is None:
                continue
            app_state = spec.app_state

            rds = app_state.laser_temperature_data
            rds.clear()

    def update_curve_color(self, spec):
        curve = self.ctl.multispec.get_hardware_feature_curve(self.name, spec.device_id)
        if curve == None:
            return
        curve.opts["pen"] = spec.color

    def copy_data(self):
        spec = self.ctl.multispec.current_spectrometer()
        copy_str = []
        for spec in self.ctl.multispec.get_spectrometers():
            if not self.ctl.multispec.check_hardware_curve_present(self.name, spec.device_id):
                continue

            app_state = spec.app_state
            if app_state is None:
                continue
            rds = app_state.laser_temperature_data
            copy_str.append(rds.get_csv_data("Laser TEC Temperature",spec.label))
        self.ctl.clipboard.raw_set_text('\n'.join(copy_str))


