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
        tip("Wavenumber Correction", "wavenumber_correction2", """
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
        tip("Laser Wavelength Precision", "laser_wavelength", """
            <p>Wasatch spectrometers with an integrated laser include a factory-calibrated 
               laser excitation wavelength stored in the EEPROM to picometer precision.
               However, if you are using external lasers, you may need to tell ENLIGHTEN
               the exact wavelength of your laser to ensure the wavenumber axis is computed
               accurately. You can do this in Expert mode, which adds a "Wavenumber" control
               to the Laser Control panel in 0.001nm precision.</p>""")
        tip("Audible Laser Warning", "ear", """
            <p>Wasatch spectrometers and ENLIGHTEN™ softwae try hard to make it extremely
               visible when your laser is firing: there is a red LED on the spectrometer
               housing, ENLIGHTEN™'s two Laser Enable buttons both turn red, and the "Light 
               Source" virtual LED / Status Indicator in the lower-right corner turns a 
               warning orange.</p>
            <p>However, sometimes your eyes are elsewhere while managing a measurement, and
               that's why we added an optional audible indicator as an added level of safety
               for those who wish it. Use the Settings view to opt-in to Sound Effects if
               you prefer to hear that comforting warble to let you know when you're emitting.</p>""")
        tip("Copy Graph to Excel", "clipboard", """
            <p>Most graphs in ENLIGHTEN™, including the main Scope, have a "clipboard" 📋 icon
               in the upper corner. You can tap that at any time to copy all data from the graph
               to the computer's system clipboard for copy-pasting between applications. The
               copied data is tab-delimited, so can be pasted directly into Microsoft Excel for
               quick processing and charting. If multiple traces are visible on the graph, each
               are included in the clipboard output as separate columns.</p>""")
        tip("Copy EEPROM to Excel", "clipboard", """
            <p>If you're juggling multiple spectrometers, it can be important to track the 
               settings, configuration and calibration of each. The Hardware view in ENLIGHTEN™
               has a little 📋 clipboard icon atop the EEPROM contents, and clicking that will
               copy the entire table to your computer's system clipboard for copy-pasting into
               Excel, Notepad or other programs.</p>""")
        tip("Selective Export", None, """
            <p>When Exporting the ENLIGHTEN™ Clipboard of saved measurements to a "wide" CSV 
               file, you can specify whether you wish to export the entire Clipboard, or just 
               the measurements currently graphed on-screen.</p>""")
        tip("Right-Click Graph", "chart_options", """
            <p>The main Scope graph in ENLIGHTEN™ -- every graph in the program, for that matter --
               can be customized by right-clicking.</p>""")
        tip("Pan and Zoom on Trackpads", None, """
            <p>All ENLIGHTEN™ graphs are easy enough to pan and zoom using a mouse while holding
               the right-click button. But what if you're on a laptop with a trackpad?</p>
            <p>Fortunately, you can still zoom and stretch your graph in two dimensions
               using trackpad gestures. Place the cursor over one of the graph axes, then
               control-drag (or two-finger drag) along the axis. The graph should zoom in or out
               in the indicated dimension, allowing you to see just the peak features you care
               about regardless of computing platform.</p>""")
        tip("Batch Collection 'Explain This'", None, """
            <p>Batch Collection settings can get pretty complex -- it's a flexible feature, 
               with many configurable delays and options, and sometimes it's hard to remember
               exactly what each field does and how that will affect the series of measurements.</p>
            <p>There's a link on the Batch Collection setup panel called "Explain This," and if
               you mouse-over it, it will display a tooltip explaining, in plain narrative prose,
               how the resulting measurement will occur, with each step tied back to the settings
               you entered.</p>""")
        tip("Status Bar Fields", "status_bar_menu", """
            <p>Below the main Scope graph is a Status Bar with key summary fields for the spectra 
               and spectrometer displayed: peak intensity, detector temperature, cursor value, etc.</p>
            <p>You can customize which fields are displayed using the "..." menu at the right end 
               of the Status Bar. This will show additional fields not included by default, and let
               you disable fields you don't need or use.</p>""")
        tip("Moveable Legend", None, """
            <p>The main Scope graph has a legend in the upper-left corner labeling each displayed
               graph trace. You can move that around the graph by dragging with a mouse, to avoid
               overwriting key peaks and spectral features.</p>""")
        tip("Resizable Clipboard and Control Palette", "screen_handles", """
            <p>We try to keep ENLIGHTEN™ usable on smaller screens and tablets, but there's so much
               detail we love to show! One way you can claw-back some screen real-estate is by grabbing
               invisible "handles" to the left and right of the Scope graph, and shrinking or growing the
               scrollable columns holding the Clipboard and Control Palette.</p>""")
        tip("Thermo Galactic SPC", "galactic", """
             <p>ENLIGHTEN™ can read and write spectra in the Thermo Galactic SPC format, 
                used by Thermo Scientific GRAMS and other popular spectroscopy software.</p>""")
        tip("Boxcar Smoothing", None, """
             <p>Boxcar smoothing applies a lightweight spatial averaging convolution
                to remove high-frequency noise from your spectrum, at the cost of
                slightly reduced peak intensity and optical resolution (increased
                effective FWHM).</p>
             <p>It can be useful to quickly make spectra "prettier" and improve 
                "apparent SNR" for human viewers, but is a lossy transformation 
                which rarely improves fundamental data quality. It can be useful
                in some types of peak-finding, by eliminating low-magnitude noise
                peaks.</p>
             <p>Note that boxcar is applied in pixel space, and does not account for the 
                non-linearity inherent in calibrated wavelength or wavenumber axes.</p>
             <p>Typical values may be 1 or 2 for Raman, or up to 10 for non-Raman
                with broad spectral features.</p>""")
        tip("Scan Averaging", None, """
             <p>Scan averaging is one of the simplest yet most effective things 
                you can do to increase Signal-to-Noise Ratio (SNR).</p>
             <p>As boxcar averages over <i>space</i>, scan averaging averages over <i>time</i>,
                averaging several samples together to reduce high-frequency noise
                and generate authentically smoothed spectra without compromising peak 
                intensity or optical resolution (but at the cost of longer measurement
                operations and laser firing time).</p>
             <p>Setting averaging to 5 is a quick way to get a measurable boost in
                effective signal. However, as signal is measured on a logarithmic
                scale, you basically need to jump to 25 spectra to get the next 
                noticable improvement in quality.</p>""")
        tip("Baseline Correction", None, """
             <p>Baseline correction allows you to select one of several 3rd-party
                open-source algorithms to perform an automated "baseline subtraction"
                from your spectra. Essentially this can be used as a simple form of
                fluorescence removal.</p>
             <p>Although multiple algorithms are provided for your experimentation,
                Wasatch recommends AirPLS for use with Raman spectroscopy.</p>
             <p>You can optionally check the "show curve" option to see the 
                computed baseline as generated by each of the different 
                baseline algorithms.</p>
             <p>If you have a better (open-source) baseline-correction algorithm 
                you'd like to see supported in ENLIGHTEN, please contact us!</p>""")
        tip("Raman Intensity Correction", "raman_intensity_correction", """
             <p>Raman Intensity Correction uses an EEPROM-stored calibration, 
                generated in the factory with NIST SRM standards, to correct 
                intensity (y-axis) on Raman spectra. This is sometimes just 
                called "SRM correction".</p>
            <p>Raman Intensity Correction is one of the most important steps you can
               take to maximize repeatability in Raman signal across instruments, time
               and operators. For more information, read our <a
               href="https://wasatchphotonics.com/technologies/reproducible-raman-measurements/">Tech
               Note"</a> on repeatable Raman measurements.</p>
             <p>ENLIGHTEN™ only allows you enable Raman Intensity Correction when
                in Raman or Expert mode, as it is only applicable to Raman spectra.
                Raman Intensity Correction also requires a dark spectrum to be stored.
                Therefore, when Raman Intensity Correction is enabled, you cannot
                clear your dark; you must first disable Raman Intensity Correction
                before clearing and refreshing your dark, then re-enabling it after.</p>
             <p>Finally, Raman Intensity Correction requires that the horizontal
                ROI be enabled. This is because NIST SRM standards are only certified
                within a given spectral range, and it would be invalid to extrapolate
                the correction factors outside the configured ROI.</p>
             <p>As a simple visual "sanity-check" of the correction factors generated
                from the SRM calibration coefficients, you can enable a normalized 
                graph trace indicating how the calibration changes over the detector.
                Typically, this will resemble a "U"-shaped parabola, with higher
                scaling factors at the edges of the detector, and curving lower
                toward the center.</p>""")

        # plugins
        # startup plugin
        # Edit ROI (lock axes)
        # Themes, Light Mode
        # RamanLines
        # Stats, StatsBuffer
        # EmissionLines
        # Horizontal ROI
        # Save/Export JSON
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

    def prev_callback(self):
        self.index -= 1
        if self.index < 0:
            self.index = len(self.tips) - 1
        self.update_dialog()

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

        hbox1_w = QWidget(parent=self.dialog)
        hbox1 = QHBoxLayout(hbox1_w)
        hbox1.addWidget(lb_wp)
        hbox1.addWidget(lb_dyk)
        hbox1.addStretch()

        ########################################################################
        # Middle Row
        ########################################################################

        # left column
        self.lb_title = QLabel("placeholder", parent=self.dialog)
        self.lb_title.setStyleSheet("font-weight: bold")

        self.tb_text = QTextBrowser(parent=self.dialog)
        self.tb_text.setOpenExternalLinks(True)
        self.tb_text.document().setDefaultStyleSheet("a { color: #27c0a1 }") 

        vbox_left_w = QWidget(parent=self.dialog)
        vbox_left = QVBoxLayout(vbox_left_w)
        vbox_left.addWidget(self.lb_title)
        vbox_left.addWidget(self.tb_text)

        # right column
        self.lb_image = QLabel("placeholder", parent=self.dialog)

        hbox2_w = QWidget(parent=self.dialog)
        hbox2 = QHBoxLayout(hbox2_w)
        hbox2.addWidget(vbox_left_w)
        hbox2.addWidget(self.lb_image)

        ########################################################################
        # Bottom Row
        ########################################################################

        self.cb_show_at_startup = QCheckBox("Show at startup", parent=self.dialog)
        self.cb_show_at_startup.setChecked(True)
        self.cb_show_at_startup.stateChanged.connect(self.show_at_startup_callback)

        bt_prev = QPushButton(parent=self.dialog)
        bt_prev.setText("Prev")
        bt_prev.clicked.connect(self.prev_callback)
        # bt_prev.setFixedSize(QtCore.QSize(50, 30))

        bt_next = QPushButton(parent=self.dialog)
        bt_next.setText("Next")
        bt_next.clicked.connect(self.next_callback)
        # bt_next.setFixedSize(QtCore.QSize(50, 30))

        self.lb_x_of_y = QLabel("Tip X/Y", parent=self.dialog)

        hbox3_w = QWidget(parent=self.dialog)
        hbox3 = QHBoxLayout(hbox3_w)
        hbox3.addWidget(self.cb_show_at_startup)
        hbox3.addStretch()
        hbox3.addWidget(bt_prev)
        hbox3.addWidget(bt_next)
        hbox3.addStretch()
        hbox3.addWidget(self.lb_x_of_y)

        vbox_all = QVBoxLayout(self.dialog)
        vbox_all.addWidget(hbox1_w)
        vbox_all.addWidget(hbox2_w)
        vbox_all.addWidget(hbox3_w)
