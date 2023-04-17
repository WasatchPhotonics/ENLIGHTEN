import pandas as pd
import numpy as np
import logging

import time

from EnlightenPlugin import *

log = logging.getLogger(__name__)

class BaselineFunctional(EnlightenPluginBase):

    def get_configuration(self):

        self.name = "Baseline"

        self.field(
            name = "Wavelength", 
            initial = 1014, minimum = 0, maximum = 10000,
            datatype = "float", direction = "input"
        )
        
        self.field(
            name = "Peak Neighborhood", 
            initial = 3, minimum = 0, maximum = 10000,
            datatype = "float", direction = "input"
        )

        self.field(
            name = "Baseline Extent", 
            initial = 10, minimum = 0, maximum = 10000,
            datatype = "float", direction = "input"
        )

        self.is_blocking = False
        self.has_other_graph = False

    def process_request(self, request):
        pr = request.processed_reading
        spectrum = pr.get_processed()
        
        wavelength = self.get_widget_from_name("Wavelength").value()
        inner_radius = self.get_widget_from_name("Peak Neighborhood").value()
        outer_radius = self.get_widget_from_name("Baseline Extent").value()

        left_start = wavelength-inner_radius-outer_radius
        left_end = wavelength-inner_radius
        right_start = wavelength+inner_radius
        right_end = wavelength+inner_radius+outer_radius

        self.plot(
            title="Wavelength",
            color="red",
            x=[wavelength, wavelength],
            y=[min(spectrum), max(spectrum)],
        )

        self.plot(
            title="Peak Neighborhood",
            color="green",
            x=[left_end, left_end],
            y=[min(spectrum), max(spectrum)],
        )
        self.plot(
            color="green",
            x=[right_start, right_start],
            y=[min(spectrum), max(spectrum)],
        )

        self.plot(
            title="Baseline Extent",
            color="blue",
            x=[left_start, left_start],
            y=[min(spectrum), max(spectrum)],
        )
        self.plot(
            color="blue",
            x=[right_end, right_end],
            y=[min(spectrum), max(spectrum)],
        )

        left_start_pixel = self.wavelength_to_pixel(left_start)
        left_end_pixel = self.wavelength_to_pixel(left_end)
        right_start_pixel = self.wavelength_to_pixel(right_start)
        right_end_pixel = self.wavelength_to_pixel(right_end)

        baseline_spectrum = list(spectrum[left_start_pixel:left_end_pixel]) + list(spectrum[right_start_pixel:right_end_pixel])
        if baseline_spectrum:
            mean_baseline = sum(baseline_spectrum)/len(baseline_spectrum)
        elif list(spectrum):
            # Provide some baseline if the user range is <=0
            mean_baseline = min(spectrum)
        else:
            # Don't crash plugin if spectrometer goes offline for a moment
            mean_baseline = 0

        self.plot(
            title="Baseline",
            color="orange",
            x=[left_start, left_end],
            y=[mean_baseline, mean_baseline],
        )
        self.plot(
            color="orange",
            x=[right_start, right_end],
            y=[mean_baseline, mean_baseline],
        )

        peak = spectrum[self.wavelength_to_pixel(wavelength)]
        area = self.area_under_curve(spectrum[left_end_pixel:right_start_pixel], left_end, right_start)
        self.table = pd.DataFrame( 
            [ mean_baseline, peak, peak - mean_baseline, area ],
            index = ["Baseline", "Original Peak", "Peak (baseline subtracted)", "Peak Area (baseline subtracted)"]
        ).T