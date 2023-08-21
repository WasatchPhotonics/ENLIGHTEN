import numpy as np
import logging

from EnlightenPlugin import *

log = logging.getLogger(__name__)

class LockSettings(EnlightenPluginBase):
    """
    A copy of the Analysis.Stats plugin, but showing how a plugin can lock various
    standard ENLIGHTEN features.
    """

    def get_configuration(self):
        self.name = "Lock Settings"
        self.field(name="Reset", datatype="button", callback=self.reset)
        self.reset()

        self.ctl.gain_db_feature.set_locked(True)
        self.ctl.laser_control.set_locked(True)

    def process_request(self, request):
        spectrum = request.processed_reading.processed

        if self.metrics is None:
            self.metrics = Metrics(spectrum)
        else:
            try:
                self.metrics.update(spectrum)
            except:
                log.error("Unable to update Stats", exc_info=1)
                self.reset()

        self.plot(title="Stats.Min", y=self.metrics.min)
        self.plot(title="Stats.Max", y=self.metrics.max)
        self.plot(title="Stats.Avg", y=self.metrics.avg)

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
        if self.cnt == 1e15:
            self.cnt /= 10
            self.sum /= 10
        self.cnt += 1 
        self.min = np.minimum(self.min, spectrum)
        self.max = np.maximum(self.max, spectrum)
        self.sum = np.add(self.sum, spectrum)
        self.avg = self.sum / self.cnt
