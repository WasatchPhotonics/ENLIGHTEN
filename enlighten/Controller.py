from threading import Thread
import webbrowser
import pyqtgraph
import functools
import datetime
import logging
import numpy as np
import struct
import copy
import math
import time
import sys
import os
import re

import PySide2
from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtCore import QObject, QEvent
from PySide2.QtWidgets import QMessageBox, QVBoxLayout, QWidget, QLabel, QMessageBox

from collections import defaultdict

from pygtail import Pygtail # for log screen

# these aren't actually used...solves an import issue for MacOS I think
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('TkAgg')

from . import util
from . import common

import wasatch
from wasatch import applog
from wasatch import utils as wasatch_utils

from wasatch.WasatchDeviceWrapper     import WasatchDeviceWrapper
from wasatch.DeviceFinderUSB          import DeviceFinderUSB
from wasatch.SpectrometerResponse     import ErrorLevel
from wasatch.StatusMessage            import StatusMessage
from wasatch.WasatchBus               import WasatchBus
from wasatch.BLEDevice                import BLEDevice
from wasatch.Reading                  import Reading

from wasatch.ProcessedReading         import ProcessedReading
from .BusinessObjects                 import BusinessObjects
from .Spectrometer                    import Spectrometer
from .TimeoutDialog                   import TimeoutDialog
from .BasicWindow                     import BasicWindow
from wasatch.RealUSBDevice            import RealUSBDevice

log = logging.getLogger(__name__)

class AcquiredReading(object):
    """ Trivial class to eliminate a tuple during memory profiling. """
    def __init__(self, reading=None, progress=0, disconnect=False):
        self.reading    = reading
        self.disconnect = disconnect
        self.progress = progress

