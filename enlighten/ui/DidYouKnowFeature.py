import random
import logging

from enlighten import common

if common.use_pyside2():
    from PySide2 import QtGui, QtCore
    from PySide2.QtWidgets import QWidget, QCheckBox, QDialog, QHBoxLayout, QVBoxLayout, QLabel, QTextBrowser, QPushButton
else:
    from PySide6 import QtGui, QtCore
    from PySide6.QtWidgets import QWidget, QCheckBox, QDialog, QHBoxLayout, QVBoxLayout, QLabel, QTextBrowser, QPushButton

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
    | WP)    Did You Know...?                [X] |
    |                                            |
    | The Tip Title                   #########  |
    |                                 #  Tip  #  |
    | The tip text goes here...       # Image #  |
    |                                 #########  |
    | [X] Show at start   [Next Tip]    Tip 1/5  |
    |____________________________________________|
    @endverbatim
    """
    def create_tips(self):
        self.tips = []

        def tip(title, image, text):
            self.tips.append(Tip(title, image, text))

        tip("Keyboard Shortcuts", "keyboard_shortcuts", 'Mouse-over the "Help" button for an on-screen cheat-sheet of keyboard shortcuts.')
        tip("What's This?", "whats_this", "<p>Click the 'What's This' button ⓘ  to change your cursor into an arrow with a ? next to it, then click another button or control you'd like to learn more about.</p><p>What's This help goes deeper than normal mouse-overs, providing live instruction into advanced topics of spectroscopy and how to use your Wasatch spectrometer.</p>")
        tip("Quick Dark", None, "Use ctrl-D to quickly take a fresh dark, or to clear the current dark if stored.")
        tip("Quick Edit", None, "Use ctrl-E to quickly edit the last-saved measurement label.")
        tip("Jump Between Scope and Hardware", None, "Use ctrl-H to quickly jump between the Scope and Hardware views.")
        tip("Open-Source", "github", """ENLIGHTEN™ is completely open-source, so you're free to see how it works, run it on new platforms, and even make changes. Find it on GitHub at <a href="https://github.com/WasatchPhotonics/ENLIGHTEN">WasatchPhotonics/ENLIGHTEN</a>.""")

    def __init__(self, ctl):
        self.ctl = ctl

        self.index = 0

        self.create_dialog()
        self.create_tips()

    def show(self):
        if self.ctl.config.has_option("DidYouKnow", "show_at_startup"):
            if not self.ctl.config.get_bool("DidYouKnow"):
                log.debug("disabled")
                return

        # pick and display a random tip
        count = len(self.tips)
        if count < 1:
            log.debug("no tips")
            return

        self.index = random.randint(0, count-1)
        self.update_dialog()
        self.dialog.exec()

    def next_callback(self):
        log.debug("next tip: was {self.index}")
        self.index = (self.index + 1) % len(self.tips)
        self.update_dialog()

    def update_dialog(self):
        if not (0 <= self.index < len(self.tips)):
            return

        tip = self.tips[self.index]
        counter = f"Tip {self.index+1}/{len(self.tips)}"
        log.debug(f"displaying counter: {tip}")

        self.lb_title.setText(tip.title)
        self.tb_text.setHtml(tip.text)
        self.lb_x_of_y.setText(counter)

        if tip.image:
            self.set_pixmap(self.lb_image, tip.image)
        else:
            self.lb_image.clear()

    def show_at_startup_callback(self):
        log.debug("show at startup clicked")
        self.ctl.config.set("DidYouKnow", "show_at_startup", not self.cb_show_at_startup.isChecked())

    def set_pixmap(self, label, name):
        pathname = f":/dyk/images/did_you_know/{name}.png"
        if self.ctl.image_resources.contains(pathname):
            label.setPixmap(QtGui.QPixmap(pathname))
        else:
            log.error(f"set_pixmap: unknown resource {pathname}")

    def create_dialog(self):
        self.dialog = QDialog(parent=self.ctl.form)
        self.dialog.setModal(True)
        self.dialog.setWindowTitle("Did You Know...?")
        self.dialog.setSizeGripEnabled(True)

        ########################################################################
        # Top Row
        ########################################################################

        lb_wp = QLabel("WP)", parent=self.dialog)
        self.set_pixmap(lb_wp, "WP")
        lb_dyk = QLabel("Did You Know...?", parent=self.dialog)
        lb_dyk.setStyleSheet("font-size: 24px; font-weight: bold")

        hb1_w = QWidget(parent=self.dialog)
        hb1 = QHBoxLayout(hb1_w)
        hb1.addWidget(lb_wp)
        hb1.addWidget(lb_dyk)
        hb1.addStretch()

        ########################################################################
        # Middle Row
        ########################################################################

        # left column
        self.lb_title = QLabel("placeholder", parent=self.dialog)
        self.lb_title.setStyleSheet("font-weight: bold")
        self.tb_text = QTextBrowser(parent=self.dialog)
        self.tb_text.setOpenExternalLinks(True)

        vb_title_text_w = QWidget(parent=self.dialog)
        vb_title_text = QVBoxLayout(vb_title_text_w)
        vb_title_text.addWidget(self.lb_title)
        vb_title_text.addWidget(self.tb_text)

        # right column
        self.lb_image = QLabel("placeholder", parent=self.dialog)

        hb2_w = QWidget(parent=self.dialog)
        hb2 = QHBoxLayout(hb2_w)
        hb2.addWidget(vb_title_text_w)
        hb2.addWidget(self.lb_image)

        ########################################################################
        # Bottom Row
        ########################################################################

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
        hb3.addStretch()
        hb3.addWidget(bt_next)
        hb3.addStretch()
        hb3.addWidget(self.lb_x_of_y)

        vb_all = QVBoxLayout(self.dialog)
        vb_all.addWidget(hb1_w)
        vb_all.addWidget(hb2_w)
        vb_all.addWidget(hb3_w)
