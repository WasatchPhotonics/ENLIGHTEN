import numpy as np
import logging

from EnlightenPlugin import EnlightenPluginBase

log = logging.getLogger(__name__)

class Stats(EnlightenPluginBase):
    """
    Adds min, max and mean series to the ENLIGHTEN scope.  All stats are on-going, 
    with a manual "reset" button to clear them.  

    See StatsBuffer for additional statistics which require keeping a buffer of 
    historical spectra in memory.

    @todo "stitch" spectra from multiple spectrometer ranges? would require 
          tracking x-coord of each pixel, in all 3 axes?
    """

    def get_configuration(self):
        self.name = "Statistics"
        self.field(name="Count", datatype=int, direction="output")
        self.field(name="Reset", datatype="button", callback=self.reset)
        self.reset()

    def process_request(self, request):
        spectrum = request.processed_reading.get_processed()

        if self.metrics is None:
            self.metrics = Metrics(spectrum)
        else:
            try:
                self.metrics.update(spectrum)
            except:
                log.error("Unable to update Stats", exc_info=1)
                self.reset()

        x_values = self.get_axis(processed_reading=request.processed_reading)
        self.plot(title="Stats.Min", y=self.metrics.min, x=x_values)
        self.plot(title="Stats.Max", y=self.metrics.max, x=x_values)
        self.plot(title="Stats.Avg", y=self.metrics.avg, x=x_values)
        self.outputs["Count"] = self.metrics.cnt

    def reset(self):
        self.metrics = None

class Metrics:
    def __init__(self, spectrum):
        self.cnt = 1
        self.min = np.array(spectrum, dtype=np.float32)
        self.max = np.array(spectrum, dtype=np.float32)
        self.avg = np.array(spectrum, dtype=np.float32)
        self.sum = np.array(spectrum, dtype=np.float64) 

    def update(self, spectrum):
        # rollover so sum can't exceed sys.float_info.max
        if self.cnt == 1e15:
            self.cnt = int(self.cnt / 10)
            self.sum /= 10.0
        self.cnt += 1 
        self.min = np.minimum(self.min, spectrum)
        self.max = np.maximum(self.max, spectrum)
        self.sum = np.add(self.sum, spectrum)
        self.avg = self.sum / self.cnt
