import pandas as pd
import numpy as np
import logging

import time

from EnlightenPlugin import *

log = logging.getLogger(__name__)

def getY(x, domain, codomain):
    """
    given two arrays (domain, codomain) which describe a collection of points
      domain: x0 x1 x2 x3 x4 ... xn
    codomain: y0 y1 y2 y3 y4 ... yn

    return the element from codomain such that the corresponding element from domain = x
    ex: getY(4, [0,2,4,6,8], [1,3,5,7,9]) --> 5

    if x is not in the domain, return the closest boundary element
    """

    for i in range(len(domain)-1):
        if domain[i] <= x < domain[i+1]:
            return codomain[i]

    if domain[-1] >= x:
        return codomain[-1]
    
    return codomain[0]

def get_intensity_from_wavelength(wavelength, wavelengths, spectrum):

    return getY(wavelength, wavelengths, spectrum)

ChE_label = "ChE Activity"
Hb_label = "Hb Content"

ChE_Blank_slope_label = "ChE Blank Slope"
ChE_Sample_slope_label = "ChE Sample Slope"

class Worek(EnlightenPluginBase):

    def __init__(self, ctl):
        super().__init__(ctl)
        self.clear_graph()

    def start_recording(self):
        self.clear_graph()
        self._isrecording = True

    def stop_recording(self):
        self._isrecording = False

    def clear_graph(self):
        self._isrecording = False
        self.startTime = time.time()

        self.sampleTimes = []
        self.ChEActivity = []
        self.HbContent = []

        self.slope_start = None
        self.slope_end = None

        self.ChEActivityY2 = None
        self.ChEActivityY1 = None

    def graph_slope(self):
        # self.get_widget_from_name("slope start") will be a QtWidgets.QDoubleSpinBox
        # same thing for slope_end_txtbox

        blank_start = self.get_widget_from_name("blank start").value()
        blank_end = self.get_widget_from_name("blank end").value()
        sample_start = self.get_widget_from_name("sample start").value()
        sample_end = self.get_widget_from_name("sample end").value()

        if not (blank_start < blank_end < sample_start < sample_end):
            return False # slope indicators in bad order

        self.ChEActivityY1 = getY(blank_start, self.sampleTimes, self.ChEActivity)
        self.ChEActivityY2 = getY(blank_end, self.sampleTimes, self.ChEActivity)
        self.ChEActivityY3 = getY(sample_start, self.sampleTimes, self.ChEActivity)
        self.ChEActivityY4 = getY(sample_end, self.sampleTimes, self.ChEActivity)

        return True

    def get_configuration(self):

        fields = []

        # return a Pandas DataFrame for the GUI table
        fields.append(EnlightenPluginField(
            name        = "Output Levels", 
            datatype    = "pandas", 
            direction   = "output"))

        fields.append(EnlightenPluginField(
            name        = "start new recording", 
            datatype    = "button", 
            callback    = self.start_recording))

        fields.append(EnlightenPluginField(
            name        = "stop recording", 
            datatype    = "button", 
            callback    = self.stop_recording))

        fields.append(EnlightenPluginField(
            name        = "ChE Activity Wavelength", 
            initial     = 436,
            minimum     = 0,
            maximum     = 10000,
            datatype    = "float", 
            direction   = "input"))
        
        fields.append(EnlightenPluginField(
            name        = "Hb Content Wavelength", 
            initial     = 546,
            minimum     = 0,
            maximum     = 10000,
            datatype    = "float", 
            direction   = "input"))

        fields.append(EnlightenPluginField(
            name        = "blank start", 
            minimum     = 0,
            maximum     = float("Inf"),
            datatype    = "float", 
            direction   = "input"))

        fields.append(EnlightenPluginField(
            name        = "blank end", 
            minimum     = 0,
            maximum     = float("Inf"),
            datatype    = "float", 
            direction   = "input"))

        fields.append(EnlightenPluginField(
            name        = "sample start", 
            minimum     = 0,
            maximum     = float("Inf"),
            datatype    = "float", 
            direction   = "input"))

        fields.append(EnlightenPluginField(
            name        = "sample end", 
            minimum     = 0,
            maximum     = float("Inf"),
            datatype    = "float", 
            direction   = "input"))

        return EnlightenPluginConfiguration(
            name             = "Worek", 
            fields           = fields,
            is_blocking      = False,
            has_other_graph  = True,
            series_names     = [ChE_label, Hb_label, ChE_Blank_slope_label, ChE_Sample_slope_label],
            x_axis_label = "time (sec)")

    def connect(self):
        return super().connect()

    def process_request(self, request):
        pr = request.processed_reading

        spectrum = pr.get_processed()
        
        if self._isrecording:
            self.sampleTimes.append(time.time() - self.startTime)
            ChE_wavelength = self.get_widget_from_name("ChE Activity Wavelength").value()
            Hb_wavelength = self.get_widget_from_name( "Hb Content Wavelength").value()

            wl_arr = request.settings.wavelengths

            self.ChEActivity.append(get_intensity_from_wavelength(ChE_wavelength, wl_arr, spectrum))
            self.HbContent.append(get_intensity_from_wavelength(Hb_wavelength, wl_arr, spectrum))
        
        series = {}
        series[ChE_label] = {
            "x": np.array(self.sampleTimes),
            "y": np.array(self.ChEActivity)
        }       
        series[Hb_label] = {
            "x": np.array(self.sampleTimes),
            "y": np.array(self.HbContent)
        }

        blank_start = self.get_widget_from_name("blank start").value()
        blank_end = self.get_widget_from_name("blank end").value()
        sample_start = self.get_widget_from_name("sample start").value()
        sample_end = self.get_widget_from_name("sample end").value()

        header = ["Sample (mE/min)", "Blank (mE/min)", "Hb (µmol/l Hb)", "Activity (µmol/l/min)", "AChE (mU/µmol Hb)" ]
        if self.graph_slope():
            series[ChE_Blank_slope_label] = {
                "x": np.array([blank_start, blank_end]),
                "y": np.array([self.ChEActivityY1, self.ChEActivityY2])
            }

            series[ChE_Sample_slope_label] = {
                "x": np.array([sample_start, sample_end]),
                "y": np.array([self.ChEActivityY3, self.ChEActivityY4])
            }

            sample = (self.ChEActivityY4 - self.ChEActivityY3) / (sample_end - sample_start) * 60 # convert mE/sec to mE/min
            blank = (self.ChEActivityY2 - self.ChEActivityY1) / (blank_end - blank_start) * 60 # convert mE/sec to mE/min

            # use Hb absorption at blank_start
            HbA0 = getY(blank_start, self.sampleTimes, self.HbContent)
            HbC = HbA0 * 1000/10.8

            Activity = (sample - blank) / 10.6

            AchE = (Activity * 1.58 * 1000) / HbC

            # these quantities are 
            # - Sample rate (comes from slopes)
            # - Blank rate
            # --------------------------
            # - Hemoglobin concentration (applying formulas)
            # - Enzyme Activity (AChE, BChE)
            # - Erythrocyte AChE
            dataframe = pd.DataFrame( 
                [ sample, blank, HbC, Activity, AchE ],
                index = header
            )
        else:
            # Show blank defaults if no slope is computed
            dataframe = pd.DataFrame( 
                [ "--", ] * len(header),
                index = header
            )

        dataframe = dataframe.T

        return EnlightenPluginResponse(request,
            series = series,
            outputs = {
                # table (looks like a spreadsheet under the graph)
                "Output Levels": dataframe,
            })

    def disconnect(self):
        super().disconnect()
