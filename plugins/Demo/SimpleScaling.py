import logging

from EnlightenPlugin import EnlightenPluginBase,        \
                            EnlightenPluginField,       \
                            EnlightenPluginResponse,    \
                            EnlightenPluginConfiguration

log = logging.getLogger(__name__)

##
# Simple plug-in to scale the current spectrum.  Demonstrates floating-point 
# inputs.  Also shows adding a second trace to the main graph.
class SimpleScaling(EnlightenPluginBase):

    def get_configuration(self):
        return EnlightenPluginConfiguration(
            name         = "Scaling", 
            fields       = [ EnlightenPluginField(name="Factor", datatype="float", initial=2, maximum=15, minimum=-5, step=0.25, direction="input") ],
            series_names = ["Scaled"])

    def connect(self):
        super().connect()
        return True

    def process_request(self, request):
        scale_factor = request.fields["Factor"]
        spectrum = request.processed_reading.processed
        scaled = [ i * scale_factor for i in spectrum ]
        series = {
            "Scaled": {
                'y': scaled
            }
        }
        return EnlightenPluginResponse(request=request, series=series)

    def disconnect(self):
        super().disconnect()
