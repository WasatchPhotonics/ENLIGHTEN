import logging
import datetime
import pyqtgraph

from enlighten.EnlightenFeature import EnlightenFeature

log = logging.getLogger(__name__)

class BatteryFeature(EnlightenFeature):
    """ 
    @todo track battery state in SpectrometerApplicationState to support multiple connected spectrometers
    """
    def __init__(self, ctl):
        super().__init__(ctl)

        cfu = ctl.form.ui

        self.curve                 = None
        self.name                  = "Battery"
        self.output_to_file        = False

        self.lb_perc = cfu.label_hardware_capture_details_battery
        self.lb_parsed = cfu.label_battery_parsed

        # MZ: consider eventually moving this to a new Feature, but fine for now
        self.lb_power_connection_state = cfu.label_power_connection_state

        self.populate_placeholder()
        ctl.multispec.register_strip_feature(self)
        ctl.hardware_file_manager.register_feature(self)

        cfu.pushButton_battery_clear_history.clicked.connect(self.clear_data)
        cfu.pushButton_battery_copy_history.clicked.connect(self.copy_data) 

    def process_reading(self, spec, reading):
        if reading.power_connection_state:
            self.lb_power_connection_state.setText(str(reading.power_connection_state))

        if reading.battery_percentage is None:
            return

        if hasattr(spec.settings.eeprom,"has_battery"):
            if not spec.settings.eeprom.has_battery:
                self.lb_perc.setText("No Battery")
                return
    
        # add state.battery_temperature_deg_c
        # add state.battery_charger_temperature_deg_c

        self.process_battery_charge_level(spec, reading)

    def process_battery_charge_level(self, spec, reading):
        app_state = spec.app_state
        rds = app_state.battery_data

        perc = reading.battery_percentage
        is_charging = reading.battery_charging
        charging_label = 'charging' if is_charging else 'discharging'

        log.debug(f"adding {perc} to RDS")
        rds.add(perc)
        current_time = datetime.datetime.now()
        if self.output_to_file:
            self.ctl.hardware_file_manager.write_line(self.name, f"{self.name}, {spec.label}, {current_time}, {perc}, {charging_label}")

        self.lb_parsed.setText(f"{perc:.2f}%, {charging_label}")
        if spec == self.ctl.multispec.current_spectrometer():
            self.lb_perc.setText(f"{perc:.2f} %")
            
        self.notify_observers_with_value( (perc, is_charging) )

        # update graph on Factory View
        active_curve = self.ctl.multispec.get_hardware_feature_curve(self.name, spec.device_id)
        if active_curve is None:
            return
        try:
            x, y = rds.get_relative_to_now()
            log.debug(f"updating battery charge curve ({len(y)} values)")
            self.ctl.graph.set_data(curve=active_curve, y=y, x=x)
        except:
            log.error("error plotting battery data", exc_info=1)

    def populate_placeholder(self):
        log.debug(f"adding battery graph")
        cfu = self.ctl.form.ui
        cfu.battery_graph = pyqtgraph.PlotWidget(name="Battery Data")
        cfu.battery_graph.invertX(True)
        cfu.stackedWidget_battery.addWidget(cfu.battery_graph)
        cfu.stackedWidget_battery.setCurrentIndex(1)

        cfu.battery_graph.setMouseEnabled(x=False, y=False)

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
            log.debug(f"clearing battery history for {spec}")
            if spec is None:
                continue
            app_state = spec.app_state
            rds = app_state.battery_data
            rds.clear()

    def update_curve_color(self, spec):
        curve = self.ctl.multispec.get_hardware_feature_curve(self.name, spec.device_id)
        if curve is None:
            return
        curve.opts["pen"] = spec.color

    def copy_data(self):
        spec = self.ctl.multispec.current_spectrometer()
        copy_str = []
        for spec in self.ctl.multispec.get_spectrometers():
            log.debug(f"copying battery history for {spec}")
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
            return

        if not spec.settings.eeprom.has_battery:
            return

        if spec.app_state.battery_data.empty():
            return

        (_, perc) = spec.app_state.battery_data.latest()
        return perc
