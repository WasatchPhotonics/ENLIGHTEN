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

class EEPROMAttribute:
    
    def __init__(self, name, qtype, widget=None, widgets=None, is_numeric=True):
        self.name = name
        self.is_numeric = is_numeric    # for lineedit attributes, should this text field be treated as a float for get/set purposes?

        self.is_scalar = False          # is this a array like wavelength_coeffs (lineedit) or bad_pixels (spinbox), or a scalar like excitation_nm_float or serial_number?
        self.is_multi = False           # does this attribute support multiple values for different wavelength calibrations per subformat 5?
        self.is_editable = False        # should this field be editable using the "wasatch" and "wasatchoem" passwords?
        self.count = 0                  # if this attribute is a list (non-scalar), how many elements does it have?
        self.calibrations = 0           # if this attribute is_multi, how many calibrations does it have?

        # validate qtype
        self.qtype = qtype.lower().lstrip("q") # "lineedit", "spinbox", "doublespinbox"
        if self.qtype not in ["checkbox", "spinbox", "doublespinbox", "lineedit"]:
            raise AttributeError(f"invalid EEPROMAttribute.qtype {self.qtype}")

        # were we only passed a single widget, or some sort of list?
        if widget is not None and widgets is None:
            # standard case for a regular scalar (e.g. serial_number)
            self.is_multi = False
            self.is_scalar = True
            self.widget = widget
            return # nothing more to do
        elif widget is None and widgets is None:
            raise AttributeError("EEPROMAttribute needs either widget or widgets populated")
        elif widget is not None and widgets is not None:
            raise AttributeError("EEPROMAttribute can only accept a widget OR widgets, but not both")

        # apparently we were passed a list of widgets, whether single-calibration
        # array, multi-wavelength scalar, or multi-wavelength array
        self.widgets = widgets

        ########################################################################
        # infer is_multi and is_scalar from widgets list structure
        ########################################################################

        # Apparently we received a list of widgets, so figure out which type:
        #
        # - Multi-wavelength attributes are indicated by a list of lists, where 
        #   the outer list is multi-wavelength index (default or 2nd), and the 
        #   inner list is element index. By way of example, the multi-wavelength 
        #   array wavelength_coeffs would be passed as 
        #   [ [ c0, c1, c2, c3, c4 ], [ c0, c1, c2, c3, c4 ] ], and the multi-
        #   wavelength scalar avg_resolution as [ [ fwhm ], [ fwhm ] ]
        #
        # - If a SINGLE-DEPTH list is passed, that would indicate an array 
        #   attribute which is NOT multi-wavelength, such as laser_power_coeffs 
        #   or adc_to_temp_coeffs.

        outer_len = len(widgets)
        nested_list = isinstance(widgets[0], list)

        if not nested_list:
            # e.g., adc_to_temp_coeffs (lineedit) or bad_pixels (spinbox)
            self.count = outer_len
            self.is_multi = False
            self.is_scalar = False
            log.debug("EEPROMAttribute: non-multi-wavelength array {name} of {outer_len} elements")
        else:
            self.is_multi = True
            self.calibrations = outer_len
            inner_len = len(widgets[0])

            if inner_len <= 0:
                raise AttributeError("EEPROMAttribute: doesn't support empty inner list")
            elif inner_len == 1:
                # e.g., excitation_nm_float or avg_resolution (doublespinbox), or roi_horizontal_start/end (spinbox)
                self.is_multi = True
                self.is_scalar = True
                log.debug("EEPROMAttribute: name {name} appears to be multi-wavelength array of {self.calibrations} scalar elements")
            else:
                # e.g., wavelength_coeffs or raman_intensity_coeffs (lineedit)
                log.debug("EEPROMAttribute: name {name} appears to be multi-wavelength matrix with {self.calibrations} arrays of {inner_len} elements")
                self.is_multi = True
                self.is_scalar = False
                self.count = inner_len 

        log.debug(f"EEPROMAttribute: name {self.name}, is_multi {self.is_multi}, is_scalar {self.is_scalar}, count {self.count}")

    def __repr__(self):
        return (f"EEPROMAttribute<name {self.name}, is_multi {self.is_multi}, is_scalar {self.is_scalar}, count {self.count}>")

    def get_widget_value(self, calibration=None, index=None):
        if calibration is None:
            calibration = 0
        if index is None:
            index = 0
        
        # get the specified widget
        widget = None
        if self.is_multi:
            widget = self.widgets[calibration][index]
        else:
            if self.is_scalar:
                widget = self.widget
            else:
                widget = self.widgets[index]

        # extract the value
        if self.qtype == "lineedit": 
            if self.is_numeric:
                return float(widget.text())
            else:
                return str(widget.text())
        elif self.qtype == "checkbox": 
            return widget.isChecked()
        elif self.qtype == "spinbox":
            return int(widget.value())
        elif self.qtype == "doublespinbox":
            return float(widget.value())
        else:
            raise AttributeError(f"invalid EEPROMAttribute.qtype {self.qtype}")

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

        self.attributes      = {}
        self.doubleSpinBoxes = {}
        self.lineEdits       = {}
        self.widgets         = []

        # mapping from eeprom.subformat to which widget should be visible
        self.subformat_frames = [
            None, # TODO: user_data_2 and user_data_3
            cfu.frame_eeprom_sub_1,
            cfu.frame_eeprom_sub_2,
            cfu.frame_eeprom_sub_3,
            cfu.frame_eeprom_sub_4,
            cfu.frame_eeprom_sub_5
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
            "active_pixels_horiz":      "active_pixels_horizontal",
            "active_pixels_vert":       "active_pixels_vertical",
            "actual_pixels_horiz":      "actual_pixels_horizontal",
            "adc_to_temp_coeffs":       "adc_to_degC_coeffs",
            "bin2x2":                   "horiz_binning_enabled",
            "calibration_by":           "calibrated_by",
            "detector_name":            "detector",
            "detector_temp_max":        "max_temp_degC",
            "detector_temp_min":        "min_temp_degC",
            "excitation_wavelength_nm": "excitation_nm",
            "flip_x_axis":              "invert_x_axis",
            "inc_battery":              "has_battery",
            "inc_cooling":              "has_cooling",
            "inc_laser":                "has_laser",
            "max_laser_power_mw":       "max_laser_power_mW",
            "min_laser_power_mw":       "min_laser_power_mW",
            "product_config":           "product_configuration",
            "rel_int_corr_order":       "raman_intensity_calibration_order",
            "roi_horiz_end":            "roi_horizontal_end",
            "roi_horiz_start":          "roi_horizontal_start",
            "serial":                   "serial_number",
            "slit_width":               "slit_size_um",
            "startup_int_time_ms":      "startup_integration_time_ms",
            "startup_tempc":            "startup_temp_degC",
            "startup_trigger_mode":     "startup_triggering_scheme",
            "temp_todac_coeffs":        "degC_to_dac_coeffs",
            "thermistor_beta":          "tec_beta",
            "thermistor_res_at298k":    "tec_r298",
            "wavecal_coeffs":           "wavelength_coeffs" }

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

    def add_attribute(self, qtype, name, widget=None, widgets=None):
        attr = EEPROMAttribute(name=name, qtype=qtype, widget=widget, widgets=widgets)
        self.attributes[name] = attr

        log.debug("add_attribute: added {attr}")

        if qtype == "checkbox":
            self.bind_checkbox(attr)
        elif qtype in ["spinbox", "doublespinbox"]:
            self.bind_spinbox(attr)
        elif qtype == "lineedit":
            self.bind_lineedit(attr)

    def bind(self):
        """
        Note that self.eeprom is used in the binding process, but just to confirm 
        whether the field exists as an attribute in the current version of 
        wasatch.EEPROM, and if so whether it's editable -- the field's VALUE is not
        (at this point in program flow) read from the EEPROM object or updated to 
        the widgets, until update_from_spec is called.

        Note that many double-precision floating-point values are rendered as 
        QLineEdits, instead of QDoubleSpinBox. That's because coefficients may
        include extremely tiny values (<1-e15) which should be entered, viewed
        and edited in scientific notation, and which do not make visual sense 
        in fixed-decimal format.
        """
        cfu = self.ctl.form.ui

        ########################################################################
        # Scalar Attributes (no arrays, no multi-wavelength)
        ########################################################################

        for name in [ "has_battery", "has_cooling", "has_laser", "invert_x_axis", "horiz_binning_enabled", 
                      "gen15", "cutoff_filter_installed", "hardware_even_odd", "sig_laser_tec", 
                      "has_interlock_feedback", "has_shutter", "disable_ble_power", "disable_laser_armed_indicator" ]:
            self.add_attribute("checkbox", name, widget=getattr(cfu, f"checkBox_ee_{name}"))

        for name in [ "active_pixels_horizontal", "active_pixels_vertical", "actual_pixels_horizontal", 
                      "slit_size_um", "baud_rate", "detector_offset", "detector_offset_odd", 
                      "startup_laser_tec_setpoint", "startup_integration_time_ms", "startup_temp_degC", "startup_triggering_scheme",
                      "min_integration_time_ms", "max_integration_time_ms", "max_temp_degC", "min_temp_degC",
                      "roi_vertical_region_1_end",   "roi_vertical_region_1_start", 
                      "roi_vertical_region_2_end",   "roi_vertical_region_2_start", 
                      "roi_vertical_region_3_end",   "roi_vertical_region_3_start", 
                      "tec_beta", "tec_r298", "raman_intensity_calibration_order", "subformat", "spline_points", "laser_warmup_sec",
                      "untethered_library_type", "untethered_library_id", "untethered_scans_to_average", 
                      "untethered_min_ramp_pixels", "untethered_min_peak_height", "untethered_match_threshold", "untethered_library_count",
                      "laser_watchdog_sec", "light_source_type", "power_timeout_sec", "detector_timeout_sec" ]:
            self.add_attribute("spinbox", name, widget=getattr(cfu, f"spinBox_ee_{name}"))

        for name in [ "max_laser_power_mW", "min_laser_power_mW", "detector_gain", "detector_gain_odd", "spline_min", "spline_max" ]:
            self.add_attribute("doublespinbox", name, widget=getattr(cfu, f"doubleSpinBox_ee_{name}"))

        for name in [ "calibrated_by", "calibration_date", "detector", "model", "serial_number", "user_text", "product_configuration" ]:
            self.add_attribute("lineedit", name, widget=getattr(cfu, f"lineEdit_ee_{name}"))

        # Arrays (but still not multi-wavelength)
        self.add_attribute("lineedit", "laser_power_coeffs", widgets=[ getattr(cfu, f"lineEdit_ee_laser_power_coeff_{i}") for i in range(4) ])
        self.add_attribute("lineedit", "linearity_coeffs",   widgets=[ getattr(cfu, f"lineEdit_ee_linearity_coeff_{i}")   for i in range(5) ])
        self.add_attribute("lineedit", "degC_to_dac_coeffs", widgets=[ getattr(cfu, f"lineEdit_ee_degC_to_dac_coeff_{i}") for i in range(3) ])
        self.add_attribute("lineedit", "adc_to_degC_coeffs", widgets=[ getattr(cfu, f"lineEdit_ee_adc_to_degC_coeff_{i}") for i in range(3) ])
        self.add_attribute("lineedit", "spline_wavelengths", widgets=[ getattr(cfu, f"lineEdit_ee_spline_wl_{i}")         for i in range(14) ])

        self.add_attribute("spinbox", "bad_pixels", widgets=[ getattr(cfu, f"spinBox_ee_bad_pixel_{i}") for i in range(15) ])

        ########################################################################
        # Multi-Wavelength attributes
        ########################################################################

        self.add_attribute("doublespinbox", "excitation_nm_float", widgets=[[cfu.doubleSpinBox_ee_excitation_nm_float], [cfu.doubleSpinBox_ee_sub5_excitation_nm_float]])
        self.add_attribute("doublespinbox", "avg_resolution",      widgets=[[cfu.doubleSpinBox_ee_avg_resolution],      [cfu.doubleSpinBox_ee_sub5_avg_resolution]])

        self.add_attribute("lineedit", "wavelength_coeffs",      widgets=[ [ getattr(cfu, f"lineEdit_ee_wavelength_coeff_{i}") for i in range(5) ],
                                                                           [ getattr(cfu, f"lineEdit_ee_sub5_wavelength_coeff_{i}") for i in range(5) ] ])
        self.add_attribute("lineedit", "raman_intensity_coeffs", widgets=[ [ getattr(cfu, f"lineEdit_ee_raman_intensity_coeff_{i}") for i in range(7) ],
                                                                           [ getattr(cfu, f"lineEdit_ee_sub5_raman_intensity_coeff_{i}") for i in range(7) ] ])

        self.add_attribute("spinbox", "roi_horizontal_end",   widgets=[ [ cfu.spinBox_ee_roi_horizontal_end   ], [ cfu.spinBox_ee_sub5_roi_horizontal_end   ] ])
        self.add_attribute("spinbox", "roi_horizontal_start", widgets=[ [ cfu.spinBox_ee_roi_horizontal_start ], [ cfu.spinBox_ee_sub5_roi_horizontal_start ] ])
        self.add_attribute("spinbox", "horiz_binning_mode",   widgets=[ [ cfu.spinBox_ee_horiz_binning_mode   ], [ cfu.spinBox_ee_sub5_horiz_binning_mode   ] ])

        ########################################################################
        # Misc Cleanup
        ########################################################################

        cfu.spinBox_ee_raman_intensity_calibration_order.setMaximum(EEPROM.MAX_RAMAN_INTENSITY_CALIBRATION_ORDER)

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

        for name, attr in self.attributes.items():
            if attr.is_multi:
                for m in range(attr.calibrations):
                    name = attr.name if m == 0 else f"{attr.name} #{m+1}"
                    table[name] = getattr(self.eeprom, attr.name) # scalar or list
            else:
                table[attr.name] = getattr(self.eeprom, attr.name) # whether scalar or list

        # read-only (don't appear in above lists; not writeable even in admin mode)
        table["format"] = self.eeprom.format

        ########################################################################
        # Extra (non-EEPROM)
        ########################################################################

        digest = self.eeprom.generate_digest(regenerate=True)
        table["digest_original"] = self.eeprom.digest
        table["digest_current"] = digest

        spec = self.ctl.multispec.current_spectrometer()
        if spec:
            for name in [ "microcontroller_firmware_version", 
                          "fpga_firmware_version", 
                          "ble_firmware_version", 
                          "microcontroller_serial_number", 
                          "detector_serial_number" ]:
                table[name] = getattr(spec.settings, name) 
            
        self.ctl.clipboard.copy_dict(table)

    def widget_callback(self, attr=None, widget=None, calibration=None, index=None, value=None):
        """
        The user has changed a value in the enlighten.EEPROMEditor, which we need to save 
        back to the wasatch.EEPROM object.
        """
        log.debug(f"widget_callback: called for calibration {calibration}, index {index}, value {value}, widget {widget}, attr {attr}")

        if attr.is_multi:
            for m in range(attr.calibrations):
                for i, w in enumerate(attr.widgets[m]):
                    log.debug(f"widget_callback: getting widget value for calibration {m}, index {i}")
                    value = attr.get_widget_value(calibration=m, index=i)
                    self.eeprom.multi_wavelength_calibration.set(name=attr.name, value=value, calbration=m, index=i)
        else:
            if attr.is_scalar:
                log.debug(f"widget_callback: getting widget value for scalar")
                value = attr.get_widget_value()
                setattr(self.eeprom, attr.name, value)
            elif index is not None:
                log.debug(f"widget_callback: getting widget value for index {index}")
                value = attr.get_widget_value(index=index)
                old = getattr(self.eeprom, attr.name)
                old[index] = value
            else:
                raise AttributeError(f"widget_callback does not support non-multi, non-scalar attributes with no index: {attr}")

        ####################################################################
        # name-based extra functionality 
        ####################################################################

        # these are pretty much all kludges...should create an observer pattern
        # based on regex, e.g. "wavelength_coeffs|excitation_nm_float"

        # Wavecal
        if attr.name.startswith("wavelength_coeffs") or attr.name == "excitation_nm_float":
            self.ctl.update_wavecal()

        # Detector
        elif self.updated_from_eeprom and ("detector_gain" in attr.name or "detector_offset" in attr.name):
            log.debug("widget_callback: gain or offset updated post-init, so forcing those downstream")
            self.ctl.update_gain_and_offset(force=True)

        # SRM
        elif "raman_intensity" in attr.name and self.settings is not None:
            self.settings.update_raman_intensity_factors()

        # subformat
        elif attr.name == "subformat":
            self.update_subformat()

        # vertical ROI
        elif "roi_vertical_region" in attr.name:
            spec = self.ctl.multispec.current_spectrometer()
            if spec is not None:
                vert_roi = self.eeprom.get_vertical_roi()
                if vert_roi is not None:
                    spec.change_device_setting("vertical_binning", vert_roi)

        # send "user" updates downstream (not when switching between spectrometers though)
        if self.updated_from_eeprom:
            self.ctl.eeprom_writer.send_to_subprocess()

        ####################################################################
        # update digest (highlight if changed)
        ####################################################################

        self.update_digest()

    # ##########################################################################
    # methods
    # ##########################################################################

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
        cfu = self.ctl.form.ui

        cfu.label_ee_format.setText(str(self.eeprom.format))
        self.lb_digest.setText(str(self.eeprom.digest))

        # update the big serial number and graphic atop Hardware Setup
        self.lb_serial.setText(self.eeprom.serial_number)
        pathname = spec.get_image_pathname()
        if self.ctl.image_resources.contains(pathname):
            self.lb_product_image.setPixmap(QtGui.QPixmap(pathname))
        else:
            log.error(f"received pathname not in resources: {pathname}")

        for name, attr in self.attributes.items():
            try:
                if attr.qtype == "checkbox":
                    attr.widget.setChecked(True if getattr(self.eeprom, attr.name) else False)

                elif attr.qtype == "spinbox":
                    if attr.is_multi:
                        if attr.is_scalar:                      # e.g. horiz_bin_method
                            for m in range(attr.calibrations):
                                widget = attr.widgets[m][0]
                                widget.setValue(int(self.eeprom.multi_wavelength_calibration.get(attr.name, m, default=0)))
                        else:                                   
                            for m in range(attr.calibrations):  # e.g. ??
                                for i, w in enumerate(attr.widgets[m]):
                                    w.setValue(int(self.eeprom.multi_wavelength_calibration.get(attr.name, m, i, default=0)))
                    else:
                        if attr.is_scalar:                      # e.g. baud_rate
                            attr.widget.setValue(int(getattr(self.eeprom, attr.name)))
                        else:                                   # e.g. bad_pixels
                            for i, w in enumerate(attr.widgets):
                                w.setValue(int(getattr(self.eeprom, attr.name)[i]))

                elif attr.qtype == "doublespinbox":
                    if attr.is_multi:
                        if attr.is_scalar:                      # e.g. excitation_nm_float, avg_resolution
                            for m in range(attr.calibrations):
                                widget = attr.widgets[m][0]
                                widget.setValue(float(self.eeprom.multi_wavelength_calibration.get(attr.name, m, default=0)))
                        else:                                   
                            for m in range(attr.calibrations):  # e.g. ??
                                for i, w in enumerate(attr.widgets[m]):
                                    w.setValue(float(self.eeprom.multi_wavelength_calibration.get(attr.name, m, i, default=0)))
                    else:
                        if attr.is_scalar:                      # e.g. detector_gain, min/max_laser_power
                            attr.widget.setValue(float(getattr(self.eeprom, attr.name)))
                        else:                                   # e.g. ??
                            for i, w in enumerate(attr.widgets):
                                w.setValue(float(getattr(self.eeprom, attr.name)[i]))

                elif attr.qtype == "lineedit":
                    if attr.is_multi:
                        if attr.is_scalar:                      # e.g. ??
                            for m in range(attr.calibrations):
                                widget = attr.widgets[m][0]
                                widget.setText(str(self.eeprom.multi_wavelength_calibration.get(attr.name, m, default=0)))
                        else:                                   
                            for m in range(attr.calibrations):  # e.g. wavelength_coeffs, raman_intensity_coeffs
                                for i, w in enumerate(attr.widgets[m]):
                                    w.setText(str(self.eeprom.multi_wavelength_calibration.get(attr.name, m, i, default=0)))
                    else:
                        if attr.is_scalar:                      # e.g. ??
                            attr.widget.setText(str(getattr(self.eeprom, attr.name)))
                        else:                                   # e.g. adc_to_degC, degC_to_dac, laser_power_coeffs
                            for i, w in enumerate(attr.widgets):
                                w.setText(str(getattr(self.eeprom, attr.name)[i]))
            except:
                log.error(f"update_from_spec: failed to update widget(s) for attr {attr}", exc_info=1)

        self.update_subformat()
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

        # subformats 3 and 5 extend subformat 1
        if sub in [3, 5]:
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

    def bind_checkbox(self, attr):
        if not attr.is_scalar:
            raise NotImplemented("{attr.name}: checkbox arrays not yet implemented")
        if attr.is_multi:
            raise NotImplemented("{attr.name}: multi-wavelength checkboxes not yet implemented")
        if not hasattr(self.eeprom, attr.name):
            raise AttributeError(f"{attr.name}: unknown EEPROM checkbox")

        log.debug(f"bind_checkbox: binding {attr}")
        attr.widget.stateChanged.connect(lambda state: self.widget_callback(attr, value=state, widget=attr.widget))
        attr.is_editable = self.eeprom.is_editable(attr.name)
        self.widgets.append(attr.widget)

    def bind_spinbox(self, attr):
        """ Hoping to use this for both QSpinBox and QDoubleSpinBox widgets """
        if attr.is_multi:
            if attr.is_scalar:
                for m in range(attr.calibrations):
                    log.debug(f"bind_spinbox: binding calibration {m} scalar: {attr}")
                    w = attr.widgets[m][0]
                    w.valueChanged.connect(lambda d: self.widget_callback(attr=attr, widget=w, calibration=m, value=d))
                    self.widgets.append(w)
            else:
                for m in range(attr.calibrations):
                    for i in range(attr.count):
                        log.debug(f"bind_spinbox: binding calibration {m} index {i}: {attr}")
                        w = attr.widgets[m][i]
                        w.valueChanged.connect(lambda d: self.widget_callback(attr=attr, widget=w, calibraton=m, index=i, value=d))
                        self.widgets.append(w)
        else:
            if attr.is_scalar:
                log.debug(f"bind_spinbox: binding scalar: {attr}")
                attr.widget.valueChanged.connect(lambda d: self.widget_callback(attr=attr, widget=attr.widget, value=d))
                self.widgets.append(attr.widget)
            else:
                for i in range(attr.count):
                    log.debug(f"bind_spinbox: binding index {i}: {attr}")
                    w = attr.widgets[i]
                    w.valueChanged.connect(lambda d: self.widget_callback(attr=attr, widget=w, index=i, value=d))
                    self.widgets.append(w)
                
        attr.is_editable = self.eeprom.is_editable(attr.name)

    def bind_lineedit(self, attr):
        if attr.is_multi:
            if attr.is_scalar:
                for m in range(attr.calibrations):
                    log.debug(f"bind_lineedit: binding calibration {m} scalar: {attr}")
                    w = attr.widgets[m][0]
                    w.editingFinished.connect(lambda: self.widget_callback(attr=attr, widget=w, calibration=m))
                    self.widgets.append(w)
            else:
                for m in range(attr.calibrations):
                    for i in range(attr.count):
                        log.debug(f"bind_lineedit: binding calibration {m}, index {i}: {attr}")
                        w = attr.widgets[m][i]
                        w.editingFinished.connect(lambda: self.widget_callback(attr=attr, widget=w, calibraton=m, index=i))
                        self.widgets.append(w)
        else:
            if attr.is_scalar:
                log.debug(f"bind_lineedit: binding scalar: {attr}")
                attr.widget.editingFinished.connect(lambda: self.widget_callback(attr=attr, widget=attr.widget))
                self.widgets.append(attr.widget)
            else:
                for i in range(attr.count):
                    log.debug(f"bind_lineedit: binding index {i}: {attr}")
                    w = attr.widgets[i]
                    w.editingFinished.connect(lambda: self.widget_callback(attr=attr, widget=w, index=i))
                    self.widgets.append(w)
                
        attr.is_editable = self.eeprom.is_editable(attr.name)

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
