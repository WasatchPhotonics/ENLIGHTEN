import logging

from enlighten import common
from enlighten.EnlightenFeature import EnlightenFeature

if common.use_pyside2():
    from PySide2 import QtCore
else:
    from PySide6 import QtCore

log = logging.getLogger(__name__)

class ProgressBarFeature(EnlightenFeature):

    def __init__(self, ctl):
        super().__init__(ctl)

        cfu = ctl.form.ui
        self.pb = cfu.readingProgressBar

        self.visible = False
        self.value = 0

        self.timer = QtCore.QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.tick)
        self.timer.start(1000)

    def tick(self):
        # default to 1Hz
        next_check_ms = 1000

        self.visible = self.value < 0 or self.value > 0

        # log.debug(f"tick: visible {self.visible}, value {self.value}")

        if not self.visible:
            self.pb.setVisible(False)
        else:
            if self.value < 0:
                # unbounded "busy" animation
                self.pb.setVisible(True)
                self.pb.setRange(0, 0)
            else:
                # round to int 0-100
                self.pb.setRange(0, 100)
                self.value = int(min(100, max(0, round(self.value, 0))))
                
                if self.value == 0:
                    # hide immediately on zero
                    self.visible = False
                    self.pb.setVisible(False)
                else:
                    self.pb.setValue(self.value)
                    self.pb.setVisible(True)

                    if self.value >= 100:
                        # hide on the NEXT tick
                        log.debug("tick: hide on next")
                        self.value = 0
                    else: 
                        # tick at 4Hz above 1%, below 100%
                        next_check_ms = 250

        self.timer.start(next_check_ms)

    def show_continuous(self):
        log.debug("show continuous")
        self.set(-1)

    def hide(self):
        log.debug("hiding")
        self.set(0)

    def set(self, value):
        """ 
        Can be called from outside GUI thread.
        New settings get applied on next tick.
        """
        if value != self.value:
            # log.debug(f"set: {value}")
            self.value = value
