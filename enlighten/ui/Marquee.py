import webbrowser
import datetime

from enlighten import common

if common.use_pyside2():
    from PySide2 import QtCore, QtWidgets
else:
    from PySide6 import QtCore, QtWidgets

import logging

log = logging.getLogger(__name__)

class Message:
    def __init__(self, msg, persist=False, token=None, benign=None, immediate=False, extra_ms=0, period_sec=None, link=None):
        """
        @param persist leave message on-screen until explicitly cleared or replaced
        @param token allows "message types / sources" to be associated, for 
                    instance so the message "Tip: enable baseline correction" 
                    with token "enable_baseline_correction" allows different 
                    objects to cancel (close) open messages tagged 
                    "enable_baseline_correction" when that condition has been 
                    satisfied, IF the currently-displayed message has that tag
        """
        self.msg = msg
        self.persist = persist 
        self.token = token
        self.benign = benign
        self.immediate = immediate
        self.extra_ms = extra_ms
        self.period_sec = period_sec
        self.link = link

    def is_error(self):
        return self.benign == False or "error" in self.msg.lower()

    def __repr__(self):
        return f"Marquee.Message: persist {self.persist}, token {self.token}, benign {self.benign}, immediate {self.immediate}, extra_ms {self.extra_ms}, period_sec {self.period_sec}, link {self.link}, msg {self.msg}"

class Marquee:
    """
    Encapsulate access to the "message display area" visible along the top of the 
    ENLIGHTEN display.

    Messages are normally shown for 3sec and then removed.  If 'persist' is set, 
    message will remain until overwritten.
    
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

        self.current_message = None


        # Shouldn't need this, but getting around a "ShellExecute error 5"
        self.label.setOpenExternalLinks(False)
        self.label.linkActivated.connect(self.link_activated_callback)

        self.next_clear_timestamp = None
        self.next_message = None
        
        # could probably use one, keeping separate for now
        self.timer = QtCore.QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.tick)
        self.timer.start(1000)

    def stop(self):
        self.timer.stop()

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

        if benign and self.showing_error():
            log.info(f"info: hiding due to error: {msg}")
            return
            
        self.next_message = Message(msg, persist=persist, token=token, benign=benign, immediate=immediate, extra_ms=extra_ms, period_sec=period_sec, link=link)

    def error(self, msg, persist=False, token=None, benign=False, immediate=False, extra_ms=0, period_sec=None, link=None):
        return self.info(msg        = msg, 
                         persist    = persist, 
                         token      = token, 
                         benign     = benign, 
                         immediate  = immediate, 
                         extra_ms   = extra_ms, 
                         period_sec = period_sec, 
                         link       = link)

    def showing_something(self):
        return self.current_message is not None

    def showing_error(self):
        if self.current_message:
            return not self.current_message.benign
            
    def persist(self): 
        if self.current_message: 
            return self.current_message.persist

    def last_token(self): 
        if self.current_message: 
            return self.current_message.token

    def extra_ms(self): 
        ms = 0
        if self.current_message: 
            ms = self.current_message.extra_ms
            if self.current_message.period_sec is not None:
                if self.current_message.period_sec * 1000 > self.DRAWER_DURATION_MS:
                    ms = self.current_message.period_sec * 1000 - self.DRAWER_DURATION_MS
        return ms

    def link(self):
        if self.current_message:
            return self.current_message.link

    def clear(self, token=None, force=False):
        if force or not self.persist() or (token and token == self.last_token()):
            self.schedule_clear(immediate=True)

    def hide(self):
        self.label.clear()
        self.current_message = None
        
        op = QtWidgets.QGraphicsOpacityEffect(self.frame)
        op.setOpacity(0)
        self.frame.setGraphicsEffect(op)
        self.frame.setAutoFillBackground(True)

    def schedule_clear(self, immediate=False):
        if immediate:
            self.hide()
            self.next_clear_timestamp = None
        elif not self.persist():
            when_ms = self.DRAWER_DURATION_MS + self.extra_ms()
            self.next_clear_timestamp = datetime.datetime.now() + datetime.timedelta(milliseconds=when_ms)

    def close_callback(self):
        self.schedule_clear(immediate=True)

    def tick(self):
        next_ = self.next_message
        if next_:
            self.next_message = None
            self.current_message = next_
            self.label.setText(next_.msg)

            op = QtWidgets.QGraphicsOpacityEffect(self.frame)
            op.setOpacity(1)
            self.frame.setGraphicsEffect(op)
            self.frame.setAutoFillBackground(True)

            if next_.is_error():
                self.ctl.stylesheets.set_benign(self.inner, False)
            else:
                self.ctl.stylesheets.apply(self.inner, self.default_css, raw=True)

            self.schedule_clear()

        elif self.next_clear_timestamp:
            now = datetime.datetime.now()
            if now >= self.next_clear_timestamp:
                self.hide()
                self.next_clear_timestamp = None

        # tick Marquee at 10Hz
        self.timer.start(100)

    def link_activated_callback(self, link):
        log.info(f"activated link: {link}")
        webbrowser.open(link)
