import logging
import pandas as pd
import scipy

from EnlightenPlugin import EnlightenPluginBase

log = logging.getLogger(__name__)

class PeakFinding(EnlightenPluginBase):
    """
    A sample ENLIGHTEN Plug-in which performs peakfinding on each received spectrum, 
    displaying an xy scatterplot of peak pixel and intensity, with a table.
    """
    def get_configuration(self):
        self.name = "Peakfinding"
        self.auto_enable = True
        self.auto_enable = True
        self.field(name="Prominence", direction="input",  datatype=float, initial=200, maximum=200000, minimum=0, step=1)
        self.field(name="Peak Count", direction="output", datatype=int)
        self.field(name="Peak Table", direction="output", datatype="pandas")
        self.field(name="Transpose",  direction="input",  datatype=bool, initial=True)

    def process_request(self, request):
        pr          = request.processed_reading
        processed   = pr.get_processed()
        wavelengths = pr.get_wavelengths()
        wavenumbers = pr.get_wavenumbers()
        settings    = request.settings
        prom        = request.fields['Prominence']

        # use scipy peakfinding to find x-coordinates of peaks in pixel space 
        (peak_x, _) = scipy.signal.find_peaks(processed, prominence=prom)
        peak_y = [ processed[x] for x in peak_x ]

        # convert to wavelength and wavenumber space
        peak_cm = None
        peak_nm = [ wavelengths[x] for x in peak_x ]
        peak_cm = [ wavenumbers[x] for x in peak_x ] if wavenumbers is not None else None

        # Pandas DataFrame to display peaks in QTableView
        dataframe = pd.DataFrame( [ peak_x,          peak_nm,            peak_cm,      peak_y ],
                          index = [ "pixel", "wavelength (nm)", "Raman shift (cm⁻¹)", "intensity" ])
        dataframe = dataframe.round(2)
        if request.fields["Transpose"]:
            dataframe = dataframe.T

        unit = self.ctl.graph.get_x_axis_unit()
        if   unit == "nm": x_vals = peak_nm
        elif unit == "cm": x_vals = peak_cm
        else             : x_vals = peak_x

        lo = min(processed)
        for y, x in zip(peak_y, x_vals):
            self.plot(y=(lo, y), x=(x, x))

        self.outputs = { "Peak Table": dataframe,    # for table
                         "Peak Count": len(peak_x) } # for widget
