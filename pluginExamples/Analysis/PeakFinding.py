import pandas as pd
import numpy as np
import logging
import scipy

from EnlightenPlugin import EnlightenPluginBase,   \
                            EnlightenPluginField,   \
                            EnlightenPluginResponse, \
                            EnlightenPluginConfiguration

log = logging.getLogger(__name__)

##
# A sample ENLIGHTEN Plug-in which performs peakfinding on each received spectrum,
# displaying an xy scatterplot of peak pixel and intensity, and including a table.
class PeakFinding(EnlightenPluginBase):

    def __init__(self):
        super().__init__()

    def get_configuration(self):
        fields = []

        # provide an input field on the GUI to allow the user to specify a "prominence" value
        fields.append(EnlightenPluginField(
            name        = "Prominence", 
            datatype    = "float", 
            initial     = 200, 
            maximum     = 200000, 
            minimum     = 0,
            step        = 1, 
            direction   = "input"))

        # specify an output field on the GUI to display the generated peak locations
        fields.append(EnlightenPluginField(
            name        = "Peak Count", 
            datatype    = "int", 
            direction   = "output"))

        # also return peaks as a Pandas DataFrame for the GUI table
        fields.append(EnlightenPluginField(
            name        = "Peak Table", 
            datatype    = "pandas", 
            direction   = "output"))

        # provide a button letting us transpose the table
        fields.append(EnlightenPluginField(
            name        = "transpose",
            datatype    = "bool",
            direction   = "input"))

        return EnlightenPluginConfiguration(
            name            = "Peakfinding", 
            fields          = fields, 
            has_other_graph = True, 
            is_blocking     = False,
            graph_type      = 'line', 
            series_names    = ['Peaks'])

    def connect(self, enlighten_info):
        return super().connect(enlighten_info)

    def process_request(self, request):
        spectrum = request.processed_reading.processed.tolist()
        settings = request.settings
        fields   = request.fields
        prom     = fields['Prominence']

        # use scipy peakfinding to find x-coordinates of peaks in pixel space 
        (peak_x, _) = scipy.signal.find_peaks(spectrum, prominence=prom)
        peak_y = [ spectrum[x] for x in peak_x ]

        # convert to wavelength and wavenumber space
        peak_cm = None
        peak_nm = [ settings.wavelengths[x] for x in peak_x ]
        peak_cm = [ settings.wavenumbers[x] for x in peak_x ] if settings.wavenumbers is not None else None

        # create Pandas DataFrame to display peaks in QTableView
        dataframe = pd.DataFrame( [ peak_x,          peak_nm,            peak_cm,      peak_y ],
                          index = [ "pixel", "wavelength (nm)", "Raman shift (cm⁻¹)", "intensity" ])
        dataframe = dataframe.round(2)
        if request.fields["transpose"]:
            dataframe = dataframe.T

        # generate a "fake graph" showing only peaks
        unit = self.enlighten_info.get_x_axis_unit()
        if unit == "nm":
            series_data = self.generate_series(settings.wavelengths, peak_nm, peak_y)
        elif unit == "cm":
            series_data = self.generate_series(settings.wavenumbers, peak_cm, peak_y)
        else:
            series_data = self.generate_series(list(range(len(spectrum))), peak_x, peak_y)

        # send the graph series and table in response
        response = EnlightenPluginResponse(
            request = request, 
            series  = { 
                "Peaks": {                      # for graph
                    'x': series_data[0],
                    'y': series_data[1]
                }
            },
            outputs = { 
                "Peak Table": dataframe,        # for table
                "Peak Count": len(peak_x)       # for widget
            }   
        )      
        return response

    def disconnect(self):
        super().disconnect()

    # ##########################################################################
    # private methods
    # ##########################################################################

    ##
    # @todo it would be kinda cool if we made a simple Guassian curve for each
    #       using settings.eeprom.avg_resolution
    # @see https://en.wikipedia.org/wiki/Gaussian_function
    # @see https://stackoverflow.com/questions/14873203/plotting-of-1-dimensional-gaussian-distribution-function
    def generate_series(self, x_axis, peak_x, peak_y):
        series_x = [ x_axis[0] ]
        series_y = [ 0 ]

        for i in range(len(peak_x)):
            (x, y) = (peak_x[i], peak_y[i])
            series_x.extend((x - 0.1, x, x + 0.1))
            series_y.extend((0,       y,       0))

        series_x.append(x_axis[-1])
        series_y.append(0)

        return (series_x, series_y)
