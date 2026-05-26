import logging
import datetime
import pyqtgraph

from enlighten.EnlightenFeature import EnlightenFeature

log = logging.getLogger(__name__)

class AmbientTemperatureFeature(EnlightenFeature):

    def __init__(self, ctl):
        super().__init__(ctl)

        cfu = ctl.form.ui

        self.strip_chart = self.ctl.strip_charts.create_chart(
            name="Ambient Temperature", 
            y_unit="Celsius (°C)", 
            format="{value:.2f}°C", 
            warn_hi=35,
            process_reading_callback=self.process_reading_callback)

    def notify(self, spec, s):
        if spec != self.ctl.multispec.current_spectrometer():
            return
        self.notify_observers_with_value(s)

    def process_reading_callback(self, spec, reading):
        """ Called by StripCharts """
        if spec is None:
            return self.notify(spec, "disconnected")

        if not spec.settings.is_xs():
            return self.notify(spec, "unsupported")
            
        degC = reading.ambient_temperature_degC
        if degC is None:
            return self.notify(spec, "none")

        self.strip_chart.add_value(spec, degC)

        self.notify(spec, f"{degC:-.2f} °C")
