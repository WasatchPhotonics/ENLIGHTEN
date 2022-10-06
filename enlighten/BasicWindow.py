import logging
import datetime

from PySide2 import QtGui, QtCore, QtWidgets

# This line imports the "enlighten_layout.py" module which is generated from 
# enlighten_layout.ui when you run scripts/rebuild_resources.sh.  
from .assets.uic_qrc import enlighten_layout

log = logging.getLogger(__name__)

class BasicWindow(QtWidgets.QMainWindow):
    """
    In the Controller, you will see myriad references to "self.form" and "sfu" --
    those refer to an object of this class (and its .ui attribute).
    """

    # see https://stackoverflow.com/questions/43126721/detect-resizing-in-widget-window-resized-signal
    # reduces some layout parts with smaller windows
    def __init__(self, title, headless):
        super(BasicWindow, self).__init__()

        self.prompt_on_exit = True

        # the all-important "sfu"
        self.ui = enlighten_layout.Ui_MainWindow()
        self.ui.setupUi(self)
        new_line = '\n'
        #log.error(f"type of main window is {type(self.ui)} {f'{new_line}'.join(dir(self.ui))}")

        self.create_signals()
        self.setWindowIcon(QtGui.QIcon(":/application/images/EnlightenIcon.ico"))
        self.setWindowTitle(title)

    def resizeEvent(self, event):
        log.debug(f"resize event called")
        self.reconfigure_layout()
        return super(BasicWindow, self).resizeEvent(event)
 
    def create_signals(self):
        class ViewClose(QtCore.QObject):
            exit = QtCore.Signal(str)
        self.exit_signal = ViewClose()

    def reconfigure_layout(self):
        if self.size().width() < 1000:
            self.ui.frame_scopeSetup_spectra.hide()
        else:
            self.ui.frame_scopeSetup_spectra.show()

    def closeEvent(self, event):
        log.debug("BasicWindow (QMainWindow) received close event")

        if self.prompt_on_exit:
            quit_msg = "Are you sure you want to exit ENLIGHTEN?" 
            reply = QtWidgets.QMessageBox.question(self, 'Confirm Exit', 
                quit_msg, QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
            if reply != QtWidgets.QMessageBox.Yes:
                log.debug('"We are cancelling the apocalypse!"')
                event.ignore()
                return

        log.debug("exit confirmed...accepting event")
        event.accept()
        log.debug("emitting BasicWindow.ViewClose.exit signal")
        self.exit_signal.exit.emit("close event")
