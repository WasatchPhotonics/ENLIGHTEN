import threading
import logging
import copy
import json
import sys
import os
import re
import numpy as np

from datetime import datetime

from enlighten import common
from enlighten.EnlightenFeature import EnlightenFeature

from .DalaiAdditionalFiles import prep_spectra_X
from .DalaiAdditionalFiles import prep_spectra_XM
from .DalaiAdditionalFiles import prep_spectra_XS 

from wasatch import utils

if common.use_pyside2():
    from PySide2 import QtCore, QtWidgets
else:
    from PySide6 import QtCore, QtWidgets

log = logging.getLogger(__name__)

class ImportWorker(threading.Thread):
    """
    This is in a Python thread, instead of a QTimer, because we don't want it to
    be on the GUI thread. It also could have been done with a QThread or signals.
    """
    def __init__(self, feature):
        threading.Thread.__init__(self)
        self.feature = feature

    def run(self):
        import tensorflow.lite as tfl
        self.feature.imported = True

class DalaiRamanFeature(EnlightenFeature):

    SECTION = "DalaiRamanFeature"
    MODEL_DIR = os.path.join("enlighten", "assets", "example_data", "dalai_models")
    COLOR = "#f7e842"

    def __init__(self, ctl):
        super().__init__(ctl)

        cfu = ctl.form.ui

        self.frame          = cfu.frame_dalai_1
        self.bt_toggle      = cfu.pushButton_dalai_toggle
        self.cb_enable      = cfu.checkBox_dalai_enable
        self.combo_model    = cfu.comboBox_dalai_model
        self.lb_combo       = cfu.label_dalai_model_label
        self.cb_left_trim   = cfu.checkBox_dalai_left_trim
        self.sb_left_trim   = cfu.spinBox_dalai_left_trim_wavenumber
        self.cb_right_trim  = cfu.checkBox_dalai_right_trim
        self.sb_right_trim  = cfu.spinBox_dalai_right_trim_wavenumber
        self.cb_deconvolute = cfu.checkBox_dalai_deconvolute

        self.expert_widgets = [ self.cb_left_trim,
                                self.cb_right_trim,
                                self.sb_left_trim,
                                self.sb_right_trim,
                                self.cb_deconvolute,
                                cfu.label_dalai_left_trim_bool_label,
                                cfu.label_dalai_right_trim_bool_label ]

        self.model_configs = {}
        self.loaded_models = {}
        self.current_model_name = None
        self.current_model_config = None

        # Visible in this case means the "DALAI-RAMAN" widget is visible on the 
        # sliding Tool Palette. It does not mean the alt-graph, combobox or other 
        # options are displayed displayed, which only appear when "enabled.
        self.visible = False

        self.import_worker = None
        self.imported = False

        self.enabled = False
        self.deconvolute = False

        self.do_left_trim = False
        self.do_right_trim = False

        self.left_trim_cm = 0
        self.right_trim_cm = 0

        np.set_printoptions(edgeitems=5, threshold=0)

        self.combo_model.clear()
        self.find_available_models()
        ordered_model_labels = [config.label for basename, config in self.model_configs.items()]
        for label in ordered_model_labels:
            self.combo_model.addItem(label)
        self.combo_model.setCurrentIndex(0 if len(ordered_model_labels) else -1)

        self.cb_enable      .stateChanged           .connect(self.enable_callback)
        self.cb_deconvolute .stateChanged           .connect(self.update_settings)
        self.cb_left_trim   .stateChanged           .connect(self.update_settings)
        self.cb_right_trim  .stateChanged           .connect(self.update_settings)
        self.sb_left_trim   .valueChanged           .connect(self.update_settings)
        self.sb_right_trim  .valueChanged           .connect(self.update_settings)
        self.combo_model    .currentIndexChanged    .connect(self.select_model_callback)
        self.bt_toggle      .clicked                .connect(self.toggle_callback)

        self.ctl.page_nav.register_observer(self.page_nav_callback)

        self.curve = self.ctl.alt_graph.add_curve("DALAI-RAMAN", pen=self.COLOR)

        self.import_time_sec = self.ctl.config.get_int(self.SECTION, "import_time_sec", default=None)
        self.import_start_time = None

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.monitor_import)
        self.timer.setSingleShot(True)

        self.page_nav_callback()

    def get_color(self):
        return self.COLOR

    def update_settings(self):
        self.enabled       = self.cb_enable.isChecked()
        self.deconvolute   = self.cb_deconvolute.isChecked()

        self.do_left_trim  = self.cb_left_trim.isChecked()
        self.do_right_trim = self.cb_right_trim.isChecked()

        self.left_trim_cm  = self.sb_left_trim.value()
        self.right_trim_cm = self.sb_right_trim.value()

        if self.enabled:
            self.lazy_load_model()

        self.update_visibility()

    def toggle_callback(self):
        self.cb_enable.setChecked(not self.enabled)

    def enable_callback(self):
        # have we already done the heavy import?
        if "tensorflow.lite" in sys.modules:
            self.update_settings()
            return

        # No, we still need to do the import. Do that in a background thread, 
        # with an activity monitor.

        self.ctl.marquee.info("Loading machine learning framework", persist=True, token="dalai_load")
        self.ctl.reading_progress_bar.set(-1 if self.import_time_sec is None else 0)

        # kick-off the thread to import TensorFlow
        self.import_start_time = datetime.now()
        self.import_worker = ImportWorker(self)
        self.import_worker.setDaemon(True)
        self.import_worker.start()

        # kick-off the timer to monitor import progress
        self.timer.start(100)

    def monitor_import(self):        
        """ This is ticked by a QTimer, so runs on GUI thread """
        elapsed_sec = (datetime.now() - self.import_start_time).total_seconds()
        if not self.imported:
            if self.import_time_sec is not None:
                self.ctl.reading_progress_bar.set(100.0 * elapsed_sec / self.import_time_sec)
            self.timer.start(250)
            return

        ########################################################################
        # ImportWorker is done
        ########################################################################

        self.ctl.marquee.clear(token="dalai_load")
        self.ctl.reading_progress_bar.hide()

        self.ctl.config.set(self.SECTION, "import_time_sec", int(round(elapsed_sec, 0)))

        self.lazy_load_model()
        self.update_settings()

    def best_model_for_current_spectrometer(self):
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return None

        spec_model = spec.settings.eeprom.model
        if "X-" in spec_model:
            spec_family = "X"
        elif "XM-" in spec_model:
            spec_family = "XM"
        elif re.match(r"XS-|XSB-|SIG", spec_model):
            spec_family = "XS"
        else:
            log.debug(f"cannot determine connected spectrometer family: {spec_model}")
            spec_family = None

        # go through model_configs (which is already ordered per JSON config)
        # and find the first matching model
        best_generic = None
        for basename, config in self.model_configs.items():
            if spec_family in config.target_spectrometer_families:
                # we found an explicit match, use that
                return basename
            elif len(config.target_spectrometer_families) == 0:
                # This model had no explicit families, meaning it's "generic"? 
                # But highly-ordered? Keep it as the new default unless a better
                # model is found further down the list.
                if best_generic is None:
                    best_generic = basename
        
        return best_generic

    def update_visibility(self):
        doing_raman = self.ctl.page_nav.doing_raman()
        doing_expert = self.ctl.page_nav.doing_expert()

        # is there a suitable DALAI model for the current spectrometer?
        #
        # Note that currently we are not forcing or defaulting the user into 
        # using the selected model...we could add that as an init_hotplug or 
        # similar.
        best_model_name = self.best_model_for_current_spectrometer()

        # determine visibility 
        self.visible = doing_raman and best_model_name is not None
        if not self.visible:
            self.enabled = False

        # display the WIDGET (if visible)
        self.frame.setVisible(self.visible)

        # display the COMBO (if enabled)
        for w in [ self.combo_model, self.lb_combo ]:
            w.setVisible(self.enabled)

        # display expert WIDGETS (if Expert)
        show_expert_widgets = self.visible and self.enabled and doing_expert
        for w in self.expert_widgets:
            w.setVisible(show_expert_widgets)

        # display alt GRAPH (if enabled)
        if self.visible and self.enabled:
            log.debug("displaying alt graph")
            self.ctl.alt_graph.set_visible(True)
        elif not self.ctl.plugin_controller.using_other_graph():
            self.ctl.alt_graph.set_visible(False)

        self.notify_observers()

    def page_nav_callback(self, arg=None):
        self.update_visibility()

    def is_visible(self):
        return self.visible

    def is_enabled(self):
        return self.enabled

    def process(self, pr):
        if not self.enabled:
            return

        if not (pr.settings.state.laser_enabled or (pr.reading.take_one_request and pr.reading.take_one_request.auto_raman_request)):
            self.ctl.marquee.error("DALAI-RAMAN requires laser")
            self.curve.setData([])
            return

        wavenumbers = pr.get_wavenumbers()
        if wavenumbers is None:
            self.ctl.marquee.error("DALAI-RAMAN requires measurements with wavenumber axis")
            self.curve.setData([])
            return

        wavenumbers = np.array(wavenumbers, dtype=np.float64).tolist()
        spectrum = np.array(pr.get_processed(), dtype=np.float64).tolist()
        log.debug(f"Wavenumbers = {len(wavenumbers)}, spectrum = {len(spectrum)}")

        unit = self.ctl.graph.get_x_axis_unit()
        if unit != "cm":
            self.ctl.marquee.error("DALAI-RAMAN requires wavenumber axis selected")
            self.curve.setData([])
            return

        log.debug("calling process_dalai")
        AI_wavenumbers, AI_spectrum = self.process_dalai(wavenumbers, spectrum, pr)
        log.debug("back from process_dalai")
        log.debug(f"AI_wavenumbers {AI_wavenumbers}")
        log.debug(f"AI_spectrum {AI_spectrum}")

        pr.wavenumbers_dalai = AI_wavenumbers
        pr.spectrum_dalai = AI_spectrum

        # interpolated arrays are for display only; we use non-interpolated data in matching
        interp = self.ctl.interp
        if interp.enabled and interp.new_axis is not None:
            AI_spectrum_display = np.interp(interp.new_axis, AI_wavenumbers, AI_spectrum)
            AI_wavenumbers_display = interp.new_axis
        else:
            AI_spectrum_display = AI_spectrum
            AI_wavenumbers_display = AI_wavenumbers

        log.debug("graphing data")
        self.curve.setData(x=AI_wavenumbers_display, y=AI_spectrum_display, color=self.COLOR)
        log.debug("back grom graph")

    def find_available_models(self):
        found_models = {}
        for filename in sorted(os.listdir(self.MODEL_DIR)):
            pathname = os.path.join(self.MODEL_DIR, filename)

            config_pathname = None
            model_type = None
            basename = None

            # only support tflite models
            if os.path.isfile(pathname) and filename.endswith(".tflite"):
                basename = filename.removesuffix(".tflite")
                found_models[basename] = ModelConfig(basename)

        # manually build 'model_configs' with insertion order ascending by 'order' (then by name)
        log.debug("Known Models:")
        for basename, config in sorted(found_models.items(), key=lambda pair: (pair[1].order, pair[0])):
            self.model_configs[basename] = config
            log.debug(f"  {basename}: {config}")

    def lazy_load_model(self, model_name=None):
        """
        Load TensorFlow model if not already loaded.

        Args:
            model_name (Optional[str]): Name of model to load, defaults to first
                in self.model_configs by insertion order. Note that this is 
                ModelConfig.basename, not .label.
        """
        log.debug(f"attempting to lazy_load model {model_name}")
        if model_name is None:
            model_name = list(self.model_configs.keys())[0]

        if model_name not in self.model_configs:
            log.debug(f"unknown model {model_name}")
            return

        if model_name in self.loaded_models:
            log.debug(f"already loaded {model_name}")
            self.current_model_name = model_name
            self.current_model_config = self.model_configs[model_name]
            return

        if self.load_model(model_name):
            log.info(f"selected model {model_name}")
            self.current_model_name = model_name
            self.current_model_config = self.model_configs[model_name]

    def load_model(self, model_name):
        """
        MZ: Moved out of DalaiAdditionalFiles/*.py because X, XM and XS versions
        were all the same.
        """
        config = self.model_configs[model_name]

        self.ctl.marquee.info(f"loading DALAI model {config.model_pathname}")
        if 'tflite' == config.model_type:
            import tensorflow.lite
            model = tensorflow.lite.Interpreter(config.model_pathname)
            model.allocate_tensors()
            log.info(f"loaded tflite model {model_name}")
            self.loaded_models[model_name] = model
            return True

    def select_model_callback(self):
        log.debug("select_model_callback: start")
        combo = self.cb_model
        if combo:
            label = combo.currentText()
            for basename, config in self.model_configs.items():
                if label == config.label:
                    self.lazy_load_model(basename)
                    return
            log.error(f"unknown model label {label}")

    def process_dalai(self, wavenumbers, spectrum, pr):
        """
        Process spectrum according to DALAI settings

        Args:
            wavenumbers: Array of wavenumber values.
            spectrum: Array of spectrum values.

        Returns:
            Tuple[np.ndarray, np.ndarray]: Processed wavenumbers and spectrum

        Note:
            Processing steps include:
            1. Etalon removal (if enabled)
            2. DALAI model processing (DALAI 2.0 or classic).  Determined by presence of 'D2' in model name.
            3. Spectrum trimming (if enabled)
            4. Deconvolution (if enabled)

            The ROI start must be non-zero for proper processing, as DALAI
            requires a good ROI start just after the filter.

            If deconvolution is requested but FWHM is zero in EEPROM,
            deconvolution will be disabled.
        """

        wavenumbers = np.array(wavenumbers)
        spectrum = np.array(spectrum)

        if self.current_model_name is None:
            log.error("doing nothing because no model selected")
            return None, None

        if self.current_model_name not in self.loaded_models:
            log.error(f"doing nothing because current_model_name {self.current_model_name} not in loaded_models: {self.loaded_models}")
            return None, None

        model     = self.loaded_models[self.current_model_name]
        eeprom    = pr.settings.eeprom
        roi_start = eeprom.roi_horizontal_start  
        roi_end   = eeprom.roi_horizontal_end
        fwhm      = eeprom.avg_resolution
        serial    = eeprom.serial_number

        trim_start = self.left_trim_cm  if self.do_left_trim  else wavenumbers[0]
        trim_end   = self.right_trim_cm if self.do_right_trim else wavenumbers[-1]

        if roi_start < 1:
            log.debug("DALAI.process: ROI start is zero - this does not work: DALAI requires a good ROI start just after the filter")
            self.ctl.marquee.error("ROI start is zero in EEPROM - DALAI does not work well across the filter edge")

        # we need to apply ROI here
        wavenumbers = wavenumbers[roi_start : roi_end + 1] 
        spectrum    = spectrum[roi_start : roi_end + 1] 

        if self.deconvolute and fwhm == 0:
            self.ctl.marquee.error("FWHM is zero in EEPROM - no deconvolution possible")
            self.deconvolute = False

        try:
            if "X" in self.current_model_config.target_spectrometer_families:
                log.debug("processing spectra with prep_spectra_X.dalai_X_cleanup")
                wavenumbers, spectrum = prep_spectra_X.clean_spectrum(model, wavenumbers, spectrum, eeprom, self.deconvolute, model_config=self.current_model_config)

            elif "XS" in self.current_model_config.target_spectrometer_families:
                log.debug("processing spectra with prep_spectra_XS.clean_spectrum")
                wavenumbers, spectrum = prep_spectra_XS.clean_spectrum(model, wavenumbers, spectrum, eeprom, self.deconvolute, model_config=self.current_model_config)

            elif "XM" in self.current_model_config.target_spectrometer_families:
                log.debug("processing spectra with prep_spectra_XM.dalai_X_cleanup")
                wavenumbers, spectrum = prep_spectra_XM.clean_spectrum(model, wavenumbers, spectrum, eeprom, self.deconvolute, model_config=self.current_model_config)

            else:
                self.ctl.marquee.error(f"selected DALAI model is not configured to target any known spectrometer family")
        except:
            msg = f"exception executing model targetting {self.current_model_config.target_spectrometer_families} spectrometers"
            self.ctl.marquee.error(msg)
            log.error(msg, exc_info=1)

        trimmed_indices = (trim_start <= wavenumbers) & (wavenumbers <= trim_end)
        wavenumbers = wavenumbers[trimmed_indices]
        spectrum = spectrum[trimmed_indices]

        log.debug("successful dalai processing")
        return wavenumbers, spectrum

    def generate_measurement(self, request, AI_wavenumbers, AI_spectrum):  # -> enlighten.measurement.Measurement
        # log.debug("generate_measurement: trying to generate an ENLIGHTEN Measurement")

        # reset horizontal ROI so it doesn't get re-cropped during saving
        settings = copy.deepcopy(request.settings)
        settings.eeprom.roi_horizontal_start = -1
        settings.eeprom.roi_horizontal_end = -1

        # strip off any .cropped or .interpolated parts, because we want this
        # ProcessedReading to be DALAI from the ground up
        pr = copy.deepcopy(request.processed_reading)
        pr.cropped = None
        pr.interpolated = None

        # Since this is a "DALAI measurement", the "raw" column should logically
        # hold an interpolated representation of the "processed ENLIGHTEN
        # measurement" it was generated from.
        pr.raw = np.interp(
            AI_wavenumbers,
            request.settings.wavenumbers,
            request.processed_reading.processed,
        )

        # we might as well similarly interpolate the original dark for completeness
        if pr.dark is not None:
            pr.dark = np.interp(
                AI_wavenumbers,
                request.settings.wavenumbers,
                request.processed_reading.dark,
            )

        # now we can overwrite the "processed" spectrum with the new DALAI intensities
        pr.processed = AI_spectrum

        settings.wavenumbers = AI_wavenumbers
        settings.wavelengths = utils.generate_wavelengths_from_wavenumbers(settings.excitation(), AI_wavenumbers)

        pr.wavenumbers = settings.wavenumbers
        pr.wavelengths = settings.wavelengths

        measurements = self.ctl.measurement_factory.create_from_dict(
            {
                "Measurement": {
                    "Label": "DalaiRamanID spectrum",
                    "SpectrometerSettings": settings.to_dict(),
                    "ProcessedReading": pr.to_dict(),
                }
            }
        )

        if measurements is None or (isinstance(measurements, list) and len(measurements) < 1):
            log.debug("generate_measurement: unable to generate ENLIGHTEN Measurement")
            return

        return measurements[0]

