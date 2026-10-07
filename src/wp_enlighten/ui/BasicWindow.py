import logging

from wp_enlighten import common

if common.use_pyside2():
    from PySide2 import QtGui, QtCore, QtWidgets
else:
    from PySide6 import QtGui, QtCore, QtWidgets

# This line imports the "enlighten_layout.py" module which is generated from 
# enlighten_layout.ui when you run scripts/rebuild_resources.sh.  
from wp_enlighten.assets.uic_qrc import enlighten_layout

log = logging.getLogger(__name__)

class BasicWindow(QtWidgets.QMainWindow):
    """
    The codebase contains myriad references to "Controller.form" and "cfu" --
    those refer to an object of this class (and its .ui attribute).
    """

    # see https://stackoverflow.com/questions/43126721/detect-resizing-in-widget-window-resized-signal
    # reduces some layout parts with smaller windows
    def __init__(self, title):
        super(BasicWindow, self).__init__()

        self.prompt_on_exit = True

        # the all-important "cfu"
        self.ui = enlighten_layout.Ui_MainWindow()
        self.ui.setupUi(self)

        self.create_signals()
        self.setWindowIcon(QtGui.QIcon(":/application/images/EnlightenIcon.ico"))
        self.setWindowTitle(title)

    def resizeEvent(self, event):
        log.debug("resize event called")
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

    def closeEvent(self, event=None):
        log.debug("BasicWindow (QMainWindow) received close event")

        if self.prompt_on_exit:
            if not self.confirm_exit():
                log.debug('"We are cancelling the apocalypse!"')
                if event is not None:
                    event.ignore()
                return

        log.debug("exit confirmed...accepting event")
        if event is not None:
            event.accept()
        log.debug("emitting BasicWindow.ViewClose.exit signal")
        self.exit_signal.exit.emit("close event")

    def confirm_exit(self):
        QMessageBox = QtWidgets.QMessageBox
        msg_box = QMessageBox(parent=self)
        msg_box.setWindowTitle("Confirm Exit")
        msg_box.setText("Are you sure you want to exit ENLIGHTEN?")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.Yes)
        response = msg_box.exec()
        return response == QMessageBox.StandardButton.Yes
