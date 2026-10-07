import numpy as np
import logging

from EnlightenPlugin import EnlightenPluginBase

log = logging.getLogger(__name__)

class PixelNoise(EnlightenPluginBase):
    """
    A common operation is to characterize detector noise by taking 100 dark 
    measurements, computing the standard deviation over time for each pixel, then 
    taking the average for all pixels.
    
    This plugin simply generalizes that, allowing the user to pick their own number
    of measurements (history buffer size).  Note that this doesn't enforce a 
    requirement that the spectra must be "dark".
    """

    def get_configuration(self):
        self.name = "Pixel Noise"

        self.field(name="History", direction="input", datatype="int", minimum=10, maximum=1000, initial=100, tooltip="Number of spectra retained for noise computation")
        self.field(name="Filled",  datatype="int",    initial=0,   tooltip="Portion of potential history currently populated")
        self.field(name="Mean",    datatype="float",  precision=2, tooltip="Average noise over all pixels over time")
        self.field(name="Median",  datatype="float",  precision=2, tooltip="Median noise over all pixels over time")
        self.field(name="Stdev",   datatype="float",  precision=2, tooltip="Standard deviation of noise over all pixels over time")
        self.field(name="Min",     datatype="float",  precision=2, tooltip="Minimum noise of any pixel over time")
        self.field(name="Max",     datatype="float",  precision=2, tooltip="Maximum noise of any pixel over time")
        self.field(name="IQR",     datatype="bool",   direction="input", callback=self.iqr_callback, tooltip="Use interquartile of history for each pixel")
        self.field(name="Clear",   datatype="button", callback=self.reset, tooltip="Clear history")

        self.reset()

    def process_request(self, request):
        spectrum = np.array(request.processed_reading.get_processed(), dtype=np.float32)
        history = request.fields["History"]
        iqr = request.fields["IQR"]

        if self.metrics is None:
            self.metrics = Metrics(spectrum, history, iqr)
        else:
            self.metrics.update(spectrum, history, iqr)

        self.outputs = { "Mean"  : self.metrics.mean,
                         "Median": self.metrics.median,
                         "Stdev" : self.metrics.stdev,
                         "Min"   : self.metrics.min,
                         "Max"   : self.metrics.max,
                         "Filled": self.metrics.height() }

    def reset(self):
        self.metrics = None

    def iqr_callback(self):
        if self.metrics is None:
            return
        b = self.get_widget_from_name(self, "IQR")
        if b.isChecked() != self.metrics.iqr:
            self.metrics = None

class Metrics:
    def __init__(self, spectrum, history, iqr):
        self.reset()
        self.iqr = iqr
        self.update(spectrum, history, iqr)

    def reset(self):
        log.debug("resetting Metrics")
        self.data = None
        self.iqr = False
        self.min = 0
        self.max = 0
        self.mean = 0
        self.stdev = 0
        self.median = 0

    def update(self, spectrum, history, iqr):
        self.history = history

        self.resize()

        if self.data is None or self.width() != len(spectrum):
            self.data = np.array(spectrum, dtype=np.float32)
        else:
            self.data = np.vstack((self.data, spectrum))

        ########################################################################
        # compute the stdev of each pixel over time
        ########################################################################

        # if IQR selected, take the middle half of each pixel's SORTED history
        if iqr and self.height() > 4:
            qtr = int(self.height() / 4)

            # start with pixel 0
            values = self.data[:, 0]
            new_data = np.sort(values)[qtr:-qtr] 

            # now append rest of pixels as new rows
            for px in range(1, self.width()):
                values = np.sort(self.data[:, px])
                new_data = np.vstack((new_data, values[qtr:-qtr]))

            # now rotate whole thing 270deg to again make pixels the major (horizontal) axis (retaining pixel 0 as pixel 0 for consistency)
            new_data = np.rot90(new_data, k=3)
        else:
            # we're not doing IQR, or we don't have enough data to extract a middle half
            new_data = self.data.copy()

        # compute the (sample) standard deviation of the selected data (IQR or otherwise)
        stdev = 0 if self.height() < 2 else np.std(new_data, axis=1)

        # generate secondary metrics of the per-pixel standard deviations (across the detector)
        self.mean   = np.mean(stdev) 
        self.median = np.median(stdev)
        self.stdev  = np.std (stdev) # stdev of the stdevs
        self.min    = np.min (stdev)
        self.max    = np.max (stdev)

    ##
    # Pops oldest row if we're full, or truncates more if history was reduced,
    # but in either case leaves us with at least one slot to append the latest
    # spectrum.
    def resize(self):
        if self.data is None:
            return
        h = self.height()
        if h == self.history:
            self.data = np.delete(self.data, 0, axis=0) # pop oldest
            log.debug("shape after popping: %s", str(self.data.shape))
        elif h > self.history:
            rows_to_delete = np.arange(h - self.history + 1)
            self.data = np.delete(self.data, rows_to_delete, axis=0)
            log.debug("shape after readjusting: %s", str(self.data.shape))

    def width(self):
        if self.data is None:
            return 0
        if len(self.data.shape) == 1:
            return self.data.shape[0]
        return self.data.shape[1]

    def height(self):
        if self.data is None:
            return 0
        if len(self.data.shape) == 1:
            return 1
        return self.data.shape[0]
