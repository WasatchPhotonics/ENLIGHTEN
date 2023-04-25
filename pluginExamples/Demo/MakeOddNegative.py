import numpy as np
import logging

from EnlightenPlugin import EnlightenPluginBase,    \
                            EnlightenPluginResponse, \
                            EnlightenPluginConfiguration

log = logging.getLogger(__name__)

## negate alternating intensities
class MakeOddNegative(EnlightenPluginBase):

    def get_configuration(self):
        return EnlightenPluginConfiguration(
            name = "Negate Odd", 
            has_other_graph = True,
            series_names = ["Odd Negative"])

    def connect(self, enlighten_info):
        return super().connect(enlighten_info)

    def process_request(self, request):
        spectrum = request.processed_reading.processed 
        return EnlightenPluginResponse(request,
            series  = { 
                "Odd Negative": [ i if i % 2 == 0 else i * -1 for i in spectrum ]
            } 
        )

    def disconnect(self):
        super().disconnect()
