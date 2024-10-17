import webbrowser
import logging

from enlighten import common
from enlighten.util import unwrap, undent

if common.use_pyside2():
    from PySide2 import QtWidgets
else:
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

        self.bt_help.setWhatsThis("Opens a web browser to ENLIGHTEN on-line help if clicked, or shows a handy cheat-sheet of keyboard shortcuts on mouse-over.")
        self.bt_what.setWhatsThis(unwrap("""
            An alternate help system which can provide richer information than we normally put into mouse-over tooltips.
            
            In particular, provides especially rich data on individual measurements in the Clipboard.

            And frankly, it lets us experiment with this Qt feature to see if it adds any value ;-)"""))

        self.bt_help.setToolTip(undent("""
            Click or press F1 to view online manual. 

            Keyboard shortcuts:
            
            Ctrl-1 Scope View
            Ctrl-2 Settings View
            Ctrl-3 Hardware View
            Ctrl-4 Log View
            Ctrl-5 Factory View
            Ctrl-` next view (backtick)
            
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
            Ctrl-X toggle eXpert mode

            Ctrl-* Auto-Raman
            
            Ctrl-Up/Down step values
            Ctrl-Left/Right move Scope cursor"""))

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
