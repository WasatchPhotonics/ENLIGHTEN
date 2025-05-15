import datetime
import logging

from enlighten import common

if common.use_pyside2():
    from PySide2 import QtCore
else:
    from PySide6 import QtCore

log = logging.getLogger(__name__)

class Tip:
    def __init__(self,
            msg,
            persist=False,
            period_sec=None,
            token=None,
            link=None):

        self.msg = msg
        self.persist = persist
        self.period_sec = period_sec
        self.token = token
        self.link = link 

    def __repr__(self):
        return f"Tip <token {self.token}, persist {self.persist}, msg {self.msg}, link {self.link}>"

class GuideFeature:
    """
    Recommends "tips" that might be suggested to the user through the Marquee.
    """
    MIN_DISPLAY_SEC = 8 
    POLL_SEC = 3

    def __init__(self, ctl):
        self.ctl = ctl
        cfu = ctl.form.ui

        self.bt_enable = cfu.pushButton_guide

        self.queue = []
        self.last_tipped = None
        self.current_tip = None
        self.shown = set()

        self.timer = QtCore.QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self._tick)

        self.bt_enable.clicked.connect(self._enable_callback)
        self.bt_enable.setWhatsThis("Recommend spectroscopy 'tips' while using ENLIGHTEN.")

        self.enabled = True
        self.update_visibility()

    # ##########################################################################
    # Public methods
    # ##########################################################################

    def update_visibility(self):
        self.ctl.gui.colorize_button(self.bt_enable, self.enabled)
        if self.enabled:
            self.timer.start()
        else:
            self.timer.stop()

    def stop(self):
        self.timer.stop()
        
    def suggest(self, msg, persist=False, period_sec=10, token=None, link=None):
        if self.current_tip and self.current_tip.msg == msg:
            log.debug(f"ignoring repeat tip {msg}")
            return

        if msg in self.shown:
            log.debug(f"ignoring previously-shown tip: {msg}")
            self.shown.add(msg)
            return

        for tip in self.queue:
            if tip.msg == msg:
                log.debug(f"ignoring duplicate queued tip: {msg}")
                return

        tip = Tip(msg=msg, persist=persist, token=token, period_sec=period_sec, link=link)
        log.debug(f"suggest: queued {msg}")
        self.queue.append(tip)

    def clear(self, token=None):
        if token:
            log.debug(f"clearing token {token} from the Marquee")
            self.ctl.marquee.clear(token)

        new_queue = []
        if token:
            for tip in self.queue:
                if token != tip.token:
                    new_queue.append(tip)
        self.queue = new_queue
        
    # ##########################################################################
    # Private methods
    # ##########################################################################

    def _enable_callback(self):
        """ @private """
        self.enabled = not self.enabled
        self.update_visibility()

    def _reset_timer(self):
        """ @private """
        self.timer.start(self.POLL_SEC * 1000)

    def _tick(self):
        """ @private """
        # don't tip during BatchCollection
        if self.ctl.batch_collection and self.ctl.batch_collection.running:
            log.debug("tick: not during BatchCollection")
            return self._reset_timer()

        # don't stop recent tips with new ones
        now = datetime.datetime.now()
        if self.last_tipped is not None and ((now - self.last_tipped).total_seconds() < self.MIN_DISPLAY_SEC):
            log.debug("tick: not time")
            return self._reset_timer()

        # don't stomp other Marquee messages (Guide tips are lowest-priority)
        if self.ctl.marquee.showing_something():
            log.debug("tick: waiting for Marquee to clear")
            return self._reset_timer()

        # anything in the tip jar?
        tip = None
        if len(self.queue):
            try:
                tip = self.queue.pop(0)
            except:
                pass
        if tip is None:
            log.debug("tick: none found")
            return self._reset_timer()

        log.debug(f"dequeued tip {tip}")
        self.current_tip = tip
        self.last_tipped = datetime.datetime.now()
        self.ctl.marquee.info(tip.msg, token=tip.token, persist=tip.persist, period_sec=tip.period_sec, link=tip.link)
        self._reset_timer()
