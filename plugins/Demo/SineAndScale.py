import numpy as np
import math

from EnlightenPlugin import EnlightenPluginBase

class SineAndScale(EnlightenPluginBase):
    """
    A simple plug-in adding a scaled sine wave to the main graph.  Purpose is to 
    demonstrate persistence (state) in plugin; also use of input checkbox.
    """

    def get_configuration(self):
        self.name = "Sine Wave"
        self.auto_enable = True

        self.field(name="Step",  datatype="float", direction="input", initial=10, maximum=100, minimum=-100, step=10)
        self.field(name="Negate", datatype="bool", direction="input")

        self.sin_progress = 0

    def process_request(self, request):
        sine_step = request.fields["Step"]
        negate    = request.fields["Negate"]
        
        spectrum = request.processed_reading.get_processed()
        if self.get_axis_short_name() == "wl":
            x = request.processed_reading.get_wavelengths()
        elif self.get_axis_short_name() == "wn":
            x = request.processed_reading.get_wavenumbers()
        else:
            x = request.processed_reading.get_pixel_axis()

        hi = max(spectrum)
        lo = min(spectrum)
        rng = hi - lo

        sin_data = np.array(list(range(len(x))))    # 0...1024
        sin_data = sin_data / len(spectrum)         # 0..1
        sin_data = sin_data * 2 * math.pi           # 0..2pi
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

        self.plot(x=x, y=sine_wave, title="Sine Wave", color="yellow")
