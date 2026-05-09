from EnlightenPlugin import EnlightenPluginBase

class EventHooks(EnlightenPluginBase):
    """ Demonstration plugin showing how to hook into enlighten.measurement.MeasurementFactory events """

    def get_configuration(self):
        self.counts = {
            "save": 0,
            "load": 0
        }
        self.last_id = None

        self.field(name="Save Count", datatype=int, direction="output")
        self.field(name="Load Count", datatype=int, direction="output")
        self.field(name="Last ID",    datatype=str, direction="output")

        self.ctl.measurement_factory.register_observer(self.save_callback, "save")
        self.ctl.measurement_factory.register_observer(self.load_callback, "load")

    def disconnect(self):
        self.ctl.measurement_factory.unregister_observer(self.save_callback, "save")
        self.ctl.measurement_factory.unregister_observer(self.load_callback, "load")
        super().disconnect()

    def process_request(self, request):
        self.outputs["Save Count"] = self.counts["save"]
        self.outputs["Load Count"] = self.counts["load"]
        self.outputs["Last ID"] = self.last_id

    def save_callback(self, measurement):
        self.last_id = measurement.measurement_id
        self.counts["save"] += 1

    def load_callback(self, measurement):
        self.last_id = measurement.measurement_id
        self.counts["load"] += 1
