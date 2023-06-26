import numpy as np
import logging

from scipy.signal import savgol_filter

from EnlightenPlugin import *

log = logging.getLogger(__name__)

class SavitzkyGolay(EnlightenPluginBase):
    """
    Note that this plug-in updates the processed spectrum in-place, rather than 
    adding a different graph line.
    """
    def get_configuration(self):
        self.name = "Savitzky-Golay"

        self.field(name="Half-Length", datatype="int",   minimum=1,   maximum=50,   initial=5,             direction="input", tooltip="Window will be n*2 - 1")
        self.field(name="Poly Order",  datatype="int",   minimum=0,   maximum=7,    initial=2,             direction="input", tooltip="Polynomial order for the fit")
        self.field(name="Deriv Order", datatype="int",   minimum=0,   maximum=7,    initial=0,             direction="input", tooltip="Deriviative order (optional)")
        self.field(name="Delta",       datatype="float", minimum=0.1, maximum=10.0, initial=1.0, step=0.1, direction="input", tooltip="Sample spacing (optional)")

        self.has_other_graph = False
        self.block_enlighten = True 

        self.overrides = {}

    def process_request(self, request):
        win_len   = self.get_widget_from_name("Half-Length").value() * 2 + 1
        polyorder = min(self.get_widget_from_name("Poly Order").value(), win_len - 1)
        deriv     = self.get_widget_from_name("Deriv Order").value()
        delta     = self.get_widget_from_name("Delta").value()

        smoothed = savgol_filter(
            x             = request.processed_reading.processed 
            window_length = win_len,    # < len(x)
            polyorder     = polyorder,  # < win_len
            deriv         = deriv,      #  # >= 0
            delta         = delta)      #  # spacing if delta>1, default 1

        return EnlightenPluginResponse(request, overrides = { "processed": smoothed } )
