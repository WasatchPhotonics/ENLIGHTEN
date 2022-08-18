# See https://gis.stackexchange.com/questions/137593/how-to-programmatically-close-a-qmessagebox-without-clicking-ok-or-x
# Presented solution by imo interestingly showing the many layers of inheritance in pyside
# all QWidgets fire show events, which can have a slot
# all QObjects can run a local QTimer that can have a slot
# Combine the two and you can have a timed dialog, or other widget really

from fileinput import close
import PySide2
from PySide2.QtWidgets import QMessageBox, QMessageBox

class TimeoutDialog(QMessageBox):
    def __init__(self, *__args):
        QMessageBox.__init__(self)
        self.timeout = 0
        self.autoclose = False
        self.msg = ""
        self.currentTime = 0
        self.closeout_msg = f", closing in {self.timeout-self.currentTime} seconds"

    def showEvent(self, QShowEvent):
        self.currentTime = 0
        if self.autoclose:
            self.startTimer(1000)

    def timerEvent(self, *args, **kwargs):
        self.currentTime += 1
        self.setText(self.msg + self.closeout_msg)
        if self.currentTime >= self.timeout:
            self.done(0)

    @staticmethod
    def showWithTimeout(timeoutSeconds, message, title, icon=QMessageBox.Information, buttons=None):
        if buttons is None:
            buttons = [("Ok", QMessageBox.Ok)]
        if not isinstance(buttons, list):
            buttons = [buttons]
        w = TimeoutDialog()
        w.autoclose = True
        w.timeout = timeoutSeconds
        w.setText(message + w.closeout_msg)
        w.msg = message
        w.setWindowTitle(title)
        w.setIcon(icon)
        btns = list[map(lambda b: w.addButton(b[0], b[1]), buttons)]
        w.exec_()
        clicked_button = w.clickedButton()
        selection = [clicked_button == btn for btn in btns]
        return selection