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

        format_int = lambda i: f"{int(i):,}" if str(i) != "--" else "--"

        header = []
        values = []

        # firstonly(i, "some string") will only have a value if i==0
        firstonly = lambda i, v: v if not i else None

        for i in range(self.count):
            x = self.get_widget_from_name("x_"+str(i)).value()
            left = self.get_widget_from_name("Left_"+str(i)).value()
            right = self.get_widget_from_name("Right_"+str(i)).value()

            start = x-left
            end = x+right

            self.plot(
                # here it is used so we only add one legend entry per multiplexed variable
                title=firstonly(i, "x"),
                color="red",
                x=[x, x],
                y=[min(spectrum), max(spectrum)],
            )

            self.plot(
                title=firstonly(i, "Range"),
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
                interpolated_baseline = sub_spectrum[0]*(1-j) + sub_spectrum[-1]*j

                self.plot(
                    title=firstonly(i, "Baseline"),
                    color="orange",
                    x=[start, end],
                    y=[sub_spectrum[0], sub_spectrum[-1]],
                )

                peak = spectrum[self.to_pixel(x)]

                peak_region = spectrum[start_pixel:end_pixel]

                # similar but different from the above calculation for interpolated_baseline
                # this time we are generating and rasterize the entire slanted local baseline 
                # the 'x' in this section is strictly in pixel space
                j = lambda x: x/(end_pixel-start_pixel) # given offset from start_pixel, produce unitless interpolation factor [0, 1]
                LB = lambda j: (sub_spectrum[0]*(1-j) + sub_spectrum[-1]*j) # given unitless interpolation factor, produce height of local baseline
                peak_region_subtracted = [peak_region[x]-LB(j(x)) for x in range(len(peak_region))]

                area = np.trapz(peak_region_subtracted, self.get_axis()[start_pixel:end_pixel])
            else:
                interpolated_baseline = "--"
                area = "--"
        
            header += [
                "%i: Baseline" % i,
                "%i: Original Peak" % i, 
                "%i: Peak (baseline subtracted)" % i, 
                "%i: Peak Area (baseline subtracted)" % i
            ]

            subtracted = peak - interpolated_baseline if str(interpolated_baseline) != "--" else -1

            values += [ format_int(interpolated_baseline), format_int(peak), format_int(subtracted), format_int(area) ]

            def set_meta(key, value):
                self.metadata[f"{self.name}.{key}.{i}"] = value

            set_meta("Baseline", interpolated_baseline)
            set_meta("OriginalPeak", peak)
            set_meta("PeakBaselineSubtracted", subtracted)
            set_meta("Area", area)

            # keep input parameters in metadata
            set_meta("Left", left)
            set_meta("Right", right)
            set_meta("x", x)

        self.table = pd.DataFrame(
            values,
            index = header
        ).T

