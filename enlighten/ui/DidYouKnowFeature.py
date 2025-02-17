import random
import logging

from enlighten import common

if common.use_pyside2():
    from PySide2 import QtGui
    from PySide2.QtWidgets import QWidget, QCheckBox, QDialog, QHBoxLayout, QVBoxLayout, QLabel, QTextBrowser, QPushButton
else:
    from PySide6 import QtGui
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

        tip("Keyboard Shortcuts", "keyboard_shortcuts", 'Mouse-over the "Help" button for an on-screen cheat-sheet of keyboard shortcuts.')
        tip("What's This?", "whats_this", """
         <p>Click the 'What's This' button ⓘ  to change your cursor into an arrow 
            with a ? next to it, then click another button or control you'd like
            to learn more about.</p>
         <p>What's This help goes deeper than normal mouse-overs, providing live
            instruction into advanced topics of spectroscopy and how to use your
            Wasatch spectrometer. It also provides a wealth of metadata and metrics
            about saved Measurements on your Clipboard!</p>""")
        tip("Quick Dark", "dark_bulb", """
            <p>Use ctrl-D to quickly take a fresh Dark, or to clear the current Dark if stored.</p>
            <p>No spoilers, but you can probably guess the shortcut for a fresh Reference :-)</p>""")
        tip("Quick Edit", "quick_edit", """
          <p>Use ctrl-E to quickly edit the last-saved measurement label.</p>
          <p>Keyboard shortcuts are intended to allow an adept user to quickly
             perform a number of data-collection tasks from the keyboard,
             such as:</p>
          <ul><li>ctrl-T to change integration time</li>
              <li>ctrl-N to edit the Note field (shift-tab and tab to edit Prefix/Postfix)</li>
              <li>ctrl-D twice, to clear and refresh the dark</li>
              <li>ctrl-L to enable the laser</li>
              <li>ctrl-S to save a new measurement</li>
              <li>ctrl-L again to disable the laser</li>
              <li>ctrl-E to edit the label of the last-saved measurement</li>
           </ul>""")
        tip("Open-Source", "github", """ENLIGHTEN™ is completely open-source, so 
             you're free to see how it works, run it on new platforms,
             and even make changes. Find it on GitHub at 
             <a href="https://github.com/WasatchPhotonics/ENLIGHTEN">WasatchPhotonics/ENLIGHTEN</a>.""")
        tip("Wavenumber Correction", "wavenumber_correction", """
            <p>Even the most assiduously calibrated laser or spectrometer can
               experience minor shifts in wavelength due to ambient changes in
               environment.</p>
            <p>ASTM E1840-96 (2022) specifies a procedure for daily, or even hourly
               correction of the Raman wavenumber axis. This is performed using one
               of eight approved reference samples, whose Raman peaks are measured
               and compared to expected locations. Any deltas are averaged together
               to create a temporary (session) offset to the wavenumber axis, improving
               accuracy of Raman peak locations in graphed and saved data.</p>
            <p>In addition to selecting your approved reference sample, you can
               optionally visualize the "expected" Raman peaks on the graph to compare
               against the measured spectrum, and to see which compound peaks are used
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
            <p>Wasatch spectrometers and ENLIGHTEN™ software try hard to make it extremely
               visible when your laser is firing: there is a red LED on the spectrometer
               housing, ENLIGHTEN™'s two Laser Enable buttons both turn red, and the "Light
               Source" virtual LED / Status Indicator in the lower-right corner turns a
               warning orange.</p>
            <p>However, sometimes your eyes are elsewhere whilst managing a complex measurement, and
               that's why we added an optional audible indicator as an added level of safety
               for those who wish it. Use the Settings view to opt-in to Audible Feedback if
               you prefer to hear that comforting warble to let you know when you're emitting.</p>""")
        tip("Copy Graph to Excel", "clipboard", """
            <p>Most graphs in ENLIGHTEN™, including the main Scope, have a 
               "clipboard" 📋 icon in the upper corner. You can click that at 
               any time (or just <b>hit Ctrl-C</b>) to copy all data from the 
               graph to the computer's system clipboard for copy-pasting between 
               applications.</p>
            <p>The copied data is tab-delimited, so can be pasted directly into 
               Microsoft Excel for quick processing and charting. If multiple 
               traces are visible on the graph, each are included in the 
               clipboard output as separate columns.</p>""")
        tip("Copy EEPROM to Excel", "clipboard", """
            <p>If you're juggling multiple spectrometers, it can be important to track the
               settings, configuration and calibration of each. The Hardware view in ENLIGHTEN™
               has a little 📋 clipboard icon atop the EEPROM contents, and clicking that will
               copy the entire table to your computer's system clipboard for copy-pasting into
               Excel, Notepad or other programs.</p>""")
        tip("Selective Export", "export_selected", """
            <p>When Exporting the ENLIGHTEN™ Clipboard of saved measurements to a "wide" CSV
               file, you can specify whether you wish to export the entire Clipboard, or just
               the measurements currently graphed on-screen.</p>""")
        tip("Graph Options", "chart_options", """
            <p>You can right-click on any graph in ENLIGHTEN™ to customize its grid, axes and 
               other features.</p>""")
        tip("Pan and Zoom on Trackpads", "zoom", """
            <p>All ENLIGHTEN™ graphs are easy enough to pan and zoom using a mouse while holding
               the right-mouse button. But what if you're on a laptop with a trackpad?</p>
            <p>Fortunately, you can still zoom and stretch your graph in two dimensions
               using trackpad gestures. Place the cursor over one of the graph axes, then
               control-drag (or two-finger drag) along the axis. The graph should zoom in or out
               in the indicated dimension, allowing you to see just the peak features you care
               about regardless of computing platform.</p>""")
        tip("Batch Collection 'Explain This'", "explain_this", """
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
        tip("Moveable Legend", "moveable_legend", """
            <p>The main Scope graph has a legend in the upper-left corner labeling each displayed
               graph trace. You can move that around the graph by dragging with a mouse, to avoid
               overwriting key peaks and spectral features, lining up the perfect screenshot.</p>""")
        tip("Resizable Clipboard and Control Palette", "screen_handles", """
            <p>We try to keep ENLIGHTEN™ usable on smaller screens and tablets, but there's so much
               detail we love to show! One way you can claw-back some screen real-estate is by grabbing
               invisible "handles" to the left and right of the Scope graph, and shrinking or growing the
               scrollable columns holding the Clipboard and Control Palette.</p>""")
        tip("Thermo Galactic SPC", "galactic", """
             <p>ENLIGHTEN™ can read and write spectra in the Thermo Galactic SPC format,
                used by Thermo Scientific GRAMS and other popular spectroscopy software.</p>""")
        tip("Boxcar Smoothing", "boxcar", """
             <p>Boxcar smoothing applies a lightweight spatial averaging convolution
                to remove high-frequency noise from your spectrum, at the cost of
                slightly reduced peak intensity and optical resolution (degraded
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
        tip("Scan Averaging", "scan_averaging", """
             <p>Scan averaging is one of the simplest yet most effective things
                you can do to increase Signal-to-Noise Ratio (SNR).</p>
             <p>As boxcar averages over <i>space</i>, scan averaging averages over <i>time</i>,
                averaging several samples together to reduce high-frequency noise
                and generate authentically smoothed spectra without compromising peak
                intensity or optical resolution (but at the cost of longer measurement
                operations and laser firing time).</p>
             <p>Setting averaging to 5 is a quick way to get a measurable boost 
                in effective signal. However, as SNR increases with the square
                root of the number of averages, you basically need to jump to 25 
                spectra to get the next noticable improvement in quality.</p>""")
        tip("Baseline Correction", "baseline_correction", """
             <p>Baseline correction (currently only accessible in Expert mode) allows 
                you to select one of several 3rd-party open-source algorithms to perform 
                an automated "baseline subtraction" from your spectra. Essentially this 
                can be used as a simple form of fluorescence removal.</p>
             <p>Although multiple algorithms are provided for your experimentation,
                <b>Wasatch recommends AirPLS for use with Raman spectroscopy.</b></p>
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
                the correction factors outside the configured ROI.</p>""")
        tip("Auto-Raman", "auto_raman_tricolor", """
             <p>Auto-Raman allows automated collection of optimized, averaged, dark-collected 
                Raman measurements with a single click.</p>
             <p>When taking an automatic Raman measurement, ENLIGHTEN will do the following:</p>
             <ol>
                <li><b>Enable the laser</b>, then allow the laser to stabilize.</li>
                <li><b>Optimize acquisition parameters</b> to achieve a configured "target counts"
                    in signal. This is done by first tuning integration time as "coarse adjustment,"
                    then fine-tuning analog gain as "fine adjustment" (on XS spectrometers).</li>
                <li><b>Optimize scan averaging</b> using the selected integration time and configured 
                    "maximum measurement time."</li>
                <li><b>Collect averaged Raman sample</b> measurements using the computed scan averaging.</li>
                <li><b>Disable the laser,</b> including a throwaway integration to allow the detector to stabilize.</li>
                <li><b>Collect averaged dark</b> measurement, using the same averaging and acquisition parameters.</li>
                <li><b>Perform dark-correction</b> using the averaged sample and dark measurements.</li>
                <li><b>Save</b> the new averaged, dark-corrected measurement to disk and the ENLIGHTEN Clipboard.</li>
                <li><b>Pause display</b> until "Play" is pressed to resume free-running spectra.</li>
             </ol>
             <p>Note that Auto-Raman measurements will automatically enable the laser
                during operation. While the measurement is being collected, the standard laser
                on/off buttons will be disabled, as the laser is being controlled by the Auto-Raman
                algorithm. If at any point you need to halt an Auto-Raman measurement, you can
                do so by clicking the "Stop" button on the VCR-style controls.</p>
             <p>Auto-Raman mode has a number of different options controlling its algorithm,
                configurable in Expert mode (ctrl-X). Those include the ability to configure
                automatic saving, and whether the optimized acquisition parameters and averaged
                dark are then "retained" for use by the ongoing ENLIGHTEN session.</p>""")
        tip("JSON Output", "json", """
             <p>ENLIGHTEN's CSV file formats are specifically designed for convenience in Excel
                and other spreadsheets. As such they are regrettably not terribly convenient for 
                automated parsing by scripts for post-processing. But that's okay, because we
                provide a format which is <b>great for post-processing</b> in the script language
                of your choice!</p>
             <p>You can enable JSON output in addition to (or instead of) standard CSV files,
                and each saved measurement will be stored in metadata-rich 
                <a href="https://en.wikipedia.org/wiki/JSON">JavaScript Object Notation</a>.
                In addition to individual measurements, Exports can also be stored in JSON.</p>""")
        tip("Prefix and Suffix", "prefix_suffix", """
             <p>Two of the most useful on-screen fields for manual data collections are <b>Prefix</b>
                and <b>Suffix</b>. As their name implies, they are automatically added at the beginning
                and end of saved filenames (both individual measurements, and exports).</p>
             <p>Although the related Note field does not automatically appear in any filenames or
                labels, it <i>can</i> be automatically inserted into those, anywhere you want, by using
                the <b>{note}</b> template notation.</p>""")
        tip("Library Matching", "library_matching", """
                <p>Loading the plugin for the first time will install the
                example library in your EnlightenSpectra/MatchingLibrary. You can check the current
                library path by moving the mouse over the Select Library button.
                Point the plugin to a different library by clicking on the Select Library button and
                navigating to a different library folder. A red Select Library button indicates that a
                library is loaded.</p>
             <p>A display of the best-match library spectrum will be overlaid onto the matched sample
                spectrum and labelled as Library Spectrum. The plugin continuously matches the latest
                spectrum shown in the graph window against the library.</p>
             <p>A list of multiple top match results above the minimum score threshold is shown as a table
                below the spectra. The number of top matches shown in this table can be adjusted in the field
                next to Max. Results. Increasing the minimum score threshold will reduce False Positive Rate,
                but potentially increase False Negative Rate.</p>
             <p>To add the current spectrum to the library, click Save to Library. A small box opens
                asking for the compound name to be used in the library for this compound. Enter the name of the
                compound and click OK. The spectrum will be saved to the (user) library and is automatically
                available for matching. All user spectra are saved to the folder EnlightenSpectra/MatchingLibrary/AdditionalSpectra.</p>""")
        tip("Raman Lines", "raman_lines", """
             <p><b>Raman.RamanLines</b> is a built-in "sample" plugin, showing some of the fun and 
                useful things you can do with ENLIGHTEN's Python-based plug-in architecture.</p>
             <p>In this case, it provides a list of common chemicals spectroscopists often have
                at hand, with the Raman lines for each. If you Enable the plugin you can select
                one or more compounds to see their Raman lines graphed against your spectrum.
                (Make sure you've selected the <b>wavenumber</b> x-axis.)</p>
             <p>This can be a quick way to confirm "What is that unlabeled vial on my desk," or
                perhaps "Is that white plastic bottle HDPE or PTFE?" Plus you can always open up
                the source code in <tt>EnlightenSpectra/plugins/Raman/RamanLines.py</tt> to see how easy
                it is to write your own!</p>""")
        tip("Emission Lines", "emission_lines", """
             <p><b>Prod.EmissionLines</b> is a built-in "sample" plugin, showing some of the fun and 
                useful things you can do with ENLIGHTEN's Python-based plug-in architecture.</p>
             <p>In this case, it provides a list of noble gases often used in spectroscopy for 
                wavelength calibration, with atomic emission lines for each. If you Enable the plugin 
                you can select one or more gases to see their emission lines graphed against your spectrum.
                (Make sure you've selected the <b>wavelength</b> x-axis.)</p>
             <p>This can be a quick way to sanity-check "Is my wavelength calibration reasonable?"
                or maybe "I wonder how much argon is in these room lights?" Plus you can always open up
                the source code in <tt>EnlightenSpectra/plugins/Prod/EmissionLines.py</tt> to see how easy
                it is to write your own!</p>""")
        tip("Analysis.Stats", "stats", """
             <p><b>Analysis.Stats</b> is a built-in "sample" plugin, showing some of the fun and 
                useful things you can do with ENLIGHTEN's Python-based plug-in architecture.
                In this case, it adds min/max/mean traces to your spectral graph, showing the 
                highs, low, and average data over time. (Click "Reset" to clear previous data.)</p>
             <p>Since those metrics can be tracked with no additional memory (there's no need to store 
                each spectrum), this plugin can be left running for hours while you monitor a long-term 
                process, and you can come back later to see if anything unexpected happened while you 
                were away.  Plus you can always open up
                the source code in <tt>EnlightenSpectra/plugins/Analysis/Stats.py</tt> to see how easy
                it is to write your own!</p>""")
        tip("Analysis.StatsBuffer", "stats_buffer", """
             <p><b>Analysis.StatsBuffer</b> is a built-in "sample" plugin, showing some of the fun and 
                useful things you can do with ENLIGHTEN's Python-based plug-in architecture.
                In this case, it adds min, max, mean, median, mode and standard deviation traces 
                to your spectral graph.</p>
             <p>This plugin differs from the similarly-named "Analysis.Stats" in that several of these
                metrics require "history" for computation. Therefore, you can set the "history" buffer
                size, see how close it is to filling, and empty it at any time.  Plus you can always 
                open up the source code in <tt>EnlightenSpectra/plugins/Analysis/StatsBuffer.py</tt> 
                to see how easy it is to write your own!</p>""")
        tip("Ctrl-Up/Down Arrows", None, """
             <p>You probably know you can change numeric values with the up/down arrow keys when
                you've selected a numeric field. You can also use Ctrl-Up/Down to change the values
                in larger jumps!</p>""")
        
        # collated
        # Edit ROI (lock axes)
        # Themes, Light Mode
        # Horizontal ROI
        # Save/Export JSON

        tip("Template Macros", None, """
            <p>In the Settings view, configure template macros like <tt>{integration_time_ms}ms
               {gain_db}dB {scans_to_average}avg {note}</tt> as default Clipboard labels or measurement filenames.</p>
            <p>(Note that template fields can be used in Prefix, Suffix and Note fields as well.)</p>
            <p>Virtually any ENLIGHTEN variable name or property can be referenced...here are a few to start.</p>

            <h3>SpectrometerState</h3>

            <li>area_scan_enabled        <li>area_scan_fast            <li>battery_charging
            <li>battery_percentage       <li>battery_raw               <li>boxcar_half_width
            <li>fan_enabled              <li>gain_db                   <li>high_gain_mode_enabled
            <li>integration_time_ms      <li>lamp_enabled              <li>laser_enabled
            <li>laser_power_mW           <li>laser_power_perc          <li>mod_enabled
            <li>mod_period_us            <li>mod_width_us              <li>region
            <li>scans_to_average         <li>shutter_enabled           <li>tec_enabled
            <li>tec_setpoint_degC        <li>trigger_source            <li>use_mW
            <li>wavenumber_correction

            <h3>EEPROM</h3>

            <li>active_pixels_horizontal <li>active_pixels_vertical    <li>avg_resolution
            <li>horiz_binning_enabled    <li>cutoff_filter_installed   <li>detector
            <li>detector_gain            <li>detector_offset           <li>excitation_nm_float
            <li>has_battery              <li>has_cooling               <li>has_laser
            <li>laser_warmup_sec         <li>max_laser_power_mW        <li>min_integration_time_ms
            <li>min_laser_power_mW       <li>min_temp_degC             <li>model
            <li>roi_horizontal_end       <li>roi_horizontal_start      <li>serial_number
            <li>slit_size_um

            <h3>Reading</h3>

            <li>device_id                <li>timestamp                 <li>timestamp_complete
            <li>laser_enabled            <li>laser_temperature_raw     <li>laser_temperature_degC
            <li>detector_temperature_raw <li>detector_temperature_degC <li>ambient_temperature_degC
            <li>laser_power_perc         <li>laser_power_mW            <li>averaged
            <li>session_count            <li>battery_raw               <li>battery_percentage
            <li>battery_charging         <li>laser_can_fire            <li>laser_is_firing

            <h3>Measurement Metadata</h3>

            <p><i>(These are the same fields saved at the top of CSV measurement files…note space rather than underscore)</i></p>

            <li>model                   <li>label                      <li>detector
            <li>boxcar                  <li>timestamp                  <li>note
            <li>temperature             <li>technique                  <li>vignetted
            <li>interpolated            <li>deconvolved                <li>region

            <li>enlighten version                <li>laser wavelength
            <li>measurement id                   <li>laser enable
            <li>serial number                    <li>laser temperature
            <li>scan averaging                   <li>pixel count
            <li>integration time                 <li>declared match
            <li>baseline correction algo         <li>declared score
            <li>ccd c0                           <li>roi pixel start
            <li>ccd c1                           <li>roi pixel end
            <li>ccd c2                           <li>raman intensity corrected
            <li>ccd c3                           <li>slit width
            <li>ccd c4                           <li>wavenumber correction
            <li>ccd offset                       <li>battery %
            <li>ccd gain                         <li>fw version
            <li>ccd offset odd                   <li>fpga version
            <li>ccd gain odd                     <li>laser power %
                                                 <li>laser power mw""")

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
        self.lb_title.setStyleSheet("font-size: 18px; font-weight: bold")

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

        bt_next = QPushButton(parent=self.dialog)
        bt_next.setText("Next")
        bt_next.clicked.connect(self.next_callback)

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
