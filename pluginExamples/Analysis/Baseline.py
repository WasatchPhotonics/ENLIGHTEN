import pandas as pd
import numpy as np
import logging

import time

from EnlightenPlugin import *

log = logging.getLogger(__name__)

class Baseline(EnlightenPluginBase):

    def get_widget_from_name(self, name):
        widget = None
        for elem in self.enlighten_info.plugin_fields():
            if elem.field_name == name:
                widget = elem
        return widget.field_widget

    def get_configuration(self):

        fields = []

        # return a Pandas DataFrame for the GUI table
        fields.append(EnlightenPluginField(
            name        = "Output Levels", 
            datatype    = "pandas", 
            direction   = "output"))

        fields.append(EnlightenPluginField(
            name        = "wavelength", 
            initial     = 436,
            minimum     = 0,
            maximum     = 10000,
            datatype    = "float", 
            direction   = "input"))
        
        fields.append(EnlightenPluginField(
            name        = "inner radius", 
            initial     = 10,
            minimum     = 0,
            maximum     = 10000,
            datatype    = "float", 
            direction   = "input"))

        fields.append(EnlightenPluginField(
            name        = "outer radius", 
            initial     = 20,
            minimum     = 0,
            maximum     = float("Inf"),
            datatype    = "float", 
            direction   = "input"))

        return EnlightenPluginConfiguration(
            name             = "Baseline", 
            fields           = fields,
            is_blocking      = False,
            has_other_graph  = False,
            series_names     = ["Target", "Inner Radius", "Outer Radius"])

    def process_request(self, request):
        pr = request.processed_reading

        spectrum = pr.get_processed()
        
        wavelength = self.get_widget_from_name("wavelength").value()
        inner_radius = self.get_widget_from_name("inner radius").value()
        outer_radius = self.get_widget_from_name("outer radius").value()

        series = {}
        series["Target"] = {
            "x": np.array([wavelength, wavelength]),
            "y": np.array([min(spectrum), max(spectrum)])
        }       

        series["Inner Radius"] = {
            "x": np.array([wavelength-inner_radius, wavelength-inner_radius]),
            "y": np.array([min(spectrum), max(spectrum)])
        }   

        series["Outer Radius"] = {
            "x": np.array([wavelength-outer_radius, wavelength-outer_radius]),
            "y": np.array([min(spectrum), max(spectrum)])
        }   

        header = ["output"]
        dataframe = pd.DataFrame( 
            [ "--" ],
            index = header
        )

        dataframe = dataframe.T

        return EnlightenPluginResponse(request,
            series = series,
            outputs = {
                # table (looks like a spreadsheet under the graph)
                "Output Levels": dataframe,
            })