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
            name = "Left",
            initial = 10, minimum = 0, maximum = 10000, step = .2,
            datatype = "float", direction = "input"
        )        
        
        self.field(
            name = "Right",
            initial = 10, minimum = 0, maximum = 10000, step = .2,
            datatype = "float", direction = "input"
        )

        self.field(
            name = "Center",
            datatype = "button",
            callback = self.center
        )

        self.has_other_graph = False
        self.block_enlighten = True # for metadata

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
        left = self.get_widget_from_name("Left").value()
        right = self.get_widget_from_name("Right").value()

        start = x-left
        end = x+right

        self.plot(
            title="x",
            color="red",
            x=[x, x],
            y=[min(spectrum), max(spectrum)],
        )

        self.plot(
            title="Range",
            color="blue",
            x=[start, start],
            y=[min(spectrum), max(spectrum)],
        )
        self.plot(
            color="blue",
            x=[end, end],
            y=[min(spectrum), max(spectrum)],
        )

        start_pixel = self.to_pixel(start)
        end_pixel = self.to_pixel(end)

        sub_spectrum = list(spectrum[start_pixel:end_pixel+1])
        if sub_spectrum:

            i = (x-start)/(end-start)
            interpolated_baseline = sub_spectrum[0]*(1-i) + sub_spectrum[-1]*i

            self.plot(
                title="Baseline",
                color="orange",
                x=[start, end],
                y=[sub_spectrum[0], sub_spectrum[-1]],
            )

        peak = spectrum[self.to_pixel(x)]

        #peak_region = spectrum[left_end_pixel:right_start_pixel]
        #peak_region_subtracted = [x-interpolated_baseline for x in peak_region]
        #area = np.trapz(peak_region_subtracted, self.get_axis()[left_end_pixel:right_start_pixel])
        
        format_int = lambda i: f"{int(i):,}"

        self.table = pd.DataFrame(
            [ format_int(interpolated_baseline), format_int(peak), format_int(peak - interpolated_baseline), "--" ],
            index = ["Baseline", "Original Peak", "Peak (baseline subtracted)", "Peak Area (baseline subtracted)"]
        ).T

        self.metadata["Baseline"] = interpolated_baseline
        self.metadata["OriginalPeak"] = peak
        self.metadata["PeakBaselineSubtracted"] = peak - interpolated_baseline
        self.metadata["Area"] = "--"

        # keep input parameters in metadata
        self.metadata["Left"] = self.get_widget_from_name("Left").value()
        self.metadata["Right"] = self.get_widget_from_name("Right").value()
        self.metadata["x"] = self.get_widget_from_name("x").value()
        self.metadata["x unit"] = self.get_axis_name()
