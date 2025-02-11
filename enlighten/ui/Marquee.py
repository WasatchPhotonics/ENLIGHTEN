import webbrowser
import datetime

from enlighten import common

if common.use_pyside2():
    from PySide2 import QtCore, QtWidgets
else:
    from PySide6 import QtCore, QtWidgets

import logging

log = logging.getLogger(__name__)

class Marquee:
    """
    Encapsulate access to the "message display area" visible along the top of the 
    ENLIGHTEN display.

    Messages are normally shown for 3sec and then removed.  If 'persist' is set, 
    message will remain until overwritten.
    
    Also provides a button-less "toast" notification that auto-fades over 2sec.

    This class is more complicated than it needs to be for two reasons:

    1. The Marquee used to be animated, with gradual slide-out drawers and such.
       This is the reason for some of the "schedule" nomenclature and timing.
       Not really needed anymore, and could be simplified out.

    2. Part of the KnowItAll implementation included the concept of "hazard" vs
       "benign" identifications. We aren't currently using that, but it may come
       back.

    TODO:

    - consider restoring some level of animation (just not moving buttons, like
      we used to)
    - consider adding a "stronger" close-box with "never show again", perhaps
      via QToolButton with DelayedPopup.
    """
    
    ORIG_HEIGHT = 36

    DRAWER_DURATION_MS = 3000
    TOAST_DURATION_MS  = 3000
    TOAST_FADE_STEP_MS =   75
    TOAST_FADE_STEP_OPACITY_PERCENT = 0.05  # fade x% of original opacity each step

    def __init__(self, ctl):
        self.ctl = ctl
        cfu = ctl.form.ui

        self.frame       = cfu.frame_drawer_white
        self.inner       = cfu.frame_drawer_black
        self.label       = cfu.label_drawer

        self.height = Marquee.ORIG_HEIGHT

        # just store whatever the current theme sets
        self.default_css = self.inner.styleSheet()

        self.hide()

        cfu.pushButton_marquee_close.clicked.connect(self.close_callback)

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
        self.showing_something = False

        # Shouldn't need this, but getting around a "ShellExecute error 5"
        self.label.setOpenExternalLinks(False)
        self.label.linkActivated.connect(self.link_activated_callback)

        self.extra_ms = 0
        self.next_clear = None
        
        # could probably use one, keeping separate for now
        self.clear_timer = QtCore.QTimer()
        self.clear_timer.setSingleShot(True)
        self.clear_timer.timeout.connect(self.tick_clear)
        self.clear_timer.start(1000)

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

        is_error = "error" in msg.lower() or (benign is not None and not benign)

        self.persist = persist
        self.last_token = token
        self.extra_ms = extra_ms
        self.link = link

        if period_sec is not None and period_sec * 1000 > self.DRAWER_DURATION_MS:
            self.extra_ms = period_sec * 1000 - self.DRAWER_DURATION_MS

        if is_error:
            log.error(msg)
        else:
            log.info(msg)

        self.label.setText(msg)
        self.show()

        if is_error:
            self.show_immediate(benign=False)
        else:
            self.show_immediate(benign) # allow None to pass-through

    def error(self, msg, persist=False, token=None, benign=False, immediate=False, extra_ms=0, period_sec=None, link=None):
        return self.info(msg        = msg, 
                         persist    = persist, 
                         token      = token, 
                         benign     = benign, 
                         immediate  = immediate, 
                         extra_ms   = extra_ms, 
                         period_sec = period_sec, 
                         link       = link)

    def clear(self, token=None, force=False):
        if force or not self.persist or (token and token == self.last_token):
            self.schedule_clear(immediate=True)

    def show(self):
        op = QtWidgets.QGraphicsOpacityEffect(self.frame)
        op.setOpacity(1)
        self.frame.setGraphicsEffect(op)
        self.frame.setAutoFillBackground(True)
        self.showing_something = True

    def hide(self):
        self.label.clear()
        
        op = QtWidgets.QGraphicsOpacityEffect(self.frame)
        op.setOpacity(0)
        self.frame.setGraphicsEffect(op)
        self.frame.setAutoFillBackground(True)
        self.showing_something = False

    def schedule_clear(self, immediate=False):
        if immediate:
            self.hide()
            self.next_clear = None
        elif not self.persist:
            when_ms = self.DRAWER_DURATION_MS + self.extra_ms
            self.next_clear = datetime.datetime.now() + datetime.timedelta(milliseconds=when_ms)

    def close_callback(self):
        self.schedule_clear(immediate=True)

    def show_immediate(self, benign=None):
        # we're not currently using this, and it messes with themes at the moment
        if benign is not None:
            self.ctl.stylesheets.set_benign(self.inner, benign)
        else:
            self.ctl.stylesheets.apply(self.inner, self.default_css, raw=True)

        self.schedule_clear()
        self.ctl.app.processEvents()

    def tick_clear(self):
        if self.next_clear is not None:
            now = datetime.datetime.now()
            if now >= self.next_clear:
                self.hide()
                self.next_clear = None
        self.clear_timer.start(200)

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
        dialog = QtWidgets.QMessageBox(parent=self.ctl.form)
        dialog.setIcon(QtWidgets.QMessageBox.Critical if error else QtWidgets.QMessageBox.Information)
        dialog.setWindowTitle("Notification")
        dialog.setText(msg)
        if not (persist or error):
            self.toast_dialog = dialog
            self.toast_timer.start(self.TOAST_DURATION_MS)
            self.toast_opacity = 1.0
        dialog.exec() 

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
