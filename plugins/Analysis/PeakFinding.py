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
        self.field(name="Width",      direction="input",  datatype=int, initial=  5, maximum= 200, minimum=0, step= 10)
        self.field(name="Distance",   direction="input",  datatype=int, initial= 10, maximum= 200, minimum=0, step= 10)
        self.field(name="Prominence", direction="input",  datatype=int, initial=200, maximum=5000, minimum=0, step=100)

        self.field(name="Peak Count", direction="output", datatype=int)
        self.field(name="Peak Table", direction="output", datatype="pandas")
        self.field(name="Transpose",  direction="input",  datatype=bool, initial=True)

    def process_request(self, request):
        pr          = request.processed_reading
        processed   = pr.get_processed()
        wavelengths = pr.get_wavelengths()
        wavenumbers = pr.get_wavenumbers()
        pixels      = pr.get_pixel_axis()

        # find x-coordinates of peaks in pixel space 
        (peak_x, _) = scipy.signal.find_peaks(
            processed, 
            width      = request.fields["Width"],
            distance   = request.fields["Distance"],
            prominence = request.fields["Prominence"])

        peak_y = [ processed[x] for x in peak_x ]

        # convert to wavelength and wavenumber space
        peak_cm = None
        peak_nm = [ wavelengths[x] for x in peak_x ]
        peak_px = [ pixels[x] for x in peak_x ] # handle horizontal ROI

        if wavenumbers is None:
            dataframe = pd.DataFrame( [ peak_px,         peak_nm,    peak_y ],
                              index = [ "pixel", "wavelength (nm)", "intensity" ])
        else:
            peak_cm = [ wavenumbers[x] for x in peak_x ] 
            dataframe = pd.DataFrame( [ peak_px,         peak_nm,            peak_cm,      peak_y ],
                              index = [ "pixel", "wavelength (nm)", "Raman shift (cm⁻¹)", "intensity" ])

        dataframe = dataframe.round(2)
        if request.fields["Transpose"]:
            dataframe = dataframe.T

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

        self.outputs = { "Peak Table": dataframe,    # for table
                         "Peak Count": len(peak_x) } # for widget
