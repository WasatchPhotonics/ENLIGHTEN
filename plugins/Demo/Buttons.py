import logging

from EnlightenPlugin import EnlightenPluginBase

log = logging.getLogger(__name__)

class Buttons(EnlightenPluginBase):
    """ Demonstration plugin showing how to create buttons and callbacks. """

    def get_configuration(self):
        self.field(name="counter",   direction="output", datatype=int, initial=0, tooltip="How many times you've clicked 'increment'")
        self.field(name="increment", datatype="button",  callback=self.increment_callback)
        self.field(name="reset",     datatype="button",  callback=self.reset_callback)

        self.reset_callback()

    def process_request(self, request):
        self.output("counter", self.counter)

    def increment_callback(self):
        self.counter += 1

    def reset_callback(self):
        self.counter = 0
