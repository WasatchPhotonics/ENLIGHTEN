import logging
from datetime import datetime

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
        self.colors = [ '#0097ff', 
                        '#0fd207', 
                        '#e9ff06', 
                        '#ffb507', 
                        '#ff4d21' ]
        self.frames = 0
        self.start_time = datetime.now()

        # for quick wipe
        self.cache_integ_time = 10
        self.wipe_enabled = False
        self.wiping = False

        # self.field(name="Length", direction="input", datatype=int, minimum=1, maximum=20, initial=5, tooltip="Number of spectra in tail")

        self.field(name="Reset", datatype="button", callback=self.reset, tooltip="Clear history")
        self.field(name="Frames", datatype=int, tooltip="Frames since reset")
        self.field(name="Time", datatype=str, tooltip="Time since reset")

        self.field(name="Quick Wipe", datatype=bool, direction="input", tooltip=f"Quickly wipe detector by generating throwaway reads ot minimum integration time after a reset")
        self.field(name="Wipe Count", datatype=int , direction="input", initial=20, minimum=1, maximum=250, tooltip="How many throwaways to generate")

        self.field(name="Max Mag",  datatype=float, precision=2, direction="output")
        self.field(name="Area",     datatype=float, precision=2, direction="output")
        self.field(name="Abs Area", datatype=float, precision=2, direction="output")

    def process_request(self, request):
        spec = request.spec
        spectrum = request.processed_reading.get_processed()
        self.wipe_enabled = request.fields["Quick Wipe"]

        length = 5 # request.fields["Length"]

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
            pen = self.ctl.gui.make_pen(widget="tail", color=self.colors[len(self.curves)])
            curve.setPen(pen)
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

        self.update_metrics(request)

        self.frames += 1

        if self.wiping:
            if self.frames > request.fields["Wipe Count"]:
                self.stop_wipe()

    def update_metrics(self, request):
        spectrum = request.processed_reading.get_processed()
        dark = request.processed_reading.get_dark()

        self.outputs["Frames"] = self.frames
        self.outputs["Time"] = str(datetime.now() - self.start_time)

        if dark is None:
            return

        total = 0
        abs_total = 0
        max_mag = 0
        for i in range(len(spectrum)):
            mag = abs(spectrum[i])
            total += spectrum[i]
            abs_total += mag
            max_mag = max(max_mag, mag)

        self.outputs["Area"] = total / len(spectrum)
        self.outputs["Abs Area"] = abs_total / len(spectrum)
        self.outputs["Max Mag"] = max_mag


    def reset(self):
        # for i in range(len(curves)):
        #     self.ctl.graph.set_data(self.curves[i], x=[], y=[])
        self.frames = 0
        self.start_time = datetime.now()
        self.start_wipe()

    def stop_wipe(self):
        log.debug("trying to stop wipe")
        if not self.wiping:
            return
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return

        spec.change_device_setting("integration_time_ms", self.cache_integ_time)
        log.debug(f"finished fast wipe (count {self.frames})")
        self.wiping = False

    def start_wipe(self):
        self.wiping = False
        if not self.wipe_enabled:
            return

        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return

        log.debug("starting fast wipe")
        self.cache_integ_time = spec.settings.state.integration_time_ms
        spec.change_device_setting("integration_time_ms", spec.settings.eeprom.min_integration_time_ms)
        self.wiping = True
