import re
import os
import shutil
import pandas as pd
import logging

from PySide6 import QtWidgets
from functools import cmp_to_key
from scipy.stats import pearsonr
from scipy.interpolate import interp1d

from enlighten import common
from enlighten.EnlightenFeature import EnlightenFeature

from wasatch.CSVLoader import CSVLoader

if common.use_pyside2():
    from PySide2 import QtCore, QtWidgets
else:
    from PySide6 import QtCore, QtWidgets

log = logging.getLogger(__name__)

class LibraryMatchingFeature(EnlightenFeature):
    """
    @todo This is currently oriented toward Raman (defaulting to wavenumbers), 
          but there's no reason it couldn't also support wavelengths for non-Raman 
          (absorbance etc).
    """

    SECTION = "LibraryMatching"

    # this is the path, under "enlighten.exe", where ENLIGHTEN looks to find the
    # "distribution" matching library that "comes with" ENLIGHTEN via source or 
    # binary distributions
    DIST_LIBRARY_DIR = "enlighten/assets/example_data/matching_library"

    # this is the default directory where ENLIGHTEN will write (and check for) 
    # user-generated library spectra
    DEFAULT_USER_LIBRARY_DIR = os.path.join(common.get_default_data_dir(), "matching_library")

    TIMER_MS = 10 # tick graph update this long after match results

    def __init__(self, ctl):
        super().__init__(ctl)

        cfu = self.ctl.form.ui

        self.cb_enable          = cfu.checkBox_library_matching_enable
        self.bt_select_library  = cfu.pushButton_library_matching_select_library
        self.lb_compound        = cfu.label_library_matching_matched_compound_name
        self.lb_score           = cfu.label_library_matching_matched_compound_score
        self.ds_min_score       = cfu.doubleSpinBox_library_matching_min_score
        self.sb_max_results     = cfu.spinBox_library_matching_max_results
        self.cb_use_dist        = cfu.checkBox_library_matching_use_dist
        self.bt_save            = cfu.pushButton_library_matching_save_to_library

        # TODO: figure out what to do with Pandas
        self.df_results = None 

        # start with defaults
        self.enabled = False
        self.dist_library_dir = self.DIST_LIBRARY_DIR
        self.user_library_dir = self.DEFAULT_USER_LIBRARY_DIR
        self.min_score = 0.65
        self.max_results = 2
        self.use_dist = True

        log.debug(f"defaulting to dist_library_dir {self.dist_library_dir}")
        log.debug(f"defaulting to user_library_dir {self.user_library_dir}")

        self.init_from_ini()

        self.pearson = Pearson(self)

        self.set_library_dir(self.user_library_dir)

        # connect callbacks after initialization
        self.bt_select_library  .clicked        .connect(self.select_library_callback)
        self.bt_save            .clicked        .connect(self.add_to_library)
        self.ds_min_score       .valueChanged   .connect(self.update_settings)
        self.sb_max_results     .valueChanged   .connect(self.update_settings)
        self.cb_use_dist        .stateChanged   .connect(self.update_settings)
        self.cb_enable          .stateChanged   .connect(self.update_settings)

       #self.bt_select_library  .setToolTip("Select a directory containing a library of Raman spectra")
        self.bt_save            .setToolTip("Add the current spectrum to the matching library")
        self.lb_compound        .setToolTip("Declared matching compound (highest matching score)")
        self.lb_score           .setToolTip("The RamanID algorithm's computed score for the top-matching compound")
        self.ds_min_score       .setToolTip("Only report matches with this score or above")
        self.sb_max_results     .setToolTip("Only report this many matches")
        self.cb_use_dist        .setToolTip("Use standard ENLIGHTEN compound library in addition to user-collected spectra")
        self.cb_enable          .setToolTip("Perform Pearson Library Matching against measured spectra")

        self.add_next_to_library = False
        self.metadata_cache = {}
        self.laser_warning_issued = False

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.tick)
        self.timer.setSingleShot(True)

        self.ctl.measurement_factory.register_observer(self.factory_callback)

        # note that this curve is in the SCOPE Graph...we still need to add one in the DalaiRamanFeature Graph
        self.curve_scope = self.ctl.graph.add_curve("library_spectrum", 
                                                    rehide=False, 
                                                    in_legend=False, 
                                                    pen='#2994d3')
        self.curve_scope.setVisible(False)

    def disconnect(self):
        self.ctl.measurement_factory.unregister_observer(self.factory_callback)
        super().disconnect()

    def stop(self):
        self.timer.stop()

    def update_settings(self):
        self.min_score = self.ds_min_score.value()
        self.max_results = self.sb_max_results.value()
        self.use_dist = self.cb_use_dist.isChecked()
        self.enabled = self.cb_enable.isChecked()

    def tick(self):
        self.lb_compound.setText(self.last_compound)
        self.lb_score.setText(f"{self.last_score:0.2f}" if self.last_score is not None else "")

    def process(self, pr):
        if not self.enabled:
            return

        wavenumbers = pr.get_wavenumbers()
        spectrum = pr.get_processed()
        reading = pr.reading

        if self.ctl.page_nav.doing_raman() and not reading.laser_enabled and not self.laser_warning_issued:
            self.ctl.marquee.error("LibraryMatching in Raman mode requires the laser to be enabled")
            self.laser_warning_issued = True

        self.outputs = {
            "Compound": "None",
            "Score": 0,
            "Results": pd.DataFrame(data={' Compound ': [], ' Score ': []})
        }

        # perform matching
        compounds, scores = self.pearson.process(wavenumbers, spectrum)
        if compounds is None or scores is None or len(compounds) == 0:
            self.last_compound = None
            self.last_score = None
            self.curve_scope.setVisible(False)
            self.timer.start(self.TIMER_MS)
            return

        if len(compounds) > self.max_results:
            compounds = compounds[:self.max_results]
            scores = scores[:self.max_results]

        # spaces improve appearance
        table_data = {' Compound ': compounds, ' Score ': scores}
        self.df_results = pd.DataFrame(data=table_data).round(2)

        # if library compound names are pipe-delimited, trim to first sub-field
        best_compound = compounds[0].split("|")[0].strip()
        best_score = scores[0]

        # these need to be written to labels in GUI thread
        self.last_compound = self.wrapped(best_compound)
        self.last_score = best_score

        # TODO: determine which curve to use
        curve = self.curve_scope

        # plot best-matching Pearson library spectrum
        if self.pearson.best_library_spectrum is not None and self.pearson.best_library_wavenumbers is not None:
            # curve.setName(f"Library {best_compound}") 
            curve.setData(x=self.pearson.best_library_wavenumbers,
                          y=self.pearson.best_library_spectrum)
            self.curve_scope.setVisible(True)
        else:
            self.curve_scope.setVisible(False)

        # Add to ProcessedReading, so it will be saved with Measurement metadata.
        # Use fields already allocated for KIA.
        pr.declared_match = best_compound
        pr.declared_score = best_score

        # schedule GUI update
        self.timer.start(self.TIMER_MS)

    def set_library_dir(self, path):
        """ 
        This sets the path to the USER library dir, which is normally 
        EnlightenSpectra/matching_library but can be overridden by the user.

        Note that the "distribution" library remains under 
        enlighten/assets/example_data and cannot be moved.
        """

        self.ctl.config.set(self.SECTION, "user_library_dir", path)
        self.ctl.marquee.clear(token="existing_directory")

        log.debug(f"setting user library dir {path}")
        self.user_library_dir = path
        os.makedirs(self.user_library_dir, exist_ok=True)

        # only colorize the button if the user has selected a non-standard path
        is_custom = self.user_library_dir != self.DEFAULT_USER_LIBRARY_DIR
        self.ctl.gui.colorize_button(self.bt_select_library, is_custom)

        # always show tooltip
        self.bt_select_library.setToolTip(path)

        if self.pearson:
            self.pearson.reset()

    def init_from_ini(self):
        path = self.ctl.config.get(self.SECTION, "user_library_dir", default=None)
        if path:
            self.user_library_dir = path

        self.use_dist = self.ctl.config.get_bool(self.SECTION, "use_dist", default=True)
        self.cb_use_dist.setChecked(self.use_dist)

        self.max_results = self.ctl.config.get_int(self.SECTION, "max_results", default=2)
        self.sb_max_results.setValue(self.max_results)

        self.min_score = self.ctl.config.get_float(self.SECTION, "min_score", default=0.65)
        self.ds_min_score.setValue(self.min_score)

    def select_library_callback(self):
        """
        Callback for when user clicks "Select Library" button. Since this is
        triggered by a GUI button click, it occurs on a GUI thread and therefore
        can create and call widgets.
        """
        prompt = "Select a spectral matching library (directory of ENLIGHTEN .csv files)"
        self.ctl.marquee.info(prompt, persist=True, token="existing_directory")

        # create the dialog
        dialog = QtWidgets.QFileDialog(parent=self.ctl.form, caption=prompt)
        dialog.setFileMode(QtWidgets.QFileDialog.Directory)
        dialog.setOption(QtWidgets.QFileDialog.ShowDirsOnly)

        # default to last selection
        path = self.user_library_dir
        dialog.setDirectory(path)

        # get the user's choice
        log.debug(f"prompting user for library path (default {path})")
        path = dialog.getExistingDirectory()
        if path is None or len(path) == 0:
            log.debug("user clicked cancel")
            return

        self.set_library_dir(path)

    def add_to_library(self):
        if self.user_library_dir is None or not os.path.isdir(self.user_library_dir):
            log.debug(f"can't add_to_library w/o library_dir {self.user_library_dir}")
            return

        self.add_next_to_library = True

        log.debug("add_to_library: triggering save...")
        self.ctl.vcr_controls.save()

    def factory_callback(self, measurement, event):
        if event != "save":
            return

        if not self.add_next_to_library:
            return

        # MeasurementFactory has just saved this Measurement
        m = measurement
        self.add_next_to_library = False

        # find the current .csv pathname
        old_pathname = m.pathname_by_ext.get("csv", None)
        if old_pathname is None:
            log.error("could not find original CSV pathname")
            return
        log.debug(f"old pathname was {old_pathname}")

        # get label
        result = self.ctl.gui.msgbox_with_lineedit(
            title="Add to Library",
            lineedit_text=m.label,
            label_text="Enter a simple name for your new library compound\n" +
                       "(don't include file extension). Letters, numbers\n" +
                       "and spaces work best.")

        label = result["lineedit"].strip()
        log.debug(f"new label is {label}")
        if not result["ok"]:
            log.debug("user cancelled")
            return
        elif 0 == len(label):
            log.debug("empty filename")
            return

        os.makedirs(self.user_library_dir, exist_ok=True)
        new_pathname = os.path.join(self.user_library_dir, f"{label}.csv")

        # note that while we update the label in the .csv, we don't actually use
        # the label when we later read the .csv
        log.debug(f"copying {old_pathname} to {new_pathname}, changing label -> {label}")
        with open(new_pathname, "w") as outfile:
            with open(old_pathname, "r") as infile:
                for line in infile:
                    if re.match(r"^Label,", line):
                        outfile.write(f"Label,{label}\n")
                    else:
                        outfile.write(line)

        log.debug("bouncing engines")
        self.pearson.reset()

    def wrapped(self, s):
        """
        Manual word-wrap to prevent column from becoming so wide we can't see or
        disable buttons.

        Make this more elegant when we have time (try to break at space, comma,
        semi-colon, hyphen etc within 5-char "window" of maxlen, etc).
        """
        if s is None:
            return ""

        maxwidth = 20
        lines = []
        while s != "":
            if len(s) > maxwidth:
                t = s[:maxwidth]
                s = s[maxwidth:]
                lines.append(t)
            else:
                lines.append(s)
                break
        return "\n".join(lines)

