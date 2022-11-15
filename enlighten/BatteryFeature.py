import logging
import datetime

import pyqtgraph

log = logging.getLogger(__name__)

class BatteryFeature:
    """ 
    @todo track battery state in SpectrometerApplicationState to support multiple connected spectrometers
    """
    def __init__(self,
                 sfu,
                 graph,
                 multispec,
                 clear_btn,
                 make_pen,
                 clipboard,
                 hardware_file_manager,
                 lb_raw,
                 lb_parsed):

        self.sfu                   = sfu
        self.curve                 = None
        self.name                  = "Battery"
        self.graph                 = graph
        self.multispec             = multispec
        self.clear_btn             = clear_btn
        self.make_pen              = make_pen
        self.clipboard             = clipboard
        self.output_to_file        = False
        self.hardware_file_manager = hardware_file_manager

        self.lb_raw    = lb_raw 
        self.lb_parsed = lb_parsed

        self.populate_placeholder()
        self.multispec.register_strip_feature(self)
        self.hardware_file_manager.register_feature(self)

        self.raw = None
        self.perc = 100
        self.charging = False

        self.observers = set()

        self.clear_btn                   .clicked            .connect(self.clear_data)
        self.sfu.pushButton_battery_copy .clicked            .connect(self.copy_data)

    def register_observer(self, callback):
        self.observers.add(callback)

    def unregister_observer(self, callback):
        try:
            self.observers.remove(callback)
        except:
            pass

    def process_reading(self, spec, reading):
        current_spec = self.multispec.current_spectrometer()
        if reading.battery_raw is None:
            return

        if hasattr(spec.settings.eeprom,"has_battery"):
            if not spec.settings.eeprom.has_battery:
                self.lb_degC.setText("No Battery")
                return

        app_state = spec.app_state
        rds = app_state.battery_data
        self.raw = reading.battery_raw
        self.perc = reading.battery_percentage
        self.charging = reading.battery_charging
        rds.add(self.perc)
        current_time = datetime.datetime.now()
        if self.output_to_file:
            self.hardware_file_manager.write_line(self.name,f"{self.name},{spec.label},{current_time}, {self.perc}, charging: {self.charging}")

        self._update_labels(reading)
        for cb in self.observers:
            cb(self.perc, self.charging)

        active_curve = self.multispec.get_hardware_feature_curve(self.name, spec.device_id)
        if active_curve == None:
            return

        x_time = [(current_time-x).total_seconds() for x,y in rds.data]
        y = rds.get_values()

        try:
            self.graph.set_data(curve=active_curve, y=y, x=x_time)
        except:
            log.error("error plotting laser temperature", exc_info=1)

        if spec == current_spec:
            self.lb_degC.setText("%.2f %" % self.perc)

    def _update_labels(self, reading):
        self.lb_raw.setText("0x%06x" % reading.battery_raw)
        self.lb_parsed.setText("Battery (%.2f%%, %s)" % (
            self.perc, "charging" if self.charging else "discharging"))

    def populate_placeholder(self):
        self.sfu.battery_graph = pyqtgraph.PlotWidget(name="Battery Data")
        self.sfu.battery_graph.invertX(True)
        self.sfu.stackedWidget_battery.addWidget(self.sfu.battery_graph)
        self.sfu.stackedWidget_laser_temperature.setCurrentIndex(1)

    def add_spec_curve(self, spec):
        if self.multispec.check_hardware_curve_present(self.name, spec.device_id):
            return
        curve = self.sfu.battery_graph.plot([], pen=spec.curve.opts['pen'],name=str(spec.label))
        self.multispec.register_hardware_feature_curve(self.name, spec.device_id, curve) 
    
    def remove_spec_curve(self, spec):
        cur_curve = self.multispec.get_hardware_feature_curve(self.name, spec.device_id)
        if cur_curve is None:
            return
        # remove current curve from graph
        for curve in self.sfu.battery_graph.listDataItems():
            if curve.name() == cur_curve.name():
                self.sfu.battery_graph.removeItem(curve)
        self.multispec.remove_hardware_curve(self.name, spec.device_id)
        if self.multispec.get_spectrometers() == []:
            self.lb_degC.setText("99.99 %")

    def clear_data(self):
        for spec in self.multispec.get_spectrometers():
            if spec is None:
                continue
            app_state = spec.app_state

            rds = app_state.battery_data
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
            rds = app_state.battery_data
            copy_str.append(rds.get_csv_data("Battery Data",spec.label))
        self.clipboard.raw_set_text('\n'.join(copy_str))



