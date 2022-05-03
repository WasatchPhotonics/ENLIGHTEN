import logging
import datetime

from PySide2 import QtGui, QtCore, QtWidgets

log = logging.getLogger(__name__)

##
# Wavecal, RamanMatching and RamanConcentration use this for an on-screen text editor
# for editting models and compound databases in-app.
class BasicDialog(QtWidgets.QDialog):

    def __init__(self, layout, title="Basic Dialog", modal=False):
        log.debug("instantiating BasicDialog %s", title)
        super(BasicDialog, self).__init__()

        self.ui = layout.Ui_Dialog()
        self.ui.setupUi(self)
        self.create_signals()
        self.setWindowIcon(QtGui.QIcon(":/application/images/EnlightenIcon.ico"))
        self.setWindowTitle(title)
        self.setModal(modal)

    def display(self):
        self.show()

    def create_signals(self):
        class ViewClose(QtCore.QObject):
            exit = QtCore.Signal(str)
        self.exit_signal = ViewClose()

    def closeEvent(self, event):
        self.exit_signal.exit.emit("close event")

