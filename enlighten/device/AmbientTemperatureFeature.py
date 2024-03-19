import logging
import datetime
import pyqtgraph

log = logging.getLogger(__name__)

class AmbientTemperatureFeature:

    def __init__(self, ctl):
        self.ctl = ctl
        cfu = ctl.form.ui

        self.lb_chart_degC    = cfu.label_factory_ambient_temperature
        self.lb_hardware_degC = cfu.label_ambient_temperature
        self.bt_clear         = cfu.pushButton_clear_ambient_temperature_data
        self.bt_copy          = cfu.pushButton_copy_ambient_temperature_data
                              
        self.curve            = None
        self.name             = "Ambient_Temperature"
        self.output_to_file   = False
        self.observers        = set()

        self.populate_placeholder()

        self.ctl.multispec.register_strip_feature(self)
        self.ctl.hardware_file_manager.register_feature(self)

        self.bt_clear    .clicked             .connect(self.clear_data)
        self.bt_copy     .clicked             .connect(self.copy_data)

    def register_observer(self, callback):
        self.observers.add(callback)

    def notify(self, spec, s):
        """ if selected spectrometer, displays on Factory and sends to observers """
        log.debug(f"notify: {s}")
        if spec != self.ctl.multispec.current_spectrometer():
            return

        self.lb_chart_degC.setText(s)
        self.lb_hardware_degC.setText(s)
        for callback in self.observers:
            callback(s)

    def process_reading(self, spec, reading):
        log.debug("process_reading: start")
        if spec is None:
            return self.notify(spec, "disconnected")

        if not spec.settings.is_xs():
            return self.notify(spec, "unsupported")
            
        app_state = spec.app_state
        degC = reading.ambient_temperature_degC
        if degC is None:
            return self.notify(spec, "none")

        # @todo: move from Multispec class to SpectrometerApplicationState
        active_curve = self.ctl.multispec.get_hardware_feature_curve(self.name, spec.device_id)
        if active_curve == None:
            log.debug("process_reading: no curve")
            return 

        rds = app_state.ambient_temperature_data
        rds.add(degC)
        current_time = datetime.datetime.now()
        if self.output_to_file:
            self.ctl.hardware_file_manager.write_line(self.name, f"{self.name},{spec.label},{current_time},{degC}")

        x_time = [(current_time-x).total_seconds() for x,y in rds.data]
        y = rds.get_values()

        try:
            self.ctl.graph.set_data(curve=active_curve, y=y, x=x_time)
        except:
            log.error("error plotting ambient temperature", exc_info=1)

        self.notify(spec, f"{degC:-.2f} °C")

    def populate_placeholder(self):
        cfu = self.ctl.form.ui
        self.graph = pyqtgraph.PlotWidget(name="Ambient temperature")
        self.graph.invertX(True)
        cfu.stackedWidget_ambient_temperature.addWidget(self.graph)
        cfu.stackedWidget_ambient_temperature.setCurrentIndex(1)

    def add_spec_curve(self, spec):
        if self.ctl.multispec.check_hardware_curve_present(self.name, spec.device_id):
            return
        curve = self.graph.plot([], pen=spec.curve.opts['pen'],name=str(spec.label))
        self.ctl.multispec.register_hardware_feature_curve(self.name, spec.device_id, curve) 
    
    def remove_spec_curve(self, spec):
        log.debug("removing curve from hardware graph")
        cur_curve = self.ctl.multispec.get_hardware_feature_curve(self.name, spec.device_id)
        if cur_curve is None:
            return

        # remove current curve from graph
        for curve in self.graph.listDataItems():
            if curve.name() == cur_curve.name():
                self.graph.removeItem(curve)
        self.ctl.multispec.remove_hardware_curve(self.name, spec.device_id)
        if self.ctl.multispec.get_spectrometers() == []:
            self.lb_chart_degC.setText("disconnected")
            self.lb_hardware_degC.setText("disconnected")

    def clear_data(self):
        for spec in self.ctl.multispec.get_spectrometers():
            if spec is None:
                continue
            app_state = spec.app_state

            rds = app_state.ambient_temperature_data
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
            rds = app_state.ambient_temperature_data
            copy_str.append(rds.get_csv_data("Ambient Temperature",spec.label))
        self.ctl.clipboard.raw_set_text('\n'.join(copy_str))
