import pandas as pd
import numpy as np
import logging

import time

from EnlightenPlugin import *

log = logging.getLogger(__name__)

class LocalBaseline(EnlightenPluginBase):

    def get_configuration(self):
        self.name = "Baseline"

        self.field(
            name = "x",
            initial = 1014, minimum = -10000, maximum = 10000, step = .2,
            datatype = "float", direction = "input"
        )
        
        self.field(
            name = "Peak Neighborhood",
            initial = 3, minimum = 0, maximum = 10000, step = .2,
            datatype = "float", direction = "input"
        )

        self.field(
            name = "Baseline Extent",
            initial = 10, minimum = 0, maximum = 10000, step = .2,
            datatype = "float", direction = "input"
        )

        self.field(
            name = "Center",
            datatype = "button",
            callback = self.center
        )

        self.is_blocking = False
        self.has_other_graph = False

    def center(self):

        # PySide2.QtWidgets.QDoubleSpinBox
        x_widget = self.get_widget_from_name("x")

        x_pix = self.to_pixel(x_widget.value())
        for i in range(100):
            x_pix_n = x_pix-1+max(enumerate(self.spectrum[x_pix-1:x_pix+1+1]), key=lambda P: P[1])[0]
            if x_pix_n == x_pix:
                break
            x_pix = x_pix_n
        x_widget.setValue(self.to_graph(x_pix))

    def process_request(self, request):
        pr = request.processed_reading
        spectrum = pr.get_processed()

        x = self.get_widget_from_name("x").value()
        inner_radius = self.get_widget_from_name("Peak Neighborhood").value()
        outer_radius = self.get_widget_from_name("Baseline Extent").value()

        left_start = x-inner_radius-outer_radius
        left_end = x-inner_radius
        right_start = x+inner_radius
        right_end = x+inner_radius+outer_radius

        self.plot(
            title="x",
            color="red",
            x=[x, x],
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

        left_start_pixel = self.to_pixel(left_start)
        left_end_pixel = self.to_pixel(left_end)
        right_start_pixel = self.to_pixel(right_start)
        right_end_pixel = self.to_pixel(right_end)

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

        peak = spectrum[self.to_pixel(x)]
        peak_region = spectrum[left_end_pixel:right_start_pixel]
        peak_region_subtracted = [x-mean_baseline for x in peak_region]
        area = np.trapz(peak_region_subtracted, self.get_axis()[left_end_pixel:right_start_pixel])
        self.table = pd.DataFrame(
            [ f"{mean_baseline:.2f}", f"{peak:.2f}", f"{peak - mean_baseline:.2f}", f"{area:.2f}" ],
            index = ["Baseline", "Original Peak", "Peak (baseline subtracted)", "Peak Area (baseline subtracted)"]
        ).T