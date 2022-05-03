import platform
import logging
import os

from EnlightenPlugin import EnlightenPluginBase,    \
                            EnlightenPluginField,    \
                            EnlightenPluginResponse,  \
                            EnlightenPluginConfiguration

log = logging.getLogger(__name__)

##
# A simple plug-in to display a vignetted (cropped) segment of a spectrum.
# The purpose is to demonstrate input fields.
class SegmentSpectrum(EnlightenPluginBase):

    def __init__(self):
        super().__init__()

    def get_configuration(self):
        fields = []

        fields.append(EnlightenPluginField(name="Start",     datatype="int",    direction="input",  maximum=2048))
        fields.append(EnlightenPluginField(name="End",       datatype="int",    direction="input",  maximum=2048, initial=200))
        fields.append(EnlightenPluginField(name="Length",    datatype="int",    direction="output"))
        fields.append(EnlightenPluginField(name="Click Me!", datatype="button", direction="input",  callback=self.button_callback))

        return EnlightenPluginConfiguration(name            = "Segment", 
                                            fields          = fields,
                                            has_other_graph = True, 
                                            graph_type      = 'xy',
                                            series_names    = ["Segment"],
                                            x_axis_label    = "Data Point")
    def connect(self, enlighten_info):
        super().connect(enlighten_info)
        return True

    def button_callback(self):
        if "Windows" in platform.platform():
            # open the Device Manager, just for funz
            os.system("devmgmt.msc")

    def process_request(self, request):
        spectrum = request.processed_reading.processed
        start = int(request.fields["Start"])
        end   = int(request.fields["End"])

        # in case the user switched the order
        if start > end:
            (start, end) = (end, start)

        start = min(start, len(spectrum))
        end   = min(end,   len(spectrum))
        
        outputs = { "Length": end - start }
        series  = { 
            "Segment": {
                'x': list(range(start, end)),
                'y': spectrum[start:end]
            }
        }

        return EnlightenPluginResponse(request, series=series, outputs=outputs)

    def disconnect(self):
        super().disconnect()
