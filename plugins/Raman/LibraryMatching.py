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
from EnlightenPlugin import EnlightenPluginBase

from wasatch.CSVLoader import CSVLoader

log = logging.getLogger(__name__)

class LibraryMatching(EnlightenPluginBase):
    """
    @todo This is currently oriented toward Raman (defaulting to wavenumbers), 
          but there's no reason it couldn't also support wavelengths for non-Raman 
          (absorbance etc).
    """

    SECTION = "Plugin.Matching.LibraryMatching"

    def get_configuration(self):
        self.name = "Library Matching"
        self.has_other_graph = True
        self.is_blocking = True

        self.library_dir = None
        self.add_next_to_library = False
        self.metadata_cache = {}

        self.soft_install_matching_library()
        self.pearson = Pearson(self)

        self.configure_fields()
        self.ctl.measurement_factory.register_observer(self.factory_callback)

    def disconnect(self):
        self.ctl.measurement_factory.unregister_observer(self.factory_callback)
        super().disconnect()

    def configure_fields(self):
        path = self.get_library_dir_from_ini()
        if path:
            self.set_library_dir(path)

        self.field(name="Select Library",
                   datatype="button",
                   callback=self.select_library_callback,
                   stylesheet="red_gradient_button" if self.library_dir else None,
                   tooltip=self.library_dir if self.library_dir else "Select a directory containing a library of Raman spectra")

        self.field(name="Compound", datatype=str, tooltip="Declared matching compound (highest matching score)")
        self.field(name="Score", datatype=float, precision=2, tooltip="The RamanID algorithm's computed score for the top-matching compound")
        self.field(name="Min Score", direction="input", datatype=int, initial=65, minimum=0, maximum=100, tooltip="Only report matches with this score or above")
        self.field(name="Max Results", direction="input", datatype=int, initial=2, minimum=1, maximum=20, tooltip="Only report this many matches")

        self.field(name="Save to Library",
                   direction="input",
                   datatype="button",
                   callback=self.add_to_library,
                   tooltip="Add the current spectrum to the matching library")

        self.field(name="Results", datatype="pandas", tooltip="table of matching compounds")

    def process_request(self, request):
        pr = request.processed_reading
        wavenumbers = pr.get_wavenumbers()
        spectrum = pr.get_processed()

        self.outputs = {
            "Compound": "None",
            "Score": 0,
            "Results": pd.DataFrame(data={' Compound ': [], ' Score ': []})
        }

        # try to perform matching
        compounds, scores = self.pearson.process(request, wavenumbers, spectrum)
        if compounds is None or scores is None or len(compounds) == 0:
            return

        max_results = request.fields["Max Results"]
        if len(compounds) > max_results:
            compounds = compounds[:max_results]
            scores = scores[:max_results]

        # spaces improve appearance
        table_data = {' Compound ': compounds, ' Score ': scores}
        self.outputs["Results"] = pd.DataFrame(data=table_data).round(2)

        # if library compound names are pipe-delimited, trim to first sub-field
        best_compound = compounds[0].split("|")[0].strip()
        best_score = scores[0]

        self.outputs["Compound"] = self.wrapped(best_compound)
        self.outputs["Score"] = best_score

        # plot best-matching Pearson library spectrum
        if self.pearson.best_library_spectrum is not None and self.pearson.best_library_wavenumbers is not None:
            self.plot(x=self.pearson.best_library_wavenumbers,
                      y=self.pearson.best_library_spectrum,
                      title=f"Library {best_compound}",
                      color='#2994d3')

    def set_library_dir(self, path):
        self.ctl.config.set(self.SECTION, "library_dir", path)
        self.ctl.marquee.clear(token="existing_directory")

        self.library_dir = path
        log.debug(f"using library dir: {path}")

        self.colorize_button_field("Select Library", active=True, tooltip=path)

        self.pearson.reset()

    def get_library_dir_from_ini(self):
        section = self.SECTION
        log.debug(f"getting library dir from {section}")
        path = self.ctl.config.get(section, "library_dir", default=None)
        if path:
            if os.path.isdir(path):
                log.debug(f"returning {path}")
                return path
            else:
                log.debug(f"not a directory? [{path}]")
        else:
            log.debug(f"library dir not found in {section}")

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
        path = self.get_library_dir_from_ini()
        if path is None:
            path = common.get_default_data_dir()
        dialog.setDirectory(path)

        # get the user's choice
        log.debug(f"prompting user for library path (default {path})")
        path = dialog.getExistingDirectory()
        if path is None or len(path) == 0:
            log.debug("user clicked cancel")
            return

        self.set_library_dir(path)

    def add_to_library(self):
        if self.library_dir is None or not os.path.isdir(self.library_dir):
            log.debug(f"can't add_to_library w/o library_dir {self.library_dir}")
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

        additional_dir = os.path.join(self.library_dir, "AdditionalSpectra")
        os.makedirs(additional_dir, exist_ok=True)

        new_pathname = os.path.join(additional_dir, f"{label}.csv")
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

    def soft_install_matching_library(self):
        """
        If ~/EnlightenSpectra/MatchingLibrary does not exist, populate it from 
        the distribution plugins/Raman/MatchingLibrary. If it already exists,
        leave it alone.
        """

        dst = os.path.join(self.ctl.save_options.get_directory(), "MatchingLibrary")
        if os.path.exists(dst):
            log.debug(f"{dst} already exists")
            return

        src = os.path.join(os.getcwd(), "plugins", "Raman", "MatchingLibrary")
        log.error(f"checking for src {src}")
        if not os.path.exists(src):
            log.error(f"{src} not found")
            return

        # src exists, but not dst, so perform the copy
        log.debug(f"performing recursive copy from {src} to {dst}")
        shutil.copytree(src, dst)

    def colorize_button_field(self, field_name, active, tooltip):
        """
        It's kind of fascinating that this actually works. Note that 
        get_plugin_field returns a PluginFieldWidget, NOT the actual QPushButton.
        However, PluginFieldWidget extends QWidget, which has a layout, and that
        layout contains (in this case) a QPushButton. Applying the tooltip and 
        CSS to the parent widget apparently updates the subordinate widget 
        through the 'parent' relationship.
        """
        button = self.get_plugin_field(field_name)
        log.debug(f"colorize_button_field: button {button}")
        if button:
            button.setToolTip(tooltip)
            color = "red" if active else "gray"
            self.ctl.stylesheets.apply(button, f"{color}_gradient_button")

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
    def __init__(self, plugin):
        self.plugin = plugin
        self.ctl = self.plugin.ctl
        self.reset()

    def reset(self):
        self.library_spectra = None
        self.best_library_spectrum = None
        self.best_library_wavenumbers = None

    def lazy_load_library(self):
        if self.library_spectra:
            log.debug("Pearson.lazy_load_spectra: Library was already loaded")
            return

        if not self.plugin.library_dir:
            log.debug("Pearson.lazy_load_spectra: missing library dir")
            return

        self.compound_names = []  # positional, so not required to be unique
        self.library_spectra = []

        for (dirpath, _dirnames, filenames) in os.walk(self.plugin.library_dir):
            for filename in sorted(filenames):
                if filename.startswith(".") or not filename.endswith(".csv"):
                    log.debug(f"Pearson.lazy_load_spectra: ignoring {filename}")
                    continue

                basename = filename.removesuffix(".csv")
                pathname = os.path.join(dirpath, filename)
                self.compound_names.append(basename)

                log.debug(f"Pearson.lazy_load_spectra: loading {basename} ({pathname})")
                csv_loader = CSVLoader(pathname)
                pr, metadata = csv_loader.load_data(scalar_metadata=True)

                df = pd.DataFrame({
                    'Wavenumber': pr.get_wavenumbers(),
                    'Intensity': pr.get_processed()
                })
                self.library_spectra.append(df)

    def process(self, request, wavenumbers, spectrum):
        if not self.plugin.library_dir:
            self.marquee_message = "Select library directory to perform Raman matching"
            return None, None

        try:
            self.lazy_load_library()

            match_result = self.generate_result(request, wavenumbers, spectrum)
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

    def generate_result(self, request, wavenumbers, spectrum):
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
            if 100 * correlation >= request.fields["Min Score"]:
                matches.append({"Score": 100 * correlation, "Name": self.compound_names[libraryID]})

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
