import logging
from EnlightenPlugin import EnlightenPluginBase

log = logging.getLogger(__name__)

class Tail(EnlightenPluginBase):
    """
    Adds a configurable spectral "tail" showing history.

    @todo properly delete curves when history size reduced
    @todo understand QTimer warning in error log
    @todo add disconnect to delete curves
    @todo auto-color "fade" based on assigned Spectrometer color
    @todo support multiple spectrometers
    """

    def get_configuration(self):
        self.name = "Tail"
        self.block_enlighten = True 
        self.curves = []
        self.data = []

        self.field(name="Length", direction="input", datatype=int, minimum=1, maximum=20, initial=5, tooltip="Number of spectra in tail")
        self.field(name="Clear", datatype="button", callback=self.reset, tooltip="Clear history")

    def process_request(self, request):
        spec = request.spec
        spectrum = request.processed_reading.get_processed()
        length = request.fields["Length"]

        # if length reduced, delete extra curves
        while len(self.curves) > length:
            curve = self.curves.pop()
            log.debug(f"removing tail curve {curve.name}")
            self.ctl.graph.set_data(curve, x=[], y=[])
            self.ctl.graph.remove_curve(name=curve.name)

        # if length grew, add extra curves
        while len(self.curves) < length:
            name = f"{spec.settings.eeprom.serial_number}-tail-{len(self.curves)}"
            log.debug(f"adding curve {name}")
            curve = self.ctl.graph.add_curve(name=name, rehide=False, in_legend=False)
            self.curves.append(curve)

        # pop oldest history
        while len(self.data) > length:
            self.data.pop()

        # add new history
        x = self.get_axis(processed_reading=request.processed_reading)
        self.data.insert(0, (x, spectrum))

        # update curves with shifted history
        for i in range(len(self.curves)):
            curve = self.curves[i]
            x = []
            y = []
            if i < len(self.data):
                x = self.data[i][0]
                y = self.data[i][1]
            self.ctl.graph.set_data(curve, x=x, y=y)

    def reset(self):
        for i in range(len(curves)):
            self.ctl.graph.set_data(self.curves[i], x=[], y=[])
