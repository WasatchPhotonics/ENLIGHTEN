import logging
import datetime

from EnlightenPlugin import EnlightenPluginBase

log = logging.getLogger(__name__)

class StripChart(EnlightenPluginBase):
    """
    Simple plug-in showing how to implement a strip chart (rolling time window), as
    well as demonstrating non-spectral metadata that can be extracted from 
    wasatch.ProcessedReading and wasatch.Reading (as well as other ENLIGHTEN
    business objects, like Cursor).
    
    @author Cary Academy Interns, 2024
    @todo this is an example of a plug-in that would benefit from multiple y-axes
    """

    def get_configuration(self):
        self.name = "Strip Chart"
        self.has_other_graph = True
        self.multi_devices = True
        self.block_enlighten = True

        self.data = {} # serial_number -> datetime -> HardwareState
        self.x_axis_label = "Time (Sec)"

        self.field(name="Window (sec)", datatype=int, direction="input", initial=10, maximum=30, minimum=1, step=1)
        self.field(name="Cursor",  datatype=bool, direction="input", initial=False)
        self.field(name="Battery", datatype=bool, direction="input", initial=False)
        self.field(name="Det °C",  datatype=bool, direction="input", initial=False)

    def process_request(self, request):
        spec       = request.spec
        eeprom     = request.settings.eeprom
        serial     = eeprom.serial_number
        pr         = request.processed_reading
        reading    = pr.reading

        window_sec = request.fields["Window (sec)"]
        show_curs  = request.fields["Cursor"] 
        show_batt  = request.fields["Battery"] 
        show_temp  = request.fields["Det °C"]

        ########################################################################
        # add these to our rolling window
        ########################################################################

        # track this spectrometer if we haven't seen it before
        if serial not in self.data:
            self.data[serial] = {}

        # collect data for this timestamp
        now = datetime.datetime.now()

        cursor_x, cursor_y = self.ctl.cursor.get_pos(spec) 
        batt_perc = reading.battery_percentage if eeprom.has_battery else None
        det_temp_degC = reading.detector_temperature_degC if eeprom.has_cooling else None

        self.data[serial][now] = HardwareState(cursor=cursor_y, battery=batt_perc, temp=det_temp_degC)

        # Note that not all spectrometers have batteries, or temperature readout, so
        # only graph data we actually found

        for sn in sorted(self.data.keys()):
            series_curs = Series()
            series_batt = Series()
            series_temp = Series()

            for t in sorted(self.data[sn].keys()): # t = timestamp
                sec_ago = (now - t).total_seconds()
                if sec_ago > window_sec:
                    del self.data[sn][t]
                    continue

                state = self.data[sn][t]
                if show_curs and state.cursor  is not None: series_curs.add(-sec_ago, state.cursor)
                if show_batt and state.battery is not None: series_batt.add(-sec_ago, state.battery)
                if show_temp and state.temp    is not None: series_temp.add(-sec_ago, state.temp)
        
            if len(series_curs.x): self.plot(y=series_curs.y, x=series_curs.x, title=f"{sn} Cursor")
            if len(series_batt.x): self.plot(y=series_batt.y, x=series_batt.x, title=f"{sn} Battery")
            if len(series_temp.x): self.plot(y=series_temp.y, x=series_temp.x, title=f"{sn} Det °C")

class HardwareState:
    def __init__(self, cursor=None, battery=None, temp=None):
        self.cursor = cursor
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
