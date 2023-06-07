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
        self.cb_json                 = None
        self.cb_pixel                = None
        self.cb_raw                  = None
        self.cb_reference            = None
        self.cb_text                 = None
        self.cb_wavelength           = None
        self.cb_wavenumber           = None
        self.config                  = None
        self.directory               = None
        self.lb_location             = None
        self.le_label_template       = None
        self.le_note                 = None
        self.le_prefix               = None
        self.le_suffix               = None
        self.line_number             = 0
        self.multispec               = None
        self.rb_by_col               = None
        self.rb_by_row               = None

    def __init__(
             self,
             bt_location,    
             cb_all,
             cb_allow_rename,
             cb_append,
             cb_collated,
             cb_csv,
             cb_spc,
             cb_dark,
             cb_excel,
             cb_json, 
             cb_load_raw,
             cb_pixel,
             cb_raw,
             cb_reference,
             cb_text,
             cb_wavelength,
             cb_wavenumber,
             config,
             file_manager,
             interp,
             lb_location,    
             le_label_template,
             le_note,
             le_prefix,
             le_suffix,
             multispec,    
             rb_by_col,
             rb_by_row
        ):

        self.bt_location          = bt_location    
        self.cb_all               = cb_all
        self.cb_allow_rename      = cb_allow_rename
        self.cb_append            = cb_append
        self.cb_collated          = cb_collated
        self.cb_csv               = cb_csv
        self.cb_spc               = cb_spc
        self.cb_dark              = cb_dark
        self.cb_excel             = cb_excel
        self.cb_json              = cb_json
        self.cb_load_raw          = cb_load_raw
        self.cb_pixel             = cb_pixel
        self.cb_raw               = cb_raw
        self.cb_reference         = cb_reference
        self.cb_text              = cb_text
        self.cb_wavelength        = cb_wavelength
        self.cb_wavenumber        = cb_wavenumber
        self.config               = config
        self.file_manager         = file_manager
        self.interp               = interp
        self.lb_location          = lb_location
        self.le_label_template    = le_label_template
        self.le_note              = le_note
        self.le_prefix            = le_prefix
        self.le_suffix            = le_suffix
        self.multispec            = multispec
        self.rb_by_col            = rb_by_col
        self.rb_by_row            = rb_by_row

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
        self.cb_json            .stateChanged       .connect(self.update_widgets)
        self.cb_pixel           .stateChanged       .connect(self.update_widgets)
        self.cb_raw             .stateChanged       .connect(self.update_widgets)
        self.cb_reference       .stateChanged       .connect(self.update_widgets)
        self.cb_text            .stateChanged       .connect(self.update_widgets)
        self.cb_wavelength      .stateChanged       .connect(self.update_widgets)
        self.cb_wavenumber      .stateChanged       .connect(self.update_widgets)
        self.le_label_template  .editingFinished    .connect(self.update_widgets)
        self.le_note            .editingFinished    .connect(self.update_widgets)
        self.le_prefix          .editingFinished    .connect(self.update_widgets)
        self.le_suffix          .editingFinished    .connect(self.update_widgets)
        self.rb_by_col          .toggled            .connect(self.update_widgets)
        self.rb_by_row          .toggled            .connect(self.update_widgets)

        log.debug("instantiated SaveOptions")

    ## Load initial state of SaveOptions from config file
    def init_from_config(self):
        s = "save"

        by_row = self.config.get(s, "order").lower() == "row"

        log.debug("init_from_config: by_row %s", by_row)

        self.rb_by_row    .setChecked(    by_row) # should not be possible that
        self.rb_by_col    .setChecked(not by_row) #   neither is checked...

        self.init_checkbox(self.cb_csv,          "format_csv")
        self.init_checkbox(self.cb_collated,     "collated")
        self.init_checkbox(self.cb_spc,          "format_spc")
        self.init_checkbox(self.cb_text,         "format_txt")
        self.init_checkbox(self.cb_excel,        "format_excel")
        self.init_checkbox(self.cb_json,         "format_json")
        self.init_checkbox(self.cb_append,       "append")
        self.init_checkbox(self.cb_pixel,        "pixel")
        self.init_checkbox(self.cb_wavelength,   "wavelength")
        self.init_checkbox(self.cb_wavenumber,   "wavenumber")
        self.init_checkbox(self.cb_all,          "all_spectrometers")
        self.init_checkbox(self.cb_allow_rename, "allow_rename_files")
        self.init_checkbox(self.cb_raw,          "raw")
        self.init_checkbox(self.cb_dark,         "dark")
        self.init_checkbox(self.cb_reference,    "reference")

        if self.config.has_option(s, "label_template"):
            self.le_label_template  .setText   (self.config.get(s, "label_template"))

        self.le_prefix          .setText   (self.config.get(s, "prefix"))
        self.le_suffix          .setText   (self.config.get(s, "suffix"))
        self.le_note            .setText   (re.sub(",", "", self.config.get(s, "note")))

    def init_checkbox(self, cb, option):
        value = self.config.get_bool("save", option)
        cb.setChecked(value)

    ## Update widgets and config state when:
    #
    # - user clicked on a SaveOption widget
    # - user selects a different spectrometer (might have different capabilities)
    # - user takes or clears a dark or reference
    def update_widgets(self):
        spec = self.multispec.current_spectrometer()

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

        # dependent on excitation
        self.cb_wavenumber.setEnabled(spec.has_excitation() if spec else False)

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
        # update config
        ########################################################################

        s = "save"
        self.config.set(s, "order", "row" if self.save_by_row() else "col")
        self.config.set(s, "collated",           self.save_collated())
        self.config.set(s, "format_csv",         self.save_csv())
        self.config.set(s, "format_spc",         self.save_spc())
        self.config.set(s, "format_txt",         self.save_text())
        self.config.set(s, "format_excel",       self.save_excel())
        self.config.set(s, "format_json",        self.save_json())
        self.config.set(s, "append",             self.append())
        self.config.set(s, "pixel",              self.save_pixel())
        self.config.set(s, "wavelength",         self.save_wavelength())
        self.config.set(s, "wavenumber",         self.save_wavenumber())
        self.config.set(s, "raw",                self.save_raw())
        self.config.set(s, "dark",               self.save_dark())
        self.config.set(s, "reference",          self.save_reference())
        self.config.set(s, "prefix",             self.prefix())
        self.config.set(s, "suffix",             self.suffix())
        self.config.set(s, "note",               self.note())
        self.config.set(s, "label_template",     self.label_template())
        self.config.set(s, "allow_rename_files", self.allow_rename_files())
        self.config.set(s, "all_spectrometers",  self.save_all_spectrometers())
            
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
    def save_pixel              (self): return self.cb_pixel.isChecked() or self.save_with_pixel
    def save_raw                (self): return self.cb_raw.isChecked() or self.save_with_raw
    def save_text               (self): return self.cb_text.isChecked()
    def save_reference          (self): return self.cb_reference.isChecked()
    def save_something          (self): return self.save_csv() or self.save_excel() or self.save_json() or self.save_text()
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
        directory = self.file_manager.get_directory()
        if directory is None:
            return

        self.directory = directory
        display_path = self.generate_display_path(directory)
        self.lb_location.setText(display_path)

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
        if len(path) > 25:
            return "...%s" % path[-25:]
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