class Controller:
    """
    Main application controller class for ENLIGHTEN.
    
    This class is still way bigger than it should be, but it's gradually coming
    under control.
    
    - most feature logic has been extracted into "business objects" which own and
      configure their own GUI widgets and internal state
    """

    # ##########################################################################
    # Constants
    # ##########################################################################

    ACQUISITION_TIMER_SLEEP_MS      =  100
    STATUS_TIMER_SLEEP_MS           = 1000
    BUS_TIMER_SLEEP_MS              = 1000
    LOG_READER_TIMER_SLEEP_MS       = 3000
    MAX_MISSED_READINGS             =    2
    USE_ERROR_DIALOG                = False
    SPEC_ERROR_MAX_RETRY            = 3
    SPEC_RESET_MAX_RETRY            = 3

    URL_HELP = "https://wasatchphotonics.com/software-support/enlighten/"

    # ##########################################################################
    # Lifecycle
    # ##########################################################################

    def __init__(self,
                app,
                log_queue,
                log_level         = "INFO",
                max_memory_growth = 0,
                run_sec           = 0,
                serial_number     = None,
                stylesheet_path   = None,
                set_all_dfu       = False,
                headless          = False,
            ):
        """
        All of the parameters are normally parsed from via command-line arguments
        in Enlighten.py.  Typically the only argument that changes in normal
        operation is log_level.
        
        @param app        the running QApplication, to which the Controller
                          will add the BasicWindow form
        @param log_level  string in ["debug", "info", "warning", "error", "critical"]
                          (https://docs.python.org/2/library/logging.html#logging-levels)
        @param max_memory_growth how much process RAM usage is allowed to increase
                          as a percentage before ENLIGHTEN automatically shuts down
        @param run_sec    automatically exit after this many seconds
        @param serial_number only connect to this unit if found.
        @param stylesheet_path pathname to CSS "skin" to use for overriding enlighten.css
        @param set_all_dfu set each ARM spectrometer to DFU mode as they connect
        """

        self.app                    = app
        self.log_queue              = log_queue # currently needed for KnowItAll.Wrapper
        self.log_level              = log_level # passed to LoggingFeature
        self.max_memory_growth      = max_memory_growth
        self.run_sec                = run_sec
        self.dialog_open            = False
        self.grid_display           = False
        self.serial_number_desired  = serial_number
        self.stylesheet_path        = stylesheet_path
        self.set_all_dfu            = set_all_dfu
        self.headless               = headless
        self.spec_timeout           = 30

        # Before we apply the commanded debug level, set the logger to DEBUG so
        # initialization (enumeration, etc) is always captured in customer logfiles,
        # making support tickets much easier.  (We will apply the commanded log
        # level after the first spectrometer has successfully connected.)
        logging.getLogger().setLevel(logging.DEBUG)

        log.info("ENLIGHTEN version %s",     common.VERSION)
        log.info("Wasatch.PY version %s",    wasatch.version)
        log.info("applog at %s",             applog.get_location())

        log.info("Stylesheet path %s",       self.stylesheet_path)

        log.info("Python version %s",        util.python_version())
        log.info(f"Operating system {sys.platform} {struct.calcsize('P')*8 } bit")
        log.info("PySide version %s",        PySide2.__version__)
        log.info("PySide QtCore version %s", QtCore.__version__)
        log.info("QtCore version %s",        QtCore.qVersion())

        ########################################################################
        # GUI Configuration
        ########################################################################

        # instantiate form (a QMainWindow with named "MainWindow")
        self.form = BasicWindow(title="ENLIGHTEN %s" % common.VERSION,headless=self.headless)

        # hide these immediately (KIA shouldn't be visible in Scope)
        sfu = self.form.ui
        for widget in [ sfu.frame_kia_outer,
                        sfu.frame_id_results_white,
                        sfu.tabWidget_advanced_features
                      ]:
            widget.setVisible(False)
        sfu.pushButton_reset_fpga.clicked.connect(self.perform_fpga_reset)

        # immediately show Scope Capture screen
        #self.set_main_page(common.Pages.SCOPE_CAPTURE)

        ########################################################################
        # Create startup Business Objects
        ########################################################################

        # instantiate the initial Business Objects we'll need to complete startup
        self.seen_errors = defaultdict(lambda: defaultdict(int))
        self.business_objects = BusinessObjects(self)
        self.business_objects.create_first()

        ########################################################################
        # Support skinning
        ########################################################################

        self.stylesheets.apply(self.form, "enlighten") # MZ: I don't think this is working...

        ########################################################################
        # Lifecycle
        ########################################################################

        self.shutting_down = False
        self.exit_code = 0

        # add Qt signal handlers to this Controller object
        self.create_signals()

        # resource tracking
        self.start_time = datetime.datetime.now()

        # ######################################################################
        # logging
        # ######################################################################

        self.log_reader_timer = None

        # ######################################################################
        # versions
        # ######################################################################

        sfu.label_python_version.setText(util.python_version())

        # ######################################################################
        # logical state
        # ######################################################################

        self.last_laser_toggle = None

        ########################################################################
        # Populate Placeholders
        ########################################################################

        # populate missing GUI elements, so we can pass them to Business Objects
        # @todo have Business Objects create their own
        self.populate_thumbnail_column()

        ########################################################################
        # Events and Timers
        ########################################################################

        # define GUI callbacks
        self.bind_gui_signals()

        ########################################################################
        # Application Business Objects
        ########################################################################

        # instantiate major business objects (require access to populated placeholders)
        self.business_objects.create_rest()
        self.graph.rehide_curves()

        # immediately show Scope Capture screen
        self.page_nav.set_main_page(common.Pages.SCOPE_CAPTURE)

        # configure acquisition loop
        self.setup_main_event_loops() # MZ: move to end?

        # setup GUI access to log outputs
        self.setup_log_interface()

        # setup timer to check for hardware changes
        self.setup_bus_listener()

        self.setup_hardware_strip_listener() # move to StripChartFeature

        # bind keyboard shortcuts
        self.bind_shortcuts()

        self.page_nav.post_init()

        sfu.pushButton_graphGrid.clicked.connect(self.graph_grid_toggle)
        sfu.pushButton_roi_toggle.clicked.connect(self.toggle_roi_process)
        self.default_roi_btn = self.form.ui.pushButton_roi_toggle.styleSheet()
        self.default_graph_btn = self.form.ui.pushButton_graphGrid.styleSheet()
        self.form.ui.pushButton_roi_toggle.setStyleSheet("background-color: #aa0000")
        self.roi_enabled = True
        self.enlighten_graphs = {
                "scope graph": [self.graph, "plot"],
                "plugin graph": [self.plugin_controller, "graph_plugin", "plot"],
            }

        self.header("Controller ctor done")
        self.other_devices = []

    def disconnect_device(self, spec=None, closing=False):
        if spec in self.other_devices:
            self.other_devices.remove(spec)
        if spec is None:
            spec = self.current_spectrometer()
        if spec is None:
            log.error("disconnect_device: no more devices")
            return False

        device_id = spec.device_id
        if spec.device.is_ble:
            self.form.ui.readingProgressBar.setValue(0)
        self.marquee.info("disconnecting %s" % spec.label)
        self.multispec.set_disconnecting(device_id, True)

        ########################################################################
        # avoid confusing/dangerous behavior on re-launch
        ########################################################################

        for feature in [ self.laser_control,
                         self.accessory_control,
                         self.area_scan,
                         self.raman_mode_feature ]:
            feature.disconnect()

        if spec.settings.is_gen15():
            log.debug("disconnect_device[%s]: disabling fan", device_id)
            spec.change_device_setting("fan_enable", False)

        log.debug("disconnect_device[%s]: disabling TEC", device_id)
        spec.change_device_setting("detector_tec_enable", False)

        # The background thread only applies changes BETWEEN spectra, so give it
        # time to collect at least one more acquisition so the changes can take 
        # effect.
        final_delay_sec = float(2 * spec.settings.state.integration_time_ms / 1000.0 + 0.200)
        log.debug("disconnect_device[%s]: final delay of %.2fsec", device_id, final_delay_sec)
        time.sleep(final_delay_sec)

        ########################################################################
        # close
        ########################################################################


        log.debug("disconnect_device[%s]: closing", device_id)
        spec.close()

        log.debug("disconnect_device[%s]: removing from Multispec", device_id)
        self.detector_temperature.remove_spec_curve(spec)
        self.laser_temperature.remove_spec_curve(spec)
        self.area_scan.remove_spec_curve(spec)
        self.multispec.spec_most_recent_reads.pop(spec, None)
        if not self.multispec.remove(spec):
            log.error("disconnect_device[%s]: failed to remove from Multispec", device_id)
            return False

        if self.multispec.count() == 0:
            self.marquee.info("searching for spectrometers", immediate=True, persist=True)
            self.advanced_options.update_visibility()

        self.status_indicators.update_visibility()

        return True

    def close(self, event_arg_str):
        log.critical("closing")

        self.shutting_down = True

        log.debug("stopping all timers")
        for feature in [ self.batch_collection,
                         self.status_indicators,
                         self.ble_manager ]:
            feature.stop()

        for timer in [ self.bus_timer,
                       self.acquisition_timer,
                       self.status_timer,
                       self.log_reader_timer,
                       self.hard_strip_timer]: # StripChartFeature
            if timer is not None:
                timer.stop()

        try:
            self.config.save_file()
        except:
            log.critical("Caught exception saving config file", exc_info=1)

        while self.multispec.count() > 0:
            log.debug("close: multispec.count = %d", self.multispec.count())
            if not self.disconnect_device(closing=True):
                log.error("close: had problems disconnecting device, terminating anyway")
                break

        self.business_objects.destroy()

        self.exit_code = self.resource_monitor.exit_code
        log.critical("emitting control level close (exit_code %d)", self.exit_code)
        self.control_exit_signal.exit.emit("Control level close")
        log.critical("emitted control level close (exit_code %d)", self.exit_code)

    def create_signals(self):
        """ Add Qt signal handlers to the Controller instance. """

        ## inherits from QObject, hence supports Qt signals
        class ControlClose(QtCore.QObject):

            # exit is an instance of the QtCore.Signal class and takes a single string arg
            exit = QtCore.Signal(str)

        ## creating control_exit_signal as a QObject with an "exit" signal
        self.control_exit_signal = ControlClose()

    # ##########################################################################
    # Multispec Shortcuts
    # ##########################################################################

    def current_spectrometer(self):
        if self.multispec is None:
            log.error("current_spectrometer: multispec is None")
            return None
        spec = self.multispec.current_spectrometer()
        if spec is None:
            log.error("current_spectrometer: spectrometer is None")
        return spec

    def settings(self):
        spec = self.current_spectrometer()
        if spec is None:
            return None
        return spec.settings

    def app_state(self):
        spec = self.current_spectrometer()
        if spec is None:
            return None
        return spec.app_state

    # ##########################################################################
    #                                                                          #
    #                                Timers                                    #
    #                                                                          #
    # ##########################################################################

    def setup_bus_listener(self):
        """
        Poll the USB bus periodically for new connection events (including 
        devices connected at application launch).
        """
        self.marquee.info("searching for spectrometers", immediate=True, persist=True)
        self.bus = WasatchBus()
        self.bus_timer = QtCore.QTimer()
        self.bus_timer.timeout.connect(self.tick_bus_listener)
        self.bus_timer.setSingleShot(True)
        self.bus_timer.start(500)

    def setup_hardware_strip_listener(self):
        """ @todo move to StripChartFeature """
        self.hard_strip_timer = QtCore.QTimer()
        self.hard_strip_timer.timeout.connect(self.process_hardware_strip)
        self.hard_strip_timer.setSingleShot(True)
        self.hard_strip_timer.start(1000)

    def process_hardware_strip(self):
        """ @todo move to StripChartFeature """
        for spec, recent_read in self.multispec.spec_most_recent_reads.items():
            for feature in [self.detector_temperature,
                            self.laser_temperature,
                            self.battery_feature]:
                feature.process_reading(spec, recent_read) 
        if self.page_nav.get_current_technique() == common.Techniques.HARDWARE or self.form.ui.checkBox_feature_file_capture.isChecked():
            self.hard_strip_timer.start(self.form.ui.spinBox_integration_time_ms.value())
            return
        self.hard_strip_timer.start(1000)

    def tick_bus_listener(self):
        """
        If a device is listed on the bus, and it is not currently connected,
        attempt to make a connection.
        """
        if self.shutting_down:
            return self.bus_timer.stop()

        # if a spectrometer is already in the process of connecting, let it
        # finish before starting another one
        if self.multispec.have_any_in_process():
            self.check_ready_initialize()
            return self.bus_timer.start(self.BUS_TIMER_SLEEP_MS)

        # refresh the list of visible spectrometers on the USB bus
        self.bus.update()

        # refresh the list of visible spectrometers on the BLE list
        self.ble_manager.check_complete_scans()

        self.multispec.check_ejected_unplugged(self.bus.device_ids)
        ########################################################################
        # attempt connection to the first untried (not connected, not in-process)
        # device on the list
        ########################################################################

        self.connect_new()

        # Continue polling bus at 1Hz.
        #
        # This will ensure one full second passes before completing the
        # connection and initialization of the last device, and even scanning
        # the bus for the next potential connection (deliberately slowing
        # down the connection process).
        self.bus_timer.start(self.BUS_TIMER_SLEEP_MS)

    def connect_new(self, other_device=None):
        """
        # If there are any visible spectrometers that ENLIGHTEN has not yet
        # connected to, try to connect to them.  Only connect one device per pass;
        # let bus_listener kick-off and call connect_new() again if more remain.
        #
        # Note that this method gets called whether there are any spectrometers
        # on the bus or not, and whether any or all of them have already connected
        # or not.
        #
        # @param other_device: can be a BLEDevice from BLEManager
        """
        # do we see any spectrometers on the bus?  (WasatchBus will pre-filter to
        # only valid spectrometer devices)
        if other_device is not None and other_device not in self.other_devices:
            self.other_devices.append(other_device)
        self.bus.device_ids.extend(self.other_devices)

        # MZ/ED: If DeviceFinderUSB.USE_MONITORING is True, I had to disable this call to remove_all:
        if self.bus.is_empty() and self.multispec.count() > 0 and not DeviceFinderUSB.USE_MONITORING:

            # no need to make this persistent, it'll be renewed 1/sec
            self.marquee.info("no spectrometers found...calling remove_all") 
            self.multispec.remove_all()

            self.update_feature_visibility
            return

        # handle the special case in which the user specified a single 
        # device on the cmd-line they wish to connect to
        if self.multispec.found_desired():
            log.debug("already found our spectrometer")
            return

        # iterate over every device we saw on the bus
        new_device_id = None
        for device_id in self.bus.device_ids:

            # ignore devices we've already connected to in Multispec
            if self.multispec.is_connected(device_id):
                # log.debug("connect_new: already connected: %s", device_id)
                continue

            if self.multispec.check_spec_user_ejected(device_id):
                continue

            # this is not the spectrometer we're trying to connect
            if self.multispec.is_gave_up(device_id):
                log.debug("connect_new: already gave up connection attempt: %s", device_id)
                continue

            if self.multispec.is_in_process(device_id):
                log.error("connect_new: shouldn't be called whilst spectrometers are in-process")
                return

            # Kludge around the fact that individual Andor cameras sometimes
            # (but not consistently) show up on multiple USB port addresses and thus
            # have multiple unique DeviceIDs as we are tracking them through libusb.
            if device_id.is_andor():
                log.debug(f"connect_new: considering Andor {device_id}")
                if self.multispec.have_any_andor():
                    log.error("connect_new: only supporting one Andor unit for now (ignoring new)")
                    continue
                else:
                    log.debug("connect_new: don't have any Andor so far")

            if self.multispec.is_disconnecting(device_id):
                log.info("connect_new: called connect on spectrometer that is disconnected, removing from record and passing to next bus update.")
                self.multispec.set_disconnecting(device_id, False)
                return

            # for whatever reason (DFU, HW error, previous filter check) we've 
            # decided that we don't want to connect to this device
            if self.multispec.is_ignore(device_id):
                log.debug("connect_new: ignoring: %s", device_id)
                continue

            # we found the ID of a DEVICE that we wish to connect to; 
            # stop, as there's no reason to continue
            new_device_id = device_id
            break

        if new_device_id is None:
            return

        ####################################################################
        # try to connect to this device
        ####################################################################
        
        self.bus.device_ids.remove(new_device_id)
        if new_device_id in self.other_devices:
            self.other_devices.remove(new_device_id)

        # attempt to connect the device
        if new_device_id.is_andor():
            self.marquee.info("connecting to XL spectrometer (please wait)", persist=True)
        else:
            self.marquee.info(f"connecting to {new_device_id}", persist=True)
        
        log.debug("connect_new: instantiating WasatchDeviceWrapper with %s", new_device_id)
        device = WasatchDeviceWrapper(
            device_id = new_device_id,
            log_level = self.logging_feature.level)

        # flag that an attempt to connect to the device is ongoing
        self.header("connect_new: setting in-process: %s" % new_device_id)
        self.multispec.set_in_process(new_device_id, device)

        log.debug("connect_new: calling WasatchDeviceWrapper.connect()")
        if not device.connect():
            log.critical("connect_new: can't connect to device_id, giving up: %s", new_device_id)
            self.multispec.set_gave_up(device_id)
            return

        ####################################################################
        # Yay, a new spectrometer has connected!
        # Continue on and have the bus poll for settings
        ####################################################################

        return True

    def check_ready_initialize(self):
        """
        Check if an identified spectrometer succeeded in returning settings
        With this complete, initialize and start operating the spec
        """
        in_process_specs = list(self.multispec.in_process.items()) 
        for device_id, device in in_process_specs:
            if device is None or type(device) is bool:
                log.debug("check_ready_initialize: ignoring {device_id} ({device})")
                continue

            log.debug(f"checking {device_id} for settings results")
            disconnect_device = False

            poll_result = device.poll_settings()
            if poll_result is not None:
                if poll_result.data:
                    self.header("check_ready_initialize: successfully connected %s" % device_id)
                    self.initialize_new_device(device)

                    # remove the "in-process" flag, as it's now in the "connected" list
                    # and fully initialized
                    if device.is_ble:
                        self.form.ui.readingProgressBar.show()

                    self.initialize_new_device(device)

                    self.multispec.remove_in_process(device_id)
                    self.header("connect_new: done (%s)" % device_id)
                else:
                    self.marquee.error(poll_result.error_msg)
                    disconnect_device = True
                    
            else:
                # didn't get settings so check for timeout
                if device.connect_start_time + datetime.timedelta(seconds=self.spec_timeout) < datetime.datetime.now():
                    log.error(f"{device_id} settings timed out, giving up on the spec")
                    disconnect_device = True

            if disconnect_device:
                device.disconnect()
                self.multispec.set_gave_up(device_id)
                self.multispec.remove_in_process(device_id)

    # also called by PageNavigation.set_technique_common
    def update_feature_visibility(self):
        # disable anything that shouldn't be on without a spectrometer
        # (could grow this considerably)
        for feature in [ self.accessory_control,
                         self.advanced_options,
                         self.raman_mode_feature,
                         self.raman_intensity_correction,
                         self.raman_shift_correction,
                         self.reference_feature,
                         self.baseline_correction,
                         self.kia_feature]:
            feature.update_visibility()

    # ##########################################################################
    # Spectrometer Initialization
    # ##########################################################################

    def initialize_new_device(self, device):
        """
        This method is called in two very different circumstances:
        
        - by Controller.connect_new(), when we connect to a new spectrometer
          - this is considered a "hotplug" event
          - this includes when a previously dropped/disconnected spectrometer
            reattaches / re-enumerates
        - by Multispec, when the user manually changes the "currently selected
          spectrometer" select-box on the GUI (frequent)
        
        The method itself determines the calling case by inferring a "hotplug"
        variable from whether the passed device was already connected or not.
        
        Probably we should split this function into two:
        
        - move 'hotplug' logic to initialize_newly_connected_device()
        - leave rest in initialize_gui_from_current_device()
        - have hotplug function call initialize_gui() at end
        """
        sfu = self.form.ui

        if self.shutting_down:
            log.debug("initialize_new_device: shutting down")
            return

        # reject filtered spectrometers
        if self.multispec.reject_undesireable(device):
            self.marquee.error("rejecting %s" % device.settings.eeprom.serial_number)
            device.disconnect()
            return

        # a very rare setting -- user has asked us to flip every connected 
        # spectrometer to DFU and then disconnect, as a convenience when updating
        # firmware
        if self.set_all_dfu:
            self.marquee.info("enabling DFU mode on %s" % device.settings.eeprom.serial_number)
            self.multispec.set_ignore(device.device_id)
            device.change_setting("dfu_enable", 1)
            time.sleep(0.2)
            device.disconnect()
            return

        ########################################################################
        # initialize from cloud
        ########################################################################

        if device.is_andor:
            # Note that currently we're doing this BEFORE determining if it's a 
            # hotplug; ideally, we should only need to connect to the Cloud
            # on hotplug.  

            # attempt to backfill missing EEPROM settings from cloud
            # (allow overrides from local configuration file)
            log.debug("attempting to download Andor EEPROM")
            andor_eeprom = self.cloud_manager.get_andor_eeprom(device.settings.eeprom.detector_serial_number)
            if andor_eeprom == {}:
                log.error(f"got empty dict for Andor eeprom. Serial number incorrect or no entry in dynamo table.")
            else:
                log.debug(f"andor_eeprom = {andor_eeprom}")

                def default_missing(local_name, empty_value=None, cloud_name=None):
                    if cloud_name is None:
                        cloud_name = local_name
                    current_value = getattr(device.settings.eeprom, local_name) 
                    if current_value != empty_value:
                        log.debug(f"keeping non-default {local_name} {current_value}")
                    else:
                        if cloud_name in andor_eeprom:
                            cloud_value = andor_eeprom[cloud_name]
                            log.info(f"using cloud-recommended default of {local_name} {cloud_value}")
                            setattr(device.settings.eeprom, local_name, cloud_value)

                default_missing("excitation_nm_float", 0)
                default_missing("wavelength_coeffs",  [0, 1, 0, 0])
                default_missing("model", None, "wp_model")
                default_missing("detector", "iDus")
                default_missing("serial_number", device.settings.eeprom.detector_serial_number, "wp_serial_number")

                device.change_setting("save_config", device.settings.eeprom)

            sfu.label_detector_serial.setText(device.settings.eeprom.detector_serial_number)
        else:
            sfu.label_detector_serial.setText("")

        ########################################################################
        # update Multispec
        ########################################################################

        device_id = device.device_id

        log.info("initialize_new_device: device_id %s", device_id)

        # infer if this is a "hotplug" situation
        if self.multispec.is_connected(device_id): #or self.multispec.is_in_reset(device_id):
            log.debug("initialize_new_device: re-selecting already-connected device")
            hotplug = False
            if self.multispec.is_in_reset(device_id):
                log.debug(f"readding reset device")
                self.multispec.readd_spec_object(device_id)
        else:
            log.debug("initialize_new_device: initializing newly-connected device")
            self.multispec.add(device)
            hotplug = True

        spec = self.current_spectrometer()
        spec.app_state.spec_timeout_prompt_shown = False
        if spec is None:
            log.critical("impossible: current_spectrometer is none, just added spectrometer?")
            return

        self.multispec.update_hide_others()
        self.multispec.update_color()

        if device.is_andor:
            self.update_wavecal()

        ########################################################################
        # announce connection
        ########################################################################

        if hotplug:
            self.marquee.info("Connected to %s (%s)" % (
                    spec.settings.eeprom.serial_number, 
                    spec.settings.full_model()), 
                immediate=True, 
                extra_ms=2000)

        self.gui.update_window_title(spec)

        ########################################################################
        # backup eeprom
        ########################################################################

        if hotplug:
            self.eeprom_writer.backup()

        ########################################################################
        # display firmware
        ########################################################################

        sfu.label_microcontroller_firmware_version.setText(spec.settings.microcontroller_firmware_version)
        sfu.label_fpga_firmware_version.setText(spec.settings.fpga_firmware_version)

        ########################################################################
        # update EEPROM Editor
        ########################################################################

        # start by applying the settings we received from the spectrometer 
        self.eeprom_editor.update_from_spec()

        ########################################################################
        # update integration time & gain
        ########################################################################
        
        # Use the EEPROM's startup value as our "default" integration time and
        # gainDB; we do this BEFORE loading the .ini file so the .ini file can
        # override.  Note that other objects' init_hotplug events are further
        # down this function
        if hotplug:
            for obj in [ self.integration_time_feature,
                         self.gain_db_feature ]:
                obj.init_hotplug()

        ########################################################################
        # default TEC setpoint based on detector
        ########################################################################

        # Note this may be different than eeprom.startup_tec_setpoint. This may
        # be an ENLIGHTEN requirement which differs from Wasatch.PY requirement.

        if hotplug:
            self.detector_temperature.init_hotplug()
        self.detector_temperature.update_visibility()

        ########################################################################
        # Now override the EEPROM and Detector defaults with the .INI file
        ########################################################################

        # override settings (including many EEPROM values) from .ini file
        if hotplug:
            self.set_from_ini_file()

        ########################################################################
        # Configure GUI based on device features (AFTER .ini file...)
        ########################################################################

        log.debug("Configure GUI based on device features")

        # high-gain mode for InGaAs detectors
        self.high_gain_mode.update()

        # disable laser power control if not applicable
        sfu.frame_lightSourceControl.setVisible(spec.settings.eeprom.has_laser)

        ########################################################################
        # integration time and Gain
        ########################################################################

        log.debug("configure integration time limits")
        self.integration_time_feature.reset(hotplug)
        self.gain_db_feature.reset(hotplug)

        ########################################################################
        # send miscellaneous settings downstream
        ########################################################################

        log.debug("configure miscellaneous")

        # degC-to-DAC coeffs (to support .ini overrides)
        if hotplug:
            spec.change_device_setting("degC_to_dac_coeffs", spec.settings.eeprom.degC_to_dac_coeffs)

        # gain and offset...why does this need to be done?  Wasn't it already
        # done by the earlier call to self.eeprom_editor.update_from_spec?
        # Perhaps we're just making sure?
        self.update_gain_and_offset()

        # scan averaging
        self.scan_averaging.initialize()

        # tell all drivers to adjust their timeouts accordingly
        self.multispec.change_device_setting("num_connected_devices", self.multispec.count(), all=True)

        ########################################################################
        # finish initializing the GUI
        ########################################################################

        # re-hide hidden curves
        self.rehide_curves()

        # weight new curve
        self.multispec.check_callback()

        # update all curves
        self.graph.rescale_curves()

        if hotplug:
            if spec.settings.eeprom.has_laser:
                self.laser_temperature.add_spec_curve(spec)
            if spec.settings.eeprom.has_cooling:
                self.detector_temperature.add_spec_curve(spec)
            # This plots on the live graph on the hardware capture page
            # This graph is held by the area scan object and is a 1D spectra
            # Not the scan waterfall that is a 2D layout
            self.area_scan.add_spec_curve(spec)

        # scope capture buttons
        if hotplug:
            spec.app_state.paused = False

        # update x-axis options as appropriate for connected spectrometers
        # ...what does this do, if we have a WP-785 and WP-VIS connected, and we switch to wavenumbers?
        self.graph.enable_wavenumbers(self.multispec.any_has_excitation())

        # reference and dark (handles SaveOptions as well)
        for feature in [ self.dark_feature, self.reference_feature ]:
            feature.clear(quiet=True) if hotplug else feature.display()


        ########################################################################
        # Business Objects
        ########################################################################

        # Activate business objects which have connection / selection events

        if hotplug:
            # cursor
            self.cursor.center()
            for feature in [ self.accessory_control,
                             self.laser_control ]:
                feature.init_hotplug()

        for feature in [ self.accessory_control,
                         self.advanced_options,
                         self.area_scan,
                         self.boxcar,
                         self.dark_feature,
                         self.external_trigger,
                         self.gain_db_feature,
                         self.graph,
                         self.laser_control,
                        #self.multi_pos,
                         self.raman_shift_correction,
                         self.raman_intensity_correction,
                         self.raman_mode_feature,
                         self.reference_feature,
                         self.richardson_lucy,
                         self.status_indicators,
                         self.vcr_controls ]:
            feature.update_visibility()

        ########################################################################
        # Batch Collection should kick-off on the FIRST connected spectrometer
        ########################################################################

        if self.batch_collection.start_on_connect:
            log.info("Starting Batch Collection on connect")
            self.vcr_controls.pause()
            self.batch_collection.start_collection()
        else:
            log.info("not starting Batch Collection on connect")

        ########################################################################
        # done
        ########################################################################

        # we've connected to at least one spectrometer, so set logging to 
        # whatever the user selected (we default at DEBUG until connection)
        logging.getLogger().setLevel(self.logging_feature.level)
        log.info(f"successfully %s {spec.label}", "initialized" if hotplug else "selected")

        # updates from initialization to match time window in spinbox
        # call StripChartFeature getter
        spec.app_state.reset_temperature_data(time_window=sfu.spinBox_strip_window.value(), hotplug=hotplug)

    def rehide_curves(self):
        """
        Adding/removing a trace to a graph apparently makes all curves visible,
        so call this method to allow business objects to re-hide any curves
        (or other widgets) based on internal business object state.
        
        @todo move to Graph and allow other business objects to register as observers
        @todo Probably need to integrate PluginController into this too.
        """
        for feature in [ self.baseline_correction,
                         self.raman_shift_correction ]:
            feature.update_visibility()

    # ##########################################################################
    # More GUI Setup
    # ##########################################################################

    def setup_log_interface(self):
        """ @todo move to LoggingFeature """
        try:
            offset_file = applog.get_location() + ".offset"
            if os.path.exists(offset_file):
                os.remove(offset_file)
        except:
            log.info("error removing old Pygtail offset", exc_info=1)

        # MZ: it seems like this happens all the time, even if we're not
        #     viewing the log? Seems wasteful...but needed to flash the
        #     indicator colors.
        self.log_reader_timer = QtCore.QTimer()
        self.log_reader_timer.setSingleShot(True)
        #self.log_reader_timer.timeout.connect(self.tick_log_reader)
        self.log_reader_timer.start(Controller.LOG_READER_TIMER_SLEEP_MS)

    # ##########################################################################
    # Logging
    # ##########################################################################

    def tick_log_reader(self):
        """
        Periodically tail the logfile to the QTextEdit in Hardware -> Setup -> Logging.
        
        @todo move to LoggingFeature
        """
        if self.area_scan.enabled:
            return

        if self.shutting_down:
            self.log_reader_timer.stop()
            return

        sfu = self.form.ui
        if not sfu.checkBox_logging_pause.isChecked():
            try:
                sfu.textEdit_log.clear()

                # is there a less memory-intensive way to do this?
                # maybe implement ring-buffer inside the loop...
                lines = []
                for line in Pygtail(applog.get_location()):
                    lines.append(line)

                if len(lines) > 150:
                    lines = lines[-150:]
                    lines.insert(0, "...snip...")

                for line in lines:
                    line = re.sub(r"[\r\n]", "", line)
                    line = self.colorize_log(line)
                    sfu.textEdit_log.append(line)
            except IOError as exc:
                log.info("Cannot tail log file")

            sfu.textEdit_log.moveCursor(QtGui.QTextCursor.End)

        self.log_reader_timer.start(Controller.LOG_READER_TIMER_SLEEP_MS)

    def colorize_log(self, line):
        """
        This gets ticked by tick_log_reader.
        
        @todo move to LoggingFeature
        """
        if " CRITICAL " in line:
            color = "980000" # red
        elif " ERROR " in line:
            color = "ba8023" # orange
        elif " WARNING " in line:
            color = "cac401" # yellow
        else:
            color = None

        if color:
            self.status_indicators.raise_hardware_error()
            return "<p><span style='color: #%s'>%s</span></p>" % (color, line)
        else:
            return "<p>" + line + "</p>"

    # ##########################################################################
    # Setup (populate widget placeholders)
    # ##########################################################################

    def populate_thumbnail_column(self):
        """
        Create the required widget and layout configuration for adding newly
        saved entries from the scope capture interface.
        
        This generates a HIDDEN graph (it'll be "underneath" the displayed
        stackedWidget of saved spectra), which is nonetheless actively used when
        generating thumbnails of new traces.
        
        This could probably be moved into MeasurementFactory, the sole user of
        these widgets.
        """
        sfu = self.form.ui

        log.debug("Placeholder scope capture save")

        # This layout isn't used anywhere else.  In fact, it's not even visible
        # in the Designer Object Inspector, although you can see it in the .ui.
        # It seems to be under page_scope_capture_save_design though.
        layout = sfu.verticalLayout_scope_capture_save_design

        # this is a fake graph (chart)
        self.thumbnail_render_graph = pyqtgraph.PlotWidget(name="Measurement Thumbnail Renderer")

        # this is a fake curve (trace) on the chart
        data = list(range(1024, 1638)) # MZ: ???
        self.thumbnail_render_curve = self.thumbnail_render_graph.plot(
            data,
            pen=self.gui.make_pen(widget="thumbnail"),
            name="Thumbnail Renderer")

        # make the graph small, and hide both axes
        self.thumbnail_render_graph.hideAxis("left")
        self.thumbnail_render_graph.hideAxis("bottom")
        self.thumbnail_render_graph.setMinimumHeight(120)
        self.thumbnail_render_graph.setMaximumHeight(120)
        self.thumbnail_render_graph.setMinimumWidth(170)
        self.thumbnail_render_graph.setMaximumWidth(170)

        # insert the graph into the layout
        layout.insertWidget(0, self.thumbnail_render_graph)

        # This hides page_scope_capture_save_design (which holds the above pre-
        # render widgets) beneath page_scope_capture_save (where the visible
        # rendered ThumbnailWidgets will be shown).  In other words, you'll never
        # see any of the above bits on the runtime GUI, as the following line
        # hides them.
        sfu.stackedWidget_scope_capture_save.setCurrentIndex(1)

    # ##########################################################################
    # GUI setup (bindings)
    # ##########################################################################

    def bind_gui_signals(self):
        sfu = self.form.ui

        ########################################################################
        # appropriate for Controller
        ########################################################################

        self.form.exit_signal                       .exit               .connect(self.close)

        sfu.pushButton_help                         .clicked            .connect(self.help_callback)

        ## move to StripChartFeature
        sfu.spinBox_strip_window                    .valueChanged       .connect(self.update_hardware_window)
        
        # OEM tab
        sfu.checkBox_swap_alternating_pixels        .stateChanged       .connect(self.swap_alternating_pixels_callback)
        sfu.checkBox_graph_alternating_pixels       .stateChanged       .connect(self.graph_alternating_pixels_callback)

    def bind_shortcuts(self):
        """ Set up application-wide shortcut keys (called AFTER business object creation). """
        log.debug("Set up shortcuts")

        self.shortcuts = {}

        def make_shortcut(kseq, callback):
            shortcut = QtWidgets.QShortcut(QtGui.QKeySequence(kseq), self.form)
            shortcut.activated.connect(callback)
            self.shortcuts[kseq] = shortcut

        # techniques
        make_shortcut("F1",     self.page_nav.set_technique_hardware)
        make_shortcut("F2",     self.page_nav.set_technique_scope)
        make_shortcut("F3",     self.page_nav.set_technique_raman)
        make_shortcut("F4",     self.page_nav.set_technique_transmission)
        make_shortcut("F5",     self.page_nav.set_technique_absorbance)

        # operation modes
        make_shortcut("F6",     self.page_nav.set_operation_mode_setup)
        make_shortcut("Ctrl+1", self.page_nav.set_operation_mode_setup)

        make_shortcut("F7",     self.page_nav.set_operation_mode_capture)
        make_shortcut("Ctrl+2", self.page_nav.set_operation_mode_capture)

        # Dark/Reference
        make_shortcut("F8",     self.dark_feature.toggle)
        make_shortcut("Ctrl+D", self.dark_feature.toggle)

        make_shortcut("F9",     self.reference_feature.toggle)
        make_shortcut("Ctrl+R", self.reference_feature.toggle)

        # Play/Pause/Save
        make_shortcut("F10",    self.vcr_controls.play)
        make_shortcut("F11",    self.vcr_controls.pause)

        make_shortcut("F12",    self.vcr_controls.save)
        make_shortcut("Ctrl+S", self.vcr_controls.save)

        # Convenience
        make_shortcut("Ctrl+A", self.authentication.login) # authenticate, advanced
        make_shortcut("Ctrl+C", self.graph.copy_to_clipboard_callback)
        make_shortcut("Ctrl+H", self.page_nav.toggle_hardware_and_scope)
        make_shortcut("Ctrl+L", self.laser_control.toggle_laser)
        make_shortcut("Ctrl+P", self.vcr_controls.toggle) # pause/play

        # Cursor
        make_shortcut(QtGui.QKeySequence.MoveToPreviousWord, self.cursor.dn_callback) # ctrl-left
        make_shortcut(QtGui.QKeySequence.MoveToNextWord,     self.cursor.up_callback) # ctrl-right

    # ##########################################################################
    # GUI utility methods
    # ##########################################################################

    def help_callback(self):
        url = Controller.URL_HELP
        log.debug(f"opening {url}")
        webbrowser.open(url)

    # ##########################################################################
    # save spectra
    # ##########################################################################

    def save_current_spectra(self):
        """
        This is a GUI method (used as a callback) to generate one Measurement from
        the most-recent ProcessedReading of EACH connected spectrometer.
        
        Originally there was no thought of Measurements "knowing" what technique
        was in use when they were created.  However, we (currently) only want the
        ID button to show up on Raman measurements, so...let's see where this goes.
        """
        technique = self.page_nav.get_current_technique()

        if self.save_options.save_all_spectrometers():
            for spec in self.multispec.get_spectrometers():
                self.measurements.create_from_spectrometer(spec=spec, technique=technique)
        else:
            self.measurements.create_from_spectrometer(spec=self.current_spectrometer(), technique=technique)

    # ##########################################################################
    # miscellaneous callbacks
    # ##########################################################################

    def update_gain_and_offset(self, force=False):
        """
        @param force: There was a time when production FID spectrometers were 
                      not being assigned gain and offset values in their 
                      EEPROMs.  Therefore EEPROM values were considered 
                      suspicious (offset in particular was unreliable).  So we
                      don't want to just push possibly-invalid EEPROM defaults
                      downstream.  However, we do want to allow explicit changes
                      via the EEPROMEditor and .ini files to be pushed down.  So
                      the EEPROMEditor sends the "force" parameter.
        """
        sfu = self.form.ui
        spec = self.current_spectrometer()
        if spec is None:
            return

        # sync whatever the GUI shows (in EEPROMEditor) to the EEPROM object
        #
        # (Why does this need to be done?  Isn't the EEPROMEditor initialized
        # FROM the EEPROM object, and any changes to the EEPROMEditor fields
        # updated to the EEPROM object as a matter of course.)
        ee = self.settings().eeprom
        ee.detector_gain       = sfu.doubleSpinBox_ee_detector_gain      .value()
        ee.detector_gain_odd   = sfu.doubleSpinBox_ee_detector_gain_odd  .value()
        ee.detector_offset     = sfu.      spinBox_ee_detector_offset    .value()
        ee.detector_offset_odd = sfu.      spinBox_ee_detector_offset_odd.value()

        if force:
            # send the new values to the FPGA via opcodes
            spec.change_device_setting("detector_gain",       ee.detector_gain)
            spec.change_device_setting("detector_gain_odd",   ee.detector_gain_odd)
            spec.change_device_setting("detector_offset",     ee.detector_offset)
            spec.change_device_setting("detector_offset_odd", ee.detector_offset_odd)

    def swap_alternating_pixels_callback(self):
        """ Doesn't seem any point in tracking state on this? """
        sfu = self.form.ui
        spec = self.current_spectrometer()
        if spec is None:
            return

        enabled = sfu.checkBox_swap_alternating_pixels.isChecked()
        spec.change_device_setting("swap_alternating_pixels", enabled)

    def graph_alternating_pixels_callback(self):
        sfu = self.form.ui
        spec = self.current_spectrometer()
        if spec is None:
            return

        enabled = sfu.checkBox_graph_alternating_pixels.isChecked()

        self.settings().state.graph_alternating_pixels = enabled
        spec.change_device_setting("graph_alternating_pixels", enabled)

    # ##########################################################################
    # Event Loops
    # ##########################################################################

    def setup_main_event_loops(self):
        """ Create and start the timer to tick our event loop. """
        log.debug("Setup main event loops")

        # @todo eventually move to AcquisitionFeature?
        self.acquisition_timer = QtCore.QTimer()
        self.acquisition_timer.setSingleShot(True)
        self.acquisition_timer.timeout.connect(self.tick_acquisition)

        # @todo eventually move to StatusFeature?
        self.status_timer = QtCore.QTimer()
        self.status_timer.setSingleShot(True)
        self.status_timer.timeout.connect(self.tick_status)

        # don't attempt the FIRST ticks for 1 second
        self.acquisition_timer     .start(1000)
        self.status_timer          .start(1000)
        self.status_indicators     .start(1000)

    def tick_acquisition(self):
        """
        This polls every spectrometer's worker thread at 10Hz (or less) to 
        receive the latest Reading from their Queue.
        
        To be clear, that means that ENLIGHTEN cannot read more than 10 spectra 
        per second from a spectrometer, even though Wasatch spectrometers have 
        "scan rates" many times that.
        
        This is because ENLIGHTEN was designed as a real-time data VIEWING 
        program, not a real-time DATA ANALYSIS or COLLECTION program.  For data 
        analysis, in which you are generating statistics on every spectra 
        generated by the spectrometer, you would need to run at a faster rate.  
        In this case, all we're trying to do is graph "the latest" spectrum from
        the spectrometer, and for that 10Hz seems fine.
        
        Note that when multiple spectrometers are connected, we actually poll a 
        little slower.
        
        Also note that we're still not really polling at 10Hz...we're starting 
        each new polling cycle 100ms after the last one finished, and it's 
        possible that some cycles (especially if using blocking plugins) may take
        many milliseconds to complete.
        """
        if self.shutting_down:
            return

        # poll all spectrometer threads for SPECTRA
        for spec in self.multispec.get_spectrometers():
            if not spec.app_state.hidden:
                self.attempt_reading(spec)

        if not self.shutting_down:
            self.acquisition_timer.start(self.ACQUISITION_TIMER_SLEEP_MS + (50 * (self.multispec.count() - 1)))

    def tick_status(self):
        if self.area_scan.enabled:
            return

        if self.shutting_down:
            return

        ########################################################################       
        # confirm we have no runaway resources
        ########################################################################       

        if not self.resource_monitor.copacetic():
            log.critical("tick_status: Resource Monitor indicated need to shutdown")
            self.exit_code = self.resource_monitor.exit_code
            self.form.prompt_on_exit = False
            self.form.close()
            return

        ########################################################################       
        # poll all spectrometer threads for STATUS
        ########################################################################       

        for spec in self.multispec.get_spectrometers():

            # send a heartbeat to keep the child thread alive
            # (not sure this is still useful)
            spec.change_device_setting("heartbeat")

            # look for any inbound status messages from the subprocess
            while True:
                try:
                    if spec.device is None:
                        break

                    msg = spec.device.acquire_status_message()
                    if msg is None:
                        break
                    self.process_status_message(msg)
                except:
                    log.debug("Error reading or processing StatusMessage on %s", spec.device_id, exc_info=1)

        ########################################################################       
        # Tick plug-ins
        ########################################################################       

        # note that we could probably do this more efficiently in an event-based
        # manner using QSignals from PluginWorker
        self.plugin_controller.process_responses()

        # We're going to tick KnowItAll from here, because we want queued
        # Measurements (from ThumbnailWidget button clicks) to process even
        # when spectra is paused, or theoretically even no spectrometers are
        # connected.
        #
        # Note that this in turn calls update_visibility, so there is no separate
        # external call to update visibility on hotplug or spectrometer selection
        # events.
        self.kia_feature.update()

        if not self.shutting_down:
            self.status_timer.start(self.STATUS_TIMER_SLEEP_MS)

    # ##########################################################################
    #                                                                          #
    #                              Acquisition                                 #
    #                                                                          #
    # ##########################################################################

    def attempt_reading(self, spec) -> None:
        """
        Attempt to acquire a reading from the subprocess response queue,
        process and render data in the GUI.
        """
        sfu = self.form.ui
        if spec is None:
            return

        device_id = spec.device_id

        # check for a full reading (spectrum + temperature and other metadata)
        acquired_reading = self.acquire_reading(spec)

        if acquired_reading is not None and acquired_reading.disconnect:
            log.critical("Read poison pill from WasatchDeviceWrapper -- disconnect requested")
            self.disconnect_device(spec)
            return

        # we collected the reading (to clear the queue), but don't do anything with it
        if spec.app_state.paused and not self.batch_collection.running:
            return

        if acquired_reading is None or acquired_reading.reading is None:
            log.debug("attempt_reading(%s): no reading available", device_id)
            if self.vcr_controls.paused or self.batch_collection.running or not spec.is_acquisition_timeout():
                return

            if self.external_trigger.is_enabled():
                log.debug("attempt_reading(%s): ignoring timeout while externally triggered");
                return

            if spec.settings.state.area_scan_enabled:
                log.debug("attempt_reading(%s): ignoring timeout in area scan");
                return

            now = datetime.datetime.now()
            if spec.settings.state.ignore_timeouts_until is not None and \
                    spec.settings.state.ignore_timeouts_until > now:
                log.debug("attempt_reading(%s): temporarily ignoring timeouts");
                return
            spec.settings.state.ignore_timeouts_until = None

            # apparently we've missed our projected acquisition interval
            spec.app_state.missed_reading_count += 1

            # this doesn't have to be done after each keepalive...we could do this at 1Hz or so
            if spec.app_state.missed_reading_count > self.MAX_MISSED_READINGS and \
                    not spec.app_state.spec_timeout_prompt_shown and \
                    not self.multispec.is_in_reset(spec.device.device_id):
                log.info("displaying Timeout Warning MessageBox (stay connected, or disconnect)")
                spec.app_state.spec_timeout_prompt_shown = True
                dlg = QMessageBox(self.form)
                dlg.setWindowTitle("Timeout Warning")
                dlg.setText("Spectrometer acquisition has timed out. Would you like to stay connected to try to fix the issue?")
                dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                dlg.setIcon(QMessageBox.Question)
                button = dlg.exec_()

                if button == QMessageBox.No:
                    log.info("user opted to disconnect following timeout")
                    log.error("spectrometer acquisition timed-out...disconnecting")
                    self.disconnect_device(spec)
                else:
                    log.info("user opted to stay connected in spite of timeout")
                    log.error("spectrometer acquisition timed-out...user indicated persist")

            return

        reading = acquired_reading.reading
        self.multispec.spec_most_recent_reads[spec] = reading
        if reading.failure is not None:
            # WasatchDeviceWrapper currently turns these into upstream poison-pills,
            # so this is not expected
            log.critical("Hardware ERROR on device_id %s: %s", device_id, reading.failure)
            return

        if reading.spectrum is None:
            # this should not happen
            log.critical("null spectrum device_id %s", device_id)
            return

        ########################################################################
        # apparently it was a valid reading
        ########################################################################

        spec.app_state.reading_count += 1
        spec.app_state.missed_reading_count = 0
        spec.app_state.spec_timeout_prompt_shown = False

        if spec.device.is_ble and acquired_reading.progress != 1:
            self.form.ui.readingProgressBar.setValue(acquired_reading.progress*100)
            # got an incomplete ble reading so stop proceeding for now
            return
        elif spec.device.is_ble:
            self.form.ui.readingProgressBar.setValue(100)

        # @todo need to update DetectorRegions so this will pass (use total_pixels)

        pixels = len(reading.spectrum)
        if pixels != spec.settings.pixels():
            self.marquee.info(f"{device_id} provided incorrect spectra length of {pixels}. Expected {spec.settings.pixels()}")
            log.error("attempt_reading(%s): ignoring malformed spectrum of %d pixels (expected %d)",
                device_id, pixels, spec.settings.pixels())
            reading = None
            return

        log.debug("attempt_reading(%s): update spectrum data: %s and length (%s)", device_id, str(reading.spectrum[0:5]), str(len(reading.spectrum)))

        # When using BatchCollection's Spectrum LaserMode, the driver may attach
        # an averaged dark to the Reading.
        if reading.dark is not None:
            log.debug("attempt_reading: setting dark from Reading: %s", reading.dark)
            self.dark_feature.store(dark=reading.dark)

        # Scope Capture
        self.update_scope_graphs(reading)

        # Area Scan
        self.area_scan.process_reading(reading)

        # active spectrometer gets additional processing
        if self.multispec.is_selected(device_id):

            # display raw temperatures on Hardware Setup page
            # if reading.secondary_adc_raw is not None:
            #     text = "0x%03x" % reading.secondary_adc_raw
            #     if reading.secondary_adc_calibrated is not None:
            #         text += " (%.2f)" % reading.secondary_adc_calibrated
            #     sfu.label_secondary_adc_raw.setText(text)

            # @todo move to AmbientTemperatureFeature
            # display ambient temperature on Hardware Setup
            if spec.settings.is_gen15() and reading.ambient_temperature_degC is not None:
                sfu.label_ambient_temperature.setText("%.2f°C" % reading.ambient_temperature_degC)
            else:
                sfu.label_ambient_temperature.setText("unknown")

            # update laser status
            # self.update_laser_status(reading)

    def update_laser_status(self, reading):
        spec = self.multispec.current_spectrometer()
        if spec is None:
            return

        if reading is None or reading.laser_enabled is None:
            return

        if reading.laser_enabled == spec.settings.state.laser_enabled:
            return

        # apparently the GUI laser status is inaccurate, so debounce and correct
        if self.last_laser_toggle is not None:
            debounce_ms = 100 + spec.settings.state.integration_time_ms * 2
            elapsed_ms = (datetime.datetime.now() - self.last_laser_toggle).total_seconds() * 1000.0
            if (elapsed_ms > debounce_ms):
                log.debug("toggling laser because reading.laser_enabled %s but state.laser_enabled %s (and elapsed_ms %d > debounce_ms %d)",
                    reading.laser_enabled, spec.settings.state.laser_enabled, elapsed_ms, debounce_ms)
                self.toggle_laser()

    def acquire_reading(self, spec: Spectrometer) -> AcquiredReading:
        """
        Poll the spectrometer thread (WasatchDeviceWrapper) for a 
        SpectrometerResponse.
        
        @see wasatch.WasatchDeviceWrapper.acquire_data
        @see wasatch.WasatchDevice.acquire_data
        
        @todo eventually move to AcquisitionFeature

        @returns one of three things: 
                 1. AcquiredReading(reading=Reading) with an actual Reading 
                    (could still contain an error etc), or 
                 2. AcquiredReading(disconnect=True) if it all went sidewides, or
                 3. None if it's neither good nor bad and no action should be 
                    taken (keepalive etc)
        """

        device = spec.device
        if spec is None or device is None:
            # silently ignore...this should be rare, and likely indicates a delay
            # during initial connection or tear-down
            log.error("acquiring reading from missing device?")
            return 

        device_id = spec.device_id

        try:
            spectrometer_response = device.acquire_data()
            if spectrometer_response.poison_pill:
                log.error(f"acquire_reading: received poison-pill from spectrometer: {spectrometer_response}") # disposition AFTER displaying user message

            if spectrometer_response.poison_pill or \
                    (spectrometer_response.error_msg != "" and spectrometer_response.error_lvl != ErrorLevel.ok) \
                    and spectrometer_response.keep_alive is not True:
                # We received an error from the device.  Don't do anything about it immediately;
                # don't disconnect for instance.  It may or may not be a poison-pill...we're not
                # even checking yet, because we want to let the user decide what to do.
                log.debug("acquire_reading: prompting user to disposition error")
                log.debug(f"response from spec was {spectrometer_response}")

                self.seen_errors[spec][spectrometer_response.error_msg] += 1
                error_count = self.seen_errors[spec][spectrometer_response.error_msg]
                if error_count <= self.SPEC_ERROR_MAX_RETRY and not spectrometer_response.poison_pill:
                    # retry reading a few times before calling a reset
                    log.debug(f"temporarily ignoring brief glitch (seen_errors {error_count} <= {self.SPEC_ERROR_MAX_RETRY}")
                    return

                stay_connected = self.display_response_error(spec, spectrometer_response.error_msg)
                log.debug(f"dialog disposition: stay_connected {stay_connected}")

               #tries = self.multispec.reset_tries(device_id)
                tries = device.reset_tries
                if stay_connected:
                    log.debug("acquire_reading: either the user said this was okay, or they're still thinking about it")
                elif tries > self.SPEC_RESET_MAX_RETRY:
                    # the user said to shut things down
                    log.debug(f"reset tries is {tries}") 
                    log.error("acquire_reading: user said to disconnect or hit max resets so give up")
                    self.multispec.set_gave_up(device_id)
                    return AcquiredReading(disconnect=True)
                else:
                    self.marquee.info(f"{device_id} had errors. Attempting reset to recover, try number {tries}", immediate=True, persist=True)
                    self.seen_errors[spec][spectrometer_response.error_msg] = 0
                    device.reset()
                    self.disconnect_device(spec)
                   #log.debug(f"adding spec model and serial to be reset on connect")
                    self.bus.update(poll=True)
                    return

            if spectrometer_response.poison_pill:
                # the user hasn't [yet] decided to disconnect, but we can't really "do anything" with data that's
                # coming from a spectrometer throwing poison-pills, so for now treat it as a keepalive
                log.debug(f"received poison-pill from spectrometer, but the user has not [yet] opted to disconnect")
                return 

            if spectrometer_response.keep_alive:
                return 

            if spectrometer_response.data is None:
                # we got a None...treat as keepalive
                return

            if type(spectrometer_response.data) is Reading:
                reading = spectrometer_response.data

                # did the Reading have a failure flag set?
                if reading.failure is not None:
                    # Apparently there was an error in the thread worker.
                    # However, the device didn't send a poison-pill, so
                    # just log this and wait for further updates.
                    log.critical("acquire_reading(%s): failure in reading: %s", str(device_id), str(reading.failure))
                    return 

                # apparently it was a GOOD reading!
                spec.reset_acquisition_timeout()
                return AcquiredReading(reading=reading, progress=spectrometer_response.progress)

            else:
                log.error(f"received a SpectrometerResponse where data is {type(spectrometer_response.data)}")
                return 

        except Exception as exc:
            # we didn't receive notification of an error which occurred downstream
            # in the thread, we actually had a problem communicating with the
            # thread "full stop."  The thread is hosed, so cut it loose.
            log.critical("acquire_reading(%s): problem acquiring from connected device", str(device_id), exc_info=1)
            return AcquiredReading(disconnect=True)

        # I don't see how you'd get here.  Call it a poison-pill and log it.
        log.critical("acquire_reading(%s): how did we get here?!", str(device_id))
        return AcquiredReading(disconnect=True)

    def process_status_message(self, msg):
        """
        Used to handle StatusMessage objects received from spectrometer
        subprocesses (as opposed to the Readings we normally receive).
        
        These are not common in the current architecture.  These were used
        initially to provide progress updates to the GUI when loading long series
        of I2C overrides to the IMX before firmware encapsulated sensor control.
        
        @param msg - presumably a StatusMessage from a spectrometer process
        """
        sfu = self.form.ui

        if msg is None:
            return

        log.debug("should process message: %s", msg)
        if not isinstance(msg, StatusMessage):
            log.error("received invalid StatusMessage", exc_info=1)
            return

        elif msg.setting == "marquee_info":
            self.marquee.toast(msg.value)

        elif msg.setting == "marquee_error":
            self.marquee.toast(msg.value) # could add error window type

        elif msg.setting == "detector_regions":
            settings = self.settings()
            if settings is not None:
                log.debug(f"applying DetectorRegions from StatusMessage: {msg.value}")
                settings.state.detector_regions = msg.value

        else:
            log.debug("unsupported StatusMessage: %s", msg.setting)

    # ##########################################################################
    #                                                                          #
    #                            Reading Processing                            #
    #                                                                          #
    # ##########################################################################

    def get_last_reading(self):
        return self.app_state().processed_reading.reading

    def refresh_scope_graphs(self):
        self.update_scope_graphs()

    # called by attempt_reading
    def update_scope_graphs(self, reading=None):
        sfu = self.form.ui
        app_state = self.app_state()

        # log.debug("update_scope_graphs: reading %d", reading.session_count)

        # if we weren't handed a fresh reading, just re-process the last one
        if reading is None and app_state.processed_reading.reading:
            log.debug("update_scope_graphs: re-processing last reading")
            reading = app_state.processed_reading.reading

        if reading is None or reading.spectrum is None:
            return

        device_id = reading.device_id
        spec = self.multispec.get_spectrometer(device_id)
        if spec is None:
            log.error("updating scope from unknown spectrometer %s", device_id)
            return
        selected = self.multispec.is_selected(device_id)

        self.scan_averaging.update_label(spec, reading.sum_count)
        self.process_reading(reading, spec=spec)

        self.cursor.update()

    def reprocess(self, measurement):
        """
        Called by Measurements.create_from_file if save_options.load_raw.  This
        takes the loaded raw, dark and reference, and re-feeds them back through
        process_reading, along with the loaded Settings object containing wavecal,
        pixel count etc.  This will display the re-processed spectrum on screen,
        then return the new ProcessedReading object.  We pass that back to the
        caller, who will update the new ProcessedReading into the originally
        loaded Measurement, update the measurement_id / timestamps, generate the
        thumbnail and re-save.
        
        @param measurement (Input) Measurement
        @returns new ProcessedReading
        """
        log.debug("reprocessing")
        pr = measurement.processed_reading
        if pr.raw is None:
            log.error("can't reprocess missing raw")
            return
        settings = measurement.settings
        log.debug("reprocessing: settings.wavelength_coeffs: %s", str(settings.eeprom.wavelength_coeffs))
        log.debug("reprocessing: settings.wavelengths: %s", str(settings.wavelengths))

        # create a fake Reading and push it back through with temporary
        # app_state overrides
        reading = Reading()
        reading.spectrum = pr.raw

        return self.process_reading(
            reading  = reading,
            spec     = None,
            dark     = pr.dark,
            ref      = pr.reference,
            settings = settings)

    def process_reading(self, reading, spec=None, dark=None, ref=None, settings=None):
        """
        @todo split into "update graphs" and "post-processing"
        
        Requested order of operations, per Michael Matthews:
        
        - Remove excess data points (vertical or horizontal areas of interest)
        - Scan Averaging
          - snap usable dark
        - Subtract Dark
        - Correction for detector non-linearity* (when enabled)
        - Correct for stray light*  (when enabled)
        - Correct for intensity* (when enabled, per your suggested OoO)
        - Apply Boxcar Smoothing
        - Baseline removal / fluorescence removal, etc
        - Laser X-Axis shift
        - X-Axis Interpolation (when enabled)
        
        * Requires Dark Corrected Spectra
        
        @par Reprocessing loaded spectra
        
        If no Spectrometer is passed in, use the current one. Therefore,
        reprocessed spectra will use the SpectrometerState and SpectrometerApplicationState
        associated with the current Spectrometer.  However, we do try to re-use the
        SpectrometerSettings instantiated when we reloaded the measurement.
        
        Of particular note are dark and reference, which can be manually
        passed-in for reprocessed measurements if found in input file. Likewise, we
        pass in the loaded Settings object so that the x-axis can be generated from
        the correct wavecal, pixel count, as well as the correct vignetting ROI.
        
        Keywords to help people find this function:
        - update graphs
        - perform processing
        - post-process
        - apply business logic
        """
        sfu = self.form.ui

        if settings is None:
            # we are NOT reprocessing
            reprocessing = False
            if spec is not None:
                settings = spec.settings
            else:
                # is this a use-case?
                log.debug("process_reading: wasn't passed either settings or spec?")
                settings = self.settings()
        else:
            # we are reprocessing
            reprocessing = True

        app_state = None
        selected = False
        if spec is None:
            spec = self.multispec.current_spectrometer()
            settings = spec.settings
        if spec is not None:
            app_state = spec.app_state
            selected = self.multispec.is_selected(spec.device_id)

        # don't graph incomplete averages
        if self.scan_averaging.enabled(spec) and not reading.averaged:
            return

        # graph the raw spectrum in the Scope Setup "live" window if nothing else
        # MZ: I don't think that graph normally includes an x-axis, so no reason to generate it
        if selected:
            # x_axis = self.generate_x_axis(settings=settings)
            # self.set_curve_data(self.graph.live_curve, x=x_axis, y=reading.spectrum, label="process_reading[live]")
            self.set_curve_data(self.graph.live_curve, y=reading.spectrum, label="process_reading[live]")

        # todo: maybe make a ProcessedReadingFactory, which would automatically
        # associate the "at creation" x-axis and some of this other setup?
        #
        # Currently, this is where "recordable_dark" is snapped
        pr = ProcessedReading(reading)

        # saturation check
        if pr.processed.max() >= 0xfffe:
            # todo: self.status_indicators.detector_warning("detector saturated")
            self.marquee.error("detector saturated")

        # post-processing begins here

        ########################################################################
        # Dark Correction
        ########################################################################

        if app_state is not None:
            pr.correct_dark(spec.app_state.dark if dark is None else dark)

        ########################################################################
        # Vignetting
        ########################################################################

        # This should be done before any processing that involves multiple
        # pixels, e.g. offset, boxcar, baseline correction, or Richardson-Lucy.
        if self.roi_enabled:
            self.vignette_roi.process(pr, settings)

        ########################################################################
        # Reference
        ########################################################################

        # add reference to ProcessedReading whether or not we're actively in a
        # reference technique, so plugins etc can access it
        if app_state and app_state.reference is not None:
            pr.reference = np.copy(spec.app_state.reference)
        elif ref is not None:
            pr.reference = np.copy(ref)
        else:
            pr.reference = None

        if self.page_nav.using_reference():
            if self.page_nav.doing_transmission():
                self.transmission.process(pr, settings)
            elif self.page_nav.doing_absorbance():
                self.absorbance.process(pr, settings)

        ########################################################################
        # non-reference techniques
        ########################################################################

        if not self.page_nav.using_reference():

            ####################################################################
            # Raman intensity correction
            ####################################################################

            if self.page_nav.doing_raman():
                self.raman_intensity_correction.process(pr, spec)

            # Dieter goes back and forth on the order of these next two:

            # a potentially better approach might be:
            # - trim spectrum to useful range
            # - intensity correction using SRM on nominal wavenumber axis
            # - BASELINE CORRECTION
            # - DECONVOLUTION
            # - wavenumber axis calibration --WP-00413 report, p200

            # If we invert the order of operation, applying the intensity
            # correction first, then the DECONVOLUTION, and the BASELINE
            # CORRECTION last, we see a better performance, especially with the
            # alternate baseline method "ALS". --WP-00413 report, p217

            ####################################################################
            # baseline correction
            ####################################################################

            # Obviously baseline correction would benefit from ROI vignetting,
            # as would boxcar, Offset, Raman ID etc, so add a
            # "processed_vignetted" attribute for use downstream.
            self.baseline_correction.process(pr, spec)

            # on 2020-05-19 Deiter asked this to be moved before vignetting
            if not self.page_nav.using_reference():
                self.richardson_lucy.process(pr, spec)

        if self.form.ui.checkBox_despike_enable.isChecked():
            pr = self.despiking_feature.process(pr)

        ########################################################################
        # Boxcar Smoothing
        ########################################################################

        # Do this last, so it doesn't screw anything else up.
        self.boxcar.process(pr, spec)

        ########################################################################
        # Plugins
        ########################################################################

        # So if we want to let the plugin response add metadata to the processed
        # reading which can then be stored in any Measurements created from that
        # reading, then we kind of need to "block" here until the plugin is done.
        #
        # Also, if we want to let plugins to TRANSFORM live spectra (actually
        # affect ProcessedReading.processed), we kind of need that to happen 
        # here.
        if self.plugin_controller.enabled:
            self.plugin_controller.process_reading(pr, settings, spec)

        ########################################################################
        # Graph Post-Processed Spectrum
        ########################################################################

        if spec is None:
            # We're not responsible for graphing spectra which didn't come from a
            # live, connected spectrometer.  If we're reprocessing loaded spectra,
            # those loaded Measurements can land on the thumbnail bar, and the 
            # user can display traces themselves.  However, we do want to flow
            # the reprocessed spectra down into KIA, so keep going.
            log.debug("not graphing spectra which didn't come from a live spectrometer")
        else:
            graphed = False
            if pr.has_processed():

                # @todo needs updated to support DetectorRegions: multiple curves, 
                #       multiple wavecals...unsure how to handle interpolation.
                #
                #       Should we treat each DetectorROI as a separate "spectrometer"
                #       of sorts?  Probably not.  Should we send the pre-split 
                #       sub-spectra back as separate ROIs?  Not sure.  They really
                #       are "one reading"...for now, split the spectra into different
                #       graphs via plug-in chart?
                #
                #       Two questions: (1) what to do about ONE DetectorROI, and 
                #       (2) what to do about TWO+ DetectorROI.
                #
                #       1. Treat as starting with pixel 0.  Use configured full-detector
                #          wavecal, cropping wavelengths[] array using DetectorROI.x0/x1.
                #
                #       2. Each DetectorROI Will need EEPROM storage for:
                #          numRegions (1 byte)
                #          y0, y1, x0, x1 (8 bytes)
                #          wavecal C0-3 (16 bytes) 
                #          = 2 EEPROM pages (6, 7)?
                #
                if self.interp.enabled and not self.graph.in_pixels():
                    ipr = self.interp.interpolate_processed_reading(pr, settings=settings)
                    if ipr is not None:
                        if self.graph.in_wavelengths():
                            graphed = self.set_curve_data(spec.curve, x=ipr.wavelengths, y=ipr.processed_reading.get_processed(), label="process_reading[interp:nm]")
                        elif self.graph.in_wavenumbers():
                            graphed = self.set_curve_data(spec.curve, x=ipr.wavenumbers, y=ipr.processed_reading.get_processed(), label="process_reading[interp:cm]")
                        else:
                            log.error("process_reading: impossible graph axis: %s", self.graph.get_x_axis_unit())
                    else:
                        self.marquee.error("Interpolation error. Are your interp values right?")
                        log.error("process_reading: error generating interpolated graph curve")
                else:
                    cropped = pr.is_cropped()
                    log.debug(f"process_reading: graphing non-interpolated data (vignetted = {cropped})")
                    x_axis = self.generate_x_axis(settings=spec.settings, vignetted=cropped)
                    if x_axis is None:
                        # this can happen for instance if we have both Raman and
                        # non-Raman spectrometers connected, and we switch to
                        # wavenumber axis
                        log.error(f"process_reading: unable to generate x-axis of non-interpolated (vignetted = {cropped})?")
                    else:
                        # this is where most spectra is graphed
                        log.debug(f"process_reading: x_axis of {len(x_axis)} points (cropped {cropped}) is {x_axis[:3]} .. {x_axis[-3:]}") 
                        graphed = self.set_curve_data(spec.curve, x=x_axis, y=pr.get_processed(), label="process_reading[non-interp]")

            if not graphed:
                # This can happen in transmission or absorbance mode before a reference
                # is collected.  
                #
                # It can also happen if we have a mixture of Raman and non-Raman
                # units connected, and the user selected wavenumber axis.

                # clear the processed spectra (allow traces to remain); also, don't
                # "delete" the curve, just set it to empty data so we don't have to
                # recreate it later
                log.error("process_reading: failure in post-processing")
                self.set_curve_data(spec.curve, y=[], x=[], label="processing_reading[d]")

                # we probably should not go further; if this reading couldn't be
                # graphed, we don't want to use it for anything else
                return

        ########################################################################
        # KnowItAll
        ########################################################################

        if self.page_nav.doing_raman():
            log.debug("process_reading: sending KIA request (reprocessing = %s)", reprocessing)
            if pr.device_id == self.multispec.current_spectrometer().device_id:
                self.kia_feature.process(pr, settings)

        ########################################################################
        # Re-Processing complete
        ########################################################################

        # If we were re-processing a previously-loaded spectra, let's call it
        # quits here; the loaded spectrum may well have a different pixel count,
        # wavecal etc from the current spectrometer, so let's not associate them
        # more than we have to.
        if reprocessing:
            return pr

        # store our processed reading
        if app_state:
            app_state.processed_reading = pr

        # were we only taking one measurement?
        self.take_one.process(pr)

        # update on-screen ASTM peaks
        if self.page_nav.doing_raman():
            self.raman_shift_correction.update()

        # update the StatusBar
        self.status_bar.update()

    def set_curve_data(self, curve, y, x=None, label=None) -> bool:
        """
        # Lightweight wrapper over pyqtgraph.PlotCurveItem.setData.
        #
        # Checks for case where x[0] is higher than x[1] (happens with a default
        # wavecal of [0, 1, 0, 0] and positive excitation in wavenumber space).
        # Also traps for unequal array lengths, etc.
        #
        # @todo merge into Graph.set_data (calling it is a start)
        # @returns True if graph was updated
        """
        if curve is None:
            log.error("set_curve_data[%s]: no curve")
            return False

        if y is None:
            log.error("set_curve_data[%s]: no y")
            return False

        if x is None:
            log.debug("set_curve_data[%s]: no x (y_len = %d, y=%s, curve = %s)", label, len(y), y[:5], str(curve))
            self.graph.set_data(curve=curve, y=y)
            return True

        if len(x) != len(y):
            log.debug("%s: ignoring attempt to plot %d y-values against %d x-values", label, len(y), len(x))
            return False

        if len(x) >= 3 and x[0] > x[1] and x[1] < x[2]:
            log.error(f"set_curve_data[{label}]: fixing damaged x-axis")
            # x-axis is normally ascending (x1 < x2) but first element is
            # out of order (x0 > x1) due to corner-case where wavelength[0]
            # is 0.0, converted into wavenumber space.
            tmp = x.copy()
            tmp[0] = x[1] - (x[2] - x[1])
            x = tmp

        log.debug(f"set_curve_data[{label}]: passing to Graph")
        self.graph.set_data(curve=curve, y=y, x=x)
        return True

    # ##########################################################################
    #                                                                          #
    #                               Analysis                                   #
    #                                                                          #
    # ##########################################################################

    def get_last_processed_reading(self):
        spec = self.current_spectrometer()
        if not spec:
            return None

        if spec.app_state and spec.app_state.processed_reading:
            return spec.app_state.processed_reading
        return None

    def get_last_processed_spectrum(self):
        pr = self.get_last_processed_reading()
        if not pr:
            return
        return pr.get_processed()

    # ##########################################################################
    #                                                                          #
    #                                .ini File                                 #
    #                                                                          #
    # ##########################################################################

    def set_from_ini_file(self):
        """
        Load per-spectrometer settings keyed on serial_number (not general
        ENLIGHTEN settings like sound).  
        
        called from initialize_new_device
        """
        sfu = self.form.ui
        spec = self.current_spectrometer()

        # avoid corrupted data on unprogrammed EEPROMs
        sn = "UNKNOWN"
        if spec.settings.eeprom.serial_number is not None:
            sn = util.printable(spec.settings.eeprom.serial_number)[:16]

        if not self.config.has_section(sn):
            log.debug("set_from_ini_file: %s not found in config", sn)
            return
        log.debug("set_from_ini_file: applying settings for %s", sn)

        # So, here we're loading new state settings from a config file and...
        # ...applying them to GUI widgets?  Why not directly to spec.settings
        # etc?
        #
        # Well, we probably should.  And we should probably have some kind of
        # SpectrometerSettings.bind() that would go beyond EEPROMEditor to
        # include SpectrometerState, SpectrometerApplicationState.
        #
        # Ideally we should restructure the ini file a bit (the current format
        # was long ago) to support a full eeprom.field_name, spectrometer_state.field_name,
        # application_state.field_name canonical structure that can automatically
        # and scalably support every attribute we track.  And we should convert
        # the file-format to .json.
        #
        # We'd then have to allow more control over exactly what gets saved when the
        # user clicks "Save .ini"...they wouldn't necessarily WANT to preserve things
        # like laser_enable.  And it wouldn't be good to let the .ini overwrite things
        # like serial_number, model, has_laser, max_detector_temperature_degC etc.
        #
        # And we should update the EEPROMEditor so that fields are colorized (and get
        # tooltips) based on whether they are:
        #
        # - from the EEPROM
        # - from the .ini
        # - manually changed by the user this session

        #                         Key GUI_Widget                                     INI_file_key
        # SpectrometerState (control widgets)
        self.update_spinBox      (sn, sfu.spinBox_integration_time_ms,               "integration_time_ms")
        self.update_spinBox      (sn, sfu.spinBox_boxcar_half_width,                 "boxcar_half_width")
        self.update_spinBox      (sn, sfu.spinBox_detector_setpoint_degC,            "detector_tec_setpoint_degC")

        # EEPROM
        #
        # Would this be much better? Same result...
        #
        # self.eeprom_editor.update_from_config(sn, ini="adc_to_degC_coeff_0", attr="adc_to_degC_coeffs", index=0)
        #
        self.update_checkBox     (sn, sfu.checkBox_ee_has_laser,                     "has_laser")
        self.update_lineEdit     (sn, sfu.lineEdit_ee_adc_to_degC_coeff_0,           "adc_to_degC_coeff_0")
        self.update_lineEdit     (sn, sfu.lineEdit_ee_adc_to_degC_coeff_1,           "adc_to_degC_coeff_1")
        self.update_lineEdit     (sn, sfu.lineEdit_ee_adc_to_degC_coeff_2,           "adc_to_degC_coeff_2")
        self.update_lineEdit     (sn, sfu.lineEdit_ee_degC_to_dac_coeff_0,           "degC_to_dac_coeff_0")
        self.update_lineEdit     (sn, sfu.lineEdit_ee_degC_to_dac_coeff_1,           "degC_to_dac_coeff_1")
        self.update_lineEdit     (sn, sfu.lineEdit_ee_degC_to_dac_coeff_2,           "degC_to_dac_coeff_2")
        self.update_lineEdit     (sn, sfu.lineEdit_ee_wavelength_coeff_0,            "wavelength_coeff_0")
        self.update_lineEdit     (sn, sfu.lineEdit_ee_wavelength_coeff_1,            "wavelength_coeff_1")
        self.update_lineEdit     (sn, sfu.lineEdit_ee_wavelength_coeff_2,            "wavelength_coeff_2")
        self.update_lineEdit     (sn, sfu.lineEdit_ee_wavelength_coeff_3,            "wavelength_coeff_3")
        self.update_spinBox      (sn, sfu.spinBox_ee_max_temp_degC,                  "detector_tec_max_degC")
        self.update_spinBox      (sn, sfu.spinBox_ee_min_temp_degC,                  "detector_tec_min_degC")
        self.update_spinBox      (sn, sfu.spinBox_ee_slit_size_um,                   "slit_size_um")
        self.update_doubleSpinBox(sn, sfu.doubleSpinBox_ee_excitation_nm_float,      "excitation_nm")

        # note: because these will change the EEPROMEditor values, and the EEPROMEditor already has
        # a callback to update_gain_and_offset(force=True), INI changes should be sent downstream
        self.update_doubleSpinBox(sn, sfu.doubleSpinBox_ee_detector_gain,            "ccd_gain")
        self.update_spinBox      (sn, sfu.spinBox_ee_detector_offset,                "ccd_offset")
        self.update_doubleSpinBox(sn, sfu.doubleSpinBox_ee_detector_gain_odd,        "ccd_gain_odd")
        self.update_spinBox      (sn, sfu.spinBox_ee_detector_offset_odd,            "ccd_offset_odd")

        # this one is left for compatibility: if found in .ini file, will update
        # appropriate EEPROM field and send downstream
        self.update_checkBox     (sn, sfu.checkBox_ee_invert_x_axis,                 "invert_x_axis")

        # let .ini overrides imply TEC presence
        if not spec.settings.eeprom.has_cooling:
            if self.config.has_option(sn, "detector_tec_max_degC") and self.config.has_option(sn, "detector_tec_min_degC"):
                log.debug("inferring TEC presence from .ini file")
                spec.settings.eeprom.has_cooling = True

        # go ahead and regenerate x-axis
        self.update_wavecal()

        log.debug("set_from_ini_file: done")

    def update_spinBox(self, sn, widget, name):
        if self.config.has_option(sn, name):
            s = self.config.get(sn, name)
            try:
                widget.setValue(int(float(s))) # yes, float() required for '0.0' O_o
                return True
            except:
                log.error("ignored invalid %s", exc_info=1)

    def update_doubleSpinBox(self, sn, widget, name):
        if self.config.has_option(sn, name):
            s = self.config.get(sn, name)
            try:
                value = float(s)
                widget.setValue(value)
                return True
            except:
                log.error("ignored invalid %s", exc_info=1)

    def update_lineEdit(self, sn, widget, name):
        """
        We're reading (not loading, but getting values from) a newly-connected
        spectrometer's portion of the .ini file so that local user configuration
        can override the EEPROM etc.  As we read in values, we update the
        associated widget on the EEPROMEditor.
        
        Normally, calling setText() on a QLineEdit would trigger a textChanged
        event, such that follow-through actions would automatically follow (like
        updating the associated EEPROM field, recalculating the wavecal, etc).
        
        However, we have deliberately DISABLED the textChanged event on lineEdit
        widgets in the EEPROMEditor, because they have a nasty habit of responding
        to EVERY KEYPRESS when editing coefficients (creating bizarre behavior
        and errors on typos).
        
        Therefore, for now, we hacked EEPROMEditor.bind_lineEdit such that it
        stores a reference to each lineEdit widget's EEPROMEditor callback function
        in the widget itself, in an attribute called enlighten_trigger.
        
        We can assume that the EEPROMEditor itself was instantiated and bound at
        application startup time, long before any spectrometer connected and caused
        us to parse its .ini settings, so we can safely assume that this trigger
        callback is available to this function.
        
        So in conclusion, after an outside agency (like this .ini function)
        reaches into the EEPROMEditor and changes the values of lineEdit
        widgets owned by it, we then call that widget's enlighten_trigger()
        callback to tell the EEPROMEditor to "do whatever you would normally do
        after a user manually edited that field and pressed return."
        """
        if self.config.has_option(sn, name):
            value = self.config.get(sn, name)
            log.debug("Controller.update_lineEdit: setting %s to %s for %s", name, value, sn)
            widget.setText(value)

            # see above
            widget.enlighten_trigger()

    def update_checkBox(self, sn, widget, name):
        if self.config.has_option(sn, name):
            value = ("TRUE" == self.config.get(sn, name).upper())
            widget.setChecked(value)

    # ##########################################################################
    # X-Axis Management
    # ##########################################################################

    def update_wavecal(self, coeffs=None):
        """
        This gets called if the user has edited the EEPROM fields (coeff or 
        excitation).  Basically, update the Settings object if new versions were 
        passed; then recompute wavelengths and wavenumbers no matter what, and 
        sync excitations.
        """
        sfu = self.form.ui
        spec = self.current_spectrometer()
        ee = spec.settings.eeprom

        spec.settings.update_wavecal(coeffs)

        if ee.wavelength_coeffs:
            sfu.lineEdit_ee_wavelength_coeff_0.setText(str(ee.wavelength_coeffs[0]))
            sfu.lineEdit_ee_wavelength_coeff_1.setText(str(ee.wavelength_coeffs[1]))
            sfu.lineEdit_ee_wavelength_coeff_2.setText(str(ee.wavelength_coeffs[2]))
            sfu.lineEdit_ee_wavelength_coeff_3.setText(str(ee.wavelength_coeffs[3]))
            if len(ee.wavelength_coeffs) > 4:
                sfu.lineEdit_ee_wavelength_coeff_4.setText(str(ee.wavelength_coeffs[4]))

        # sync scope excitation widget from EEPROMEditor's
        # @todo LaserControlFeature
        sfu.doubleSpinBox_lightSourceWidget_excitation_nm.setValue(ee.excitation_nm_float)

    def generate_x_axis(self, spec=None, settings=None, unit=None, vignetted=True):
        """
        Graph.current_x_axis is not per-spectrometer, therefore:
        
        - pixels: overlapped and left-justified
        - wavelengths: partially overlapped / non-congruent (cool)
        - wavenumbers: mostly-overlapped, jagged left-edge
        
        @todo move this to Spectrometer? Graph?
        
        If you pass in a specific spectrometer, it uses the settings (wavecal &
        excitation) from THAT spectrometer.  Otherwise, if you pass in a specific
        SpectrometerSettings object (say from a saved/loaded Measurement), it
        uses that.  Otherwise it uses the current spectrometer.
        
        This function ONLY vignettes the x-axis if specifically asked to (and able to).
        
        @todo need to update for DetectorRegions
        """
        x_axis = None
        retval = None


        if settings is None:
            if spec is None:
                spec = self.current_spectrometer()
            if spec:
                settings = spec.settings

        if settings is None:
            log.error(f"settings was None even after getting current spec, not generating x-axis")
            return

        log.debug(f"generate_x_axis: spec {spec}, settings {settings}, unit {unit}, vignetted {vignetted}")

        regions = settings.state.detector_regions
        # log.debug(f"generate_x_axis: regions = {regions}")

        if unit is not None:
            if   unit == "cm": retval = np.copy(settings.wavenumbers)
            elif unit == "nm": retval = np.copy(settings.wavelengths)
            elif unit == "px": retval = np.array(list(range(settings.pixels())), dtype=np.float32)
        elif self.graph.current_x_axis == common.Axes.WAVELENGTHS:
            retval = settings.wavelengths
        elif self.graph.current_x_axis == common.Axes.WAVENUMBERS:
            retval = settings.wavenumbers
            if retval is None:
                log.debug("spectrometer has no wavenumber axis")
        else:
            retval = np.array(list(range(settings.pixels())), dtype=np.float32) 

        if vignetted:
            return self.vignette_roi.crop(retval, roi=settings.eeprom.get_horizontal_roi())

        if regions:
            log.debug("generate_x_axis: chopping into regions")
            retval = regions.chop(retval, flatten=True, orig_roi=settings.eeprom.get_horizontal_roi()) # which region?
            log.debug(f"generate_x_axis: got back {len(retval)} values ({retval[:3]}...{retval[:-3]})")

        return retval

    def perform_fpga_reset(self, spec = None):
        if spec is None:
            spec = self.multispec.current_spectrometer()

        if spec is None:
            return

        wasatch_device = spec.device

        wasatch_device.change_setting("reset_fpga", None)


    def update_hardware_window(self):
        for spec in self.multispec.spectrometers.values():
            # call StripChartFeature getter
            spec.app_state.update_rolling_data(self.form.ui.spinBox_strip_window.value())

    def toggle_roi_process(self):
        self.roi_enabled = not self.roi_enabled
        if self.roi_enabled:
            self.form.ui.pushButton_roi_toggle.setStyleSheet("background-color: #aa0000")
        else:
            self.form.ui.pushButton_roi_toggle.setStyleSheet(self.default_roi_btn)

    def display_response_error(self, spec: Spectrometer, response_error: str) -> bool:
        """
        @returns True if:
                     1. the device can stay connected (includes log views), or 
                     2. there's already a dialog open, or
                     3. we've already prompted the user about this error on this spectrometer.
                 False if:
                     1. the user said to disconnect
                     2. ENLIGHTEN was not configured to use the error dialogs
        """
        if not self.USE_ERROR_DIALOG:
            return False

        if response_error in self.seen_errors[spec].keys():
            log.debug(f"ignoring error because already seen: {response_error}")
            return True

        if self.dialog_open:
            log.debug(f"ignoring error because dialog currently open: {response_error}")
            return True
        self.dialog_open = True # todo make a mutex

        log.info(f"displaying MessageBox with the received error and options (Okay, Disconnect, Log): {response_error}")
        dlg_title = "Spectrometer Error"
        dlg_msg = ("ENLIGHTEN has encountered an error with the spectrometer. " \
                  + "The exception is shown below.  Click 'View Log' to " \
                  + "automatically open the logfile in Notepad, 'Disconnect' to " \
                  + "retry or 'Okay' to dismiss this dialog:\n\n" \
                  + response_error + "\n\n")
        dlg_btns = [("Okay", QMessageBox.AcceptRole), ("Disconnect", QMessageBox.RejectRole), ("View Log", QMessageBox.HelpRole)]

        selection = TimeoutDialog.showWithTimeout(self.form, 
                                                  10, 
                                                  dlg_msg, 
                                                  dlg_title, 
                                                  QMessageBox.Warning, 
                                                  dlg_btns)
        # Generate a bool list by comparing the clicked btn against the btn options
        self.dialog_open = False
        spec.settings.state.ignore_timeouts_until = datetime.datetime(datetime.MAXYEAR,12,1)
        if selection == [True, False, False]:
            log.info("user clicked 'Okay' to dismiss the dialog with no action")
        elif selection == [False, True, False]:
            log.info("user clicked 'Disconnect' so disconnecting the device")
            self.multispec.set_gave_up(spec.device_id)
            return False
        elif selection == [False, False, True]:
            log.info("user clicked 'View Log' so displaying the logfile")
            self.open_log()
        else:
            log.info(f"User didn't choose a button. Attempting disconnect and reconnect")
            self.seen_errors[spec].pop(response_error)
            return False
        return False

    def open_log(self):
        # Interestingly a few threads explained that this will open the default text editor
        webbrowser.open(os.path.join(common.get_default_data_dir(), "enlighten.log"))

    def get_grid_display(self):
        return self.grid_display

    def graph_grid_toggle(self):
        self.grid_display = not self.grid_display
        log.debug(f"setting grid display to {self.grid_display}")
        if self.grid_display:
            self.form.ui.pushButton_graphGrid.setStyleSheet("background-color: #aa0000")
        else:
            self.form.ui.pushButton_graphGrid.setStyleSheet(self.default_graph_btn)
        def resolve_graph_plot(head, attr):
            if head != None and hasattr(head, attr):
                return getattr(head, attr)
            else:
                None

        for name, obj_path in self.enlighten_graphs.items():
            plot = functools.reduce(resolve_graph_plot, obj_path)
            if plot != None:
                plot.showGrid(self.grid_display, self.grid_display)
            else:
                log.error(f"{name} couldn't set grid")

    def clear_response_errors(self, spec):
        """
        Reset the cached errors for a connected spec.
        Right now this is only called by eeprom editor
        after writing a new eeprom.
        """
        spec.settings.state.ignore_timeouts_until = None
        self.seen_errors[spec].clear()

    ## can't be in LoggingFeature unless log was a parameter...
    def header(self, s):
        log.debug("")
        log.debug('=' * len(s))
        log.debug(s)
        log.debug('=' * len(s))
        log.debug("")
