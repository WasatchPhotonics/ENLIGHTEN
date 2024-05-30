import logging
import datetime

from EnlightenPlugin import EnlightenPluginBase

log = logging.getLogger(__name__)

##
# Simple plug-in showing how to implement a strip chart (rolling time window), as
# well as demonstrating non-spectral metadata that can be extracted from 
# processed_readings.
# 
# @todo this is an example of a plug-in that would benefit from multiple y-axes
class StripChart(EnlightenPluginBase):

    def get_configuration(self):
        self.name = "Strip Chart"
        self.data = {} # datetime -> HardwareState
        self.field(name="Window (sec)", datatype="int", direction="input", initial=10, maximum=30, minimum=1, step=1)
        self.field(name="Battery", datatype="bool", direction="input", initial=False)
        self.field(name="Temperature", datatype="bool", direction="input", initial=False)
        self.has_other_graph = True
        self.x_axis_label = "Time (Sec)"

    # @todo could also check settings.eeprom.has_battery and has_cooling
    def process_request(self, request):
        reading    = request.processed_reading.reading
        window_sec = request.fields["Window (sec)"]
        show_batt  = request.fields["Battery"] and request.settings.eeprom.has_battery
        show_temp  = request.fields["Temperature"]

        spectrum   = request.processed_reading.get_processed()
        wavelengths = request.processed_reading.get_wavelengths()
        wavenumbers = request.processed_reading.get_wavenumbers()
        cursor_x = self.ctl.cursor.get_x_pos()

        log.debug(f"cursor x: {cursor_x}")
        log.debug(f"spectrum: {spectrum}")
        log.debug(f"wavelengths: {wavelengths}")
        log.debug(f"wavenumbers: {wavenumbers}")

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
        
        if show_batt:
            log.debug(f"series_batt = {series_batt}")
            self.plot(y=series_batt.y, x=series_batt.x, title="Battery")
        if show_temp:
            log.debug(f"series_temp = {series_temp}")
            self.plot(y=series_temp.y, x=series_temp.x, title="Temperature")

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

    def __repr__(self):
        return f"Series: x ({self.x}), y ({self.y})"
