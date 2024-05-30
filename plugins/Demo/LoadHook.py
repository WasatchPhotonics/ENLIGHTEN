import logging

from EnlightenPlugin import EnlightenPluginBase

log = logging.getLogger(__name__)

class LoadHook(EnlightenPluginBase):
    """ Demostration plugin showing how to hook into ENLIGHTEN's "load" event. """

    def get_configuration(self):
        self.counter = 0
        self.field(name="Load Count", datatype="int", direction="output")
        self.event("load", self.load_callback)

    def process_request(self, request):
        self.output("Load Count", self.counter)

    def load_callback(self, measurement):
        self.counter += 1
