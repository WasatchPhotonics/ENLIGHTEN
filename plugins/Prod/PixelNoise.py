import numpy as np
import logging

from EnlightenPlugin import EnlightenPluginBase,    \
                            EnlightenPluginField,    \
                            EnlightenPluginResponse,  \
                            EnlightenPluginConfiguration

log = logging.getLogger(__name__)

##
# A common operation is to characterize "detector noise" by taking 100 dark 
# measurements, computing the standard deviation over time for each pixel, then 
# taking the average for all pixels.
#
# This plugin simply generalizes that, allowing the user to pick their own number
# of measurements (history buffer size).  Note that this doesn't enforce a 
# requirement that the spectra must be "dark" (capped).
class PixelNoise(EnlightenPluginBase):

    def get_configuration(self):
        fields = []

        fields.append(EnlightenPluginField(name="History", direction="input", datatype="int", minimum=10, maximum=1000, initial=100,
            tooltip="Number of spectra retained for noise computation"))

        fields.append(EnlightenPluginField(name="Filled", datatype="int", initial=0,
            tooltip="Portion of potential history currently populated"))

        fields.append(EnlightenPluginField(name="Mean", datatype="float", precision=2, 
            tooltip="Average noise over all pixels over time"))

        fields.append(EnlightenPluginField(name="Stdev", datatype="float", precision=2, 
            tooltip="Standard deviation of noise over all pixels over time"))

        fields.append(EnlightenPluginField(name="Min", datatype="float", precision=2, 
            tooltip="Minimum noise of any pixel over time"))

        fields.append(EnlightenPluginField(name="Max", datatype="float", precision=2, 
            tooltip="Maximum noise of any pixel over time"))

        fields.append(EnlightenPluginField(name="Clear", datatype="button", callback=self.reset,
            tooltip="Clear history"))

        return EnlightenPluginConfiguration(name="Pixel Noise", fields=fields)

    def connect(self):
        super().connect()
        self.reset()
        return True

    def process_request(self, request):
        spectrum = np.array(request.processed_reading.processed, dtype=np.float32)
        history = request.fields["History"]

        if self.metrics is None:
            self.metrics = Metrics(spectrum, history)
        else:
            self.metrics.update(spectrum, history)

        return EnlightenPluginResponse(request, outputs = {
            "Mean"  : self.metrics.mean,
            "Stdev" : self.metrics.stdev,
            "Min"   : self.metrics.min,
            "Max"   : self.metrics.max,
            "Filled": self.metrics.height() 
        })

    def disconnect(self):
        super().disconnect()

    def reset(self):
        self.metrics = None

class Metrics:
    def __init__(self, spectrum, history):
        self.reset()
        self.update(spectrum, history)

    def reset(self):
        self.data = None
        self.avg = 0
        self.min = 0
        self.max = 0
        self.stdev = 0

    def update(self, spectrum, history):
        self.history = history

        if self.width() != len(spectrum):
            self.reset()

        self.resize()

        if self.data is None:
            self.data = np.array(spectrum, dtype=np.float32)
        else:
            self.data = np.vstack((self.data, spectrum))

        # stdev of each pixel over time
        stdev = np.std(self.data, axis=0)

        self.mean   = np.mean(stdev)
        self.stdev  = np.std (stdev) # stdev of the stdev
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
