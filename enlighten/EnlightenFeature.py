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
    """
    This is the (relatively new) Abstract Base Class (ABC) for virtually all 
    business objects in ENLIGHTEN.

    Should probably consider having this inherit from some QObject thing to
    provide access to slots and signals, and probably allow more convenient
    dispatch to the GUI thread.
    """

    ############################################################################
    # static members
    ############################################################################

    all_features = set() 

    @staticmethod
    def get_all():
        return list(EnlightenFeature.all_features)

    ############################################################################
    # lifecycle
    ############################################################################

    def __init__(self, ctl):
        # keep a handle to the Controller to access all the other Business Objects
        self.ctl = ctl
        self.observers = {} # event -> set
        self._feature_name = type(self).__name__

        self.log_header(f"instantiating {self._feature_name}")

        EnlightenFeature.all_features.add(self)

    def disconnect(self):
        pass

    def post_init(self):
        """
        May be called by Controller after ALL BusinessObjects / EnlightenFeatures
        have been constructed.
        """
        pass

    def init_hotplug(self):
        """
        Some Business Objects may need to know if a spectrometer has just 
        been connected for the first time (has not yet been seen this session),
        and needs "initialization" of some sort.
        """
        pass

    ############################################################################
    # ENLIGHTEN runtime
    ############################################################################

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

        **This method should always be called on the GUI thread.**
        """
        pass
        
    def process(self, pr):
        """
        Called by the Controller when a new ProcessedReading needs to be 
        processed. Not all EnlightenFeatures operate on ProcessedReadings,
        so not all need to impement this method.
        """
        pass

    ############################################################################
    # Observers
    ############################################################################

    def register_observer(self, callback, event=None):
        if event not in self.observers:
            self.observers[event] = set()
        self.observers[event].add(callback)
        log.debug(f"registering {self._feature_name} event {event} --> callback {callback}")

    def unregister_observer(self, callback, event=None):
        if event in self.observers:
            self.observers[event].discard(callback)

    def notify_observers(self, event=None):
        if event in self.observers:
            for callback in self.get_observers(event):
                callback()

    def notify_observers_with_value(self, value, event=None):
        if event in self.observers:
            for callback in self.get_observers(event):
                callback(value)

    def get_observers(self, event=None):
        return self.observers[event]

    ############################################################################
    # utility
    ############################################################################

    def log_header(self, msg):
        log.debug("")
        log.debug("=" * len(msg))
        log.debug(msg)
        log.debug("=" * len(msg))
        log.debug("")

        self.ctl.splash.showMessage(f"version {common.VERSION}\n\n{msg}\n", alignment=Qt.AlignHCenter | Qt.AlignBottom, color=QColor("#ccc"))
        self.ctl.app.processEvents()
