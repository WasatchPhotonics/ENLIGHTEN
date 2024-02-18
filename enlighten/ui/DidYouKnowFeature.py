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
    """ Different than GuideFeature.Tip """
    def __init__(self, title, image, text):
        self.title = title
        self.image = image
        self.text  = text

    def __repr__(self):
        return f"DYK.Tip<{self.title}>"

class DidYouKnowFeature:
    """
    This class provides a pop-up dialog when ENLIGHTEN launches, informing the
    user of new or lesser-known features they might otherwise not stumble across
    or notice in the GUI or manual.

    It is unrelated to the GuideFeature, which displays contextual tips on the 
    Marquee during measurement operations.

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

        # Note: tips are displayed as HTML, so whitespace will be normalized

        tip("Keyboard Shortcuts", "keyboard_shortcuts", 'Mouse-over the "Help" button for an on-screen cheat-sheet of keyboard shortcuts.')
        tip("What's This?", "whats_this", """<p>Click the 'What's This' button ⓘ  to change your cursor into an arrow with a ? next to it, 
            then click another button or control you'd like to learn more about.</p><p>What's This help goes deeper than normal mouse-overs, 
            providing live instruction into advanced topics of spectroscopy and how to use your Wasatch spectrometer.</p>""")
        tip("Quick Dark", None, "Use ctrl-D to quickly take a fresh dark, or to clear the current dark if stored.")
        tip("Quick Edit", None, "Use ctrl-E to quickly edit the last-saved measurement label.")
        tip("Jump Between Scope and Hardware", None, "Use ctrl-H to quickly jump between the Scope and Hardware views.")
        tip("Open-Source", "github", """ENLIGHTEN™ is completely open-source, so you're free to see how it works, run it on new platforms, 
            and even make changes. Find it on GitHub at <a href="https://github.com/WasatchPhotonics/ENLIGHTEN">WasatchPhotonics/ENLIGHTEN</a>.""")
        tip("Template Macros", None, """
            <p>Use template macros like <span style="font-family:monospace; color:yellow">{integration_time_ms}ms 
            {gain_db}dB {scans_to_average}avg</span> as the default Clipboard labels or filenames of new measurements.</p>
            <p>Virtually any ENLIGHTEN variable name or property can be referenced. See the manual for a list of supported macros.</p>""")
        tip("Wavenumber Correction", "wavenumber_correction", """
            <p>Even the most assiduously calibrated laser or spectrometer can 
               experience minor shifts in wavelength due to ambient changes in 
               environment.</p>
            <p>ASTM E1840-96 (2014) specifies a procedure for daily, or even hourly
               correction of the Raman wavenumber axis. This is performed using one
               of eight approved reference samples, whose Raman peaks are measured
               and compared to expected locations. Any deltas are averaged together
               to create a temporary (session) offset to the wavenumber axis, improving
               accuracy of Raman peak locations in graphed and saved data.</p>
            <p>In addition to selecting your approved reference sample, you can 
               optionally visualize the "expected" Raman peaks on the graph to compare
               against the measured spectrum, and to see which sample peaks are used
               in the correction. The computed offset is briefly displayed on-screen,
               and is saved in measurement metadata (as well as the updated wavenumber
               axis.)</p>
            <p>Users interested in maximizing Raman signal reproducibility across time
               and across units are recommended to perform this procedure at the 
               beginning of every ENLIGHTEN session, or even more often if temperature
               is in flux.</p>
            <p>This is a key step in ensuring reproducible Raman measurements across
               samples, units, operators and time. Read our full <a 
               href="https://wasatchphotonics.com/technologies/reproducible-raman-measurements/">Tech
               Note: Reproducible Raman Measurements</a> for additional information.</p>""")

        # @todo
        # SRM
        # plugins
        # startup plugin
        # Exact laser wavelength
        # Right-scroll in graph axes
        # Right-click graph
        # Copy spectra to Excel
        # Copy EEPROM to Excel
        # Selective Export
        # Edit ROI (lock axes)
        # Laser Sound Effects
        # Batch Collection Explain This
        # Choose StatusBar fields
        # read/write SPC
        # Themes, Light Mode
        # RamanLines
        # Stats, StatsBuffer
        # EmissionLines
        # Horizontal ROI
        # Scan Averaging
        # Boxcar
        # Baseline Correction
        # Drag Legend
        # Save/Export JSON
        # Resize Clipboard and Control Palette
        # Raman Mode

        # present tips in random order each time
        random.shuffle(self.tips)


    def __init__(self, ctl):
        self.ctl = ctl

        self.index = 0
        self.startup_key = f"show_at_startup_{common.VERSION}"

        self.create_dialog()
        self.create_tips()

    def show(self):
        # force user to re-reject tips on each version
        if self.ctl.config.has_option("DidYouKnow", self.startup_key):
            if not self.ctl.config.get_bool("DidYouKnow", self.startup_key):
                log.debug("disabled")
                return

        if self.tips:
            self.update_dialog()
            self.dialog.exec()

    def next_callback(self):
        self.index = (self.index + 1) % len(self.tips)
        self.update_dialog()

    def update_dialog(self):
        if not (0 <= self.index < len(self.tips)):
            return

        tip = self.tips[self.index]
        counter = f"Tip {self.index+1}/{len(self.tips)}"
        log.debug(f"displaying {counter}: {tip}")

        self.lb_title.setText(tip.title)
        self.tb_text.setHtml(tip.text)
        self.lb_x_of_y.setText(counter)

        if tip.image:
            self.set_pixmap(self.lb_image, tip.image)
        else:
            self.lb_image.clear()

    def show_at_startup_callback(self):
        self.ctl.config.set("DidYouKnow", self.startup_key, self.cb_show_at_startup.isChecked())

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
        self.tb_text.document().setDefaultStyleSheet("a { color: #27c0a1 }") 

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
