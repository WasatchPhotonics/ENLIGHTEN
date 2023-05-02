import numpy as np
import logging

from EnlightenPlugin import EnlightenPluginBase,        \
                            EnlightenPluginField,       \
                            EnlightenPluginResponse,    \
                            EnlightenPluginConfiguration

log = logging.getLogger(__name__)

##
# Adds min, max and mean series to the ENLIGHTEN scope.
#
# @todo "stitch" spectra from multiple spectrometer ranges? would require 
#       tracking x-coord of each pixel, in all 3 axes?
class Stats(EnlightenPluginBase):

    def get_configuration(self):
        return EnlightenPluginConfiguration(
            name         = "Statistics", 
            fields       = [ EnlightenPluginField(name="Reset", datatype="button", callback=self.reset) ],
            series_names = ["Stats.Min", "Stats.Max", "Stats.Mean"])

    def connect(self, enlighten_info):
        super().connect(enlighten_info)
        self.reset()
        return True

    def process_request(self, request):
        spectrum = request.processed_reading.processed
        if self.metrics is None:
            self.metrics = Metrics(spectrum)
        else:
            try:
                self.metrics.update(spectrum)
            except:
                log.error("Unable to update Stats", exc_info=1)
                self.metrics = Metrics(spectrum)
        return EnlightenPluginResponse(request, series = {
            "Stats.Min" : self.metrics.min,
            "Stats.Max" : self.metrics.max,
            "Stats.Mean": self.metrics.mean})

    def disconnect(self):
        super().disconnect()

    def reset(self):
        self.metrics = None

class Metrics:
    def __init__(self, spectrum):
        self.cnt  = 1
        self.min  = np.array(spectrum, dtype=np.float32)
        self.max  = np.array(spectrum, dtype=np.float32)
        self.sum  = np.array(spectrum, dtype=np.float64) 
        self.mean = np.array(spectrum, dtype=np.float32)

    ## 
    # @todo consider dividing both sum and cnt by 10 if cnt == 1e15, providing 
    #       essentially limitless runtime (with gradual loss of precision)
    def update(self, spectrum):
        self.cnt += 1 
        self.min  = np.minimum(self.min, spectrum)
        self.max  = np.maximum(self.max, spectrum)
        self.sum  = np.add(self.sum, spectrum)
        self.mean = self.sum / self.cnt
