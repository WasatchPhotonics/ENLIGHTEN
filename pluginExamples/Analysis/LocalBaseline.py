import pandas as pd
import numpy as np
import logging

import time

from EnlightenPlugin import *

log = logging.getLogger(__name__)

class LocalBaseline(EnlightenPluginBase):

    def get_configuration(self):
        self.name = "Baseline"

        self.count = 4

        for i in range(self.count):
            self.field(
                name = "x_"+str(i),
                initial = 1014, minimum = -10000, maximum = 10000, step = .2,
                datatype = "float", direction = "input"
            )
            
            self.field(
                name = "Left_"+str(i),
                initial = 10, minimum = 0, maximum = 10000, step = .2,
                datatype = "float", direction = "input"
            )        
            
            self.field(
                name = "Right_"+str(i),
                initial = 10, minimum = 0, maximum = 10000, step = .2,
                datatype = "float", direction = "input"
            )

            self.field(
                name = "Center_"+str(i),
                datatype = "button",
                callback = self.center_fn(i)
            )

        self.has_other_graph = False
        self.block_enlighten = True # for metadata

    def center_fn(self, i):
        def center():
            # PySide2.QtWidgets.QDoubleSpinBox
            x_widget = self.get_widget_from_name("x_"+str(i))

            x_pix = self.to_pixel(x_widget.value())
            for j in range(100):
                x_pix_n = x_pix-1+max(enumerate(self.spectrum[x_pix-1:x_pix+1+1]), key=lambda P: P[1])[0]
                if x_pix_n == x_pix:
                    break
                x_pix = x_pix_n
            x_widget.setValue(self.to_graph(x_pix))
        return center

    def process_request(self, request):
        pr = request.processed_reading
        spectrum = pr.get_processed()

        interpolated_baseline = []
        peak = []
        area = []

        for i in range(self.count):
            x = self.get_widget_from_name("x_"+str(i)).value()
            left = self.get_widget_from_name("Left_"+str(i)).value()
            right = self.get_widget_from_name("Right_"+str(i)).value()

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

                j = (x-start)/(end-start)
                interpolated_baseline.append(sub_spectrum[0]*(1-j) + sub_spectrum[-1]*j)

                self.plot(
                    title="Baseline",
                    color="orange",
                    x=[start, end],
                    y=[sub_spectrum[0], sub_spectrum[-1]],
                )

                peak.append(spectrum[self.to_pixel(x)])

                peak_region = spectrum[start_pixel:end_pixel]

                # similar but different from the above calculation for interpolated_baseline
                # this time we are generating and rasterize the entire slanted local baseline 
                # the 'x' in this section is strictly in pixel space
                j = lambda x: x/(end_pixel-start_pixel) # given offset from start_pixel, produce unitless interpolation factor [0, 1]
                LB = lambda j: (sub_spectrum[0]*(1-j) + sub_spectrum[-1]*j) # given unitless interpolation factor, produce height of local baseline
                peak_region_subtracted = [peak_region[x]-LB(j(x)) for x in range(len(peak_region))]

                area.append(np.trapz(peak_region_subtracted, self.get_axis()[start_pixel:end_pixel]))
            else:
                interpolated_baseline.append("--")
                area.append("--")
        
        format_int = lambda i: f"{int(i):,}"

        header = []
        values = []
        for i in range(self.count):
            header += [
                "%i: Baseline" % i,
                "%i: Original Peak" % i, 
                "%i: Peak (baseline subtracted)" % i, 
                "%i: Peak Area (baseline subtracted)" % i
            ]
            values += [ format_int(interpolated_baseline[i]), format_int(peak[i]), format_int(peak[i] - interpolated_baseline[i]), format_int(area[i]) ]
            self.metadata["Baseline_"+str(i)] = interpolated_baseline[i]
            self.metadata["OriginalPeak_"+str(i)] = peak[i]
            self.metadata["PeakBaselineSubtracted_"+str(i)] = peak[i] - interpolated_baseline[i]
            self.metadata["Area_"+str(i)] = area[i]

            # keep input parameters in metadata
            self.metadata["Left_"+str(i)] = self.get_widget_from_name("Left_"+str(i)).value()
            self.metadata["Right_"+str(i)] = self.get_widget_from_name("Right_"+str(i)).value()
            self.metadata["x_"+str(i)] = self.get_widget_from_name("x_"+str(i)).value()

        self.table = pd.DataFrame(
            values,
            index = header
        ).T

