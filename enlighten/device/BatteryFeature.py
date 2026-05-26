import logging

from enlighten.EnlightenFeature import EnlightenFeature

log = logging.getLogger(__name__)

class BatteryFeature(EnlightenFeature):
    """ 
    @todo track battery state in SpectrometerApplicationState to support multiple connected spectrometers
    """
    def __init__(self, ctl):
        super().__init__(ctl)

        cfu = ctl.form.ui

        self.lb_hw_view_level = cfu.label_hw_view_battery_parsed
        self.lb_power_connection_state = cfu.label_hw_view_power_connection_state

        self.strip_chart_level = self.ctl.strip_charts.create_chart(
            name="Battery Charge Level", 
            y_unit="Percent (%)", 
            format="{value:.2f}%", 
            warn_lo=0.20,
            process_reading_callback=self.process_reading_level)

        # todo: add strip_charts for:
        # - reading.battery_temperature_deg_c
        # - reading.battery_charger_temperature_deg_c

    def process_reading_level(self, spec, reading):
        """ Called by StripCharts """
        if reading.battery_percentage is None:
            return

        if not spec.settings.eeprom.has_battery:
            return
    
        if reading.power_connection_state:
            self.lb_power_connection_state.setText(str(reading.power_connection_state))

        perc = reading.battery_percentage
        is_charging = reading.battery_charging
        charging_label = 'charging' if is_charging else 'discharging'

        self.strip_chart_level.add_value(spec, perc)

        self.lb_hw_view_level.setText(f"{perc:.2f}%, {charging_label}")
            
        self.notify_observers_with_value( (perc, is_charging) )

    def update_visibility(self):
        spec = self.ctl.multispec.current_spectrometer()
        visible = spec and spec.settings.eeprom.has_battery
        self.strip_chart_level.set_visible(visible)

    def get_perc(self, spec=None):
        return self.strip_chart_level.get_latest()
