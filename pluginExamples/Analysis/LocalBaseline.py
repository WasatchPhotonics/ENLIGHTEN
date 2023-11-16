import pandas as pd
import numpy as np

import time

from EnlightenPlugin import *

# firstonly(i, "some string") will only have a value if i==0
# this is a workaround to prevent duplicate legend entries
firstonly = lambda i, v: v if not i else None


class LocalBaseline(EnlightenPluginBase):

    def get_configuration(self):
        self.name = "Baseline"

        self.count = 4

        for i in range(self.count):
            self.field(
                name = "x_"+str(i),
                initial = 0, minimum = -10000, maximum = 10000, step = .2,
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

    # duplicate function to support <4.0.15, see pluginExamples/EnlightenPlugin.py
    def get_axis_short_name(self):
        if self.ctl.form.ui.displayAxis_comboBox_axis.currentIndex() == common.Axes.WAVELENGTHS:
            return "wl"
        if self.ctl.form.ui.displayAxis_comboBox_axis.currentIndex() == common.Axes.WAVENUMBERS:
            return "wn"
        if self.ctl.form.ui.displayAxis_comboBox_axis.currentIndex() == common.Axes.PIXELS:
            return "px"

    # duplicate function to support <4.0.15
    def get_axis_name(self):
        if self.ctl.form.ui.displayAxis_comboBox_axis.currentIndex() == common.Axes.WAVELENGTHS:
            return "wavelengths"
        if self.ctl.form.ui.displayAxis_comboBox_axis.currentIndex() == common.Axes.WAVENUMBERS:
            return "wavenumbers"
        if self.ctl.form.ui.displayAxis_comboBox_axis.currentIndex() == common.Axes.PIXELS:
            return "pixels"

    def interp_inverse(self, y, xp, fp):
        # find the first fractional pixel that yields `target_value` when used to interpolate `array`

        # for monotonically increasing sample points this is equivalent to solving for x in the following
        # np.interp(x, xp fp) == y

        # this function does not use np.interp, and it does not require input data to be monotonically increasing

        # first find the index i such that the values of fp straddle y:
        for i in range(len(fp)-1):
            if fp[i] <= y < fp[i+1] or fp[i] >= y > fp[i+1]:
                # solve for the fractional component
                f = (y-fp[i])/(fp[i+1]-fp[i])

                # interpolate the domain using (i, f)
                return xp[i]*(1-f) + xp[i+1]*f

    def process_request(self, request):
        pr = request.processed_reading
        spectrum = pr.get_processed()

        # if given a number: produce formated number (ex: 1,000,000)
        # if given a string: it's a placeholder, just return it
        format_int = lambda i: f"{int(i):,}" if type(i) != str else i
        format_float = lambda i: f"{float(i):,.2f}" if type(i) != str else i

        header = []
        values = []

        for i in range(self.count):
            x = self.get_widget_from_name("x_"+str(i)).value()

            # turn off annotations for placeholder values 0, -1
            if x <= 0:
                continue

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
            if end_pixel > start_pixel and end > start and sub_spectrum:

                j = (x-start)/(end-start)
                interpolated_baseline = sub_spectrum[0]*(1-j) + sub_spectrum[-1]*j

                self.plot(
                    title=firstonly(i, "Baseline"),
                    color="orange",
                    x=[start, end],
                    y=[sub_spectrum[0], sub_spectrum[-1]],
                )

                peak = spectrum[self.to_pixel(x)]

                peak_region = spectrum[start_pixel:end_pixel+1]

                # similar but different from the above calculation for interpolated_baseline
                # this time we are generating and rasterize the entire slanted local baseline
                # the 'x' in this section is strictly in pixel space
                j = lambda x: x/(end_pixel-start_pixel) # given offset from start_pixel, produce unitless interpolation factor [0, 1]
                LB = lambda j: (sub_spectrum[0]*(1-j) + sub_spectrum[-1]*j) # given unitless interpolation factor, produce height of local baseline
                peak_region_subtracted = [peak_region[x]-LB(j(x)) for x in range(len(peak_region))]

                area = np.trapz(peak_region_subtracted, self.get_axis()[start_pixel:end_pixel+1])

                peak_baseline_subtracted = peak - interpolated_baseline

            else:
                peak = "--"
                interpolated_baseline = "--"
                area = "--"
                peak_baseline_subtracted = "--"

            header = [
                "Baseline",
                "Original Peak",
                "Peak",
                "Peak Area",
            ]
            values += [[
                format_int(interpolated_baseline),
                format_int(peak),
                format_int(peak_baseline_subtracted),
                format_int(area),
            ]]
            self.metadata["Baseline_"+str(i)] = interpolated_baseline
            self.metadata["OriginalPeak_"+str(i)] = peak
            self.metadata["PeakBaselineSubtracted_"+str(i)] = peak_baseline_subtracted
            self.metadata["Area_"+str(i)] = area

            # keep input parameters in metadata
            self.metadata["Left_"+str(i)] = self.get_widget_from_name("Left_"+str(i)).value()
            self.metadata["Right_"+str(i)] = self.get_widget_from_name("Right_"+str(i)).value()
            self.metadata["x_"+str(i)] = self.get_widget_from_name("x_"+str(i)).value()

        self.table = pd.DataFrame(
                [header]+values
        )

