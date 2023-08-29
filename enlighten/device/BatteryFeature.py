import logging
import datetime

import pyqtgraph

log = logging.getLogger(__name__)

class BatteryFeature:
    """ 
    @todo track battery state in SpectrometerApplicationState to support multiple connected spectrometers
    """
    def __init__(self, ctl):
        self.ctl = ctl

        self.curve                 = None
        self.name                  = "Battery"
        self.output_to_file        = False

        self.lb_perc = ctl.form.ui.label_hardware_capture_details_battery

        self.populate_placeholder()
        ctl.multispec.register_strip_feature(self)
        ctl.hardware_file_manager.register_feature(self)

        self.observers = set()

        ctl.form.ui.battery_pushButton.clicked.connect(self.clear_data)
        ctl.form.ui.pushButton_battery_copy.clicked.connect(self.copy_data) # todo rename in form

    def register_observer(self, callback):
        self.observers.add(callback)

    def unregister_observer(self, callback):
        try:
            self.observers.remove(callback)
        except:
            pass

    def process_reading(self, spec, reading):
        current_spec = self.ctl.multispec.current_spectrometer()
        if reading.battery_raw is None:
            return

        if hasattr(spec.settings.eeprom,"has_battery"):
            if not spec.settings.eeprom.has_battery:
                self.lb_perc.setText("No Battery")
                return

        app_state = spec.app_state
        rds = app_state.battery_data

        raw = reading.battery_raw
        perc = reading.battery_percentage
        charging = reading.battery_charging

        rds.add(perc)
        current_time = datetime.datetime.now()
        if self.output_to_file:
            self.ctl.hardware_file_manager.write_line(self.name,f"{self.name},{spec.label},{current_time}, {perc}, charging: {charging}")

        self.ctl.form.ui.label_battery_raw.setText("0x%06x" % reading.battery_raw)
        self.ctl.form.ui.label_battery_parsed.setText(f"Battery ({perc:.2f}%, {'charging' if charging else 'discharging'})")
            
        for cb in self.observers:
            cb(perc, charging)

        active_curve = self.ctl.multispec.get_hardware_feature_curve(self.name, spec.device_id)
        if active_curve == None:
            return

        x_time = [(current_time-x).total_seconds() for x,y in rds.data]
        y = rds.get_values()

        try:
            self.ctl.graph.set_data(curve=active_curve, y=y, x=x_time)
        except:
            log.error("error plotting battery data", exc_info=1)

        if spec == current_spec:
            self.lb_perc.setText(f"{perc:.2f} %")

    def populate_placeholder(self):
        log.debug(f"adding battery graph")
        sfu = self.ctl.form.ui
        sfu.battery_graph = pyqtgraph.PlotWidget(name="Battery Data")
        sfu.battery_graph.invertX(True)
        sfu.stackedWidget_battery.addWidget(sfu.battery_graph)
        sfu.stackedWidget_battery.setCurrentIndex(1)

    def add_spec_curve(self, spec):
        if self.ctl.multispec.check_hardware_curve_present(self.name, spec.device_id):
            return
        curve = self.ctl.form.ui.battery_graph.plot([], pen=spec.curve.opts['pen'],name=str(spec.label))
        self.ctl.multispec.register_hardware_feature_curve(self.name, spec.device_id, curve) 
    
    def remove_spec_curve(self, spec):
        cur_curve = self.ctl.multispec.get_hardware_feature_curve(self.name, spec.device_id)
        if cur_curve is None:
            return
        # remove current curve from graph
        for curve in self.ctl.form.ui.battery_graph.listDataItems():
            if curve.name() == cur_curve.name():
                self.ctl.form.ui.battery_graph.removeItem(curve)
        self.ctl.multispec.remove_hardware_curve(self.name, spec.device_id)
        if self.ctl.multispec.get_spectrometers() == []:
            self.lb_perc.setText("99.99 %")

    def clear_data(self):
        for spec in self.ctl.multispec.get_spectrometers():
            if spec is None:
                continue
            app_state = spec.app_state

            rds = app_state.battery_data
            rds.clear()

    def update_curve_color(self, spec):
        curve = self.ctl.multispec.get_hardware_feature_curve(self.name, spec.device_id)
        if curve == None:
            return
        curve.opts["pen"] = spec.assigned_color

    def copy_data(self):
        spec = self.ctl.multispec.current_spectrometer()
        copy_str = []
        for spec in self.ctl.multispec.get_spectrometers():
            if not self.ctl.multispec.check_hardware_curve_present(self.name, spec.device_id):
                continue

            app_state = spec.app_state
            if app_state is None:
                continue
            rds = app_state.battery_data
            copy_str.append(rds.get_csv_data("Battery Data",spec.label))
        self.ctl.clipboard.raw_set_text('\n'.join(copy_str))

    def update_visibility(self):
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            visible = False
        else:
            if spec.settings.eeprom.has_battery:
                visible = True
            else:
                visible = False

        self.ctl.form.ui.frame_hardware_capture_battery.setVisible(visible)

    def get_perc(self, spec=None):
        if spec is None:
            spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return None

        if not spec.settings.eeprom.has_battery:
            return None

        if spec.app_state.battery_data.empty():
            return None

        (time, perc) = spec.app_state.battery_data.latest()
        return perc
