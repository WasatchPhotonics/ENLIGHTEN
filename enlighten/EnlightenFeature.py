from enlighten import common

import logging

if common.use_pyside2():
    from PySide2.QtGui import QColor
    from PySide2.QtCore import Qt
else:
    from PySide6.QtGui import QColor
    from PySide6.QtCore import Qt

log = logging.getLogger(__name__)

class EnlightenFeature:

    all_features = set()

    @staticmethod
    def get_all():
        return list(EnlightenFeature.all_features)

    def __init__(self, ctl):
        # keep a handle to the Controller to access all the other Business Objects
        self.ctl = ctl

        feature_name = type(self).__name__
        self.log_header(f"instantiating {feature_name}")

        EnlightenFeature.all_features.add(self)

    def post_init(self):
        """
        May be called by Controller after ALL BusinessObjects / EnlightenFeatures
        have been constructed.
        """
        pass

    def update_visibility(self):
        """
        Called by the Controller when there is reason to update the visibility 
        (show/hide the whole thing, or perhaps tweak the set of supported 
        features) of one or more Business Objects.

        A good example is when a new spectrometer connects, or the user selects
        a different spectrometer from the list of connected spectrometers. It
        may be that the old spectrometer had a laser, but the new spectrometer
        does not, so LaserControlFeature should disappear. Or perhaps the old
        laser had a power calibration, but the new one does not, so power setting
        should change from mW to duty cycle.
        """
        pass
        
    def process(self, pr):
        """
        Called by the Controller when a new ProcessedReading needs to be 
        processed. Not all EnlightenFeatures operate on ProcessedReadings,
        so not all need to impement this method.
        """
        pass

    def init_hotplug(self, spec):
        """
        Some Business Objects may need to know if a spectrometer has just 
        been connected for the first time (has not yet been seen this session),
        and needs "initialization" of some sort.
        """
        pass

    def log_header(self, msg):
        log.debug("")
        log.debug("=" * len(msg))
        log.debug(msg)
        log.debug("=" * len(msg))
        log.debug("")

        self.ctl.splash.showMessage(f"version {common.VERSION}\n\n{msg}\n", alignment=Qt.AlignHCenter | Qt.AlignBottom, color=QColor("#ccc"))
        self.ctl.app.processEvents()
