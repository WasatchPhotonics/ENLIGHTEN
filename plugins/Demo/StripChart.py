import logging
import datetime

from EnlightenPlugin import EnlightenPluginBase,    \
                            EnlightenPluginField,    \
                            EnlightenPluginResponse,  \
                            EnlightenPluginConfiguration

log = logging.getLogger(__name__)

##
# Simple plug-in showing how to implement a strip chart (rolling time window), as
# well as demonstrating non-spectral metadata that can be extracted from 
# processed_readings.
# 
# @todo this is an example of a plug-in that would benefit from multiple y-axes
class StripChart(EnlightenPluginBase):

    def __init__(self, ctl):
        super().__init__(ctl)

        self.data = {} # datetime -> HardwareState

    def get_configuration(self):
        fields = [
            EnlightenPluginField(name="Window (sec)", datatype="int", direction="input", initial=10, maximum=30, minimum=1, step=1),
            EnlightenPluginField(name="Battery", datatype="bool", direction="input", initial=True),
            EnlightenPluginField(name="Temperature", datatype="bool", direction="input", initial=True)
        ]
        return EnlightenPluginConfiguration(
            name            = "Strip Chart", 
            fields          = fields,
            has_other_graph = True, 
            series_names    = ["Battery", "Temperature"], 
            x_axis_label    = "Time (Sec)", 
            y_axis_label    = "% / °C")

    def connect(self):
        super().connect()
        return True

    # @todo could also check settings.eeprom.has_battery and has_cooling
    def process_request(self, request):
        reading    = request.processed_reading.reading
        window_sec = request.fields["Window (sec)"]
        show_batt  = request.fields["Battery"]
        show_temp  = request.fields["Temperature"]

        # add these to our rolling average
        now = datetime.datetime.now()
        self.data[now] = HardwareState(reading.battery_percentage, reading.detector_temperature_degC)

        # Note that not all spectrometers have batteries, or temperature readout, so
        # only graph data we find in readings.
        series_batt = Series()
        series_temp = Series()

        for t in sorted(self.data.keys()): # t = timestamp
            sec_ago = (now - t).total_seconds()
            if sec_ago > window_sec:
                del self.data[t]
                continue
            state = self.data[t]
            if show_batt and state.battery is not None:
                series_batt.add(-sec_ago, state.battery)
            if show_temp and state.temp is not None:
                series_temp.add(-sec_ago, state.temp)
        
        return EnlightenPluginResponse(request, series = {
            "Battery":     { 'x': series_batt.x, 'y': series_batt.y },
            "Temperature": { 'x': series_temp.x, 'y': series_temp.y }
        })

    def disconnect(self):
        super().disconnect()

class HardwareState:
    def __init__(self, battery=None, temp=None):
        self.battery = battery
        self.temp = temp

class Series:
    def __init__(self):
        self.x = []
        self.y = []

    def add(self, x, y):
        self.x.append(x)
        self.y.append(y)
