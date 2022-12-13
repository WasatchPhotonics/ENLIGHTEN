import webbrowser

from PySide2 import QtCore, QtGui, QtWidgets

from . import util

import logging

log = logging.getLogger(__name__)

##
# Encapsulate access to the "message display area" atop the right-hand side of 
# the Scope Capture screen.  Messages are normally flashed for 3sec and then 
# removed.  If 'persist' is set, message will remain until overwritten.
#
# Also provides a button-less notification box that auto-fades over 2sec.
class Marquee(object):
    
    DRAWER_DURATION_MS = 3000
    TOAST_DURATION_MS  = 3000
    TOAST_FADE_STEP_MS =   75
    TOAST_FADE_STEP_OPACITY_PERCENT = 0.05  # fade x% of original opacity each step

    def __init__(self, 
            bt_close,
            form,        # needed for Toast parent
            frame,
            inner,
            label,
            stylesheets):
        self.bt_close    = bt_close
        self.form        = form
        self.frame       = frame
        self.inner       = inner
        self.label       = label
        self.stylesheets = stylesheets

        self.original_height = self.frame.height()
        self.original_height = 36
        self.height = self.original_height
        log.debug(f"original height = {self.original_height}")
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
        # for animated message drawer
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
        
        self.grow_timer = QtCore.QTimer()
        self.grow_timer.setSingleShot(True)
        self.grow_timer.timeout.connect(self.tick_grow)

        # could probably use one, keeping separate for now
        self.shrink_timer = QtCore.QTimer()
        self.shrink_timer.setSingleShot(True)
        self.shrink_timer.timeout.connect(self.tick_shrink)

    def stop(self):
        self.toast_timer.stop()
        self.grow_timer.stop()
        self.shrink_timer.stop()

    # ##########################################################################
    # Message Drawer
    # ##########################################################################

    ## 
    # display an info message to the user
    #
    # @param persist: leave message up until replaced or cancelled by token
    # @param token: to be used for later cancellation / replacement events
    # @param immediate: skip the "opening-drawer" animation
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

        if immediate:
            self.show_immediate(benign)
        else:
            self.show_animated(benign)

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

        if immediate:
            self.show_immediate(benign)
        else:
            self.show_animated(benign)

    ##
    # Clear any non-persistant messages.  If token is provided and matches last message,
    # clears even persistent message.
    #
    # @public
    def clear(self, token=None, force=False):
        if force or not self.persist or (token is not None and token == self.last_token):
            self.shrink_timer.start(0)

    ## 
    # This is a one-shot, doesn't start animation (intended to be called by ctor
    # and end of "shrink" animation)
    #
    # @private
    def hide(self):
        self.frame.setVisible(False)
        self.set_height(8) # no need to start from scratch

    def reset_timers(self):
        self.grow_timer.stop()
        self.shrink_timer.stop()

    ## @private
    def schedule_shrink(self, immediate=False):
        self.reset_timers()

        if immediate:
            self.shrink_timer.start(0)
        elif self.persist:
            self.set_height(self.original_height)
        else:
            # log.debug("scheduling shrink")
            self.shrink_timer.start(self.DRAWER_DURATION_MS + self.extra_ms)

    def close_callback(self):
        self.schedule_shrink(immediate=True)

    ## 
    # If we're doing an operation where the GUI thread may get kind of
    # jaggy (USB connection), don't animate the opening, just show the
    # message.
    # @private
    def show_immediate(self, benign=None):
        self.shrink_timer.stop()

        self.stylesheets.set_benign(self.inner, benign)
        self.frame.setVisible(True)

        self.set_height(self.original_height)
        self.schedule_shrink()

    ##
    # Kicks-off "grow" animation IFF not already fully expanded.
    #
    # @private
    def show_animated(self, benign=None):
        self.stylesheets.set_benign(self.inner, benign)
        self.frame.setVisible(True)

        self.shrink_timer.stop()

        if self.height < self.original_height:
            self.grow_timer.start()
        else:
            self.schedule_shrink()

    def tick_grow(self):
        try:
            if self.set_height(self.height + 2) < self.original_height:
                return self.grow_timer.start(int(self.height*0.5))
        except:
            log.error("exception growing drawer", exc_info=1)
            self.set_height(self.original_height)

        self.schedule_shrink()

    def tick_shrink(self):
        try:
            if self.set_height(self.height - 2) > 8:
                self.shrink_timer.start(int(self.height*0.5))
            else:
                self.hide()
        except:
            log.error("exception shrinking drawer", exc_info=1)
            self.hide()

    ## @private
    def set_height(self, h):
        h = max(0, min(h, self.original_height))
        self.frame.setMinimumHeight(h)
        self.frame.setMaximumHeight(h)
        self.height = h
        # log.debug(f"height now {h}")
        return h
            
    ## @private
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

