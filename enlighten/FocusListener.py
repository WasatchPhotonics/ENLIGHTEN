##
# This class is currently used by ThumbnailWidget to detect when the user has
# tabbed or clicked out of an "open edit" QLineEdit.
#
# @todo it would seem slightly more efficient if we actually disconnected the
#       signal in unregister(), and reconnect in register
class FocusListener(object):

    def __init__(self, app):
        self.callbacks = {}
        app.focusChanged.connect(self.on_focus_changed)

    def on_focus_changed(self, old, new):
        if not self.callbacks or old not in self.callbacks:
            return

        f = self.callbacks[old]
        self.unregister(old)
        f()

    def register(self, widget, callback):
        self.callbacks[widget] = callback

    def unregister(self, widget):
        if widget in self.callbacks:
            del self.callbacks[widget]
