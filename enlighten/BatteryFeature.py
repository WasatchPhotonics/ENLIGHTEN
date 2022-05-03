import logging

log = logging.getLogger(__name__)

##
# @todo track battery state in SpectrometerApplicationState to support multiple connected spectrometers
class BatteryFeature:

    def __init__(self,
                 lb_raw,
                 lb_parsed):

        self.lb_raw    = lb_raw 
        self.lb_parsed = lb_parsed

        self.raw = None
        self.perc = 100
        self.charging = False

        self.observers = set()

    def register_observer(self, callback):
        self.observers.add(callback)

    def unregister_observer(self, callback):
        try:
            self.observers.remove(callback)
        except:
            pass

    def process_reading(self, spec, reading):
        if reading.battery_raw is None:
            return

        self.raw = reading.battery_raw
        self.perc = reading.battery_percentage
        self.charging = reading.battery_charging

        self._update_labels(reading)
        for cb in self.observers:
            cb(self.perc, self.charging)

    def _update_labels(self, reading):
        self.lb_raw.setText("0x%06x" % reading.battery_raw)
        self.lb_parsed.setText("Battery (%.2f%%, %s)" % (
            self.perc, "charging" if self.charging else "discharging"))
