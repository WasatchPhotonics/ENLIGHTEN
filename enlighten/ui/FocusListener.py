import logging

log = logging.getLogger(__name__)

##
# This class is currently used by ThumbnailWidget to detect when the user has
# tabbed or clicked out of an "open edit" QLineEdit.
#
# @todo it would seem slightly more efficient if we actually disconnected the
#       signal in unregister(), and reconnect in register
class FocusListener(object):

    def __init__(self, ctl):
        self.callbacks = {}
        ctl.app.focusChanged.connect(self.on_focus_changed)

    def on_focus_changed(self, old, new):
        if not self.registered(old):
            return

        f = self.callbacks[old]
        f()
        self.unregister(old)

    def register(self, widget, callback):
        self.callbacks[widget] = callback

    def unregister(self, widget):
        if self.registered(widget):
            del self.callbacks[widget]

    def registered(self, widget):
        ok = widget in self.callbacks
        return ok
