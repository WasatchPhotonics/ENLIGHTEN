import numpy as np
import logging

from scipy.signal import savgol_filter

from EnlightenPlugin import EnlightenPluginBase,    \
                            EnlightenPluginField,    \
                            EnlightenPluginResponse,  \
                            EnlightenPluginConfiguration

log = logging.getLogger(__name__)

class SavitzkyGolay(EnlightenPluginBase):

    def __init__(self):
        super().__init__()

    def get_configuration(self):
        fields = []
        fields.append(EnlightenPluginField(name="Half-Length", datatype="int", minimum=1, maximum=50, initial=2, direction="input",
            tooltip="Window will be n*2 - 1"))
        fields.append(EnlightenPluginField(name="Poly Order", datatype="int", minimum=0, maximum=7, initial=1, direction="input",
            tooltip="Polynomial order for the fit"))
        fields.append(EnlightenPluginField(name="Deriv Order", datatype="int", minimum=0, maximum=7, initial=0, direction="input",
            tooltip="Deriviative order (optional)"))
        fields.append(EnlightenPluginField(name="Delta", datatype="float", minimum=0.1, maximum=10.0, initial=1.0, step=0.1, direction="input",
            tooltip="Sample spacing (optional)"))
        return EnlightenPluginConfiguration(
            name = "Savitzky-Golay", 
            fields = fields,
            series_names = ["savgol"])

    def connect(self, enlighten_info):
        return super().connect(enlighten_info)

    def process_request(self, request):
        win_len   = request.fields["Half-Length"] * 2 - 1
        polyorder = max(request.fields["Poly Order"], win_len - 1)
        deriv     = request.fields["Deriv Order"]
        delta     = request.fields["Delta"]

        savgol = savgol_filter(
            request.processed_reading.processed, 
            window_length = win_len,
            polyorder     = polyorder,
            deriv         = deriv,
            delta         = delta)
        return EnlightenPluginResponse(request, series = { "savgol": savgol })

    def disconnect(self):
        super().disconnect()
