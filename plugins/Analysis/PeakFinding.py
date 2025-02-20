import pandas as pd
import scipy
import logging

from EnlightenPlugin import EnlightenPluginBase

log = logging.getLogger(__name__)

class PeakFinding(EnlightenPluginBase):
    """
    A sample ENLIGHTEN Plug-in which performs peakfinding on each received spectrum, 
    displaying an xy scatterplot of peak pixel and intensity, with a table.
    """
    def get_configuration(self):
        self.name = "Peakfinding"
        self.multi_devices = True
        self.dataframe = None

        self.field(name="Width",      direction="input",  datatype=int, initial=  0, maximum=  200, minimum=0, step=  1, tooltip="scipy.signal.find_peaks.width: Required width of peaks in samples (datapoints, or pixels). (<1 to disable)") 
        self.field(name="Height",     direction="input",  datatype=int, initial=  0, maximum=50000, minimum=0, step=500, tooltip="scipy.signal.find_peaks.height: Required height of peaks. (<1 to disable)")
        self.field(name="Distance",   direction="input",  datatype=int, initial=  0, maximum=  200, minimum=0, step= 10, tooltip="scipy.signal.find_peaks.distance: Required minimal horizontal distance in samples (pixels) between neighbouring peaks. Smaller peaks are removed first until the condition is fulfilled for all remaining peaks. (<1 to disable)")
        self.field(name="Threshold",  direction="input",  datatype=int, initial=  0, maximum=30000, minimum=0, step=500, tooltip="scipy.signal.find_peaks.threshold: Required threshold of peaks, the vertical distance to its neighboring samples. (<1 to disable)")
        self.field(name="Prominence", direction="input",  datatype=int, initial=200, maximum= 5000, minimum=0, step=100, tooltip="scipy.signal.find_peaks.prominence: Required prominence of peaks. (<1 to disable)")

        self.field(name="Peak Count", direction="output", datatype=int)
        self.field(name="Peak Table", direction="output", datatype="pandas")
        self.field(name="Transpose",  direction="input",  datatype=bool, initial=True)

        self.field(name="Copy", datatype="button", callback=self.copy_to_clipboard, tooltip="Copy peaks to clipboard")

    def copy_to_clipboard(self):
        if self.dataframe is None:
            return
        self.ctl.clipboard.copy_dataframe(self.dataframe)

    def process_request(self, request):
        pr          = request.processed_reading
        processed   = pr.get_processed()
        wavelengths = pr.get_wavelengths()
        wavenumbers = pr.get_wavenumbers()
        pixels      = pr.get_pixel_axis()

        # find x-coordinates of peaks in pixel space 
        (peak_x, props) = scipy.signal.find_peaks(
            processed, 
            width      = request.fields["Width"     ] if request.fields["Width"     ] else None,
            height     = request.fields["Height"    ] if request.fields["Height"    ] else None,
            distance   = request.fields["Distance"  ] if request.fields["Distance"  ] else None,
            threshold  = request.fields["Threshold" ] if request.fields["Threshold" ] else None,
            prominence = request.fields["Prominence"] if request.fields["Prominence"] else None)
        log.debug(f"find_peaks -> peak_x {peak_x}, props {props}")

        peak_y = [ processed[x] for x in peak_x ]

        # convert to wavelength and wavenumber space
        peak_cm = None
        peak_nm = [ wavelengths[x] for x in peak_x ]
        peak_px = [ pixels[x] for x in peak_x ] # handle horizontal ROI

        if wavenumbers is None:
            self.dataframe = pd.DataFrame( [ peak_px,         peak_nm,    peak_y ],
                                   index = [ "pixel", "wavelength (nm)", "intensity" ])
        else:
            peak_cm = [ wavenumbers[x] for x in peak_x ] 
            self.dataframe = pd.DataFrame( [ peak_px,         peak_nm,            peak_cm,      peak_y ],
                                   index = [ "pixel", "wavelength (nm)", "Raman shift (cm⁻¹)", "intensity" ])

        self.dataframe = self.dataframe.round(2)
        if request.fields["Transpose"]:
            self.dataframe = self.dataframe.T

        unit = self.ctl.graph.get_x_axis_unit()
        if unit == "nm": 
            x_vals = peak_nm
        elif unit == "cm":
            x_vals = peak_cm
        else: 
            x_vals = peak_px

        self.series = {} # clear graph
        lo = min(processed)
        for y, x in zip(peak_y, x_vals):
            if   unit == "nm": title = f"{x:.2f}nm"
            elif unit == "cm": title = f"{x:.2f}cm⁻¹"
            else: title = f"{int(x)}px"

            self.plot(title=title, y=(lo, y), x=(x, x))
            log.debug(f"found peak at {x} {unit}")

        self.outputs = { "Peak Table": self.dataframe, # for table
                         "Peak Count": len(peak_x) }   # for widget
