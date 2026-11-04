import logging

from EnlightenPlugin import EnlightenPluginBase

log = logging.getLogger(__name__)

class MakeOddNegative(EnlightenPluginBase):
    """ Demonstrate graph possibilities by negating alternating intensities. """

    def get_configuration(self):
        # uncomment this for 2nd graph:
        # self.has_other_graph = True
        pass

    def process_request(self, request):
        spectrum = request.processed_reading.processed 
        self.plot(
            title = "Odd Negative",
            y = [ i if i % 2 == 0 else i * -1 for i in spectrum ]
        )
