import re
import json
import logging
import decimal

from wasatch.EEPROM import EEPROM
from enlighten import common
from typing import List

if common.use_pyside2():
    from PySide2 import QtGui, QtWidgets
else:
    from PySide6 import QtGui, QtWidgets

log = logging.getLogger(__name__)

class EEPROMEditor:
    """
    Unlike most business objects, just pass in self.form.ui to avoid a REALLY long list of widgets
    
    Key assumptions:
    
    - only lineEdit and spinBoxes currently support arrays
          - I didn't implement doubleSpinBox arrays because all current arrays of 
            floats/doubles are coefficients, and coefficients should be displayed 
            and editted in scientific notation rather than fixed-decimal spinners; 
            hence, lineEdit
          - also, we currently have no arrays of radioButtons or checkBoxes
    - lineEdit arrays are assumed to represent float32 (all EEPROM floats are 
      float32, and we currently have no string arrays)
    - all scalar (non-array) lineEdits are assumed to be strings
          - while we have several float scalars in the EEPROM, none are of ranges 
            benefitting from scientific notation
    
    Note that the order of widgets on the form, and the "EEPROM Pages" in which they
    appear, is solely defined in the Qt layout and may diverge from the current
    "physical" EEPROM layout.  A more ACCURATE process would be to actually expose
    each field's Page and Offset in the wasatch.EEPROM object, so the ENLIGHTEN 
    form could be dynamically generated to match various EEPROM formats, but I'm
    not sure that would actually simplify life for most end-users (though 
    developers would appreciate it).
    """
    def __init__(self, ctl):
        self.ctl = ctl
        cfu = ctl.form.ui

        self.lb_digest                       = cfu.label_eeprom_digest
        self.lb_product_image                = cfu.label_product_image
        self.lb_serial                       = cfu.label_serial

        self.updated_from_eeprom = False

        self.checkBoxes      = {}
        self.spinBoxes       = {}
        self.doubleSpinBoxes = {}
        self.lineEdits       = {}
        self.widgets         = []

        # mapping from eeprom.subformat to which widget should be visible
        self.subformat_frames = [
            None, # TODO: user_data_2 and user_data_3
            cfu.frame_eeprom_sub_1,
            cfu.frame_eeprom_sub_2,
            cfu.frame_eeprom_sub_3,
            cfu.frame_eeprom_sub_4
        ]

        # Start with a blank EEPROM.  We need this as a verification during the
        # binding process (to ensure we only bind callbacks to valid instance 
        # attribute labels).  As spectrometers connect and become active / foreground,
        # the Controller will call update_from_spec and pass-in the 
        # "real" EEPROM instance we should use for current values.
        self.eeprom = EEPROM()
        self.settings = None
        self.bind()
        self.update_subformat()

        self.ctl.authentication.register_observer(self.update_authentication)
        self.wpsc_translations = {
            "slit_width": "slit_size_um",
            "serial": "serial_number",
            "inc_battery": "has_battery",
            "inc_cooling": "has_cooling",
            "inc_laser": "has_laser",
            "calibration_by": "calibrated_by",
            "startup_int_time_ms": "startup_integration_time_ms",
            "startup_tempc": "startup_temp_degC",
            "startup_trigger_mode": "startup_triggering_scheme",
            "wavecal_coeffs": "wavelength_coeffs",
            "temp_todac_coeffs": "degC_to_dac_coeffs",
            "adc_to_temp_coeffs": "adc_to_degC_coeffs",
            "detector_temp_max": "max_temp_degC",
            "detector_temp_min": "min_temp_degC",
            "thermistor_beta": "tec_beta",
            "thermistor_res_at298k": "tec_r298",
            "detector_name": "detector",
            "actual_pixels_horiz": "actual_pixels_horizontal",
            "active_pixels_horiz": "active_pixels_horizontal",
            "active_pixels_vert": "active_pixels_vertical",
            "roi_horiz_start": "roi_horizontal_start",
            "roi_horiz_end": "roi_horizontal_end",
            "max_laser_power_mw": "max_laser_power_mW",
            "min_laser_power_mw": "min_laser_power_mW",
            "excitation_wavelength_nm": "excitation_nm",
            "product_config": "product_configuration",
            "rel_int_corr_order": "raman_intensity_calibration_order",
            "bin2x2": "horiz_binning_enabled",
            "flip_x_axis": "invert_x_axis",
            }

        # Filterable layouts are `QFormLayout`s that are filtered by row based on the
        # current search box text.

        self.filterable_layouts: List[QtWidgets.QFormLayout] = [
            cfu.formLayout_15,
            cfu.formLayout_ee_page_0,
            cfu.formLayout_ee_page_1,
            cfu.formLayout_ee_page_2,
            cfu.formLayout_ee_page_4,
            cfu.formLayout_ee_page_5,
            cfu.formLayout_ee_page_6,
            cfu.formLayout_ee_page_6_sub_2,
            cfu.formLayout_ee_page_7
        ]

    def bind(self):
        """
        Note that self.eeprom is used in the binding process, but just to confirm 
        whether the field exists as an attribute in the current version of 
        wasatch.EEPROM, and if so whether it's editable -- the field's VALUE is not
        (at this point in program flow) read from the EEPROM object or updated to 
        the widgets, until update_from_spec is called.
        """
        cfu = self.ctl.form.ui

        # Type                    Widget                                      EEPROM field                     
        self.bind_checkBox        (cfu.checkBox_ee_has_battery,               "has_battery")
        self.bind_checkBox        (cfu.checkBox_ee_has_cooling,               "has_cooling")
        self.bind_checkBox        (cfu.checkBox_ee_has_laser,                 "has_laser")
        self.bind_checkBox        (cfu.checkBox_ee_invert_x_axis,             "invert_x_axis")
        self.bind_checkBox        (cfu.checkBox_ee_horiz_binning_enabled,     "horiz_binning_enabled")
        self.bind_checkBox        (cfu.checkBox_ee_gen15,                     "gen15")
        self.bind_checkBox        (cfu.checkBox_ee_cutoff_filter_installed,   "cutoff_filter_installed")
        self.bind_checkBox        (cfu.checkBox_ee_hardware_even_odd,         "hardware_even_odd")
        self.bind_checkBox        (cfu.checkBox_ee_sig_laser_tec,             "sig_laser_tec")
        self.bind_checkBox        (cfu.checkBox_ee_has_interlock_feedback,    "has_interlock_feedback")
        self.bind_checkBox        (cfu.checkBox_ee_has_shutter,               "has_shutter")
        self.bind_checkBox        (cfu.checkBox_ee_disable_ble_power,         "disable_ble_power")
        self.bind_checkBox        (cfu.checkBox_ee_disable_laser_armed_indicator, "disable_laser_armed_indicator")

        # To be clear: we're editing the float version of excitation_nm. Edits 
        # are automatically rounded and re-saved to the integral version. We 
        # only "expose" one version (floating-point) to the user through 
        # ENLIGHTEN, although they can see both in the raw EEPROM (but not via 
        # ENLIGHTEN's EEPROM editor).
        self.bind_doubleSpinBox   (cfu.doubleSpinBox_ee_excitation_nm_float,  "excitation_nm_float")
        self.bind_doubleSpinBox   (cfu.doubleSpinBox_ee_max_laser_power_mW,   "max_laser_power_mW")
        self.bind_doubleSpinBox   (cfu.doubleSpinBox_ee_min_laser_power_mW,   "min_laser_power_mW")
        self.bind_doubleSpinBox   (cfu.doubleSpinBox_ee_detector_gain,        "detector_gain")
        self.bind_doubleSpinBox   (cfu.doubleSpinBox_ee_detector_gain_odd,    "detector_gain_odd")
        self.bind_doubleSpinBox   (cfu.doubleSpinBox_ee_spline_min,           "spline_min")
        self.bind_doubleSpinBox   (cfu.doubleSpinBox_ee_spline_max,           "spline_max")
        self.bind_doubleSpinBox   (cfu.doubleSpinBox_ee_avg_resolution,       "avg_resolution")

        self.bind_lineEdit        (cfu.lineEdit_ee_adc_to_degC_coeff_0,       "adc_to_degC_coeffs", 0)
        self.bind_lineEdit        (cfu.lineEdit_ee_adc_to_degC_coeff_1,       "adc_to_degC_coeffs", 1)
        self.bind_lineEdit        (cfu.lineEdit_ee_adc_to_degC_coeff_2,       "adc_to_degC_coeffs", 2)
        self.bind_lineEdit        (cfu.lineEdit_ee_calibrated_by,             "calibrated_by")
        self.bind_lineEdit        (cfu.lineEdit_ee_calibration_date,          "calibration_date")
        self.bind_lineEdit        (cfu.lineEdit_ee_degC_to_dac_coeff_0,       "degC_to_dac_coeffs", 0)
        self.bind_lineEdit        (cfu.lineEdit_ee_degC_to_dac_coeff_1,       "degC_to_dac_coeffs", 1)
        self.bind_lineEdit        (cfu.lineEdit_ee_degC_to_dac_coeff_2,       "degC_to_dac_coeffs", 2)
        self.bind_lineEdit        (cfu.lineEdit_ee_detector,                  "detector")
        self.bind_lineEdit        (cfu.lineEdit_ee_laser_power_coeff_0,       "laser_power_coeffs", 0)
        self.bind_lineEdit        (cfu.lineEdit_ee_laser_power_coeff_1,       "laser_power_coeffs", 1)
        self.bind_lineEdit        (cfu.lineEdit_ee_laser_power_coeff_2,       "laser_power_coeffs", 2)
        self.bind_lineEdit        (cfu.lineEdit_ee_laser_power_coeff_3,       "laser_power_coeffs", 3)
        self.bind_lineEdit        (cfu.lineEdit_ee_linearity_coeff_0,         "linearity_coeffs", 0)
        self.bind_lineEdit        (cfu.lineEdit_ee_linearity_coeff_1,         "linearity_coeffs", 1)
        self.bind_lineEdit        (cfu.lineEdit_ee_linearity_coeff_2,         "linearity_coeffs", 2)
        self.bind_lineEdit        (cfu.lineEdit_ee_linearity_coeff_3,         "linearity_coeffs", 3)
        self.bind_lineEdit        (cfu.lineEdit_ee_linearity_coeff_4,         "linearity_coeffs", 4)
        self.bind_lineEdit        (cfu.lineEdit_ee_model,                     "model")
        self.bind_lineEdit        (cfu.lineEdit_ee_serial_number,             "serial_number")
        self.bind_lineEdit        (cfu.lineEdit_ee_user_text,                 "user_text")
        self.bind_lineEdit        (cfu.lineEdit_ee_wavelength_coeff_0,        "wavelength_coeffs", 0)
        self.bind_lineEdit        (cfu.lineEdit_ee_wavelength_coeff_1,        "wavelength_coeffs", 1)
        self.bind_lineEdit        (cfu.lineEdit_ee_wavelength_coeff_2,        "wavelength_coeffs", 2)
        self.bind_lineEdit        (cfu.lineEdit_ee_wavelength_coeff_3,        "wavelength_coeffs", 3)
        self.bind_lineEdit        (cfu.lineEdit_ee_wavelength_coeff_4,        "wavelength_coeffs", 4)
        self.bind_lineEdit        (cfu.lineEdit_ee_product_configuration,     "product_configuration")
        self.bind_lineEdit        (cfu.lineEdit_ee_raman_intensity_coeff_0,   "raman_intensity_coeffs", 0)
        self.bind_lineEdit        (cfu.lineEdit_ee_raman_intensity_coeff_1,   "raman_intensity_coeffs", 1)
        self.bind_lineEdit        (cfu.lineEdit_ee_raman_intensity_coeff_2,   "raman_intensity_coeffs", 2)
        self.bind_lineEdit        (cfu.lineEdit_ee_raman_intensity_coeff_3,   "raman_intensity_coeffs", 3)
        self.bind_lineEdit        (cfu.lineEdit_ee_raman_intensity_coeff_4,   "raman_intensity_coeffs", 4)
        self.bind_lineEdit        (cfu.lineEdit_ee_raman_intensity_coeff_5,   "raman_intensity_coeffs", 5)
        self.bind_lineEdit        (cfu.lineEdit_ee_raman_intensity_coeff_6,   "raman_intensity_coeffs", 6)
        self.bind_lineEdit        (cfu.lineEdit_ee_raman_intensity_coeff_7,   "raman_intensity_coeffs", 7)
        self.bind_lineEdit        (cfu.lineEdit_ee_spline_wl_0,               "spline_wavelengths", 0)
        self.bind_lineEdit        (cfu.lineEdit_ee_spline_wl_1,               "spline_wavelengths", 1)
        self.bind_lineEdit        (cfu.lineEdit_ee_spline_wl_2,               "spline_wavelengths", 2)
        self.bind_lineEdit        (cfu.lineEdit_ee_spline_wl_3,               "spline_wavelengths", 3)
        self.bind_lineEdit        (cfu.lineEdit_ee_spline_wl_4,               "spline_wavelengths", 4)
        self.bind_lineEdit        (cfu.lineEdit_ee_spline_wl_5,               "spline_wavelengths", 5)
        self.bind_lineEdit        (cfu.lineEdit_ee_spline_wl_6,               "spline_wavelengths", 6)
        self.bind_lineEdit        (cfu.lineEdit_ee_spline_wl_7,               "spline_wavelengths", 7)
        self.bind_lineEdit        (cfu.lineEdit_ee_spline_wl_8,               "spline_wavelengths", 8)
        self.bind_lineEdit        (cfu.lineEdit_ee_spline_wl_9,               "spline_wavelengths", 9)
        self.bind_lineEdit        (cfu.lineEdit_ee_spline_wl_10,              "spline_wavelengths", 10)
        self.bind_lineEdit        (cfu.lineEdit_ee_spline_wl_11,              "spline_wavelengths", 11)
        self.bind_lineEdit        (cfu.lineEdit_ee_spline_wl_12,              "spline_wavelengths", 12)
        self.bind_lineEdit        (cfu.lineEdit_ee_spline_wl_13,              "spline_wavelengths", 13)

        for region in range(2, 5):
            for i in range(4):
                self.bind_lineEdit(getattr(cfu, f"lineEdit_ee_regions_{region}_coeff_{i}"), f"roi_wavecal_region_{region}_coeffs", i)

        self.bind_spinBox         (cfu.spinBox_ee_active_pixels_horizontal,   "active_pixels_horizontal")
        self.bind_spinBox         (cfu.spinBox_ee_active_pixels_vertical,     "active_pixels_vertical")
        self.bind_spinBox         (cfu.spinBox_ee_actual_pixels_horizontal,   "actual_pixels_horizontal")
        for i in range(15):
            self.bind_spinBox(getattr(cfu, f"spinBox_ee_bad_pixel_{i}"), "bad_pixels", i)
        self.bind_spinBox         (cfu.spinBox_ee_baud_rate,                  "baud_rate")
        self.bind_spinBox         (cfu.spinBox_ee_detector_offset,            "detector_offset")
        self.bind_spinBox         (cfu.spinBox_ee_detector_offset_odd,        "detector_offset_odd")
        self.bind_spinBox         (cfu.spinBox_ee_max_integration_time_ms,    "max_integration_time_ms")
        self.bind_spinBox         (cfu.spinBox_ee_max_temp_degC,              "max_temp_degC")
        self.bind_spinBox         (cfu.spinBox_ee_min_integration_time_ms,    "min_integration_time_ms")
        self.bind_spinBox         (cfu.spinBox_ee_min_temp_degC,              "min_temp_degC")
        self.bind_spinBox         (cfu.spinBox_ee_roi_horizontal_end,         "roi_horizontal_end")
        self.bind_spinBox         (cfu.spinBox_ee_roi_horizontal_start,       "roi_horizontal_start")
        self.bind_spinBox         (cfu.spinBox_ee_roi_vertical_region_1_end,  "roi_vertical_region_1_end")
        self.bind_spinBox         (cfu.spinBox_ee_roi_vertical_region_1_start,"roi_vertical_region_1_start")
        self.bind_spinBox         (cfu.spinBox_ee_roi_vertical_region_2_end,  "roi_vertical_region_2_end")
        self.bind_spinBox         (cfu.spinBox_ee_roi_vertical_region_2_start,"roi_vertical_region_2_start")
        self.bind_spinBox         (cfu.spinBox_ee_roi_vertical_region_3_end,  "roi_vertical_region_3_end")
        self.bind_spinBox         (cfu.spinBox_ee_roi_vertical_region_3_start,"roi_vertical_region_3_start")
        self.bind_spinBox         (cfu.spinBox_ee_slit_size_um,               "slit_size_um")
        self.bind_spinBox         (cfu.spinBox_ee_startup_integration_time_ms,"startup_integration_time_ms")
        self.bind_spinBox         (cfu.spinBox_ee_startup_temp_degC,          "startup_temp_degC")
        self.bind_spinBox         (cfu.spinBox_ee_startup_triggering_scheme,  "startup_triggering_scheme")
        self.bind_spinBox         (cfu.spinBox_ee_thermistor_beta,            "tec_beta")
        self.bind_spinBox         (cfu.spinBox_ee_thermistor_resistance_298K, "tec_r298")
        self.bind_spinBox         (cfu.spinBox_ee_raman_intensity_calibration_order, "raman_intensity_calibration_order")
        self.bind_spinBox         (cfu.spinBox_ee_subformat,                  "subformat")
        self.bind_spinBox         (cfu.spinBox_ee_spline_points,              "spline_points")
        self.bind_spinBox         (cfu.spinBox_ee_laser_warmup_sec,           "laser_warmup_sec")
        self.bind_spinBox         (cfu.spinBox_ee_untethered_library_type,    "untethered_library_type")
        self.bind_spinBox         (cfu.spinBox_ee_untethered_library_id,      "untethered_library_id")
        self.bind_spinBox         (cfu.spinBox_ee_untethered_scans_to_average,"untethered_scans_to_average")
        self.bind_spinBox         (cfu.spinBox_ee_untethered_min_ramp_pixels, "untethered_min_ramp_pixels")
        self.bind_spinBox         (cfu.spinBox_ee_untethered_min_peak_height, "untethered_min_peak_height")
        self.bind_spinBox         (cfu.spinBox_ee_untethered_match_threshold, "untethered_match_threshold")
        self.bind_spinBox         (cfu.spinBox_ee_untethered_library_count,   "untethered_library_count")
        self.bind_spinBox         (cfu.spinBox_ee_regions_count,              "region_count")
        self.bind_spinBox         (cfu.spinBox_ee_regions_4_vertical_start,   "roi_vertical_region_4_start")
        self.bind_spinBox         (cfu.spinBox_ee_regions_4_vertical_end,     "roi_vertical_region_4_end")
        self.bind_spinBox         (cfu.spinBox_ee_laser_watchdog_sec,         "laser_watchdog_sec")
        self.bind_spinBox         (cfu.spinBox_ee_light_source_type,          "light_source_type")
        self.bind_spinBox         (cfu.spinBox_ee_power_timeout_sec,          "power_timeout_sec")
        self.bind_spinBox         (cfu.spinBox_ee_detector_timeout_sec,       "detector_timeout_sec")
        self.bind_spinBox         (cfu.spinBox_ee_horiz_binning_mode,         "horiz_binning_mode")
        for region in range(2, 5):
            for node in ("start", "end"):
                self.bind_spinBox(getattr(cfu, f"spinBox_ee_regions_{region}_horiz_{node}"), f"roi_horiz_region_{region}_{node}")

        cfu.spinBox_ee_raman_intensity_calibration_order.setMaximum(EEPROM.MAX_RAMAN_INTENSITY_CALIBRATION_ORDER)

        self.lb_gain_hex = cfu.label_ee_detector_gain_hex

        cfu.pushButton_eeprom_clipboard.clicked.connect(self.copy_to_clipboard)
        cfu.pushButton_importEEPROM.clicked.connect(self.import_eeprom)
        cfu.pushButton_exportEEPROM.clicked.connect(self.export_eeprom)
        cfu.searchLineEdit.textChanged.connect(self.apply_filter)

        self.update_authentication()

    ############################################################################
    # callbacks
    ############################################################################

    def copy_to_clipboard(self):
        table = {}

        ########################################################################
        # EEPROM fields
        ########################################################################

        for name in self.checkBoxes:
            table[name] = getattr(self.eeprom, name)

        for name in self.doubleSpinBoxes:
            table[name] = getattr(self.eeprom, name)

        for name in self.spinBoxes:
            if not isinstance(self.spinBoxes[name], dict):
                table[name] = getattr(self.eeprom, name)
            else:
                for index in self.spinBoxes[name]:
                    array = getattr(self.eeprom, name)
                    k = "%s[%0*d]" % (name, 1 if len(self.spinBoxes[name]) < 10 else 2, index)
                    if array and index < len(array):
                        table[k] = array[index]
                    else:
                        table[k] = ""

        for name in self.lineEdits:
            if not isinstance(self.lineEdits[name], dict):
                table[name] = getattr(self.eeprom, name)
            else:
                for index in self.lineEdits[name]:
                    array = getattr(self.eeprom, name)
                    k = "%s[%0*d]" % (name, 1 if len(self.lineEdits[name]) < 10 else 2, index)
                    if array and index < len(array):
                        table[k] = array[index]
                    else:
                        table[k] = ""

        # read-only (don't appear in above lists)
        table["format"] = self.eeprom.format

        ########################################################################
        # Extra (non-EEPROM)
        ########################################################################

        digest = self.eeprom.generate_digest(regenerate=True)
        table["digest_original"] = self.eeprom.digest
        table["digest_current"] = digest

        spec = self.ctl.multispec.current_spectrometer()
        if spec:
            for attr in [ "microcontroller_firmware_version", 
                          "fpga_firmware_version", 
                          "microcontroller_serial_number", 
                          "detector_serial_number" ]:
                table[attr] = getattr(spec.settings, attr) 
            
        self.ctl.clipboard.copy_dict(table)

    def create_callback(self, name, index=None):
        """
        Dynamically create a new EEPROMEditor class method named for a given
        EEPROM field (with optional index).
        
        Method names will look like this:
        
        - baud_rate_callback 
        - raman_intensity_coeffs_5_callback
        
        The body of the callback function is a unique instance of the function
        f() below, which is simply a pass-through to call widget_callback() with
        the appropriate name and index.
        
        This is done so that each EEPROMEditor widget can be bound to a unique
        callback method, allowing a change in any on-screen field to correctly
        call widget_callback() with the name and index of the EEPROM attribute
        to update.  There are probably other ways to do this, but this worked 
        and was fun.
        """
        def f(*args):
            # log.debug("f: relaying callback to widget_callback(%s)" % name)
            self.widget_callback(name, index)

        if index is None:
            fullname = "%s_callback" % name
        else:
            fullname = "%s_%d_callback" % (name, index)

        setattr(EEPROMEditor, fullname, f)
        # log.debug("create_callback: created %s method" % fullname)

        return f

    def widget_callback(self, name, index=None, reset_from_eeprom=False):
        """
        The user has changed a value in the EEPROM editor, which we need to save 
        back to the EEPROM object.
        
        I really want to use a single callback method for all the EEPROMEditor
        widgets.  I'm currently doing this by dynamically creating unique callback 
        methods for each widget, where each identifies itself via a 'name' 
        parameter (see create_callback).
        
        Another option would be to have EEPROMEditor extend QObject and then use
        QObject.sender():
        https://www.blog.pythonlibrary.org/2013/04/10/pyside-connecting-multiple-widgets-to-the-same-slot/
        
        Note that because we're using getattr and setattr against the EEPROM 
        instance, it doesn't matter if someone has reassigned eeprom.wavelength_coeffs
        to a new []...the widgets are bound to the NAME of the attribute, and can't
        be left hanging with a reference to an old referent.
        
        @param reset_from_eeprom[in] If True, copy EEPROM field -> widget; if False, copy widget -> EEPROM field.
               To my knowledge, this field is ONLY added when called from LaserControlFeature.
        """
        log.debug("callback triggered for widget %s (index %s, reset %s)", name, index, reset_from_eeprom)

        value = None
        try:
            if name in self.checkBoxes:
                widget = self.checkBoxes[name]
                if reset_from_eeprom:
                    value = getattr(self.eeprom, name)
                    widget.setValue(value)
                else:
                    value = widget.isChecked()
                    setattr(self.eeprom, name, value)

            elif name in self.doubleSpinBoxes:
                widget = self.doubleSpinBoxes[name]
                if reset_from_eeprom:
                    value = getattr(self.eeprom, name)
                    log.debug("widget_callback[doubleSpinBoxes]: setting widget.value <-- %g (%.9f)", value, value)
                    widget.setValue(value)
                else:
                    value = float(widget.value())
                    log.debug("widget_callback[doubleSpinBoxes]: widget.value() = %g (%.9f)", widget.value(), widget.value())
                    setattr(self.eeprom, name, value)

            elif name in self.spinBoxes:
                if index is None:
                    widget = self.spinBoxes[name]
                    if reset_from_eeprom:
                        value = getattr(self.eeprom, name)
                        widget.setValue(value)
                    else:
                        value = int(widget.value())
                        setattr(self.eeprom, name, value)
                else:
                    widget = self.spinBoxes[name][index]
                    array = getattr(self.eeprom, name)
                    if reset_from_eeprom:
                        widget.setValue(array[index])
                    else:
                        value = int(widget.value())

                        # adding bad_pixels
                        while index >= len(array):
                            log.debug("appending %s element %d to reach %d", name, len(array), index)
                            array.append(-1)

                        # store updated value
                        array[index] = value
                
            elif name in self.lineEdits:
                if index is None:
                    widget = self.lineEdits[name]
                    if reset_from_eeprom:
                        value = getattr(self.eeprom, name)
                        widget.setText(str(value))
                    else:
                        value = widget.text()
                        setattr(self.eeprom, name, value)
                else:
                    # remember, we're assuming that all ARRAY lineEdits are FLOATS
                    widget = self.lineEdits[name][index]
                    array = getattr(self.eeprom, name)
                    if reset_from_eeprom:
                        widget.setText(self.sci_str(array[index]))
                    else:
                        value = float(widget.text())

                        # handle case where input array is None
                        if array is None or type(array) is not list:
                            log.debug("creating %s array", name)
                            array = []
                            setattr(self.eeprom, name, array)

                        # handle case where input array hasn't been sized
                        while index >= len(array):
                            log.debug("appending %s element %d", name, len(array) - 1)
                            array.append(0)

                        # store updated value
                        array[index] = value
            else:
                log.error("widget_callback: widget %s not of any recognized type", name)
                return

            if index is None:
                log.debug("widget_callback: eeprom.%s -> %s", name, value)
            else:
                log.debug("widget_callback: eeprom.%s[%d] -> %s", name, index, value)

            ####################################################################
            # name-based extra functionality 
            ####################################################################

            # these are pretty much all kludges...should create an observer pattern
            # based on regex, e.g. "wavelength_coeffs|excitation_nm_float"

            # Wavecal
            if name.startswith("wavelength_coeffs") or name == "excitation_nm_float":
                self.ctl.update_wavecal()

            # Detector
            elif self.updated_from_eeprom and ("detector_gain" in name or "detector_offset" in name):
                log.debug("widget_callback: gain or offset updated post-init, so forcing those downstream")
                self.ctl.update_gain_and_offset(force=True)
                self.update_gain_in_hex()

            # SRM
            elif "raman_intensity" in name and self.settings is not None:
                self.settings.update_raman_intensity_factors()

            # subformat
            elif name == "subformat":
                self.update_subformat()

            # vertical ROI
            elif "roi_vertical_region_1" in name:
                spec = self.ctl.multispec.current_spectrometer()
                if spec is not None:
                    end = self.eeprom.roi_vertical_region_1_end
                    start = self.eeprom.roi_vertical_region_1_start
                    spec.change_device_setting("vertical_binning", (start, end))

            # send "user" updates downstream (not when switching between spectrometers though)
            if self.updated_from_eeprom:
                self.ctl.eeprom_writer.send_to_subprocess()

            ####################################################################
            # update digest (highlight if changed)
            ####################################################################

            self.update_digest()

        except Exception:
            log.error("widget_callback: caught exception for name '%s', index %s", name, index, exc_info=1)

        # TODO: call Controller.change_setting("eeprom", self.eeprom) on 
        #       successful value change?

    # ##########################################################################
    # methods
    # ##########################################################################

    def update_gain_in_hex(self):
        """ production request: display detector_gain in hex """
        spec = self.ctl.multispec.current_spectrometer()
        if spec is not None:
            gain_uint16 = spec.settings.eeprom.float_to_uint16(spec.settings.eeprom.detector_gain)
            self.lb_gain_hex.setText("0x%04x" % gain_uint16)

    def update_digest(self):
        """
        There is a potential issue here.  We are really colorizing the 
        digest not only if fields have been actively changed on the GUI,
        but if THE CURRENT VERSION OF ENLIGHTEN would save the EEPROM with
        different buffer contents.  Therefore, if a spectrometer's EEPROM
        has format 9, and the curent version of ENLIGHTEN would save it 
        with format 11, then the digest will show a difference (red) even
        though nothing has been changed by the user.
        """
        new_digest = self.eeprom.generate_digest(regenerate=True)
        if self.eeprom.digest == new_digest:
            css = "white_text"
            tt = "EEPROM has latest format and is unchanged"
        elif self.eeprom.format != self.eeprom.latest_rev():
            css = "yellow_text"   
            tt = "EEPROM has older format (%d != %d)" % (self.eeprom.format, self.eeprom.latest_rev())
        else:
            css = "red_text"   
            tt = "EEPROM has current format but contents changed since load"
        self.ctl.stylesheets.apply(self.lb_digest, css)
        self.lb_digest.setText(new_digest)
        self.lb_digest.setToolTip(tt)

    def sci_str(self, n):
        """
        Render a floating-point value as a float32 in scientific notation, with no
        more digits of precision than Python2.7 (would have to make fields much
        wider to support Python3's apparent float64 internal precision).
        """
        decimal.getcontext().prec = 8
        return '%e' % decimal.getcontext().create_decimal_from_float(float(n))

    def update_authentication(self):
        """ The user logged-in (or -out), so update what should be updated. """
        for widget in self.widgets:
            editable = False 

            if self.ctl.authentication.has_production_rights():
                editable = True 
            elif self.ctl.authentication.has_advanced_rights():
                editable = widget.is_editable   # both Advanced and OEM can edit "many"

            widget.setEnabled(editable)

            if editable:
                widget.setStyleSheet("background: #444; color: #ccc;")
            else:
                widget.setStyleSheet("color: #eee;")

    def update_fpga_option_display(self):
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return

        fpga = spec.settings.fpga_options
        cfu = self.ctl.form.ui

        cfu.label_fpga_integration_time_resolution  .setText(fpga.stringify_resolution())
        cfu.label_fpga_data_header                  .setText(fpga.stringify_header())
        cfu.label_fpga_has_cf_select                .setText(str(fpga.has_cf_select))
        cfu.label_fpga_laser_type                   .setText(fpga.stringify_laser_type())
        cfu.label_fpga_laser_control                .setText(fpga.stringify_laser_control())
        cfu.label_has_area_scan                     .setText(str(fpga.has_area_scan))
        cfu.label_has_actual_integration_time       .setText(str(fpga.has_actual_integ_time))
        cfu.label_has_horizontal_binning            .setText(str(fpga.has_horiz_binning))

    def update_from_spec(self):
        """
        A new spectrometer has connected, or been selected in Multispec, and
        the EEPROM Editor should update its widgets to display the current
        spectrometer's settings.
        
        We don't call blockSignals(), so each call to setValue() should trigger
        the appropriate bound callback (passed-through to widget_callback()).
        
        However, we don't want to send a long stream of "send_to_subprocess"
        events, so only send one at the end of this update if needed.
        """
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return

        self.settings = spec.settings
        self.eeprom = self.settings.eeprom
        self.updated_from_eeprom = False

        self.ctl.form.ui.label_ee_format.setText(str(self.eeprom.format))
        self.lb_digest.setText(str(self.eeprom.digest))

        # update the big serial number and graphic atop Hardware Setup
        self.lb_serial.setText(self.eeprom.serial_number)
        pathname = spec.get_image_pathname()
        if self.ctl.image_resources.contains(pathname):
            self.lb_product_image.setPixmap(QtGui.QPixmap(pathname))
        else:
            log.error(f"received pathname not in resources: {pathname}")

        for name in self.checkBoxes:
            value = getattr(self.eeprom, name)
            if value is not None:
                widget = self.checkBoxes[name]
                widget.setChecked(True if value else False)
            else:
                log.debug("update_from_spec: checkbox bool %s is None", name)

        try:
            log.debug("update_from_spec: doublespinboxes")
            for name in self.doubleSpinBoxes:
                value = getattr(self.eeprom, name)
                if value is not None:
                    log.debug("update_from_spec: %s -> %s", name, value)
                    widget = self.doubleSpinBoxes[name]
                    widget.setValue(float(value))
                else:
                    log.debug("update_from_spec: doublespinbox float %s is None", name)

            log.debug("update_from_spec: spinboxes")
            for name in self.spinBoxes:
                if not isinstance(self.spinBoxes[name], dict):
                    # this is an int scalar
                    value = getattr(self.eeprom, name)
                    if value is not None:
                        widget = self.spinBoxes[name]
                        widget.setValue(int(value))
                    else:
                        log.debug("update_from_spec: spinbox int scalar %s is None", name)
                else:
                    # this is an array of ints like "bad_pixels"...which is variable-sized, unlike the coeffs :-/
                    for index in self.spinBoxes[name]:
                        array = getattr(self.eeprom, name)
                        if index < len(array):
                            value = array[index]
                            if value is not None:
                                widget = self.spinBoxes[name][index]
                                widget.setValue(int(value))
                            else:
                                log.debug("update_from_spec: spinbox int array %s %d is None", name, index)
        except:
            log.error("exception populating EEPROM numeric fields", exc_info=1)            

        log.debug("update_from_spec: lineEdits")
        for name in self.lineEdits:
            if not isinstance(self.lineEdits[name], dict):
                # this is a string scalar
                value = getattr(self.eeprom, name)
                if value is not None:
                    widget = self.lineEdits[name]
                    widget.setText(str(value))
                else:
                    log.debug("update_from_spec: lineedit int scalar %s is None", name)
            else:
                # this is an array of floats edited as strings, like "wavelength_coeffs"
                for index in self.lineEdits[name]:
                    array = getattr(self.eeprom, name)
                    if array:
                        if index < len(array):
                            value = array[index]
                            widget = self.lineEdits[name][index]
                            widget.setText(self.sci_str(value))
                            continue
                    log.debug("update_from_spec: could not update lineedit string array %s %d", name, index)

        self.update_subformat()
        self.update_gain_in_hex()
        self.update_fpga_option_display()

        self.updated_from_eeprom = True

    def update_subformat(self):
        """ Update our display of which (if any) frame representing page 6-7 fields is visible. """

        # hide them all
        log.debug("updating subformat")
        for frame in self.subformat_frames:
            if frame is not None:
                frame.setVisible(False)

        sub = self.eeprom.subformat

        if sub < len(self.subformat_frames):
            frame = self.subformat_frames[sub]
            if frame:
                frame.setVisible(True)
                log.debug("visualizing frame %d", sub)

        # subformat 3 extends subformat 1
        if sub == 3:
            self.subformat_frames[1].setVisible(True)

    def apply_filter(self, filter_text: str) -> None:
        """
        Hides all widgets to which the filter applies.
        """
        for layout in self.filterable_layouts:
            if isinstance(layout, QtWidgets.QFormLayout):
                rows = [[None, None] for _ in range(0, layout.rowCount())]

                for i in range(0, layout.count()):
                    rowIndex, role = layout.getItemPosition(i)
                    rows[rowIndex][role.value] = layout.itemAt(i)

                for i, row in enumerate(rows):
                    matches_filter = False

                    for cell in row:
                        if self.contains_text(cell, filter_text):
                            matches_filter = True

                    if matches_filter:
                        for cell in row:
                            self.show(cell)
                    else:
                        for cell in row:
                            self.hide(cell)

    @classmethod
    def contains_text(cls, root: any, filter_text: str) -> bool:
        """
        Recursively searches `root` for any label containing the string `filter_text`.
        """
        if isinstance(root, QtWidgets.QLayout):
            for i in range(0, root.count()):
                if cls.contains_text(root.itemAt(i), filter_text):
                    return True

            return False
        elif isinstance(root, QtWidgets.QLayoutItem):
            widget = root.widget()

            if not isinstance(widget, QtWidgets.QLabel):
                return False

            return re.search(re.escape(filter_text), widget.text(), re.IGNORECASE)
        else:
            return False

    @classmethod
    def hide(cls, root: any) -> None:
        """
        Recursively hides all children of `root`.
        """
        if isinstance(root, QtWidgets.QLayout):
            for i in range(0, root.count()):
                cls.hide(root.itemAt(i))
        elif isinstance(root, QtWidgets.QLayoutItem):
            widget = root.widget()

            if widget is not None:
                widget.hide()

    @classmethod
    def show(cls, root: any) -> None:
        """
        Recursively shows all children of `root`.
        """
        if isinstance(root, QtWidgets.QLayout):
            for i in range(0, root.count()):
                cls.show(root.itemAt(i))
        elif isinstance(root, QtWidgets.QLayoutItem):
            widget = root.widget()

            if widget is not None:
                widget.show()

    # ##########################################################################
    # Binding
    # ##########################################################################

    def bind_checkBox(self, widget, name):
        if not hasattr(self.eeprom, name):
            log.error("unknown EEPROM field: %s", name)
            return
        self.checkBoxes[name] = widget
        widget.stateChanged.connect(self.create_callback(name))
        widget.is_editable = self.eeprom.is_editable(name)
        self.widgets.append(widget)

    def bind_doubleSpinBox(self, widget, name):
        if not hasattr(self.eeprom, name):
            log.error("unknown EEPROM field: %s", name)
            return
        self.doubleSpinBoxes[name] = widget
        widget.valueChanged.connect(self.create_callback(name))
        widget.is_editable = self.eeprom.is_editable(name)
        self.widgets.append(widget)

    def bind_spinBox(self, widget, name, index=None):
        if not hasattr(self.eeprom, name):
            log.error("unknown EEPROM field: %s", name)
            return

        if index is None:
            self.spinBoxes[name] = widget
        else:
            if name not in self.spinBoxes:
                self.spinBoxes[name] = {}
            self.spinBoxes[name][index] = widget

        # note that we're not currently using anything like "editingFinished"
        # with spinboxen, so intermediate changes will probably fire multiple
        # events (if you try to type 1234, it may fire events with values of 1,
        # 12, 123 and 1234 in sequence).  
        #
        # If those incremental changes get sent to the spectrometer process
        # downstream, the "auto-dedupping" in WasatchPhotonicsWrapper MAY
        # eliminate some of the incremental steps and retain only the the
        # final ones (depends on your typing speed...)
        widget.valueChanged.connect(self.create_callback(name, index))
        widget.is_editable = self.eeprom.is_editable(name)
        self.widgets.append(widget)

    def bind_lineEdit(self, widget, name, index=None, sub_index=None):
        if not hasattr(self.eeprom, name):
            log.error("unknown EEPROM field: %s", name)
            return

        if index is None:
            self.lineEdits[name] = widget
        else:
            if name not in self.lineEdits:
                self.lineEdits[name] = {}
            self.lineEdits[name][index] = widget

        callback = self.create_callback(name, index)
        widget.editingFinished.connect(callback)
        widget.is_editable = self.eeprom.is_editable(name)
        self.widgets.append(widget)

        # MZ: I'm sure there's a better way to do this
        widget.enlighten_trigger = callback

    def parse_wpsc_report(self, wpsc_report: dict) -> dict:
        eeprom_dump = wpsc_report["EEPROMDump"]
        translation_keys = self.wpsc_translations.keys()

        def capital_to_snake(key):
            snake_case = re.sub(r"(.)([A-Z])(?=[a-z]+)|(.)([A-Z]{2,})$", r'\1\3_\2\4', key) # catches most
            snake_case = snake_case.lower()
            log.debug(f"got key {key}, converted to {snake_case}")
            if snake_case in translation_keys:
                snake_case = self.wpsc_translations[snake_case]
                log.debug(f"key found in translation, returning instead {snake_case}")
            else:
                log.debug(f"key {snake_case} not found in translation, returning as is")
            return snake_case

        eeprom_dump = {capital_to_snake(key): item for key, item in eeprom_dump.items()}
        eeprom_dump["excitation_nm_float"] = eeprom_dump["excitation_nm"]
        roi_starts = eeprom_dump["roi_vert_region_starts"]
        roi_ends = eeprom_dump["roi_vert_region_ends"]

        for idx, region in enumerate(zip(roi_starts, roi_ends)):
            start, end = region
            eeprom_dump[f"roi_vertical_region_{idx + 1}_start"] = start
            eeprom_dump[f"roi_vertical_region_{idx + 1}_end"] = end

        return eeprom_dump

    def import_eeprom(self, file_name=None):
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return False
        self.settings = spec.settings
        self.eeprom = self.settings.eeprom

        if not file_name: 
            log.debug(f"no file provided for import, prompting user for eeprom")
            file_name = QtWidgets.QFileDialog.getOpenFileName(None,
                "Open EEPROM", common.get_default_data_dir(), "EEPROM Files (*.json)")
            if file_name is not None:
                # file_name is a tuple with the first element being the actual name
                with open(file_name[0],'r') as eeprom_file:
                    eeprom_json = json.load(eeprom_file)
            else:
                log.error("Error in selecting eeprom file to load")
                return False
        else:
            with open(file_name,'r') as eeprom_file:
                eeprom_json = json.load(eeprom_file)

        eeprom_dict = dict(eeprom_json)
        eeprom_keys = list(eeprom_dict.keys())
        if eeprom_keys[0].lower() != eeprom_keys[0]:
            log.debug(f"capital case found, converting wpsc keys")
            eeprom_dict = self.parse_wpsc_report(eeprom_dict)
            if eeprom_dict == {}:
                log.error(f"error in wpsc parse, receveid an empty dict")
                return False
        for key, value in eeprom_dict.items():
            setattr(self.eeprom,key,value)
        self.update_from_spec()
        return True

    def export_eeprom(self):
        file_name = QtWidgets.QFileDialog.getSaveFileName(None,
            "Export EEPROM", common.get_default_data_dir(), "EEPROM Files (*.json)")
        if file_name is not None:
            self.ctl.eeprom_writer.backup(file_name[0])
        else:
            log.error("Error in selecting save location path for eeprom")
