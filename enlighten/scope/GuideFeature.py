import multiprocessing
import datetime
import logging
import time
import os

from enlighten import common

if common.use_pyside2():
    from PySide2 import QtCore
else:
    from PySide6 import QtCore

log = logging.getLogger(__name__)

class Tip(object):
    def __init__(self,
            msg,
            persist=False,
            token=None,
            link=None):
        self.msg = msg
        self.persist = persist
        self.token = token
        self.link = link 

class GuideFeature:

    MIN_DISPLAY_SEC = 8 
    POLL_SEC = 1

    def __init__(self, ctl):
        self.ctl = ctl
        sfu = ctl.form.ui

        self.bt_enable = sfu.pushButton_guide

        self.queue = multiprocessing.Queue()
        self.last_tipped = None
        self.current_tip = None

        self.timer = QtCore.QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self._tick)

        self.bt_enable          .clicked        .connect(self._enable_callback)

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
        
    def suggest(self, msg, persist=True, token=None, link=None):
        if self.current_tip is not None:
            if self.current_tip.msg == msg:
                log.debug("ignoring repeat tip: %s", msg)
                return

        queued = self.copy_queue()
        for tip in queued:
            if tip.msg == msg:
                log.debug("ignoring duplicate queued tip: %s", msg)
                return

        tip = Tip(msg=msg, persist=persist, token=token, link=link)
        log.debug("queued %s", msg)
        self.queue.put(tip)

    ##
    # Clear the given token, both from the current Marquee display and also from
    # any queued tips
    # @public
    def clear(self, token):
        self.ctl.marquee.clear(token)
        self.copy_queue(drop_token=token)

    ##
    # returns a copy of the current queue contents as a list
    # @param drop_token if provided, removes matching tips from queue during copy
    def copy_queue(self, drop_token=None):
        requeue = []
        while True:
            tip = None
            try:
                tip = self.queue.get_nowait()
            except:
                pass
            if tip is None:
                break

            if tip.token != drop_token:
                requeue.append(tip)
        
        for tip in requeue:
            self.queue.put(tip)

        return requeue
        
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
        if self.ctl.BatchCollection.running:
            log.debug("tick: not during BatchCollection")
            return self._reset_timer()

        # don't stop recent tips with new ones
        now = datetime.datetime.now()
        if self.last_tipped is not None and ((now - self.last_tipped).total_seconds() < self.MIN_DISPLAY_SEC):
            log.debug("tick: not time")
            return self._reset_timer()

        # anything in the tip jar?
        tip = None
        try:
            tip = self.queue.get_nowait()
        except:
            pass
        if tip is None:
            log.debug("tick: none found")
            return self._reset_timer()

        self.current_tip = tip
        self.last_tipped = datetime.datetime.now()
        self.ctl.marquee.info(tip.msg, token=tip.token, persist=tip.persist, link=tip.link)
        self._reset_timer()
