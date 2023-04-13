# See https://gis.stackexchange.com/questions/137593/how-to-programmatically-close-a-qmessagebox-without-clicking-ok-or-x
# Presented solution by imo interestingly showing the many layers of inheritance in pyside
# all QWidgets fire show events, which can have a slot
# all QObjects can run a local QTimer that can have a slot
# Combine the two and you can have a timed dialog, or other widget really

import logging
from fileinput import close
from PySide2 import QtCore, QtWidgets
from PySide2.QtWidgets import QMessageBox

log = logging.getLogger(__name__)

class TimeoutDialog(QMessageBox):
    def __init__(self, *args):
        QMessageBox.__init__(self, *args)
        self.timeout = 0
        self.autoclose = False
        self.msg = ""
        self.currentTime = 0

    def showEvent(self, QShowEvent):
        self.currentTime = 0
        if self.autoclose:
            self.startTimer(1000)

        if False:
            # from https://wiki.qt.io/How_to_Center_a_Window_on_the_Screen,
            # but doesn't work in current state

            app = QtWidgets.QApplication.instance()
            window = app.activeWindow()

            self.setGeometry(
                QtWidgets.QStyle.alignedRect(
                    QtCore.Qt.LeftToRight,
                    QtCore.Qt.AlignCenter,
                    window.size(),
                    app.desktop().availableGeometry(),
                )
            )

    def timerEvent(self, *args, **kwargs):
        self.currentTime += 1
        self.setText(self.msg)
        if self.currentTime >= self.timeout and self.timeout != -1:
            self.done(0)

    @staticmethod
    def showWithTimeout(parent, timeoutSeconds, message, title, icon=QMessageBox.Information, buttons=None):
        if buttons is None:
            log.debug("default buttons")
            buttons = [("Ok", QMessageBox.AcceptRole)]
        if not isinstance(buttons, list):
            log.debug("listifying buttons")
            buttons = [buttons]
        w = TimeoutDialog(parent)
        w.autoclose = True
        w.timeout = timeoutSeconds
        w.setText(message)
        w.msg = message
        w.setWindowTitle(title)
        w.setIcon(icon)
        log.debug(f"buttons = {repr(buttons)}")
        btns = [w.addButton(b[0], b[1]) for b in buttons]
        w.exec_()
        clicked_button = w.clickedButton()
        selection = [clicked_button == btn for btn in btns]
        return selection
