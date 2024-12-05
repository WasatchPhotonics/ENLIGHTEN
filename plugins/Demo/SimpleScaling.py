import logging

from EnlightenPlugin import EnlightenPluginBase

class SimpleScaling(EnlightenPluginBase):
    """
    Simple plug-in to scale the current spectrum.  Demonstrates floating-point 
    inputs.  Also shows adding a second trace to the main graph.
    """

    def get_configuration(self):
        self.name = "Scaling"
        self.field(name="Factor", datatype="float", initial=2, maximum=15, minimum=-5, step=0.25, direction="input")
            series_names = ["Scaled"])

    def process_request(self, request):
        scale_factor = request.fields["Factor"]
        spectrum = request.processed_reading.processed
        scaled = [ i * scale_factor for i in spectrum ]
        self.plot(title="Scaled", { 'y': scaled })
