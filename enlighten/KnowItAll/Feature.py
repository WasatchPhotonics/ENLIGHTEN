from queue import Queue
import datetime
import platform
import logging
import time
import os

from PySide2 import QtGui, QtWidgets

from .Wrapper import Wrapper
from .Config  import Config 
from ..ScrollStealFilter import ScrollStealFilter

from .. import util

log = logging.getLogger(__name__)

##
# Given that compounds may be referenced by either original name or aliases,
# provide a simple way to access the varied name types.
#
# @public
class AliasedName(object):
    def __init__(self):
        self.orig = None
        self.preferred = None
        self.all_names = set()

    ## @public
    def is_aliased(self):
        return self.orig != self.preferred

##
# This is ultimately what we turn the KnowItAll list of possible matches
# into.
#
# @public
class DeclaredMatch(object):
    def __init__(self, aliased_name=None, score=0.0, hazard=False, benign=False):
        self.aliased_name   = aliased_name
        self.score          = score
        self.hazard         = hazard
        self.benign         = benign

    def __str__(self):
        return self.aliased_name.preferred

##
# This class encapsulates all KnowItAll data, widgets and processing.
# 
# @par KnowItAll
#
# ENLIGHTEN primarily supports Raman compound ID using KnowItAll 
# software, abbreviated in some code as KIA.
# 
# The KnowItAll API was documented here:
# 
# - https://sciencesolutions.wiley.com/knowitall-sdk/
# 
# All communication between ENLIGHTEN and KnowItAll is encapsulated in 
# this C++ wrapper program:
# 
# - https://github.com/WasatchPhotonics/KnowItAllWrapper
#
# @par KIAConsole.exe
# 
# The wrapper is currently left as an out-of-process executable (KIAConsole.exe) 
# as it crashes intermittently, and this way it doesn't bring down ENLIGHTEN.
# 
# Currently the KIAConsole.exe binary is stored in the ENLIGHTEN distribution 
# under dist/, and is not dynamically built as part of the ENLIGHTEN build 
# procedure.  
# 
# It is rolled into the ENLIGHTEN installer by Application_InnoSetup.iss,
# which places KIAConsole.exe into \\Program Files (x86)\\Wasatch Photonics\\Enlighten\\ENLIGHTEN, 
# alongside enlighten.exe.
# 
# Note that KIAConsole.exe requires the Visual C++ Redistributable Runtime be 
# installed, which can be obtained from:
# 
# - https://support.microsoft.com/en-us/help/2977003/the-latest-supported-visual-c-downloads
# 
# This runtime is now automatically installed by the InnoSetup installer.
# 
# @par Licensing
# 
# The vendor provides a free 1-year trial license of KnowItAll Vibrational 
# Spectroscopy Edition to all ENLIGHTEN users.  Users are required to renew the 
# license if they wish to continue using KnowItAll after the first year.
# 
# @par Installation
# 
# The KnowItAll software is installed as follows:
# 
# - Go to https://get.knowitall.com 
# - (Wasatch employees may enter a special access code, not committed to Git)
# - Fill out the form with your \@wasatchphotonics.com email address
# - Follow the instructions in the ensuing email on how to download, install, 
#   and activate the KnowItAll software and databases, i.e.:
#     - download KnowItAllInstall_offline.exe from http://www.knowitall.com/download 
#
# Note that significant functionality is further encapsulated into KnowItAll.Wrapper
# (a sibling to this class)..  
#
# That class is deliberately kept small and, significantly, devoid of callback 
# functions to any class which "holds" Qt objects (like Controller, or Feature
# itself), as those were found to cause pickling exceptions in 
# multiprocessing.Process.start.
#
# @par Configuration
#
# The configuration needs of this feature exceed what Configuration's .ini format
# can easily provide, so KnowItAll.Config was provided to support configuration 
# in JSON.  
#
# @par Aliases
#
# I'm treating the aliases as though the config file may be human-edited, and
# thus end up with cylic graphs like a -> b -> a, converging roots like a -> b 
# and c -> b, and chains like a -> b -> c.  One thing that CANNOT occur is 
# diverging roots, i.e. a -> b and a -> c (such can appear in the file, but only 
# one will win).
#
# This is probably overcomplicating things, but down the rabbit-hole I went.
#
class Feature(object):

    # ##########################################################################
    # Constants
    # ##########################################################################

    ## @todo make this configurable, some might not have it on C: etc
    KNOW_IT_ALL_DIRECTORY   = "C:\\Program Files\\KnowItAll"
    KIA_CONSOLE_NAME        = "KIAConsole.exe" # no path, so assumed sibling of enlighten.exe

    RESULTS_COL_SCORE       = 0
    RESULTS_COL_COMPOUND    = 1

    RECENT_COL_TIME         = 0
    RECENT_COL_COMPOUND     = 1 

    BENIGN_COLOR_NAME       = 'enlighten_benign' # 'enlighten_name_n1'
    HAZARD_COLOR_NAME       = 'enlighten_hazard' # 'enlighten_name_n2'

    HAZARD_PROPERTY         = "wpHazard"
    BENIGN_PROPERTY         = "wpBenign"

    KIA_STYLED_NAME         = '<html><head/><body><p>KnowItAll<sup>®</sup></p></body></html>'

    CLEAR_LAST_MATCH_SEC    = 10

    # ##########################################################################
    # Lifecycle
    # ##########################################################################

    ##
    # Note there is no "cb_sharpen_peaks" or similar -- that is handled by the 
    # RichardsonLucy class, which is currently independent of KnowItAll.
    def __init__(self,
            baseline_correction,
            bt_alias,
            bt_benign,
            bt_clear,
            bt_hazard,
            bt_id,
            bt_reset,
            bt_suppress,
            cb_all,                         # display all results
            cb_enabled,
            cb_hazard,
            colors,
            file_manager,
            frame_results,
            frame_side,
            generate_x_axis,
            get_last_processed_reading,
            guide,
            lb_logo,
            lb_name,
            lb_path,
            lb_processing,
            lb_score,     
            logging_feature,
            marquee,
            measurements,
            multispec,
            page_nav,
            raman_intensity_correction,
            sb_max_results,
            sb_score_min,      
            sounds,
            stylesheets,
            table_recent,
            table_results,
            vcr_controls,
            horiz_roi):

        self.baseline_correction        = baseline_correction
        self.bt_alias                   = bt_alias
        self.bt_benign                  = bt_benign
        self.bt_clear                   = bt_clear
        self.bt_hazard                  = bt_hazard
        self.bt_id                      = bt_id
        self.bt_reset                   = bt_reset
        self.bt_suppress                = bt_suppress
        self.cb_all                     = cb_all
        self.cb_enabled                 = cb_enabled
        self.cb_hazard                  = cb_hazard
        self.colors                     = colors
        self.file_manager               = file_manager
        self.frame_results              = frame_results
        self.frame_side                 = frame_side
        self.generate_x_axis            = generate_x_axis
        self.get_last_processed_reading = get_last_processed_reading
        self.guide                      = guide
        self.lb_logo                    = lb_logo
        self.lb_name                    = lb_name
        self.lb_path                    = lb_path
        self.lb_processing              = lb_processing
        self.lb_score                   = lb_score
        self.logging_feature            = logging_feature
        self.marquee                    = marquee
        self.measurements               = measurements
        self.multispec                  = multispec
        self.page_nav                   = page_nav
        self.raman_intensity_correction = raman_intensity_correction
        self.sb_score_min               = sb_score_min
        self.sb_max_results             = sb_max_results
        self.sounds                     = sounds
        self.stylesheets                = stylesheets
        self.table_recent               = table_recent
        self.table_results              = table_results
        self.vcr_controls               = vcr_controls
        self.horiz_roi                  = horiz_roi

        self.kia_pathname = None         # where KnowItAll is installed
        self.executable_pathname = None

        self.wrapper = None
        self.enabled = False
        self.closing = False
        self.last_tip = None
        self.sent_install_tip = False

        # we're not using these right now
        self.bt_benign.setVisible(False)
        self.bt_hazard.setVisible(False)

        # when we moved to Qt5 (or probably PySide2), some features in automatic table 
        # creation broke, so just populate them programmatically for now
        self._init_tables()

        # for ThumbnailWidgets on which the ID button has been clicked
        self.measurement_queue = []
        
        self.display_all = self.cb_all.isChecked()
        self.score_min   = self.sb_score_min.value() 
        self.max_results = self.sb_max_results.value()

        self.recent_matches = {} # recent[compound] = datetime
        self.last_declared_match = None
        self.last_response = None

        # note that this is KIAFeature.Config, not enlighten.Configuration
        self.config = Config()

        # bindings
        self.bt_alias           .clicked        .connect(self._alias_callback)
        self.bt_benign          .clicked        .connect(self._benign_callback)
        self.bt_clear           .clicked        .connect(self._clear_callback)
        self.bt_hazard          .clicked        .connect(self._hazard_callback)
        self.bt_id              .clicked        .connect(self._id_callback)
        self.bt_reset           .clicked        .connect(self._reset_callback)
        self.bt_suppress        .clicked        .connect(self._suppress_callback)
        self.cb_all             .stateChanged   .connect(self._all_callback)
        self.cb_enabled         .stateChanged   .connect(self._enabled_callback)
       #self.cb_hazard          .stateChanged   .connect(self._hazard_callback) # MZ: is this right? No, it isn't :-(
        self.sb_score_min       .valueChanged   .connect(self._score_callback)
        self.sb_max_results     .valueChanged   .connect(self._max_results_callback)
        self.table_recent       .cellClicked    .connect(self._table_recent_callback)
        self.table_results      .cellClicked    .connect(self._table_results_callback)

        # disable scroll stealing
        for key, item in self.__dict__.items():
            if key.startswith("cb_") or key.startswith("sb_"):
                item.installEventFilter(ScrollStealFilter(item))

        # validate installation
        self.is_installed = self._check_installed()
        if self.is_installed:
            self.lb_path.setText(self.kia_pathname)
        else:
            self.lb_path.setText("not installed")

        self._reset()

        self.update_visibility()

    ## @public
    def disconnect(self):
        self.closing = True

        if self.wrapper:
            log.debug("disconnecting wrapper")
            self.wrapper.disconnect()
            self.wrapper = None

    # ##########################################################################
    #                           
    #                              Public Methods
    #                           
    # ##########################################################################

    ## 
    # The user has clicked the "fingerprint" ID button on a saved Measurement
    # thumbnail.
    #
    # @public
    def enqueue_measurement(self, measurement):
        # connect if not already 
        if self.wrapper is None:
            if not self._connect():
                self.marquee.error("Failed to connect")
                return
        else:
            self._clear_response("(processing)")

        self.measurement_queue.append(measurement)
        log.debug("enqueued %s for ID", measurement.measurement_id)
        if not self.wrapper:
            self._connect()
    
    ## @private
    def _update_table_buttons(self):
        self.bt_clear .setEnabled(len(self.recent_matches) > 0)

        compound_name = self._get_selected_compound_name()
        if compound_name is None:
            self.bt_reset   .setEnabled(False)
            self.bt_hazard  .setEnabled(False)
            self.bt_benign  .setEnabled(False)
            self.bt_alias   .setEnabled(False)
            self.bt_suppress.setEnabled(False)
            return

        an = self._get_aliased_name(compound_name)

        hazard = util.sets_intersect(an.all_names, self.config.hazards)
        benign = util.sets_intersect(an.all_names, self.config.benigns)
        # log.debug("update_table_buttons: hazard %s, benign %s", hazard, benign)

        self.bt_reset   .setEnabled(hazard or benign or an.is_aliased())
        self.bt_hazard  .setEnabled(not hazard)
        self.bt_benign  .setEnabled(not benign)
        self.bt_alias   .setEnabled(True)
        self.bt_suppress.setEnabled(True)

    ## @public
    def update_visibility(self):
        side = False
        results = False
        button = False

        if self.is_installed and (self.page_nav.doing_raman() or self.page_nav.is_expert()):
            side = True
            button = True
            results = self.display_all

        self.frame_side     .setVisible(side)
        self.frame_results  .setVisible(results)
        self.bt_id          .setVisible(button)

        # hide this until we've implemented it
        self.cb_hazard      .setVisible(False) 

        if results:
            self._update_table_buttons()

        self.lb_logo.setVisible(True)

        self._queue_tip()

    ## 
    # Put a helpful suggestion in the tip box.
    #
    # @private
    def _queue_tip(self):
        # only generate tips while we're on Raman Scope Capture
        if not (self.page_nav.doing_raman() and self.page_nav.doing_scope()):
            log.debug("not tipping because not raman")
            return

        spec = self.multispec.current_spectrometer()
        if spec is None:
            log.debug("not tipping because no spec")
            return

        # add more tips as we think of them
        if not self.is_installed and not self.sent_install_tip:
            self.sent_install_tip = True
            return self.guide.suggest("""<html>Tip: install Wiley <a href="https://get.knowitall.com" style="color: #73f0d7">KnowItAll™</a> for automated Raman ID (enter code 'RAMAN')</html>""", persist=True)

        if not spec.app_state.has_dark():
            return self.guide.suggest("Tip: take dark for better matching", token="take_dark")

        if self.raman_intensity_correction.is_supported() and not self.raman_intensity_correction.enabled:
            return self.guide.suggest("Tip: enable Raman Intensity Correction for better matching", token="enable_raman_intensity_correction")

        if not self.baseline_correction.enabled and self.baseline_correction.allowed:
            return self.guide.suggest("Tip: enable baseline correction for better matching", token="enable_baseline_correction")

    # This is currently ticked from the Controller's "status" loop (1Hz at writing),
    # so it isn't dependent on integration time, or even if acquisitions are running.
    #
    # @public
    def update(self):
        if self.closing:
            return

        self.update_visibility()

        if self.wrapper is None:
            self.lb_processing.setText("disconnected")
            return

        # if not self.enabled and not self.processing:
        #     log.debug("ignoring update whilst disabled")
        #     return

        # ######################################################################
        # Handle incoming (completed) responses
        # ######################################################################

        # Check to see if there's a pending response from the subprocess.  We do
        # this REGARDLESS of whether we're enabled (processing all spectra) or not,
        # as we may need to pick up the response to a manual (pushbutton) ID request.
        response = self.wrapper.get_response()
        if response:
            log.debug("got response <- Wrapper")

            if response.disconnect:
                log.critical("KnowItAll wrapper child died...resetting")
                self.lb_processing.setText("disconnecting")
                return self._reset()

            self._process_response(response)

            self.stylesheets.apply(self.bt_id, "gray_gradient_button") # applies only if main ID button was pressed
            self.lb_processing.setText(self._get_elapsed_time_str() + " (complete)")
            self.processing = False

        # ######################################################################
        # Update processing timer
        # ######################################################################

        if self.processing:
            self.lb_processing.setText(self._get_elapsed_time_str())

            elapsed_sec = (datetime.datetime.now() - self.processing_start_time).total_seconds()
            if elapsed_sec > self.CLEAR_LAST_MATCH_SEC:
                self._clear_response("(processing)")
            return

        # ######################################################################
        # Handle outgoing (new) requests
        # ######################################################################

        # check to see if there are any queued Measurements from ThumbnailWidgets
        try:
            m = self.measurement_queue.pop()
            if not self._send_cropped_request(
                    pr              = m.processed_reading,
                    settings        = m.settings,
                    measurement_id  = m.measurement_id):
                log.debug("measurement %s rejected by Wrapper...requeueing", m.measurement_id)
                self.measurement_queue.append(m)
        except IndexError:
            # there were no queued measurements 
            pass
        except:
            log.error("error popping queued Measurement from ThumbnailWidget", exc_info=1)

    ##
    # Called by Controller.process_reading to apply any Raman ID for whatever we 
    # just read (or re-read)
    def process(self, pr, settings):
        if self.processing or not self.enabled:
            log.debug(f"self.processing is {self.processing} or not self.enabled is {not self.enabled}, returning")
            return

        if pr is None or settings is None:
            log.debug(f"pr is {pr} or settings is {settings}, returning")
            return

        log.info("kia feature processing is sending to cropped request")
        self._send_cropped_request(pr=pr, settings=settings)

    def process_last(self):
        if self.processing:
            log.error("process_last: already processing")
            return

        pr = self.get_last_processed_reading()
        if pr is None or pr.processed is None or len(pr.processed) == 0:
            log.error("process_last: no usable last ProcessedReading")
            return

        spec = self.multispec.current_spectrometer()
        if spec is None:
            log.error("process_last: no usable spectrometer")
            return

        # send request to subprocess
        self._send_cropped_request(pr=pr, settings=spec.settings)

    # ##########################################################################
    #
    #                              Private methods
    #
    # ##########################################################################

    # ##########################################################################
    # Callbacks
    # ##########################################################################

    ## The user clicked on the fingerprint button atop the scope screen, 
    #  indicating to identify the current processed reading (hopefully when 
    #  paused).  
    def _id_callback(self):
        if self.processing:
            self.marquee.error("Identification already in process")
            return

        self._clear_response("(processing)")

        if self.wrapper is None:
            if not self._connect():
                self.marquee.error("Failed to connect")
                return

        self.stylesheets.apply(self.bt_id, "red_gradient_button")
        self.process_last()

    ## The user has clicked the "continuous" checkbox which enables or disables 
    #  KIA processing of each acquired spectrum, so connect if necessary.
    def _enabled_callback(self, plugin_process = False):
        if self.closing:
            return

        checked = self.cb_enabled.isChecked()
        if checked or plugin_process:
            if self.wrapper is None:
                if self._connect():
                    self.enabled = True
                else:
                    self.enabled = False
            else:
                self.enabled = True
        else:
            self.enabled = False

        if not self.enabled:
            self.lb_processing.setText("disabled")
        else:
            self._queue_tip()

        if self.measurements:
            self.measurements.update_kia()

    ## The user has flagged a compound as benign.
    def _benign_callback(self):
        name = self._get_selected_compound_name()
        if name is None:
            return

        # this should always add ORIGINAL names, not aliases
        self.config.benigns.add(name)
        self._update_result_table()
        self._update_recent_table()
        self.config.save()

    ## The user has suppressed a compound.
    def _suppress_callback(self):
        name = self._get_selected_compound_name()
        if name is None:
            return

        # this should always add ORIGINAL names, not aliases
        self.config.suppressed.add(name)
        self._update_result_table()
        self._update_recent_table()
        self.config.save()

    ## The user has flagged a compound as hazardous.
    def _hazard_callback(self):
        name = self._get_selected_compound_name()
        if name is None:
            return

        # this should always add ORIGINAL names, not aliases
        self.config.hazards.add(name)
        self._update_result_table()
        self._update_recent_table()
        self.config.save()

    ## The user has created an alias for a compound name.
    def _alias_callback(self):
        name = self._get_selected_compound_name()
        if name is None:
            return

        (alias, ok) = QtWidgets.QInputDialog().getText(
            None,                               # parent
            "Compound Alias",                   # title
            "Compound Name:",                   # label
            QtWidgets.QLineEdit.Normal)
        if not ok or not alias:
            return 

        self.config.aliases[name] = alias
        self._update_result_table()
        self._update_recent_table()
        self.config.save()

    def _reset_callback(self):
        name = self._get_selected_compound_name()
        if name is None:
            return

        an = self._get_aliased_name(name)
        for alias in an.all_names:
            if alias in self.config.aliases:
                del self.config.aliases[alias]
            if alias in self.config.unalias:
                del self.config.unalias[alias]
            if alias in self.config.hazards:
                self.config.hazards.remove(alias)
            if alias in self.config.benigns:
                self.config.benigns.remove(alias)
        self.config.save()

    def _clear_callback(self):
        self.last_declared_match = None
        self.recent_matches = {}
        self._update_recent_table()

    def _score_callback(self):
        self.score_min = self.sb_score_min.value()

    def _max_results_callback(self):
        self.max_results = self.sb_max_results.value()

    ## The user clicked the "guide" checkbox
    def _guide_callback(self):
        self.guide = self.cb_guide.isChecked()
        self.update_visibility()

    ## The user clicked the "show all results" checkbox, so display or hide the 
    #  table.
    def _all_callback(self):
        self.display_all = self.cb_all.isChecked()
        self.update_visibility()

    ## The user clicked on a row, so enable buttons relevant to that compound.
    def _table_recent_callback(self, row, column=0):
        self.table_results.clearSelection()
        self._update_table_buttons()

    ## The user clicked on a row, so enable buttons relevant to that compound.
    def _table_results_callback(self, row, column=0):
        self.table_recent.clearSelection()
        self._update_table_buttons()

    # ##########################################################################
    # Lifecycle
    # ##########################################################################

    ## @private
    def _connect(self):
        if self.connecting or self.wrapper:
            log.info("KIA wrapper already exists, returning")
            return True

        self.connecting = True

        log.debug("instantiating Wrapper")
        self.lb_processing.setText("connecting")
        library_pathname    = None#self.ext_library    if self._ext_enabled() else None
        wrapper = Wrapper(
            log_queue = Queue(),
            log_level = self.logging_feature.level,
            executable_pathname = self.executable_pathname,
            library_pathname = library_pathname)

        log.debug("connecting Wrapper")
        if not wrapper.connect():
            self.lb_processing.setText("error")
            self.connecting = False
            return False

        self.wrapper = wrapper
        self.connecting = False

        return True
        
    ## @private
    def _reset(self):
        self.wrapper = None
        self.ext_wrapper = None
        self.connecting = False

        self.processing = False 
        self.processing_start_time = None
        self.current_processed_reading = None  # whatever we're processing now

        self.last_response = None
        self.last_declared_match = None

        self._enabled_callback()

    ## 
    # Test whether both the Know-It-All application, and our executable
    # wrapper, are installed.
    #
    # @private
    def _check_installed(self):
        if platform.system().lower() != "windows":
            self.lb_path.setText("not supported")
            return False

        # check for Know-It-All application (must be separately installed)
        pathname = Feature.KNOW_IT_ALL_DIRECTORY
        found = os.path.exists(pathname)
        log.debug("%s found = %s", pathname, found)
        if found:
            self.kia_pathname = pathname
        else:
            return False

        # check for our KIAConsole wrapper executable (ultimately installed in 
        # same directory as ENLIGHTEN.exe, but in dev environments may be in dist/)
        for path in [ ".", "dist" ]:
            pathname = os.path.join(path, Feature.KIA_CONSOLE_NAME)
            found = os.path.exists(pathname)
            log.debug("%s found = %s", pathname, found)
            if found:
                self.executable_pathname = pathname
                return True

        return False

    # ##########################################################################
    # Processing Requests
    # ##########################################################################

    ## @private
    def _get_elapsed_time_str(self):
        if self.processing_start_time is None:
            return "NA"
        elapsed_sec = (datetime.datetime.now() - self.processing_start_time).total_seconds()
        return time.strftime('%H:%M:%S', time.gmtime(elapsed_sec))

    ## @private
    def _send_cropped_request(self, pr, settings=None, measurement_id=None):
        log.debug("sending spectrum -> Wrapper")

        x_axis = settings.wavenumbers
        if x_axis is None or len(x_axis) == 0:
            log.error("no wavenumbers x-axis")
            return

        roi = settings.eeprom.get_horizontal_roi()
        log.debug("orig roi = %s, x_axis = %s", roi, x_axis)

        spectrum = pr.get_processed()
        if pr.is_cropped():
            log.debug("cropped spectrum")
            if roi is not None:
                log.debug("cropping x-axis")
                x_axis = self.horiz_roi.crop(x_axis, roi=roi)

        log.debug("new x_axis = %s", x_axis)

        if len(x_axis) != len(spectrum):
            log.error("len x_axis %d != len spectrum %d", len(x_axis), len(spectrum))
            return False

        wrapper = self.wrapper
        if wrapper is None:
            log.error("no KnowItAll.Wrapper available")
            return False

        ok = wrapper.send_request(
            x_axis         = x_axis, 
            spectrum       = spectrum,
            max_results    = self.max_results, 
            min_score      = self.score_min,
            measurement_id = measurement_id)

        if ok:
            self.processing = True
            self.processing_start_time = datetime.datetime.now()
            self.current_processed_reading = pr

        return ok

    ## @private
    def _clear_response(self, label=""):
        self.last_response = None
        self.lb_name.setText(label)
        self.lb_score.setText("NA")
        self._update_result_table()
        self._update_recent_table()
        self.marquee.clear(token="KnowItAll")

    ## @private
    def _process_response(self, response):
        if self.closing:
            return

        # if we just haven't gotten anything back from the subprocess yet,
        # don't do anything
        if response is None:
            return

        def exit_processing():
            self._clear_response("(no match)")
            self.current_processed_reading = None
            if response.measurement_id is not None:
                self.measurements.id_callback(measurement_id=response.measurement_id, declared_match=None)

        # clear suppressed results
        self._clear_suppressed(response)

        # does at least one compound meet the score threshold?
        if response.match_count < 1 or response.entries[0].score < self.score_min:
            log.debug("process_response: no entries meet score threshold")
            return exit_processing()

        self.last_response = response

        # pick DeclaredMatch, resolving any ties and determining flags / aliases
        dm = self._declare_match(response)
        if dm is None:
            log.debug("process_response: failed to resolve ties")
            self._update_result_table(response=response)
            return exit_processing()

        self.last_declared_match = dm

        ########################################################################
        # we have a declared match of one compound; 
        # we know its hazard/benign status; 
        # we know its aliases, preferred and original name
        ########################################################################

        # display to the widget
        self.lb_name.setText(dm.aliased_name.preferred)
        self.lb_score.setText("%.2f" % dm.score)

        if dm.hazard:
            log.debug("process_response: coloring hazard")
            benign = False
            self._play_sound("hazard")
        elif dm.benign:
            log.debug("process_response: coloring benign")
            benign =True 
            self._play_sound("benign")
        else:
            benign = None
            self._play_sound("unknown")

        if dm.aliased_name.preferred == "(null)":
            self.marquee.error("Please check KnowItAll license", persist=True)
        else:
            self.marquee.info(dm.aliased_name.preferred, persist=True, benign=benign, token="KnowItAll")

        self._update_result_table()
        self._update_recent_table()

        if response.measurement_id is not None:
            self.measurements.id_callback(measurement_id=response.measurement_id, declared_match=dm)

        # disconnect from the ProcessedReading...if Controller still has it, 
        # fine, else let it GC
        self.current_processed_reading = None

    ## 
    # Using the Response object, return a DeclaredMatch with hazards, benigns, 
    # and aliases resolved.
    #
    # @private
    def _declare_match(self, response):

        # take a handle to the top-ranked response (may be part of a tie)
        first = response.entries[0]
        score = first.score

        # if no tie, just take top match
        if response.match_count == 1 or score > response.entries[1].score:
            an = self._get_aliased_name(first.compound_name)
            dm = DeclaredMatch(aliased_name=an, score=score)

            if util.sets_intersect(an.all_names, self.config.hazards):
                dm.hazard = True
            elif util.sets_intersect(an.all_names, self.config.benigns):
                dm.benign = True
            return dm

        # get all names tied for top
        tied_names = set(first.compound_name)
        for i in range(1, response.match_count):
            if score == response.entries[i].score:
                tied_names.add(response.entries[i].compound_name)
            else:
                break

        # are there any hazards in the ties?
        name = self._find_one_in_set(tied_names, within=self.config.hazards)
        if name:
            log.debug("resolved tie via hazard")
            an = self._get_aliased_name(name)
            if an:
                return DeclaredMatch(aliased_name=an, score=score, hazard=True) 
        
        # are there any benigns in the ties?
        name = self._find_one_in_set(tied_names, within=self.config.benigns)
        if name:
            log.debug("resolved tie via benign")
            an = self._get_aliased_name(name)
            if an:
                return DeclaredMatch(aliased_name=an, score=score, benign=True) 

        # is there exactly one alias in the ties?
        name = self._find_one_aliased(tied_names)
        if name:
            log.debug("resolved tie via alias")
            an = self._get_aliased_name(name)
            if an:
                return DeclaredMatch(aliased_name=an, score=score) 

        # declare no match
        log.error("could not resolve tie: %s", tied_names)
        return

    ##
    # @private
    def _is_hazard(self, names):
        return util.sets_intersect(names, self.config.hazards)

    ##
    # @private
    def _is_benign(self, names):
        return util.sets_intersect(names, self.config.benigns)

    ##
    # Remove any "suppressed" MatchResultEntries from the MatchResponse.
    #
    # @private
    def _clear_suppressed(self, response):
        if response.match_count == 0:
            return

        keep = []
        for entry in response.entries:

            is_suppressed = False
            an = self._get_aliased_name(entry.compound_name)
            for alias in an.all_names:
                if alias in self.config.suppressed:
                    is_suppressed = True
                    break

            if not is_suppressed:
                keep.append(entry)
        
        response.match_count = len(keep)
        response.entries = keep

    # ##########################################################################
    # Tables
    # ##########################################################################

    ##
    # @private
    def _update_result_table(self):
        t = self.table_results
        t.setRowCount(0)

        response = self.last_response
        if response is None:
            return

        # populate the table
        for entry in response.entries:

            # resolve aliases
            an = self._get_aliased_name(entry.compound_name)

            row = t.rowCount()
            t.insertRow(row)
            self.table_results.setItem(row, Feature.RESULTS_COL_SCORE,    QtWidgets.QTableWidgetItem("%.2f" % entry.score))
            self.table_results.setItem(row, Feature.RESULTS_COL_COMPOUND, QtWidgets.QTableWidgetItem(an.preferred))

            if an.is_aliased():
                t.item(row, Feature.RESULTS_COL_COMPOUND).setToolTip(an.orig)

            self._colorize_table_row(table=t, row=row, aliased_name=an)
    
    ##
    # @private
    def _update_recent_table(self):
        t = self.table_recent
        t.setRowCount(0)

        # add or update latest declared match in the dict
        dm = self.last_declared_match
        if dm:
            self.recent_matches[dm.aliased_name.orig] = datetime.datetime.now()

        # convert recent_matches (keyed on name) to a dict ordered by time
        # (duplicates almost unthinkably unlikely, but even so)
        times = {}
        for name in self.recent_matches:
            time = self.recent_matches[name]
            if time not in times:
                times[time] = []
            times[time].append(name)

        # populate the table
        for time in times:
            for name in sorted(times[time]):
                an = self._get_aliased_name(name)

                row = t.rowCount()
                t.insertRow(row)
                self.table_recent.setItem(row, Feature.RECENT_COL_TIME,     QtWidgets.QTableWidgetItem(time.strftime("%H:%M:%S")))
                self.table_recent.setItem(row, Feature.RECENT_COL_COMPOUND, QtWidgets.QTableWidgetItem(an.preferred))

                if an.is_aliased():
                    t.item(row, Feature.RECENT_COL_COMPOUND).setToolTip(an.orig)

                self._colorize_table_row(table=t, row=row, aliased_name=an)

    ## 
    # @returns NON-ALIASED version (caller can always re-alias it)
    # @todo could return AliasedName
    # @private
    def _get_selected_compound_name(self):
        item = self._get_selected_item_results()
        if item is None:
            item = self._get_selected_item_recent()

        if item:
            tt = item.toolTip()         # returns a string, not a QToolTip
            if tt is not None and len(tt) > 0:
                return tt
            return item.text()

    ##
    # @private
    def _get_selected_item_results(self):
        row = self.table_results.currentRow()
        if row is not None:
            return self.table_results.item(row, Feature.RESULTS_COL_COMPOUND)

    ##
    # @private
    def _get_selected_item_recent(self):
        row = self.table_recent.currentRow()
        if row is not None:
            return self.table_results.item(row, Feature.RECENT_COL_COMPOUND)

    ## @private
    def _colorize_table_row(self, table, row, aliased_name):
        hexcolor = None
        if self._is_hazard(aliased_name.all_names):
            hexcolor = self.colors.color_names.get(Feature.HAZARD_COLOR_NAME)
        elif self._is_benign(aliased_name.all_names):
            hexcolor = self.colors.color_names.get(Feature.BENIGN_COLOR_NAME)

        if hexcolor:
            log.debug("setting table row %d to color %s", row, hexcolor)
            util.set_table_row_color(table, row, QtGui.QColor(hexcolor))

    ##
    # This method is provided to deal with an apparent bug in the pyside2-uic.exe
    # tool that comes with PySide2 5.13.0.  As far as I can tell, if enlighten_layout.ui
    # contains two QTableWidgets within the same...something...that have NAMED COLUMN
    # HEADERS, pyside2-uic gets internally confused and conflates the tables when
    # converting the XML to Python.
    #
    # In this case, the QTableWidgets table_results and table_recent both appear on
    # the scope screen within frame_id_results.  Each has two columns, which are 
    # (Score, Compound) and (Time, Compound) respectively.  Each pair should
    # be internally numbered (0, 1) within the table.
    #
    # However, when pyside2-uic tries to assign the column names, it conflates the
    # tables, thinking there actually 4 columns, and so treats the first column of
    # the second table as column 2 rather than the second column 0:
    # \code
    #     self.tableWidget_id_match_recent.horizontalHeaderItem(2).setText(QtWidgets.QApplication.translate("MainWindow", "Time", None, -1))
    #     AttributeError: 'NoneType' object has no attribute 'setText'
    # \endcode
    #
    # I'd hoped that by wrapping each table inside its own QFrame and QWidget
    # I might break this connection between them, but no dice.
    #
    # Therefore, for now I'm creating and naming the columns programmatically.
    # This will possibly be fixed in pyside2-uic by the time you read this, but
    # who knows.
    #
    # @private
    def _init_tables(self):
        self._init_table(self.table_results, ["Score", "Compound"])
        self._init_table(self.table_recent,  ["Time", "Compound"])

    ## @private
    def _init_table(self, table, cols):
        table.setRowCount(0)
        
        count = len(cols)
        table.setColumnCount(count)
        for (index, name) in enumerate(cols):
            table.setHorizontalHeaderItem(index, QtWidgets.QTableWidgetItem())
            table.horizontalHeaderItem(index).setText(QtWidgets.QApplication.translate("MainWindow", name, None, -1))
            table.setColumnWidth(index, 100)

        table.resizeRowsToContents()
        # table.resizeColumnsToContents()

        table.setSelectionMode    (QtWidgets.QAbstractItemView.SingleSelection)
        table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setStretchLastSection(True)

    # ##########################################################################
    # Aliases
    # ##########################################################################

    ## 
    # Given a compound name (possibly an alias), return an AliasedName containing
    # the original (KnowItAll) name, the preferred alias (perhaps an alias-of-aliases,
    # in case of manually-editted config files), and a non-empty set of all names 
    # (both the original and all known aliases).
    #
    # In the case of converging roots (a -> b and c -> b), moving "back out to the root"
    # could yield the wrong root, so hopefully this function won't need to be called
    # from a non-root name.  (Currently that is the case.)
    #
    # This could be a static function in AliasedName ("create()"), but requires
    # access to config, so we'd really need an AliasedNameFactory.  Just leave it.
    #
    # @private
    def _get_aliased_name(self, root):
        an = AliasedName()

        # back out to original name (not a safe operation if convergent roots)
        orig = root
        while True:
            if orig in self.config.unalias:
                orig = self.config.unalias[name]
            else:
                break
        an.orig = orig
            
        # find preferred alias (supports alias chains)
        preferred = root 
        while True:
            an.all_names.add(preferred)
            if preferred in self.config.aliases:
                preferred = self.config.aliases[preferred]
            else:
                break
        an.preferred = preferred

        return an

    ## 
    # Given a list of names (presumably tied compounds), if EXACTLY ONE
    # has an alias, return that name.
    #
    # @private
    def _find_one_aliased(self, names, within):
        found = set()
        for name in names:
            an = self._get_aliased_name(name)
            if an.is_aliased():
                found.add(name)
        if len(found) == 1:
            for name in found:
                return name

    ## 
    # Given a list of names (presumably tied compounds), and a set 'within'
    # (presumably hazards or benigns), if EXACTLY ONE of the list of names
    # (including aliases of those names) falls within the set, return that 
    # name.
    #
    # @private
    def _find_one_in_set(self, names, within):
        found = set()
        for name in names:
            an = self._get_aliased_name(name)
            for alias in an.all_names:
                if alias in within:
                    found.add(name) # add the name, not the alias
        if len(found) == 1:
            for name in found:
                return name

    ## 
    # For now, just play a standard Windows exclamation if matching a hazard.
    # Later we can check self.config.sounds to see if it names a sound to use
    # for "hazard", "benign" or "unknown"
    # 
    # @private
    def _play_sound(self, category):
        if self.sounds:
            if category == "hazard":
                self.sounds.play("exclamation")