class Pearson:
    def __init__(self, feature):
        self.feature = feature
        self.ctl = self.feature.ctl
        self.reset()

    def reset(self):
        self.library_spectra = None
        self.best_library_spectrum = None
        self.best_library_wavenumbers = None

    def lazy_load_library(self):
        if self.library_spectra:
            # log.debug("Pearson.lazy_load_spectra: Library was already loaded")
            return

        self.compound_names = []  # positional, so not required to be unique
        self.library_spectra = []

        library_dirs = []
        if self.feature.use_dist:
            library_dirs.append(self.feature.dist_library_dir)
        library_dirs.append(self.feature.user_library_dir)

        # recursively iterate down through each folder tree, looking for .csv files
        for library_dir in library_dirs:
            if not os.path.isdir(library_dir):
                continue

            for (dirpath, _dirnames, filenames) in os.walk(library_dir):
                for filename in sorted(filenames):
                    if filename.startswith(".") or not filename.endswith(".csv"):
                        log.debug(f"Pearson.lazy_load_spectra: ignoring {filename}")
                        continue

                    basename = filename.removesuffix(".csv")
                    pathname = os.path.join(dirpath, filename)

                    # append asterisk when matching to user-generated spectra
                    if library_dir == self.feature.user_library_dir:
                        basename += "*"

                    self.compound_names.append(basename)

                    log.debug(f"Pearson.lazy_load_spectra: loading {basename} ({pathname})")
                    try:
                        # note that we load metadata, but don't do anything with it (even label)
                        csv_loader = CSVLoader(pathname)
                        pr, metadata = csv_loader.load_data(scalar_metadata=True)
                    except:
                        self.ctl.marquee.error(f"LibraryMatching: error loading {pathname}")
                        log.error(f"Failed to load library spectrum {pathname}", exc_info=1)
                        continue

                    df = pd.DataFrame({
                        'Wavenumber': pr.get_wavenumbers(),
                        'Intensity': pr.get_processed()
                    })
                    self.library_spectra.append(df)

    def process(self, wavenumbers, spectrum):
        try:
            self.lazy_load_library()

            match_result = self.generate_result(wavenumbers, spectrum)
            if match_result is None or len(match_result) == 0:
                log.debug("Pearson.process: ignoring null response for now")
                return None, None

            # extract matches from response
            compounds = []
            scores = []
            for result in match_result:
                compounds.append(result["Name"])
                scores.append(result["Score"])
            return compounds, scores

        except Exception:
            log.debug(f"caught exception during Pearson.process", exc_info=1)
            return None, None

    def generate_result(self, wavenumbers, spectrum):
        """
            a simple correlation routine

            1. find wavenumber overlap
            2. interpolate to same wavenumber axis
            3. do Pearson correlation

            library spectra as list of pandas data frames
              self.library_spectra = list of pd-df
            expects return to be used as follows:
               for result in match_result:
                  compounds.append(result["Name"])
                  scores.append(result["Score"])
        """

        pd_spectrum = pd.DataFrame({"Wavenumber": wavenumbers, "Intensity": spectrum})
        pd_spectrum = pd_spectrum.dropna()

        # we need to find the overlap
        spectrum_min_wavenumber = pd_spectrum["Wavenumber"].min()
        spectrum_max_wavenumber = pd_spectrum["Wavenumber"].max()

        best_correlation = -1
        self.best_library_spectrum = None
        self.best_library_wavenumbers = None

        matches = []
        for libraryID in range(len(self.library_spectra)):
            library_spectrum = self.library_spectra[libraryID]

            library_length = len(library_spectrum["Wavenumber"].to_numpy())
            library_min_wavenumber = library_spectrum["Wavenumber"].min()
            library_max_wavenumber = library_spectrum["Wavenumber"].max()

            # this is the overlap region in wavenumbers
            start_wavenumber = max(spectrum_min_wavenumber, library_min_wavenumber)
            end_wavenumber = min(spectrum_max_wavenumber, library_max_wavenumber)

            # restrict the range we are interpolating to
            # if library is wider, we will restrict to sample range
            # if sample is wider, we wil restrict to library range
            library_wavenumbers = library_spectrum["Wavenumber"].to_numpy()
            library_wavenumbers_subset = [i for i in range(library_length) if
                                          library_wavenumbers[i] >= start_wavenumber and library_wavenumbers[
                                              i] <= end_wavenumber]

            # now interpolate spectrum to library wavenumbers
            spectrum_interpolater = interp1d(pd_spectrum["Wavenumber"].to_numpy(), pd_spectrum["Intensity"].to_numpy())
            library_wavenumbers_interp = library_wavenumbers[library_wavenumbers_subset]
            spectrum_interp = spectrum_interpolater(library_wavenumbers_interp)

            # and now for the actual match - use Pearson correlation
            library_spectrum = library_spectrum["Intensity"].to_numpy()
            library_spectrum = library_spectrum[library_wavenumbers_subset]
            correlation, _ = pearsonr(library_spectrum, spectrum_interp)

            # track all matches that meet the minimum score
            if correlation >= self.feature.min_score:
                matches.append({"Score": correlation, "Name": self.compound_names[libraryID]})

                # track best correlation so we can graph top-matching library spectrum
                if (best_correlation < correlation):
                    best_correlation = correlation

                    # scale library intensity to measurement (probably a numpy call for this)
                    low = min(library_spectrum)
                    rng = max(library_spectrum) - low
                    top = max(spectrum_interp)
                    self.best_library_spectrum = [top * ((v - low) / rng) for v in library_spectrum]
                    self.best_library_wavenumbers = library_wavenumbers_interp

                    log.debug(f"library_spectrum = {len(self.best_library_spectrum)}, "
                              f"library_wavenumbers = {len(self.best_library_wavenumbers)}")

        def cmp_score(a, b):
            if a["Score"] < b["Score"]: return -1
            if a["Score"] > b["Score"]: return +1
            return 0

        # sort matches in descending order by score
        return sorted(matches, key=cmp_to_key(cmp_score), reverse=True)
