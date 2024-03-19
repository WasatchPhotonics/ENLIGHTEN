import os
import re
import logging

from html import escape
from pygtail import Pygtail 

from wasatch import applog
from enlighten import common

if common.use_pyside2():
    from PySide2 import QtCore, QtGui
else:
    from PySide6 import QtCore, QtGui

log = logging.getLogger(__name__)

class LoggingFeature:
    """
    Currently this timer runs continuously, as it is what provides the "Hardware" Status Indicator.
    """

    TIMER_SLEEP_MS = 2000

    def __init__(self, ctl):
        self.ctl = ctl
        cfu = ctl.form.ui

        self.cb_paused  = cfu.checkBox_logging_pause
        self.cb_verbose = cfu.checkBox_verbose_logging
        self.te_log     = cfu.textEdit_log

        self.cb_verbose.setVisible(True) # MZ: when would this be False?

        self.timer = QtCore.QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.tick)
        self.timer.start(LoggingFeature.TIMER_SLEEP_MS)

        self.cb_verbose                         .stateChanged   .connect(self.verbose_callback)
        cfu.pushButton_copy_log_to_clipboard    .clicked        .connect(self.copy_to_clipboard)

        # if verbose logging was specified at the command-line OR 
        # previously set via .ini, use that
        if log.isEnabledFor(logging.DEBUG) or self.ctl.config.get_bool("logging", "verbose"):
            self.cb_verbose.setChecked(True)

        try:
            offset_file = applog.get_location() + ".offset"
            if os.path.exists(offset_file):
                os.remove(offset_file)
        except:
            log.info("error removing old Pygtail offset", exc_info=1)

        self.timer.start(LoggingFeature.TIMER_SLEEP_MS)

    def stop(self):
        self.timer.stop()

    def verbose_callback(self):
        enabled = self.cb_verbose.isChecked()

        if enabled:
            log.info("enabling verbose logging")
            logging.getLogger().setLevel(logging.DEBUG)
            self.ctl.config.set("logging", "verbose", "True")
            self.ctl.log_level = "DEBUG"
        else:
            log.info("disabling verbose logging")
            logging.getLogger().setLevel(logging.INFO)
            self.ctl.config.set("logging", "verbose", "False")
            self.ctl.log_level = "INFO"

    def paused(self):
        return self.cb_paused.isChecked()

    def copy_to_clipboard(self):
        if self.ctl.clipboard:
            s = self.te_log.toPlainText()
            self.ctl.clipboard.raw_set_text(s)

    def tick(self):
        # need to run all the time to populate Hardware Status Indicator :-(
        lines = None
        if not self.paused():
            try:
                # is there a less memory-intensive way to do this?
                # maybe implement ring-buffer inside the loop...
                lines = []
                for line in Pygtail(applog.get_location(), encoding="utf-8"):
                    lines.append(line)
                self.process(lines)
            except IOError:
                log.warn("Cannot tail log file")

        self.timer.start(self.TIMER_SLEEP_MS)

    def process(self, lines):
        if lines is None or lines == []:
            return

        if len(lines) > 150:
            lines = lines[-150:]
            lines.insert(0, "...snip...")

        self.te_log.clear()
        for line in lines:
            self.te_log.append(self.format(line))
        self.te_log.moveCursor(QtGui.QTextCursor.End)

    def format(self, line):
        line = re.sub(r"[\r\n]", "", line)
        html = escape(line)

        color = None
        error = False

        if " CRITICAL " in html:
            color = "980000" # red
            error = True
        elif " ERROR " in html:
            color = "ba8023" # orange
            error = True
        elif " WARNING " in html:
            color = "cac401" # yellow

        if color:
            html = f"<span style='color: #{color}'>" + html + "</span>"

        if error and self.ctl.status_indicators:
            self.ctl.status_indicators.raise_hardware_error(line)

        return html
