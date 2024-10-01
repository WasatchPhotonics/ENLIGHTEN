import logging
import numpy as np
import math

from EnlightenPlugin import EnlightenPluginBase,    \
                            EnlightenPluginField,    \
                            EnlightenPluginResponse,  \
                            EnlightenPluginConfiguration

log = logging.getLogger(__name__)

##
# A simple plug-in adding a scaled sine wave to the main graph.  Purpose is to 
# demonstrate persistence (state) in plugin; also use of input checkbox.
class SineAndScale(EnlightenPluginBase):

    def __init__(self, ctl):
        super().__init__(ctl)

        self.sin_progress = 0

    def get_configuration(self):
        self.name = "Sine Wave"
        self.field(name="Step",  datatype="float", direction="input", initial=2, maximum=30, minimum=-30, step=5)
        self.field(name="Negate", datatype="bool", direction="input")

    def connect(self):
        super().connect()
        return True

    def process_request(self, request):
        sine_step    = request.fields["Step"]
        negate       = request.fields["Negate"]
        
        spectrum     = request.processed_reading.processed

        hi = max(spectrum)
        lo = min(spectrum)
        rng = hi - lo

        sin_data = np.array(list(range(len(spectrum)))) # 0...1024
        sin_data = sin_data / len(spectrum)             # 0..1
        sin_data = sin_data * 2 * math.pi               # 0..2pi
        increment = sin_data[int(abs(sine_step))] - sin_data[0] 

        if sine_step < 0:
            increment *= -1

        if negate:
            increment *= -1

        self.sin_progress += increment
        sin_data = sin_data + self.sin_progress
        sine_wave = np.sin(sin_data)
        sine_wave = sine_wave * rng / 2.0
        sine_wave = sine_wave + (lo + rng / 2.0)

        self.plot(y=sine_wave, title="Sine Wave", color="yellow")

    def disconnect(self):
        super().disconnect()
