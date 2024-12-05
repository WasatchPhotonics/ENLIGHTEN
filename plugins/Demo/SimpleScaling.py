import logging

from EnlightenPlugin import EnlightenPluginBase

class SimpleScaling(EnlightenPluginBase):
    """
    Simple plug-in to scale the current spectrum.  Demonstrates floating-point 
    inputs.  Also shows adding a second trace to the main graph.
    """

    def get_configuration(self):
        self.name = "Scaling"
        self.field(name="Factor", datatype=float, initial=2, maximum=15, minimum=-5, step=0.25, direction="input")

    def process_request(self, request):
        pr = request.processed_reading
        scale_factor = request.fields["Factor"]

        spectrum = pr.get_processed()
        scaled = [ i * scale_factor for i in spectrum ]

        x_axis = self.get_axis(processed_reading=pr)
        self.plot(title="Scaled", y=scaled, x=x_axis)
