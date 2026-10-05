import logging
import pandas as pd
import numpy as np

from EnlightenPlugin import EnlightenPluginBase

log = logging.getLogger(__name__)

class LocalBaseline(EnlightenPluginBase):

    def get_configuration(self):

        self.name = "LocalBaseline"

        self.count = 1
        for i in range(self.count):
            self.field(name=f"x_{i}",      initial=1230, minimum=-10000, maximum=10000, step=0.2, datatype=float, direction="input")
            self.field(name=f"Left_{i}",   initial=38,   minimum=0,      maximum=10000, step=0.2, datatype=float, direction="input")
            self.field(name=f"Right_{i}",  initial=31.4, minimum=0,      maximum=10000, step=0.2, datatype=float, direction="input")
            self.field(name=f"Center_{i}", datatype="button", callback=self.center_fn(i))

        self.has_other_graph = False
        #self.block_enlighten = True # for metadata

        self.last_request = None

    def center_fn(self, i):
        """ 
        This method generates an anonymous function (closure) for the "Center" 
        button keypress event on a particular peak. 
        """
        def center():
            x_widget = self.get_widget_from_name(f"x_{i}")
            x_pix = self.to_pixel(x_widget.value())
            for j in range(100):
                x_pix_n = x_pix-1+max(enumerate(self.spectrum[x_pix-1:x_pix+1+1]), key=lambda P: P[1])[0]
                if x_pix_n == x_pix:
                    break
                x_pix = x_pix_n
            x_widget.setValue(self.to_graph(x_pix))

        return center

    def commas(self, n): 
        return "--" if n is None else f"{int(n):,}"

    def process_request(self, request):
        pr = request.processed_reading
        spectrum = pr.get_processed()

        # firstonly(i, "some string") will only have a value if i==0.
        # Used with self.plot to avoid over-defining the legend
        # this is pretty bad, @todo remove this
        # better to ignore repeat titles sent to self.plot
        firstonly = lambda i, v: v if not i else None

        # handle each peak for which we're computing local baseline
        values = []
        for i in range(self.count):
            x     = self.get_widget_from_name(f"x_{i}"    ).value()
            left  = self.get_widget_from_name(f"Left_{i}" ).value()
            right = self.get_widget_from_name(f"Right_{i}").value()

            start = x - left
            end   = x + right

            self.plot(title=firstonly(i, "x"), # only add one legend entry per multiplexed variable
                      color="red",
                      x=[x, x],
                      y=[min(spectrum), max(spectrum)])
            self.plot(title=firstonly(i, "Range"),
                      color="blue",
                      x=[start, start],
                      y=[min(spectrum), max(spectrum)])
            self.plot(color="blue",
                      x=[end, end],
                      y=[min(spectrum), max(spectrum)])

            start_pixel = self.to_pixel(start)
            end_pixel   = self.to_pixel(end)

            sub_spectrum = list(spectrum[start_pixel:end_pixel+1])

            interpolated_baseline = None
            peak = None
            peak_baseline_subtracted = None
            area = None
    
            if end_pixel > start_pixel and end > start and sub_spectrum:

                j = (x-start)/(end-start)
                interpolated_baseline = sub_spectrum[0]*(1-j) + sub_spectrum[-1]*j

                self.plot(title=firstonly(i, "Baseline"),
                          color="orange",
                          x=[start, end],
                          y=[sub_spectrum[0], sub_spectrum[-1]])

                peak = spectrum[self.to_pixel(x)]
                peak_region = spectrum[start_pixel:end_pixel+1]

                # Similar but different from the above calculation for 
                # interpolated_baseline. This time we are generating and 
                # rasterize the entire slanted local baseline. The 'x' in 
                # this section is strictly in pixel space.
                
                j = lambda x: x/(end_pixel-start_pixel) # given offset from start_pixel, produce unitless interpolation factor [0, 1]
                LB = lambda j: (sub_spectrum[0]*(1-j) + sub_spectrum[-1]*j) # given unitless interpolation factor, produce height of local baseline
                peak_region_subtracted = [peak_region[x]-LB(j(x)) for x in range(len(peak_region))]

                peak_baseline_subtracted = peak - interpolated_baseline
                area = np.trapz(peak_region_subtracted, self.get_axis()[start_pixel:end_pixel+1])

            # use comma formatting for the on-screen table
            values += [[ 
                self.commas(interpolated_baseline),
                self.commas(peak),
                self.commas(peak_baseline_subtracted),
                self.commas(area)
            ]]

            # don't use commas for metadata destined for CSV
            self.metadata[f"Baseline_{i}"] = interpolated_baseline
            self.metadata[f"OriginalPeak_{i}"] = peak
            self.metadata[f"PeakBaselineSubtracted_{i}"] = peak_baseline_subtracted
            self.metadata[f"Area_{i}"] = area

            # keep input parameters in metadata
            self.metadata[f"Left_{i}"]  = self.get_widget_from_name(f"Left_{i}") .value()
            self.metadata[f"Right_{i}"] = self.get_widget_from_name(f"Right_{i}").value()
            self.metadata[f"x_{i}"]     = self.get_widget_from_name(f"x_{i}")    .value()

        headers = [ "Baseline", "Original Peak", "Peak", "Peak Area" ]
        self.table = pd.DataFrame([headers] + values)

        self.last_request = request
