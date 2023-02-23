import pandas as pd
import numpy as np
import logging

import time

from EnlightenPlugin import EnlightenPluginBase, EnlightenPluginField, EnlightenPluginResponse, EnlightenPluginConfiguration

log = logging.getLogger(__name__)

"""
HEMO-PLUGIN by s.bee

Currently outputs three labeled scalars using dataframe

TODO: enable-able only in non-Raman mode
    [x] requires PluginWorker connect on main thread
    [x] fixes workaround sleep for error, error msg

TODO: fix graphing bugs
    [x] graph only shows up sometimes?
        - forgot to "enable"!
    [x] series_names duplicates
        - seems to be caused by bad series_name declarations
    [x] add clear graph button
    [ ] add callbacks to buttons
    [ ] hide pd frame until calculation is made?

TODO: actually compute the scalars
    - depends on slope
TODO: actually compute AU/min
    [ ] add start / stop measure slope buttons
    * maintain a history of Absorbance spectra
    * for wavelengths 436nm(ChE activity) & 412nm(Hb)
        - how much did it change in the past minute
            - extrapolate from shorter time interval?
                - results can vary wildly. 
                    - 1AU/1ms -> 60kAU/m
                    - .2AU/1s -> 18AU/m
            - find avg derivative, or simply slope endpoints?
                - might be the same due to IVT

MISC:
linear relationship btwn absorbance and enzyme: (1961)
    rate moles/1.  per min = dA/min / 1.36e4

"Yellow" ~= 578 nm light (1961)

1999 paper is explicit: 436nm (blue) for enzyme activity
546 nm (green) absorption for hemoglobin determination

1999:
hemo = A * 1000/10.8
activity = (sample mE - blank mE) / 10.6
AChE = activity * 1.58e3
activity = (sample mE - blank mE) * 1.58e3 / 10.6 

=== PLUGINS IN ENLIGHTEN ===

- get_peak_from_wavelength
- get_widget_from_name

"""

def get_peak_from_wavelength(wavelength, request):

    wl_arr = request.settings.wavelengths
    spectrum = request.processed_reading.processed

    for i in range(len(wl_arr)-1):
        if wl_arr[i] <= wavelength < wl_arr[i+1]:
            return spectrum[i]

    if wl_arr[-1] == wavelength:
        return spectrum[-1]

    raise Exception("Target wavelength %d not available." % wavelength)


ChE_label = "ChE Activity (436 nm)"
Hb_label = "Hb Content (546 nm)"

Slope_start_label = "Slope Start"
Slope_end_label = "Slope End"
Slope_label = "Slope"

class Worek(EnlightenPluginBase):

    def __init__(self):
        super().__init__()
        self.clear_graph()
        self.start_recording()

    def start_recording(self):
        self._isrecording = True

    def stop_recording(self):
        self._isrecording = False

    def clear_graph(self):
        self.startTime = time.time()

        self.sampleTimes = []
        self.ChEActivity = []
        self.HbContent = []

        self.slope_start = None
        self.slope_end = None

    def get_widget_from_name(self, name):
        widget = None
        for elem in self.enlighten_info.plugin_fields():
            if elem.field_name == name:
                widget = elem
        return widget.field_widget

    def graph_slope(self):
        # self.get_widget_from_name("slope start") will be a QtWidgets.QDoubleSpinBox
        # same thing for slope_end_txtbox

        self.slope_start = self.get_widget_from_name("slope start").value()
        self.slope_end = self.get_widget_from_name("slope end").value()

    def get_configuration(self):

        fields = []

        NOOP = lambda *k: None

        # return a Pandas DataFrame for the GUI table
        fields.append(EnlightenPluginField(
            name        = "Output Levels", 
            datatype    = "pandas", 
            direction   = "output"))

        fields.append(EnlightenPluginField(
            name        = "clear", 
            datatype    = "button", 
            callback    = self.clear_graph))

        fields.append(EnlightenPluginField(
            name        = "start recording", 
            datatype    = "button", 
            callback    = self.start_recording))

        fields.append(EnlightenPluginField(
            name        = "stop recording", 
            datatype    = "button", 
            callback    = self.stop_recording))

        fields.append(EnlightenPluginField(
            name        = "slope start", 
            minimum     = 0,
            datatype    = "float", 
            direction   = "input"))

        fields.append(EnlightenPluginField(
            name        = "slope end", 
            minimum     = 0,
            datatype    = "float", 
            direction   = "input"))

        fields.append(EnlightenPluginField(
            name        = "graph slope", 
            datatype    = "button", 
            callback   = self.graph_slope))

        fields.append(EnlightenPluginField(
            name        = "calculate values", 
            datatype    = "button", 
            callback    = NOOP))

        return EnlightenPluginConfiguration(
            name             = "Worek", 
            fields           = fields,
            is_blocking      = False,
            has_other_graph  = True,
            series_names     = [ChE_label, Hb_label, Slope_start_label, Slope_end_label, Slope_label],
            x_axis_label = "time (sec)")

    def connect(self, enlighten_info):
        # if enlighten_info.ctl.page_nav.operation_mode != 4: # 4 = ABSORBANCE
        #     # can be found in log:
        #     # enlighten.Plugins.PluginWorker CRITICAL
        #     # does not interrupt plugin connect tho :/
        #     # must set PluginWorker error message somehow
        #     log.critical("Worek plugin requires Non-Raman>Technique>Absorbance")
        #     raise Exception("Worek plugin requires Non-Raman>Technique>Absorbance")

        return super().connect(enlighten_info)

    def process_request(self, request):
        spectrum = request.processed_reading.processed

        if self._isrecording:
            self.sampleTimes.append(time.time() - self.startTime)
            self.ChEActivity.append(get_peak_from_wavelength(1014, request))
            self.HbContent.append(get_peak_from_wavelength(912.29, request))

        # these quantities are 
        # - Hemoglobin concentration
        # - Enzyme Activity (AChE, BChE)
        # - Erythrocyte AChE
        dataframe = pd.DataFrame( 
            [ -1, "--", -1 ],
            index = ["Hb (µmol/l Hb)", "Activity (µmol/l/min)", "AChE (mU/µmol Hb)" ]
        )

        dataframe = dataframe.T
        
        series = {}
        series[ChE_label] = {
            "x": np.array(self.sampleTimes),
            "y": np.array(self.ChEActivity)
        }       
        series[Hb_label] = {
            "x": np.array(self.sampleTimes),
            "y": np.array(self.HbContent)
        }

        if self.slope_start != None:
            # draw a vertical line at the time when they click "start measure slope"
            series[Slope_start_label] = {
                "x": np.array([self.slope_start, self.slope_start]),
                # set y coordinates of line to min and max of data so we can see it clearly
                "y": np.array([min(self.ChEActivity+self.HbContent), max(self.ChEActivity+self.HbContent)])
            }

        if self.slope_end != None:
            # draw a vertical line at the time when they click "end measure slope"
            series[Slope_end_label] = {
                "x": np.array([self.slope_end, self.slope_end]),
                # set y coordinates of line to min and max of data so we can see it clearly
                "y": np.array([min(self.ChEActivity+self.HbContent), max(self.ChEActivity+self.HbContent)])
            }

        return EnlightenPluginResponse(request,
            series = series,
            outputs = {
                # table (looks like a spreadsheet under the graph)
                "Output Levels": dataframe,
            })

    def disconnect(self):
        super().disconnect()