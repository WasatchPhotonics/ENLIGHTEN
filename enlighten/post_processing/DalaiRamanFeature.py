import copy
import json
import logging
import os
import re
import signal
import numpy as np
import pandas as pd
import pexpect

from typing import List, Optional, Tuple, Union
from PySide6 import QtWidgets

from enlighten import common
from enlighten.EnlightenFeature import EnlightenFeature

from wasatch import utils

DALAI_MODULES_FOUND = True
try:
    from .DalaiAdditionalFiles import prep_spectra_X
    from .DalaiAdditionalFiles import prep_spectra_XM
    from .DalaiAdditionalFiles import prep_spectra_XS 
except ImportError:
    DALAI_MODULES_FOUND = False

log = logging.getLogger(__name__)

class DalaiRamanFeature(EnlightenFeature):

    SECTION = "DalaiRamanFeature"
    MODEL_DIR = os.path.join("enlighten", "assets", "example_data", "dalai_models")

    def __init__(self, ctl):
        super().__init__(ctl)

        """
        DALAI-RAMAN
         --------------------------
        | [x] Enable               |
        |                          |
        | model: [_XM_Wide______v] |
        |                          |
        | [x] Left Trim            |
        |     [v] ____0____ [^]    |
        | [x] Right Trim           |
        |     [v] ____0____ [^]    |
        |                          |
        | [x] Deconvolute          |
        |__________________________|
        """
        cfu = ctl.form.ui

        self.frame          = cfu.frame_dalai_1
        self.cb_enable      = cfu.checkBox_dalai_enable
        self.combo_model    = cfu.comboBox_dalai_model
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
                                cfu.label_dalai_left_trim_value_label,
                                cfu.label_dalai_right_trim_bool_label,
                                cfu.label_dalai_right_trim_value_label,
                                cfu.label_dalai_deconvolute_label ]

        self.model_configs = {}
        self.loaded_models = {}
        self.current_model_name = None
        self.current_model_config = None

        self.visible = False
        self.enabled = False
        self.deconvolute = False

        self.do_left_trim = False
        self.do_right_trim = False

        self.left_trim_cm = 0
        self.right_trim_cm = 0

        self.combo_model.clear()
        self.find_available_models()
        ordered_model_labels = [config.label for basename, config in self.dalai.model_configs.items()]
        for label in ordered_model_labels:
            self.combo_model.addItem(label)
        self.combo_model.setCurrentIndex(0 if len(ordered_model_labels) else -1)

        self.cb_enable      .stateChanged           .connect(self.update_settings)
        self.cb_deconvolute .stateChanged           .connect(self.update_settings)
        self.cb_left_trim   .stateChanged           .connect(self.update_settings)
        self.cb_right_trim  .stateChanged           .connect(self.update_settings)
        self.sb_left_trim   .valueChanged           .connect(self.update_settings)
        self.sb_right_trim  .valueChanged           .connect(self.update_settings)
        self.combo_model    .currentIndexChanged    .connect(self.combo_callback)

        self.ctl.page_nav.register_observer(self.page_nav_callback)

        self.curve = self.ctl.alt_graph.add_curve("DALAI-RAMAN", pen="#f7e842")

        self.page_nav_callback()

    def update_settings(self):
        self.enabled       = self.cb_enabled.isChecked()
        self.deconvolute   = self.cb_deconvolute.isChecked()

        self.do_left_trim  = self.cb_left_trim.isChecked()
        self.do_right_trim = self.cb_right_trim.isChecked()

        self.left_trim_cm  = self.sb_left_trim.value()
        self.right_trim_cm = self.sb_right_trim.value()

        self.update_visibility()

    def combo_callback(self):
        model_label = self.combo_spectrometer.currentText()

    def update_visibility(self):
        doing_raman = self.ctl.page_nav.doing_raman()
        doing_expert = self.ctl.page_nav.doing_expert()

        self.visible = DALAI_MODULES_FOUND and (doing_raman or doing_expert)
        self.frame.setVisible(self.visible)

        for w in self.expert_widgets:
            w.setVisible(doing_expert)

        if self.visible:
            self.alt_graph.set_visible(True)
        elif not self.plugin_controller.using_other_graph():
            self.alt_graph.set_visible(False)

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
            return

        wavenumbers = pr.get_wavenumbers()
        if wavenumbers is None:
            self.ctl.marquee.error("DALAI-RAMAN requires wavenumber axis [1]")
            return

        wavenumbers = np.array(wavenumbers, dtype=np.float64).tolist()
        spectrum = np.array(pr.get_processed(), dtype=np.float64).tolist()
        log.debug(f"Wavenumbers = {len(wavenumbers)}, spectrum = {len(spectrum)}")

        unit = self.ctl.graph.get_x_axis_unit()
        if unit != "cm":
            self.ctl.marquee.error("DALAI-RAMAN requires wavenumber axis [2]")
            return

        AI_wavenumbers, AI_spectrum = self.process_dalai(wavenumbers, spectrum, pr)

        pr.dalai_wavenumbers = AI_wavenumbers
        pr.dalai_spectrum = AI_spectrum

        # interpolated arrays are for display only; we use non-interpolated data in matching
        interp = self.ctl.interp
        if interp.enabled and interp.new_axis is not None:
            AI_spectrum_display = np.interp(interp.new_axis, AI_wavenumbers, AI_spectrum)
            AI_wavenumbers_display = interp.new_axis
        else:
            AI_spectrum_display = AI_spectrum
            AI_wavenumbers_display = AI_wavenumbers

        self.curve.setData(x=AI_wavenumbers_display, y=AI_spectrum_display, color="#f7e842")

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

        msg = f"loading DALAI model {config.model_pathname}"
        self.plugin.marquee_message = msg
        log.debug(msg)

        if 'tflite' == config.model_type:
            model = tfl.Interpreter(config.model_pathname)
            model.allocate_tensors()
            log.info(f"loaded tflite model {model_name}")
            self.loaded_models[model_name] = model
            return True

    def select_model_callback(self):
        log.debug("select_model_callback: start")
        combo = self.plugin.get_field_widget("DALAI Model")
        if combo:
            label = combo.currentText()
            for basename, config in self.model_configs.items():
                if label == config.label:
                    self.lazy_load_model(basename)
                    return
            log.error(f"unknown model label {label}")

    def process_dalai(self, wavenumbers, spectrum, pr):
        """
        Process spectrum according to DALAI plugin settings

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

        if self.current_model_name is None or self.current_model_name not in self.loaded_models:
            return None, None

        model     = self.loaded_models[self.current_model_name]
        eeprom    = pr.settings.eeprom
        roi_start = eeprom.roi_horizontal_start  
        roi_end   = eeprom.roi_horizontal_end
        fwhm      = eeprom.avg_resolution
        serial    = eeprom.serial_number

        deconvolute = request.fields["Deconvolute DALAI spectrum"]
        etalon_correction_enable = request.fields["Remove Etalon Before DALAI processing"]

        trim_start = request.fields["Left Wavenumber"] if request.fields["Left Trim?"] else wavenumbers[0]
        trim_end   = request.fields["Right Wavenumber"] if request.fields["Right Trim?"] else wavenumbers[-1]

        if roi_start < 1:
            log.debug("DALAI.process: ROI start is zero - this does not work: DALAI requires a good ROI start just after the filter")
            self.plugin.marquee_message = "ROI start is zero in EEPROM - DALAI does not work well across the filter edge"

        # we need to apply ROI here
        wavenumbers = wavenumbers[roi_start : roi_end + 1] 
        spectrum    = spectrum[roi_start : roi_end + 1] 

        if deconvolute and fwhm == 0:
            self.ctl.marquee.error("FWHM is zero in EEPROM - no deconvolution possible")
            deconvolute = False

        try:
            if "X" in self.current_model_config.target_spectrometer_families:
                log.debug("processing spectra with prep_spectra_X.dalai_X_cleanup")
                wavenumbers, spectrum = prep_spectra_X.clean_spectrum(model, wavenumbers, spectrum, eeprom, deconvolute, model_config=self.current_model_config)

            elif "XM" in self.current_model_config.target_spectrometer_families:
                log.debug("processing spectra with prep_spectra_XM.dalai_X_cleanup")
                wavenumbers, spectrum = prep_spectra_XM.clean_spectrum(model, wavenumbers, spectrum, eeprom, deconvolute, model_config=self.current_model_config)

            elif "XS" in self.current_model_config.target_spectrometer_families:
                log.debug("processing spectra with prep_spectra_XS.clean_spectrum")
                wavenumbers, spectrum = prep_spectra_XS.clean_spectrum(model, wavenumbers, spectrum, eeprom, deconvolute, model_config=self.current_model_config)

            else:
                msg = "selected DALAI model is not configured to target any known spectrometer family"
                self.plugin.marquee_message = f"ERROR: {msg}"
                log.error(msg)
        except:
            msg = f"exception executing model targetting {self.current_model_config.target_spectrometer_families} spectrometers"
            self.plugin.marquee_message = f"ERROR: {msg}"
            log.error(msg, exc_info=1)

        trimmed_indices = (trim_start <= wavenumbers) & (wavenumbers <= trim_end)
        wavenumbers = wavenumbers[trimmed_indices]
        spectrum = spectrum[trimmed_indices]

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
                    "Plugin Name": self.plugin.name,  # note, not quite what PluginController sets
                    "SpectrometerSettings": settings.to_dict(),
                    "ProcessedReading": pr.to_dict(),
                }
            }
        )

        if measurements is None or (isinstance(measurements, list) and len(measurements) < 1):
            log.debug("generate_measurement: unable to generate ENLIGHTEN Measurement")
            return

        return measurements[0]

    def preset_get_id_engine(self):
        combo = self.plugin.get_field_widget("ID Engine")
        if combo:
            return combo.currentText()

    def preset_set_id_engine(self, value):
        combo = self.plugin.get_field_widget("ID Engine")
        if combo:
            combo.setCurrentText(value)

    def preset_get_model(self):
        combo = self.plugin.get_field_widget("DALAI Model")
        if combo:
            return combo.currentText()

    def preset_set_model(self, value):
        combo = self.plugin.get_field_widget("DALAI Model")
        if combo:
            combo.setCurrentText(value)

    def preset_get_left_trim(self):
        value = False
        cb = self.plugin.get_field_widget("Left Trim?")
        if cb:
            value = cb.isChecked()

        return value

    def preset_set_left_trim(self, value):
        cb = self.plugin.get_field_widget("Left Trim?")
        if cb:
            flag = "true" == str(value).lower()
            cb.setChecked(flag)
        else:
            log.debug(f"preset_set_left_trim: ignoring value {value}")

    def preset_get_left_wavenumber(self):
        value = None
        sb = self.plugin.get_field_widget("Left Wavenumber")
        if sb:
            value = sb.value()

        return value

    def preset_set_left_wavenumber(self, value):
        sb = self.plugin.get_field_widget("Left Wavenumber")
        if sb:
            wn = int(value)
            sb.setValue(wn)
        else:
            log.debug(f"preset_set_left_wavenumber: ignoring value {value}")

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
        self.model_pathname = os.path.join(self.MODEL_DIR, f"{basename}.tflite")
        self.config_pathname = os.path.join(self.MODEL_DIR, f"{basename}.json")

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
