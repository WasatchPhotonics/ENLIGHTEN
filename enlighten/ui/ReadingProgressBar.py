from enlighten import common

if common.use_pyside2():
    from PySide2 import QtCore
else:
    from PySide6 import QtCore

class ReadingProgressBar:

    def __init__(self, ctl):
        self.ctl = ctl

        cfu = ctl.form.ui
        self.pb = cfu.readingProgressBar

        self.hide_timer = QtCore.QTimer()
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.hide)

    def hide(self):
        self.pb.setVisible(False)

    def set(self, value):
        """ Hide at zero. Set timer to disappear 3sec after reaching 100. """

        if value < 0:
            # unbounded "busy" animation
            self.pb.setVisible(True)
            self.pb.setRange(0, 0)
        else:
            # round to int 0-100
            self.pb.setRange(0, 100)
            value = int(min(100, max(0, round(value, 0))))
            
            if value == 0:
                self.pb.setVisible(False)
            else:
                self.pb.setValue(value)
                self.pb.setVisible(True)

                if value >= 100:
                    self.hide_timer.start(1000)
