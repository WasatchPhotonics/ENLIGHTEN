import datetime
import logging
import re
import os

from enlighten import common
from enlighten import util

log = logging.getLogger(__name__)

class SaveOptions():
    """
    Encapsulates the many options regarding how spectra are to be saved.
    """

    DEFAULT_LABEL_TEMPLATE = "{time} {serial_number}"
    DEFAULT_FILENAME_TEMPLATE = "{measurement id}"

    # ##########################################################################
    # Lifecycle
    # ##########################################################################

    ## allows deep-copying of Measurement
    def __deepcopy__(self, memo):
        log.debug("blocking deepcopy")

    def clear(self):
        self.append_pathname         = None
        self.appended_serial_numbers = None
        self.bt_location             = None
        self.cb_all                  = None
        self.cb_append               = None
        self.cb_collated             = None
        self.cb_csv                  = None
        self.cb_spc                  = None
        self.cb_dark                 = None
        self.cb_excel                = None
        self.cb_filename_as_label    = None
        self.cb_json                 = None
        self.cb_dx                   = None
        self.cb_pixel                = None
        self.cb_raw                  = None
        self.cb_reference            = None
        self.cb_text                 = None
        self.cb_wavelength           = None
        self.cb_wavenumber           = None
        self.directory               = None
        self.lb_location             = None
        self.le_label_template       = None
        self.le_filename_template    = None
        self.le_note                 = None
        self.le_prefix               = None
        self.le_suffix               = None
        self.line_number             = 0
        self.multipart_suffix        = None # currently set/cleared by BatchCollection, used by Measurement
        self.rb_by_col               = None
        self.rb_by_row               = None

    def __init__(self, ctl):
        self.clear()

        self.ctl = ctl
        cfu = ctl.form.ui

        self.bt_location          = cfu.pushButton_scope_setup_change_save_location
        self.cb_all               = cfu.checkBox_save_all
        self.cb_allow_rename      = cfu.checkBox_allow_rename_files
        self.cb_append            = cfu.checkBox_save_data_append
        self.cb_collated          = cfu.checkBox_save_collated
        self.cb_csv               = cfu.checkBox_save_csv
        self.cb_spc               = cfu.checkBox_save_spc
        self.cb_dark              = cfu.checkBox_save_dark
        self.cb_excel             = cfu.checkBox_save_excel
        self.cb_filename_as_label = cfu.checkBox_save_filename_as_label
        self.cb_json              = cfu.checkBox_save_json
        self.cb_dx                = cfu.checkBox_save_dx
        self.cb_load_raw          = cfu.checkBox_load_raw
        self.cb_pixel             = cfu.checkBox_save_pixel
        self.cb_raw               = cfu.checkBox_save_raw
        self.cb_reference         = cfu.checkBox_save_reference
        self.cb_text              = cfu.checkBox_save_text
        self.cb_wavelength        = cfu.checkBox_save_wavelength
        self.cb_wavenumber        = cfu.checkBox_save_wavenumber
        self.lb_location          = cfu.label_scope_setup_save_location
        self.le_label_template    = cfu.lineEdit_save_label_template
        self.le_filename_template = cfu.lineEdit_save_filename_template
        self.le_note              = cfu.lineEdit_scope_capture_save_note
        self.le_prefix            = cfu.lineEdit_scope_capture_save_prefix
        self.le_suffix            = cfu.lineEdit_scope_capture_save_suffix
        self.rb_by_col            = cfu.radioButton_save_by_column
        self.rb_by_row            = cfu.radioButton_save_by_row

        # used for plugins indicating to save
        self.save_with_raw = False
        self.save_with_pixel = False
        self.save_with_wavelength = False
        self.save_with_wavenumber = False

        # not passed in
        self.append_pathname = None
        self.appended_serial_numbers = set()
        self.line_number  = 0
        self.last_prefix = None
        self.last_suffix = None

        # initialize
        self.directory = common.get_default_data_dir()
        self.lb_location.setText(self.directory)
        self.init_from_config()
        self.update_widgets()

        # ######################################################################
        # binding
        # ######################################################################

        self.bt_location        .clicked            .connect(self.update_location)
        self.cb_all             .stateChanged       .connect(self.update_widgets)
        self.cb_allow_rename    .stateChanged       .connect(self.update_widgets)
        self.cb_append          .stateChanged       .connect(self.update_widgets)
        self.cb_collated        .stateChanged       .connect(self.update_widgets)
        self.cb_csv             .stateChanged       .connect(self.update_widgets)
        self.cb_spc             .stateChanged       .connect(self.update_widgets)
        self.cb_dark            .stateChanged       .connect(self.update_widgets)
        self.cb_excel           .stateChanged       .connect(self.update_widgets)
        self.cb_filename_as_label.stateChanged      .connect(self.update_widgets)
        self.cb_json            .stateChanged       .connect(self.update_widgets)
        self.cb_dx              .stateChanged       .connect(self.update_widgets)
        self.cb_pixel           .stateChanged       .connect(self.update_widgets)
        self.cb_raw             .stateChanged       .connect(self.update_widgets)
        self.cb_reference       .stateChanged       .connect(self.update_widgets)
        self.cb_text            .stateChanged       .connect(self.update_widgets)
        self.cb_wavelength      .stateChanged       .connect(self.update_widgets)
        self.cb_wavenumber      .stateChanged       .connect(self.update_widgets)
        self.le_label_template  .editingFinished    .connect(self.update_widgets)
        self.le_filename_template.editingFinished   .connect(self.update_widgets)
        self.le_note            .editingFinished    .connect(self.update_widgets)
        self.le_prefix          .editingFinished    .connect(self.update_widgets)
        self.le_suffix          .editingFinished    .connect(self.update_widgets)
        self.rb_by_col          .toggled            .connect(self.update_widgets)
        self.rb_by_row          .toggled            .connect(self.update_widgets)

        log.debug("instantiated SaveOptions")

    ## Load initial state of SaveOptions from config file
    def init_from_config(self):
        s = "save"

        by_row = self.ctl.config.get(s, "order").lower() == "row"

        log.debug("init_from_config: by_row %s", by_row)

        self.rb_by_row    .setChecked(    by_row) # should not be possible that
        self.rb_by_col    .setChecked(not by_row) #   neither is checked...

        self.init_checkbox(self.cb_csv,          "format_csv")
        self.init_checkbox(self.cb_collated,     "collated")
        self.init_checkbox(self.cb_spc,          "format_spc")
        self.init_checkbox(self.cb_text,         "format_txt")
        self.init_checkbox(self.cb_excel,        "format_excel")
        self.init_checkbox(self.cb_filename_as_label, "filename_as_label")
        self.init_checkbox(self.cb_json,         "format_json")
        self.init_checkbox(self.cb_dx,           "format_dx")
        self.init_checkbox(self.cb_append,       "append")
        self.init_checkbox(self.cb_pixel,        "pixel")
        self.init_checkbox(self.cb_wavelength,   "wavelength")
        self.init_checkbox(self.cb_wavenumber,   "wavenumber")
        self.init_checkbox(self.cb_all,          "all_spectrometers")
        self.init_checkbox(self.cb_allow_rename, "allow_rename_files")
        self.init_checkbox(self.cb_raw,          "raw")
        self.init_checkbox(self.cb_dark,         "dark")
        self.init_checkbox(self.cb_reference,    "reference")

        if self.ctl.config.has_option(s, "label_template"):
            self.le_label_template.setText(self.ctl.config.get(s, "label_template"))
        if self.ctl.config.has_option(s, "filename_template"):
            self.le_filename_template.setText(self.ctl.config.get(s, "filename_template"))

        self.le_prefix          .setText   (self.ctl.config.get(s, "prefix"))
        self.le_suffix          .setText   (self.ctl.config.get(s, "suffix"))
        self.le_note            .setText   (re.sub(",", "", self.ctl.config.get(s, "note")))

        self.directory = self.ctl.config.get("SaveOptions", "save_location", default=common.get_default_data_dir())

        display_path = self.generate_display_path(self.directory)
        self.lb_location.setText(display_path)

    def init_checkbox(self, cb, option):
        value = self.ctl.config.get_bool("save", option)
        cb.setChecked(value)

    ## Update widgets and config state when:
    #
    # - user clicked on a SaveOption widget
    # - user selects a different spectrometer (might have different capabilities)
    # - user takes or clears a dark or reference
    def update_widgets(self):
        spec = self.ctl.multispec.current_spectrometer()

        ########################################################################
        # decide which widgets should be ENABLED (not checked)
        ########################################################################

        save_csv = self.save_csv()

        # these widgets are dependent on the CSV checkbox
        self.rb_by_row.setEnabled(save_csv)
        self.rb_by_col.setEnabled(save_csv)
        self.cb_append.setEnabled(save_csv and self.save_by_row())

        # always enable these
        self.cb_dark.setEnabled(True)
        self.cb_reference.setEnabled(True)

        # always enable wavenumbers, as we might want to load/export Raman
        # data even when not connected to a Raman spectrometer
        self.cb_wavenumber.setEnabled(True)

        self.le_label_template.setEnabled(not self.filename_as_label())

        ########################################################################
        # Reset append_pathname when disabled or prefix/suffix changes
        ########################################################################

        # this way, toggling "append" off and on again will generate a new file
        if not self.cb_append.isChecked():
            self.reset_appendage()

        if self.prefix() != self.last_prefix:
            self.reset_appendage()
            self.last_prefix = self.prefix()

        if self.suffix() != self.last_suffix:
            self.reset_appendage()
            self.last_suffix = self.suffix()

        ########################################################################
        # these may not be blank
        ########################################################################

        if not self.label_template():
            self.le_label_template.setText(self.DEFAULT_LABEL_TEMPLATE)
        if not self.filename_template():
            self.le_filename_template.setText(self.DEFAULT_FILENAME_TEMPLATE)

        ########################################################################
        # update config
        ########################################################################

        s = "save"
        self.ctl.config.set(s, "order", "row" if self.save_by_row() else "col")
        self.ctl.config.set(s, "collated",           self.save_collated())
        self.ctl.config.set(s, "format_csv",         self.save_csv())
        self.ctl.config.set(s, "format_spc",         self.save_spc())
        self.ctl.config.set(s, "format_txt",         self.save_text())
        self.ctl.config.set(s, "format_excel",       self.save_excel())
        self.ctl.config.set(s, "format_json",        self.save_json())
        self.ctl.config.set(s, "format_dx",          self.save_dx())
        self.ctl.config.set(s, "append",             self.append())
        self.ctl.config.set(s, "pixel",              self.save_pixel())
        self.ctl.config.set(s, "wavelength",         self.save_wavelength())
        self.ctl.config.set(s, "wavenumber",         self.save_wavenumber())
        self.ctl.config.set(s, "raw",                self.save_raw())
        self.ctl.config.set(s, "dark",               self.save_dark())
        self.ctl.config.set(s, "reference",          self.save_reference())
        self.ctl.config.set(s, "prefix",             self.prefix())
        self.ctl.config.set(s, "suffix",             self.suffix())
        self.ctl.config.set(s, "note",               self.note())
        self.ctl.config.set(s, "label_template",     self.label_template())
        self.ctl.config.set(s, "filename_template",  self.filename_template())
        self.ctl.config.set(s, "allow_rename_files", self.allow_rename_files())
        self.ctl.config.set(s, "all_spectrometers",  self.save_all_spectrometers())
        self.ctl.config.set(s, "filename_as_label",  self.filename_as_label())

    # ##########################################################################
    # Accessors
    # ##########################################################################

    def wrap_name(self, name, pre, post):
        def clean(foo):
            return re.sub(r"[:/\\]", "-", foo)

        s = name
        pre = clean(pre)
        post = clean(post)
        if len(pre) > 0:
            s = "%s-%s" % (pre, s)
        if len(post) > 0:
            s = "%s-%s" % (s, post)

        return s

    def allow_rename_files      (self): return self.cb_allow_rename.isChecked()
    def append                  (self): return self.cb_append.isChecked() and self.cb_append.isEnabled()
    def note                    (self): return re.sub(",", "", self.le_note.text()).strip()
    def prefix                  (self): return self.le_prefix.text().strip()
    def label_template          (self): return self.le_label_template.text().strip()
    def filename_template       (self): return self.le_filename_template.text().strip()
    def filename_as_label       (self): return self.cb_filename_as_label.isChecked()
    def load_raw                (self): return self.cb_load_raw.isChecked()
    def save_all_spectrometers  (self): return self.cb_all.isChecked()
    def save_by_col             (self): return self.rb_by_col.isChecked()
    def save_by_row             (self): return self.rb_by_row.isChecked()
    def save_collated           (self): return self.cb_collated.isChecked()
    def save_csv                (self): return self.cb_csv.isChecked()
    def save_spc                (self): return self.cb_spc.isChecked()
    def save_dark               (self): return self.cb_dark.isChecked()
    def save_excel              (self): return self.cb_excel.isChecked()
    def save_json               (self): return self.cb_json.isChecked()
    def save_dx                 (self): return self.cb_dx.isChecked()
    def save_pixel              (self): return self.cb_pixel.isChecked() or self.save_with_pixel
    def save_raw                (self): return self.cb_raw.isChecked() or self.save_with_raw
    def save_text               (self): return self.cb_text.isChecked()
    def save_reference          (self): return self.cb_reference.isChecked()
    def save_something          (self): return self.save_csv() or self.save_excel() or self.save_json() or self.save_text() or self.save_dx()
    def save_wavelength         (self): return self.cb_wavelength.isChecked() or self.save_with_wavelength
    def save_wavenumber         (self): return self.cb_wavenumber.isChecked() and self.cb_wavenumber.isEnabled() or self.save_with_wavenumber
    def suffix                  (self): return self.le_suffix.text().strip()
    def save_processed          (self): return True
    def has_prefix              (self): return len(self.prefix()) > 0
    def has_suffix              (self): return len(self.suffix()) > 0
    def has_note                (self): return len(self.note()) > 0

    # ##########################################################################
    # Methods
    # ##########################################################################

    ##
    # Called by Controller on first visit to Raman Mode
    def force_wavenumber(self):
        self.cb_wavenumber.setChecked(True)

    ## Show the directory dialog selection, set the default save location
    #  to the selected directory.
    def update_location(self):
        directory = self.ctl.file_manager.get_directory()
        if directory is None:
            return

        self.directory = directory
        display_path = self.generate_display_path(directory)
        self.lb_location.setText(display_path)

        # persist save location in .ini
        self.ctl.config.set("SaveOptions", "save_location", directory)

    ## nicer than having plugins etc access attributes directly
    def get_directory(self):
        return self.directory

    def generate_today_dir(self):
        now = datetime.datetime.now()
        today = now.strftime("%Y-%m-%d")
        today_dir = os.path.expanduser(os.path.join(self.directory, today))
        util.safe_mkdirp(today_dir)
        return today_dir

    def generate_display_path(self, path):
        if len(path) > 100:
            return "...%s" % path[-100:]
        return path

    ##
    # We've started a new by-row CSV file which could theoretically be later
    # appended to, so track some metadata about that.
    def reset_appendage(self, pathname=None):
        self.append_pathname = pathname
        self.appended_serial_numbers = set()
        self.line_number = 0

    ##
    # Track that we've appended data from this serial number to the current
    # file.  This can guide decisions in whether certain metadata needs to be
    # re-appended on successive writes.
    def set_appended_serial(self, serial_number):
        self.appended_serial_numbers.add(serial_number)

    ##
    # Return whether we have appended data from the given serial number to the
    # current file.
    def have_appended_serial(self, serial_number):
        return serial_number in self.appended_serial_numbers

    def focus_note(self):
        self.le_note.setFocus()
        self.le_note.selectAll()

    # static
    def get_default_configuration():
        return {
            "order": "col",
            "append": False,

            "pixel": True,
            "wavelength": True,
            "wavenumber": True,

            "raw": False,
            "dark": False,
            "reference": False,

            "all_spectrometers": True,
            "allow_rename_files": True,

            "format_csv": True,
            "format_txt": False,
            "format_excel": False,
            "format_json": False,
            "format_dx": False,

            "label_template": SaveOptions.DEFAULT_LABEL_TEMPLATE,
            "filename_template": SaveOptions.DEFAULT_FILENAME_TEMPLATE,

            "prefix": "enlighten",
            "suffix": "",
            "note": "",
        }

