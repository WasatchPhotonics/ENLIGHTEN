import logging

from scipy.signal import savgol_filter

from EnlightenPlugin import *

log = logging.getLogger(__name__)

class SavitzkyGolay(EnlightenPluginBase):
    """
    This plugin applies the Savitzky-Golay smoothing algorithm on the current 
    spectrum.  It does not add an additional "smoothed" graph line, and instead
    actively smooths the "standard" spectrum, much as if you used Boxcar 
    Smoothing or Scan Averaging to smooth the spectrum.

    The main advantage of Savitzky-Golay over a simple "boxcar" is that it tries
    to preserve peak intensity (height).

    Parameters:
    - Half-Width is defined the same as in Boxcar Smoothing for consistency:
      the number of pixels to the left and right of each "smoothed" pixel which
      will be used in the moving window convolved across the spectrum. Lower
      values will provide less smoothing, and higher values will provide more
      smoothing (at the cost of lost detail).  A half-width of 5 means the
      actual window will be 11 (5 pixels to either side, plus the central pixel).
    - Poly Order is the polynomial order (a 2nd-order polynomial will use 3 
      coefficients).

    For insight into other parameters see scipy.signal.savgol_filter documentation.

    @see https://en.wikipedia.org/wiki/Savitzky%E2%80%93Golay_filter
    @see https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.savgol_filter.html
    """
    def get_configuration(self):
        self.name = "Savitzky-Golay"

        self.field(name="Half-Width",  datatype="int",   minimum=1,   maximum=50,   initial=5,             direction="input", tooltip="Window will be n*2 - 1")
        self.field(name="Poly Order",  datatype="int",   minimum=0,   maximum=7,    initial=2,             direction="input", tooltip="Polynomial order for the fit")
        self.field(name="Deriv Order", datatype="int",   minimum=0,   maximum=7,    initial=0,             direction="input", tooltip="Deriviative order (optional)")
        self.field(name="Delta",       datatype="float", minimum=0.1, maximum=10.0, initial=1.0, step=0.1, direction="input", tooltip="Sample spacing (optional)")

        self.has_other_graph = False
        self.block_enlighten = True 

        self.overrides = {}

    def process_request(self, request):
        win_len   = self.get_widget_from_name("Half-Width").value() * 2 + 1
        polyorder = min(self.get_widget_from_name("Poly Order").value(), win_len - 1)
        deriv     = self.get_widget_from_name("Deriv Order").value()
        delta     = self.get_widget_from_name("Delta").value()

        smoothed = savgol_filter(
            x             = request.processed_reading.processed,
            window_length = win_len,    # < len(x)
            polyorder     = polyorder,  # < win_len
            deriv         = deriv,      #  # >= 0
            delta         = delta)      #  # spacing if delta>1, default 1

        return EnlightenPluginResponse(request, overrides = { "processed": smoothed } )
