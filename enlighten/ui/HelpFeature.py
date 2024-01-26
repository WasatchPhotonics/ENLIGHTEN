import webbrowser
import logging
import re

from enlighten import common

if common.use_pyside2():
    import PySide2
    from PySide2 import QtWidgets
else:
    import PySide6
    from PySide6 import QtWidgets

log = logging.getLogger(__name__)

class HelpFeature:
    
    HELP_URL = "https://wasatchphotonics.com/software-support/enlighten/"

    def __init__(self, ctl):
        self.ctl = ctl

        cfu = ctl.form.ui

        self.bt_help = cfu.pushButton_help
        self.bt_what = cfu.pushButton_whats_this

        self.bt_help.clicked.connect(self.help_callback)
        self.bt_what.clicked.connect(self.what_callback)

        tt = """Click or press F1 to view online manual. 

                Keyboard shortcuts:

                Ctrl-1 Scope View
                Ctrl-2 Settings View
                Ctrl-3 Hardware View
                Ctrl-4 Log View

                Ctrl-A Authenticate
                Ctrl-C Copy to system clipboard
                Ctrl-D take/clear Dark
                Ctrl-E Edit last saved measurement
                Ctrl-G enter Gain
                Ctrl-H toggle between Hardware and scope
                Ctrl-L toggle Laser firing
                Ctrl-N enter new Note
                Ctrl-P Pause/Play
                Ctrl-R take/clear Reference
                Ctrl-S Save measurement
                Ctrl-T enter integration Time

                Ctrl-Left  move cursor
                Ctrl-Right move cursor"""
        tt = re.sub(r"([\n\r]+) *", r"\1", tt)
        log.debug(f"tt now {tt}")

        self.bt_help.setToolTip(tt)

    def help_callback(self):
        url = self.HELP_URL
        log.debug(f"opening {url}")
        webbrowser.open(url)

    def what_callback(self):
        wt = QtWidgets.QWhatsThis
        if wt.inWhatsThisMode():
            log.debug("leaving WhatsThis mode")
            wt.leaveWhatsThisMode()
        else:
            log.debug("entering WhatsThis mode")
            wt.enterWhatsThisMode()
