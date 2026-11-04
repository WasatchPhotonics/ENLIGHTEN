from EnlightenPlugin import EnlightenPluginBase

class Buttons(EnlightenPluginBase):
    """ Demonstration plugin showing how to create buttons and callbacks. """

    def get_configuration(self):
        self.field(name="counter",   direction="output", datatype=int, initial=0, tooltip="How many times 'increment' was clicked")
        self.field(name="increment", datatype="button",  callback=self.increment)
        self.field(name="reset",     datatype="button",  callback=self.reset)
        self.reset()

    def process_request(self, request):
        self.outputs["counter"] = self.counter

    def increment(self):
        self.counter += 1

    def reset(self):
        self.counter = 0
