import random
import logging

from enlighten import common

if common.use_pyside2():
    from PySide2 import QtGui
    from PySide2.QtWidgets import QWidget, QCheckBox, QDialog, QHBoxLayout, QVBoxLayout, QLabel, QTextEdit, QPushButton
else:
    from PySide6 import QtGui
    from PySide6.QtWidgets import QWidget, QCheckBox, QDialog, QHBoxLayout, QVBoxLayout, QLabel, QTextEdit, QPushButton

log = logging.getLogger(__name__)

class Tip:
    def __init__(self, title, image, text):
        self.title = title
        self.image = image
        self.text  = text

    def __repr__(self):
        return f"DYK.Tip <{self.title}>"


class DidYouKnowFeature:
    """
    @verbatim
     ____________________________________________
    | WP)    Did You Know...?                [X] |  hb1
    |                                            |
    | The Tip Title                   #########  |  hb2
    |                                 #  Tip  #  |    vb21   lb_pic
    | The tip text goes here...       # Image #  |
    |                                 #########  |
    | [X] Show at start   [Next Tip]    Tip 1/5  |  hb3
    |____________________________________________|
    @endverbatim
    """

    def __init__(self, ctl):
        self.ctl = ctl

        self.create_dialog()
        self.create_tips()

    def display(self):
        if self.ctl.config.has_option("DidYouKnow", "show_at_startup"):
            if not self.ctl.config.get_bool("DidYouKnow"):
                log.debug("disabled")
                return

        # pick and display a random tip
        log.debug("picking tip")
        count = len(self.tips)
        if count < 1:
            log.debug("no tips")
            return

        i = random.randint(0, count-1)
        tip = self.tips[i]
        log.debug(f"picked {tip}")

        self.lb_title.setText(tip.title)
        self.te_text.setText(tip.text)
        self.lb_x_of_y.setText(f"Tip {i}/{count}")
        
        if tip.image:
            self.set_pixmap(lb_image, self.image)

        self.dialog.exec()

    def create_dialog(self):
        self.dialog = QDialog(parent=self.ctl.form)
        self.dialog.setModal(True)
        self.dialog.setWindowTitle("Did You Know...?")
        self.dialog.setSizeGripEnabled(True)

        lb_wp = QLabel("WP)", parent=self.dialog)
        self.set_pixmap(lb_wp, "WP")
        lb_dyk = QLabel("Did You Know...?", parent=self.dialog)
        lb_dyk.setStyleSheet("QLabel { font-size: 24px; font-weight: bold }")
        hb1_w = QWidget(parent=self.dialog)
        hb1 = QHBoxLayout(hb1_w)
        hb1.addWidget(lb_wp)
        hb1.addWidget(lb_dyk)

        self.lb_title = QLabel("placeholder", parent=self.dialog)
        self.te_text = QTextEdit(parent=self.dialog)
        vb_title_text_w = QWidget(parent=self.dialog)
        vb_title_text = QVBoxLayout(vb_title_text_w)
        vb_title_text.addWidget(self.lb_title)
        vb_title_text.addWidget(self.te_text)

        self.lb_image = QLabel("placeholder", parent=self.dialog)

        hb2_w = QWidget(parent=self.dialog)
        hb2 = QHBoxLayout(hb2_w)
        hb2.addWidget(vb_title_text_w)
        hb2.addWidget(self.lb_image)

        self.cb_show_at_startup = QCheckBox("Show at startup", parent=self.dialog)
        self.cb_show_at_startup.setChecked(True)
        self.cb_show_at_startup.stateChanged.connect(self.show_at_startup_callback)

        bt_next = QPushButton(parent=self.dialog)
        bt_next.setText("Next Tip")
        bt_next.clicked.connect(self.next_callback)

        self.lb_x_of_y = QLabel("Tip X/Y", parent=self.dialog)

        hb3_w = QWidget(parent=self.dialog)
        hb3 = QHBoxLayout(hb3_w)
        hb3.addWidget(self.cb_show_at_startup)
        hb3.addWidget(bt_next)
        hb3.addWidget(self.lb_x_of_y)

        vb_all = QVBoxLayout(self.dialog)
        vb_all.addWidget(hb1_w)
        vb_all.addWidget(hb2_w)
        vb_all.addWidget(hb3_w)

    def show_at_startup_callback(self):
        log.debug("show at startup clicked")
        self.ctl.config.set("DidYouKnow", "show_at_startup", not self.cb_show_at_startup.isChecked())

    def next_callback(self):
        log.debug("next clicked")

    def set_pixmap(self, label, name):
        pathname = f":/dyk/images/did_you_know/{name}.png"
        if self.ctl.image_resources.contains(pathname):
            label.setPixmap(QtGui.QPixmap(pathname))
        else:
            log.error(f"set_pixmap: unknown resource {pathname}")

    def create_tips(self):
        self.tips = []

        def tip(title, image, text):
            self.tips.append(Tip(title, image, text))

        tip("Keyboard Shortcuts", "keyboard_shortcuts", 'Mouse-over the "Help" button for an on-screen cheat-sheet of keyboard shortcuts.')
        tip("Quick Dark", None, "Use ctrl-D to quickly take a fresh dark, or to clear the current dark if stored.")
        tip("Quick Edit", None, "Use ctrl-E to quickly edit the last-saved measurement label.")
        tip("Jump Between Scope and Hardware", None, "Use ctrl-H to quickly jump between the Scope and Hardware views.")
