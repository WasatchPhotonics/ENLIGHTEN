import platform
import logging
import os

from EnlightenPlugin import EnlightenPluginBase

log = logging.getLogger(__name__)

class SegmentSpectrum(EnlightenPluginBase):
    """
    A simple plug-in to display a cropped segment of a spectrum.
    The purpose is to demonstrate input fields.
    """

    def get_configuration(self):
        self.field(name="Start",     datatype="int",    direction="input",  maximum=2048)
        self.field(name="End",       datatype="int",    direction="input",  maximum=2048, initial=200)
        self.field(name="Length",    datatype="int",    direction="output")
        self.field(name="Click Me!", datatype="button", direction="input",  callback=self.button_callback)

        self.has_other_graph = True
        self.graph_type      = 'xy'
        self.x_axis_label    = "Data Point"
        self.y_axis_label    = "💥 Not Photons ⚠️"

    def button_callback(self):
        """ open the Device Manager, just for funz """
        if "Windows" in platform.platform():
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
        
        self.output("Length", end - start)
        self.plot(title="Segment",
                  x=list(range(start, end)),
                  y=spectrum[start:end])
