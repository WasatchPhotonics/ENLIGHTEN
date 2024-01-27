import logging

from enlighten import common

if common.use_pyside2():
    from PySide2 import QtCore
else:
    from PySide6 import QtCore

log = logging.getLogger(__name__)

##
# Provides a generic ramp that ticks a callback with ascending/descending value
# at a specified rate.
class Ramp:

    def __init__(self, callback, name="unknown"):

        self.callback = callback
        self.name     = name

        self.running = False
        self.timer = QtCore.QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.tick)

    def start(self, start_value, end_value, seconds):
        if start_value == end_value or seconds <= 0:
            log.error("invalid Ramp %s", self.name)
            self.running = False
            return

        self.start_value = start_value
        self.end_value   = end_value

        self.value     = self.start_value
        self.ascending = end_value > start_value
        self.delay_ms  = int(float(seconds * 1000) / abs(end_value - start_value))

        log.debug("Ramp[%s]: starting (delay_ms %d)", self.name, self.delay_ms)
        self.running   = True
        self.timer.start(self.delay_ms)

    def stop(self):
        if self.running:
            log.debug("Ramp[%s]: stopped", self.name)
            self.running = False

    def tick(self):
        log.debug("Ramp[%s]: ticked (value %d)", self.name, self.value)
        if not self.running:
            return

        # handle endpoint U-turn
        if self.ascending and self.value >= self.end_value:
            self.ascending = False
            self.value = self.end_value
        elif not self.ascending and self.value <= self.start_value:
            self.ascending = True
            self.value = self.start_value

        # send the moving value back to the caller
        self.callback(self.value)

        # advance the value
        if self.ascending:
            self.value += 1
        else:
            self.value -= 1

        # schedule the next tick
        self.timer.start(self.delay_ms)