class ModelConfig:

    def __init__(self, basename):
        # common attributes
        self.basename = basename
        self.found = False
        self.label = None
        self.order = 999
        self.model_type = "tflite"
        self.target_spectrometer_families = []

        # custom attributes
        self.input_must_be_normalized = False
        self.is_wide = False

        # generate pathnames
        current_folder = os.path.dirname(os.path.realpath(__file__))
        self.model_pathname = os.path.join(DalaiRamanFeature.MODEL_DIR, f"{basename}.tflite")
        self.config_pathname = os.path.join(DalaiRamanFeature.MODEL_DIR, f"{basename}.json")

        if os.path.exists(self.config_pathname):
            with open(self.config_pathname, "r", encoding="utf-8") as infile:
                log.debug(f"loading {basename} config from {self.config_pathname}")
                config = json.load(infile)
                self.found = True

                if "label" in config:
                    self.label = config["label"]

                if "order" in config:
                    self.order = config["order"]

                if "is_wide" in config:
                    self.is_wide = config["is_wide"]

                if "input_must_be_normalized" in config:
                    self.input_must_be_normalized = config["input_must_be_normalized"]

                if "target_spectrometer_families" in config:
                    self.target_spectrometer_families = [model.upper() for model in config["target_spectrometer_families"]]

    def __repr__(self):
        return f"ModelConfig<basename {self.basename}, label {self.label}, order {self.order}, type {self.model_type}>"
