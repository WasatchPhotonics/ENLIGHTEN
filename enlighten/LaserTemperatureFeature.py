import logging
import datetime
import pyqtgraph

log = logging.getLogger(__name__)

class LaserTemperatureFeature:

    def __init__(self,
             sfu,
             graph,
             multispec,
             lb_degC,
             clear_btn,
             make_pen,
             clipboard,
             hardware_file_manager):

        self.sfu                   = sfu
        self.curve                 = None
        self.name                  = "Laser_TEC_Temperature"
        self.graph                 = graph
        self.multispec             = multispec
        self.lb_degC               = lb_degC
        self.clear_btn             = clear_btn
        self.make_pen              = make_pen
        self.clipboard             = clipboard
        self.output_to_file        = False
        self.hardware_file_manager = hardware_file_manager

        self.populate_placeholder()
        self.multispec.register_strip_feature(self)
        self.hardware_file_manager.register_feature(self)

        self.clear_btn                   .clicked            .connect(self.clear_data)
        self.sfu.pushButton_laser_copy   .clicked            .connect(self.copy_data)

    def process_reading(self, spec, reading):
        current_spec = self.multispec.current_spectrometer()
        if spec is None:
            return

        if spec.settings.eeprom.format <= 12:
            self.lb_degC.setText("Ambient")
            return

        # This should have a value but if for some reason an instance is built that doesnt
        # This will handle the error
        if hasattr(spec.settings.eeprom,"has_laser_tec"):
            if not spec.settings.eeprom.has_laser_tec:
                self.lb_degC.setText("Ambient")
                return

        app_state = spec.app_state
        degC = reading.laser_temperature_degC
        if degC is None:
            return

        active_curve = self.multispec.get_hardware_feature_curve(self.name, spec.device_id)
        if active_curve == None:
            return

        rds = app_state.laser_temperature_data
        rds.add(degC)
        current_time = datetime.datetime.now()
        if self.output_to_file:
            self.hardware_file_manager.write_line(self.name,f"{self.name},{spec.label},{current_time},{degC}")

        x_time = [(current_time-x).total_seconds() for x,y in rds.data]
        y = rds.get_values()

        try:
            self.graph.set_data(curve=active_curve, y=y, x=x_time)
        except:
            log.error("error plotting laser temperature", exc_info=1)

        if spec == current_spec:
            self.lb_degC.setText("%.2f °C" % degC)

    def populate_placeholder(self):
        self.sfu.laser_temperature_graph = pyqtgraph.PlotWidget(name="Laser temperature")
        self.sfu.laser_temperature_graph.invertX(True)
        self.sfu.stackedWidget_laser_temperature.addWidget(self.sfu.laser_temperature_graph)
        self.sfu.stackedWidget_laser_temperature.setCurrentIndex(1)

    def add_spec_curve(self, spec):
        if self.multispec.check_hardware_curve_present(self.name, spec.device_id):
            return
        curve = self.sfu.laser_temperature_graph.plot([], pen=spec.curve.opts['pen'],name=str(spec.label))
        self.multispec.register_hardware_feature_curve(self.name, spec.device_id, curve) 
    
    def remove_spec_curve(self, spec):
        cur_curve = self.multispec.get_hardware_feature_curve(self.name, spec.device_id)
        if cur_curve is None:
            return
        # remove current curve from graph
        for curve in self.sfu.laser_temperature_graph.listDataItems():
            if curve.name() == cur_curve.name():
                self.sfu.laser_temperature_graph.removeItem(curve)
        self.multispec.remove_hardware_curve(self.name, spec.device_id)
        if self.multispec.get_spectrometers() == []:
            self.lb_degC.setText("0.0 °C")

    def clear_data(self):
        for spec in self.multispec.get_spectrometers():
            if spec is None:
                continue
            app_state = spec.app_state

            rds = app_state.laser_temperature_data
            rds.clear()

    def update_curve_color(self, spec):
        curve = self.multispec.get_hardware_feature_curve(self.name, spec.device_id)
        if curve == None:
            return
        curve.opts["pen"] = spec.assigned_color

    def copy_data(self):
        spec = self.multispec.current_spectrometer()
        copy_str = []
        for spec in self.multispec.get_spectrometers():
            if not self.multispec.check_hardware_curve_present(self.name, spec.device_id):
                continue

            app_state = spec.app_state
            if app_state is None:
                continue
            rds = app_state.laser_temperature_data
            copy_str.append(rds.get_csv_data("Laser TEC Temperature",spec.label))
        self.clipboard.raw_set_text('\n'.join(copy_str))


