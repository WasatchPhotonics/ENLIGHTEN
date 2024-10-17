import numpy as np
import scipy.stats 
import logging

from EnlightenPlugin import EnlightenPluginBase

log = logging.getLogger(__name__)

class StatsBuffer(EnlightenPluginBase):
    """
    This is similar to the Analysis.Stats plugin, but adds additional statistics
    (mode, median, stdev) which require that a buffer of recent spectra be cached
    in memory.  

    Allows the user to set the history size, and displays the buffer size as it 
    fills.

    Allows the computed median to be exported back to ENLIGHTEN as the next 
    potential dark measurement, meaning that you can use this to generate a
    true "median dark" (which some spectroscopists prefer to "averaged dark").
    """

    def get_configuration(self):
        self.name = "Buffered Statistics"
        self.series_names = ["Min", "Max", "Mean", "Median", "Mode", "Sigma.lo", "Sigma.hi"]

        for name in self.series_names:
            self.field(name=name, datatype=bool, initial=True, direction="input", tooltip="Display {name}")

        self.field(name="History", direction="input", datatype=int, minimum=3, maximum=1000, initial=50, tooltip="Number of historical spectra retained for statistics")
        self.field(name="Filled", datatype=int, initial=0, tooltip="Portion of potential history currently populated")
        self.field(name="Export Median", datatype=bool, initial=False, direction="input", tooltip="Allow 'Store Dark' to use computed median (also add column to CSV)")
        self.field(name="Clear", datatype="button", callback=self.reset, tooltip="Clear history")

        self.block_enlighten = True

        self.reset()

    def process_request(self, request):
        self.series = {}
        self.outputs = {}
        self.metadata = {}
        self.overrides = {}
        try:
            spectrum = np.array(request.processed_reading.processed, dtype=np.float32)
            history = request.fields["History"]

            if self.metrics is None:
                self.metrics = Metrics(spectrum, history)
            else:
                self.metrics.update(spectrum, history)

            for name, y_values in zip(self.series_names, [ 
                    self.metrics.min,       # YOU MUST KEEP THIS
                    self.metrics.max,       # LIST SYNCHRONIZED
                    self.metrics.mean,      # WITH SELF.SERIES_NAMES
                    self.metrics.median,    
                    self.metrics.mode,     
                    self.metrics.sigma_lo, 
                    self.metrics.sigma_hi ]):
                if request.fields[name] and y_values is not None: 
                    self.plot(title=name, y=y_values)

            if request.fields["Export Median"]:
                self.overrides["recordable_dark"] = self.metrics.median  
                self.metadata["MedianDark"] = self.metrics.median        

            self.outputs = { "Filled": self.metrics.height() }
        except:
            log.error("something went awry", exc_info=1)
            self.reset()

    def reset(self):
        self.metrics = None

class Metrics:
    def __init__(self, spectrum, history):
        self.reset()
        self.update(spectrum, history)

    def reset(self):
        self.data     = None
        self.min      = None
        self.max      = None
        self.mean     = None
        self.median   = None
        self.mode     = None
        self.sigma_hi = None
        self.sigma_lo = None

    def update(self, spectrum, history):
        self.history = history

        if self.width() != len(spectrum):
            self.reset()

        self.resize()

        if self.data is None:
            self.data = np.array(spectrum, dtype=np.float32)
        else:
            self.data = np.vstack((self.data, spectrum))

        self.compute()

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
            log.debug(f"shape after deleting rows {rows_to_delete}: %s", str(self.data.shape))

    def compute(self):
        if self.height() < 2:
            return

        self.min    = np.amin         (self.data, axis=0)
        self.max    = np.amax         (self.data, axis=0)
        self.mean   = np.mean         (self.data, axis=0)
        self.median = np.median       (self.data, axis=0)
        self.stdev  = np.std          (self.data, axis=0)
        self.mode   = scipy.stats.mode(self.data, axis=0)[0]
        self.sigma_hi = self.mean + self.stdev
        self.sigma_lo = self.mean - self.stdev

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
