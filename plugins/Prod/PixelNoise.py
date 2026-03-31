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
        self.field(name="IQR",     datatype="bool",   direction="input", callback=self.iqr_callback, tooltip="Use interquartile instead of full detector")
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

        if iqr:
            qtr = int(len(spectrum)/4)
            spectrum = sorted(spectrum)[qtr:-qtr]

        if self.data is None or self.width() != len(spectrum):
            self.data = np.array(spectrum, dtype=np.float32)
        else:
            self.data = np.vstack((self.data, spectrum))

        # stdev of each pixel over time
        stdev = 0 if self.height() < 2 else np.std(self.data, axis=1)

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
