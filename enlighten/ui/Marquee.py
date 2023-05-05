import webbrowser

from PySide2 import QtCore, QtGui, QtWidgets

from enlighten import util

import logging

log = logging.getLogger(__name__)

##
# Encapsulate access to the "message display area" atop the right-hand side of 
# the Scope Capture screen.  Messages are normally flashed for 3sec and then 
# removed.  If 'persist' is set, message will remain until overwritten.
#
# Also provides a button-less notification box that auto-fades over 2sec.
class Marquee:
    
    ORIG_HEIGHT = 36

    DRAWER_DURATION_MS = 3000
    TOAST_DURATION_MS  = 3000
    TOAST_FADE_STEP_MS =   75
    TOAST_FADE_STEP_OPACITY_PERCENT = 0.05  # fade x% of original opacity each step

    def __init__(self, 
            app,
            bt_close,
            form,        # needed for Toast parent
            frame,
            inner,
            label,
            stylesheets):
        self.app         = app
        self.bt_close    = bt_close
        self.form        = form
        self.frame       = frame
        self.inner       = inner
        self.label       = label
        self.stylesheets = stylesheets

        self.height = Marquee.ORIG_HEIGHT

        self.hide()

        self.bt_close.clicked.connect(self.close_callback)

        ########################################################################
        # for pop-ups
        ########################################################################

        self.toast_timer = QtCore.QTimer()
        self.toast_timer.setSingleShot(True)
        self.toast_timer.timeout.connect(self.fade_toast)
        self.toast_dialog = None
        self.toast_opacity = 1.0

        ########################################################################
        # for message drawer
        ########################################################################

        # leave message on-screen until explicitly cleared or replaced
        self.persist = False

        # allows "message types / sources" to be associated, for instance so the
        # message "Tip: enable baseline correction" with token "enable_baseline_correction"
        # allows different objects to cancel (close) open messages tagged 
        # "enable_baseline_correction" when that condition has been satisfied, IF 
        # the currently-displayed message has that tag
        self.last_token = None

        self.link = None

        # Shouldn't need this, but getting around a "ShellExecute error 5"
        self.label.setOpenExternalLinks(False)
        self.label.linkActivated.connect(self.link_activated_callback)

        self.extra_ms = 0
        
        # could probably use one, keeping separate for now
        self.clear_timer = QtCore.QTimer()
        self.clear_timer.setSingleShot(True)
        self.clear_timer.timeout.connect(self.tick_clear)

    def stop(self):
        self.toast_timer.stop()
        self.clear_timer.stop()

    # ##########################################################################
    # Message Drawer
    # ##########################################################################

    ## 
    # display an info message to the user
    #
    # @param persist: leave message up until replaced or cancelled by token
    # @param token: to be used for later cancellation / replacement events
    # @param immediate: ignored as we've removed animation
    # @param benign: see Stylesheets.set_benign
    # @param extra_ms: leave message up this much longer than default (relative)
    # @param period_sec: if longer than the default, use this display time (absolute)
    # @param link: clickable URL 
    #
    # @see Stylesheets.set_benign
    # @public
    def info(self, msg, persist=False, token=None, benign=None, immediate=False, extra_ms=0, period_sec=None, link=None):
        if msg is None:
            return

        self.reset_timers()

        self.persist = persist
        self.last_token = token
        self.extra_ms = extra_ms
        self.link = link

        if period_sec is not None and period_sec * 1000 > self.DRAWER_DURATION_MS:
            self.extra_ms = period_sec * 1000 - self.DRAWER_DURATION_MS

        log.info(msg)
        self.label.setText(msg)

        self.show_immediate(benign)

    ## 
    # display an error warning to the user
    #
    # You can make errors show up as red "hazards" by defaulting benign
    # to False.  I tried it but didn't really like it.  Too alarming.
    #
    # @public
    def error(self, msg, persist=False, token=None, benign=None, immediate=False, extra_ms=0):
        if msg is None:
            return

        self.reset_timers()

        self.persist = persist
        self.last_token = token
        self.extra_ms = extra_ms

        log.error(msg)
        self.label.setText(msg)
        self.last_token = token

        self.show_immediate(benign)

    ##
    # Clear any non-persistant messages.  If token is provided and matches last message,
    # clears even persistent message.
    #
    # @public
    def clear(self, token=None, force=False):
        if force or not self.persist or (token is not None and token == self.last_token):
            self.schedule_clear()

    ## 
    # @private
    def hide(self):
        self.label.clear()

    ##
    # Deliberately does not interact with Toast.
    def reset_timers(self):
        self.clear_timer.stop()

    def schedule_clear(self, immediate=False):
        self.reset_timers()

        if immediate:
            self.label.clear()
        elif not self.persist:
            self.clear_timer.start(self.DRAWER_DURATION_MS + self.extra_ms)

    def close_callback(self):
        self.schedule_clear(immediate=True)

    def show_immediate(self, benign=None):
        self.clear_timer.stop()
        self.stylesheets.set_benign(self.inner, benign)
        self.schedule_clear()
        self.app.processEvents()

    def tick_clear(self):
        self.label.clear()

    def link_activated_callback(self, link):
        log.debug("activated link: [%s]", link)
        webbrowser.open(link)

    # ##########################################################################
    # Pop-up Toasts (unrelated to message drawer, consider separate class)
    # ##########################################################################

    ##
    # Show a pop-up (non-modal) dialog box which auto-fades and closes (but can
    # be immediately dismissed by the user)
    #
    # @public
    def toast(self, msg, persist=False, error=False):
        log.info("toast: %s", msg)
        dialog = QtWidgets.QMessageBox(parent=self.form)
        dialog.setIcon(QtWidgets.QMessageBox.Critical if error else QtWidgets.QMessageBox.Information)
        dialog.setWindowTitle("Notification")
        dialog.setText(msg)
        if not (persist or error):
            self.toast_dialog = dialog
            self.toast_timer.start(self.TOAST_DURATION_MS)
            self.toast_opacity = 1.0
        retval = dialog.exec() # MZ: exec_()?

    ## 
    # Recursively calls itself until opacity is zero.
    # @private
    def fade_toast(self):
        if self.toast_dialog is None:
            return

        try:
            self.toast_opacity -= Marquee.TOAST_FADE_STEP_OPACITY_PERCENT
            if self.toast_opacity > 0.0:
                self.toast_dialog.setWindowOpacity(self.toast_opacity)
                self.toast_timer.start(Marquee.TOAST_FADE_STEP_MS)
            else:
                self.toast_dialog.close()
                self.toast_dialog = None
        except:
            log.error("exception fading toast dialog", exc_info=1)
            self.toast_dialog = None
