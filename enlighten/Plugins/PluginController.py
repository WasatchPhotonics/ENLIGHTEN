import re
import os
import sys
import time
import copy
import shutil
import pickle
import logging
import platform
import tokenize
import threading
import pyqtgraph
import traceback
import numpy as np
import importlib.util

from time import sleep
from queue import Queue
from PySide2 import QtGui, QtWidgets, QtCore
from PySide2.QtWidgets import QMessageBox, QCheckBox
from PySide2.QtCore import Qt

from .EnlightenApplicationInfoReal import EnlightenApplicationInfoReal
from .PluginFieldWidget import PluginFieldWidget
from .PluginModuleInfo  import PluginModuleInfo
from .PluginValidator   import PluginValidator
from .PluginWorker      import PluginWorker
from .TableModel        import TableModel

from .. import common
from ..ScrollStealFilter import ScrollStealFilter

from enlighten.scope.Graph import Graph

# this is in ../../pluginExamples
from EnlightenPlugin import EnlightenPluginField,   \
                            EnlightenPluginRequest,  \
                            EnlightenApplicationInfo, \
                            EnlightenPluginConfiguration

from wasatch import utils as wasatch_utils

log = logging.getLogger(__name__)

##
# @par Requirements
#
# - NOT required:
#   - auto-detect new plugins placed in watch directories while ENLIGHTEN is running
#   - auto-recompile edited plugins while ENLIGHTEN is running
#   - load plugins from arbitrary directories (EnlightenSpectra/plugins is fine)
#
# @par GUI Logic
#
# - [1] when you FIRST select a plugin, it will:
#   - show the unchecked cb_connected
#   - hide the unchecked cb_enabled
#   - load the module
#   - instantiate the plugin
#   - call plugin.get_configuration()
#   - update the GUI to display the module
#   - NOT create a worker
#   - NOT start passing ProcessedReadings
#
# - [2] if you then select a DIFFERENT plugin (before checking Connect), it will:
#   - leave cb_conenct shown but unchecked
#   - cache the previous configuration
#   - load the new module
#   - load the new configuration
#   - instantiate the plugin
#   - update the GUI for the new configuration
#   - NOT create a worker
#   - NOT start passing ProcessedReadings
#
# - [3] when you finally click Connect (which is only visible when a valid plugin is selected),
#   - it will disable combo_module (you can't change plugins while connected)
#   - it will create a worker
#   - it will start() the worker
#   - the WORKER will call plugin.start() (such that any sub-processes etc are entirely within the thread)
#   - the worker will run() until it receives a None (poison-pill)
#   - it will show and CHECK the Enable button
#
# - [4] when you uncheck Enable
#   - PluginController will set .enabled = False, stop sending readings to the request_queue, and ignore responses coming from response_queue
#   - the worker will keep running, quietly, in the background
#   - the GUI will stay configured for the connected plugin's fields
#
# - [5] if you uncheck Connect (whether Enabled or not)
#   - it will uncheck and HIDE Enabled
#   - it will send a poison-pill downstream to the worker
#   - the worker will call plugin.stop()
#   - the worker will close
#   - it will re-enable combo_module
#   - it will delete the worker object
#   - you will basically be back at [1]
#
# Notes:
# - cb_connected determines
#       - whether combo_module is enabled, and worker exists
# - cb_enabled determines whether we actively push readings to the request_queue
# - combo_module determines how the GUI is currently configured
#
# @par Apologia
#
# For posterity, some of the changes I made to Evan's original version were
# because I was trying to avoid fully destroying / shutting down previously-used
# plugins when changing to a new plugin; and playing with thoughts of having
# multiple plug-ins running at one time.  I've come to accept this would be
# undesirable complexity at this time.
class PluginController:

    SELECT_STRING = "Select a plugin"

    # ##########################################################################
    # initialization
    # ##########################################################################

    def clear(self):
        self.plugin_plot      = None  # a pyqtgraph chart for displaying returned plugin arrays or strip charts
        self.graph_plugin     = None  # second enlighten.Graph object associated with self.plugin_chart
        self.table_view       = None  # where panda_field gets displayed
        self.panda_field      = None  # if the plugin provided an export of type "pandas", this points to it

        self.module_infos     = None  # will hold and cache all the metadata (PluginModuleInfo) about each plugin we know about
        self.module_name      = None  # the string module name of the selected plugin
        self.enlighten_info   = None

        self.connected        = False # whether we've successfully called connect() on the selected plugin
        self.enabled          = False # whether the user is choosing to send new ProcessedReadings to the connected plugin
        self.blocking_request = None  # if the connected module is_blocking (don't send a new request until last is processed), the last request we sent

        self.worker           = None  # will hold a PluginWorker to run in the background when a PluginModuleInfo is connected
        self.request_queue  = Queue()
        self.response_queue = Queue()

        # re-initialized and re-created when we select a new plugin
        self.plugin_field_widgets = []
        self.plugin_curves = {}

        self.max_rows = 0
        self.max_cols = 0

        self.next_request_id = 0

    def __init__(self, ctl,
            colors,
            config,             # enlighten.Configuration
            generate_x_axis,
            get_last_processed_reading,
            get_settings,
            graph_scope,        # enlighten.Graph object associated with Scope Capture primary pyqtgraph
            gui,
            marquee,
            measurement_factory,
            multispec,
            parent,
            save_options,
            kia_feature,
            measurements_clipboard,
            crop_feature,

            button_process,
            cb_connected,
            cb_enabled,
            combo_graph_pos,
            combo_module,
            frame_control,
            frame_fields,
            layout_graphs,
            lb_graph_pos,
            lb_title,
            lb_widget,
            vlayout_fields,
            measurements):

        log.debug("instantiating PluginController")

        self.clear()

        self.ctl = ctl

        # business objects and callbacks
        self.colors                     = colors
        self.config                     = config
        self.generate_x_axis            = generate_x_axis
        self.get_last_processed_reading = get_last_processed_reading
        self.get_settings               = get_settings
        self.graph_scope                = graph_scope
        self.gui                        = gui
        self.marquee                    = marquee
        self.measurement_factory        = measurement_factory
        self.multispec                  = multispec
        self.parent                     = parent
        self.save_options               = save_options
        self.kia_feature                = kia_feature
        self.measurements_clipboard     = measurements_clipboard
        self.crop_feature               = crop_feature

        # widgets
        self.button_process             = button_process
        self.cb_connected               = cb_connected
        self.cb_enabled                 = cb_enabled
        self.combo_module               = combo_module
        self.combo_graph_pos            = combo_graph_pos
        self.frame_control              = frame_control
        self.frame_fields               = frame_fields
        self.lb_graph_pos               = lb_graph_pos
        self.lb_title                   = lb_title
        self.lb_widget                  = lb_widget
        self.vlayout_fields             = vlayout_fields
        self.layout_graphs              = layout_graphs
        self.measurements               = measurements

        # provide post-creation
        self.grid = None

        # start up check examples exist
        self.directory = common.get_default_data_dir()
        self.stub_plugin()

        # EnlightenApplicationInfo
        self.reset_enlighten_info()

        # initialize GUI
        self.frame_control.setVisible(False)
        self.plugin_fields_layout = QtWidgets.QVBoxLayout()
        self.vlayout_fields.addLayout(self.plugin_fields_layout)
        self.combo_graph_pos.setVisible(False)
        self.combo_graph_pos.setEnabled(False)
        self.button_process.setEnabled(False)
        self.cb_connected.setEnabled(False)
        self.cb_connected.setChecked(False)
        self.cb_enabled.setChecked(False)
        self.combo_graph_pos.setCurrentIndex(0) # bottom

        # configure our search directories
        self.plugin_dirs = [
            "pluginExamples",                                       # (for developers running from source)
            os.path.join(common.get_default_data_dir(), "plugins")  # (installed EnlightenSpectra/plugins)
        ]
        self.initialize_python_path()
        self.module_infos = self.find_all_plugins()
        self.populate_plugin_list()

        # mutex
        self.mut = QtCore.QMutex()

        # bindings
        self.button_process.clicked.connect(self.button_process_callback)
        self.cb_connected.clicked.connect(self.connected_callback)
        self.cb_enabled.stateChanged.connect(self.enabled_callback)
        self.combo_module.currentIndexChanged.connect(self.combo_module_callback)
        self.combo_graph_pos.currentIndexChanged.connect(self.graph_pos_callback)

        # events
        log.debug("registering observer on MeasurementFactory")
        self.combo_module.installEventFilter(ScrollStealFilter(self.combo_module))
        self.measurement_factory.register_observer(self.events_factory_callback)
        self.measurements.register_observer("export", self.export_event_callback)

    def stub_plugin(self):
        """Create the plugins folder if it does not exist"""
        log.debug(f"starting plugin stub")
        plugin_dst = os.path.join(self.directory, "plugins")
        if os.path.exists(plugin_dst):
            log.debug(f"plugin destination exists. Assumming created so not stubbing")
            return
        os.mkdir(plugin_dst)

        cwd = os.getcwd()
        plugin_src = os.path.join(cwd, "pluginExamples")

        if os.path.exists(plugin_src):
            plugin_src_items = os.listdir(plugin_src)
            log.debug(f"in search items {plugin_src} found items {plugin_src_items}")
            shutil.copytree(plugin_src, plugin_dst, dirs_exist_ok=True)
        else:
            log.error(f"couldn't find plugin src {plugin_src} so not creating stub")

    ##
    # releases any custom attributes created for a plugin
    def reset_enlighten_info(self):
        def reference_is_dark_corrected():
            spec = self.multispec.current_spectrometer()
            if spec is None or spec.app_state is None:
                return False
            return spec.app_state.reference_is_dark_corrected

        self.enlighten_info = EnlightenApplicationInfoReal(
            graph_scope = self.graph_scope, 
            reference_is_dark_corrected = reference_is_dark_corrected,
            save_options = self.save_options,
            kia_feature = self.kia_feature,
            plugin_settings = self.get_current_settings,
            measurement_factory = self.measurement_factory,
            measurements_clipboard = self.measurements_clipboard,
            read_measurements = self.measurements.read_measurements,
            crop_feature = self.crop_feature,
            plugin_fields = self.get_plugin_fields
        ) # leaving read measurement call for legacy purposes

    def initialize_python_path(self):
        log.debug("initializing plugin path")
        log.debug("Python include path was: %s", sys.path)
        for path in self.plugin_dirs:
            if os.path.exists(path):
                if path not in sys.path:
                    log.debug(f"appending to system path: {path}")
                    sys.path.append(path)
                else:
                    log.debug(f"already in system path: {path}")
            else:
                log.debug(f"plugin_dir not found: {path}")
        log.debug("Python include path now: %s", sys.path)

    ##
    # returns a hash of PluginModuleInfo
    # @todo prefix name with module hierarchy, i.e. Prod.DarkNoise, Demo.NullOddBlock
    def find_all_plugins(self):
        module_infos = {}
        for start_dir in self.plugin_dirs:
            if not os.path.exists(start_dir):
                log.debug(f"missing start_dir: {start_dir}")
                continue

            log.debug("looking for plugins under %s", start_dir)
            # Use scandir to get folder paths, search through the first level of folder
            try:
                classification_folders = [folder.path for folder in os.scandir(start_dir) if os.path.isdir(folder.path)]
            except Exception as e:
                log.error(f"error trying to search start_dir of {start_dir} with error {e}")
                continue
            # Again scandir for paths and make tuples to help track associated folder,
            # goes through each classification folder and picks up the files
            plugin_files = [(file.path, folder) for folder in classification_folders for file in os.scandir(folder) if os.path.isfile(file.path)]
            for file, folder in plugin_files:
                # find_all_plugins: file C:\Users\mzieg\Documents\EnlightenSpectra\plugins\Analysis\Despiking.py, folder C:\Users\mzieg\Documents\EnlightenSpectra\plugins\Analysis
                try:
                    filename = os.path.basename(file)
                    package = os.path.basename(folder)
                    if filename.endswith('.py') and filename != "EnlightenPlugin.py" and not filename.startswith("_"):
                        log.debug(f"find_all_plugins:   package {package}, filename {filename}, file {file}") # package Demo, filename BlockNullOdd.py
                        module_info = PluginModuleInfo(pathname=file, package=package, filename=filename, ctl=self.ctl)
                        full_module_name = module_info.full_module_name
                        if full_module_name not in module_infos:
                            log.debug(f"find_all_plugins:     added module {full_module_name}")
                            module_infos[full_module_name] = module_info
                        else:
                            log.debug("    skipping duplicate module_name %s", full_module_name)
                except Exception as e:
                    log.error(f"problem accessing file {file} of {e}")
                    continue
        return module_infos

    def populate_plugin_list(self):
        # log.debug("populating plugin list")
        self.combo_module.clear()
        self.combo_module.addItem(PluginController.SELECT_STRING)
        for module_name in sorted(self.module_infos):
            # log.debug("adding %s", module_name)
            self.combo_module.addItem(module_name)

    ##
    # This is how ENLIGHTEN destroys Business Objects, so use this as indication
    # ENLIGHTEN is shutting down.
    def disconnect(self):
        log.debug("disconnecting current worker")
        self.cancel_worker()
        self.reset_enlighten_info()

    # ##########################################################################
    # callbacks
    # ##########################################################################

    ##
    # The user just selected a different plugin.  Don't do anything drastic at
    # this point, just allow them to connect if a valid module was chosen.
    def combo_module_callback(self):
        module_name = self.combo_module.currentText()
        if module_name not in self.module_infos:
            self.cb_connected.setEnabled(False)
            return

        log.debug(f"user selected plugin {module_name}")
        self.cb_connected.setEnabled(True)
        self.cb_connected.setChecked(False) # should be in this state anyway

    # - [3] when you click Connect (which is only visible when a valid plugin is
    #     selected)
    #   - it will disable combo_module (you can't change plugins while connected)
    #   - it will create and run the worker
    #   - the WORKER will call plugin.connect() (such that any sub-processes etc
    #     are entirely within the thread)
    #   - the worker will run() until it receives a None (poison-pill)
    #   - it will show and CHECK the Enable button
    #
    # - [5] if you uncheck Connect (whether Enabled or not)
    #   - it will uncheck and HIDE Enabled
    #   - it will send a poison-pill downstream to the worker
    #   - the worker will call plugin.stop()
    #   - the worker will close
    #   - it will re-enable combo_module
    #   - it will delete the worker object
    #   - you will basically be back at [1]
    def connected_callback(self):
        log.debug("connected_callback: start")
        module_name = self.combo_module.currentText()

        if module_name not in self.module_infos:
            log.error(f"user somehow attempted to connect to invalid module {module_name}")
            self.cb_connected.setEnabled(False)
            self.cb_connected.setChecked(False)
            return

        connected = self.cb_connected.isChecked()

        warn_suppress = self.config.get("advanced_options", "suppress_plugin_warning", default=False)
        if not warn_suppress and connected:
            plugin_ok, suppress = self.display_plugin_warning()
            if not plugin_ok:
                self.cb_connected.setChecked(False)
                return
            if suppress:
                self.config.set("advanced_options", "suppress_plugin_warning", True)

        if connected:
            log.debug("we just connected")
            self.marquee.info(f"Connecting to plug-in {module_name}...", immediate=True)

            log.debug("reconfiguring GUI for %s", module_name)
            if not self.configure_gui_for_module(module_name):
                log.error("unable to configure GUI for module, disconnecting")
                self.cb_connected.setChecked(False)
                self.do_post_disconnect()
                return

            self.combo_module.setEnabled(False)

            ####################################################################
            #
            #   This is where the PluginWorker is created, and the plugin's 
            #   .connect() is called
            #
            ####################################################################

            # This is AFTER configure_gui_for_module() is called, meaning 
            # enlighten_info.dependencies should be populated

            connected_ok = False
            try:
                connected_ok = self.run_worker()
            except:
                # if this has good info, would be worth popping-up a MsgBox
                log.error("exception spawning PluginWorker", exc_info=1)

            if not connected_ok:
                log.error("failed to run worker, disconnecting")
                self.cb_connected.setChecked(False)
                self.do_post_disconnect()
                return

            # allow the user to enable the plugin
            self.cb_enabled.setEnabled(True)
            self.cb_enabled.setChecked(False)
            self.button_process.setEnabled(True)

            # for some reason, this doesn't work from within configure_gui_for_module
            self.graph_pos_callback()

            log.debug("successfully connected")
        else:
            log.debug("we just disconnected")
            self.do_post_disconnect()

    def do_post_disconnect(self):
        log.debug("do_post_disconnect: start")
        self.cb_enabled.setChecked(False)
        self.cb_enabled.setEnabled(False)
        self.button_process.setEnabled(False)
        self.combo_graph_pos.setEnabled(False)
        self.combo_module.setEnabled(True)
        self.cancel_worker()
        self.clear_previous_layout()
        log.debug("do_post_disconnect: done")

    # need to do very little -- just open/close the gate on processing requests,
    # plus set the "process" button to the opposite state
    def enabled_callback(self):
        self.enabled = self.cb_enabled.isChecked()
        if self.button_process is not None:
            self.button_process.setEnabled(not self.enabled)

    ## The user changed the combobox indicating where the "second graph" should appear
    # @see Controller.populate_placeholder_scope_capture
    def graph_pos_callback(self):
        pos = self.combo_graph_pos.currentText().lower().strip()
        log.debug("altering graph position to %s", pos)

        if self.plugin_plot is not None:
            self.plugin_plot.deleteLater()
            self.plugin_plot = None

        self.plugin_curves = {}
        self.init_plugin_plot()

        config = self.get_current_configuration()
        if pos == "none" or config is None or not config.has_other_graph:
            return

        #     0   1   2
        #   +---+---+---+
        # 0 |   | T |   |   T = Top
        #   +---+---+---+   L = Left
        # 1 | L | G | R |   G = Scope Capture Graph
        #   +---+---+---+   R = Right
        # 2 |   | B |   |   B = Bottom
        #   +---+---+---+
                                                                         # row, col, row span, col span
        if   pos == "top"   : self.layout_graphs.addWidget(self.plugin_plot, 0, 1)
        elif pos == "bottom": self.layout_graphs.addWidget(self.plugin_plot, 2, 1)
        elif pos == "left"  : self.layout_graphs.addWidget(self.plugin_plot, 1, 0)
        elif pos == "right" : self.layout_graphs.addWidget(self.plugin_plot, 1, 2)

    ##
    # The user clicked the "process" button on the control panel indicating
    # "please process the current spectrum".
    def button_process_callback(self):
        log.debug("user pressed process button")
        self.button_process.setEnabled(False)
        pr = self.get_last_processed_reading()
        settings = self.get_settings()
        spec = self.multispec.current_spectrometer()
        self.process_reading(pr, settings, spec, manual=True)

    # ##########################################################################
    # PluginWorker
    # ##########################################################################

    def run_worker(self):
        if self.worker != None:
            log.error("can't create new PluginWorker when one is already running")
            return False

        module_info = self.get_current_module_info()
        if module_info is None:
            log.error("can't run_worker without PluginModuleInfo")
            return False
        module_name = module_info.module_name

        log.debug("create_worker: creating")
        self.worker = PluginWorker(
            request_queue   = self.request_queue,
            response_queue  = self.response_queue,
            module_info     = module_info,
            enlighten_info  = self.enlighten_info)

        log.debug("create_worker: setting daemon")
        self.worker.setDaemon(True)

        log.debug("create_worker: starting")
        self.worker.start()
        log.debug("create_worker: done")

        # freeze GUI briefly to give worker a chance to fail on connect()
        sleep(0.05)

        if self.worker.error_message is not None:
            self.display_exception(f"Plugin {module_name} failed to start", self.worker.error_message)
            return False

        log.debug("PluginWorker error message is empty")
        return True

    def cancel_worker(self, send_downstream=True):
        if self.worker is None:
            return

        if send_downstream:
            log.debug("cancel_worker: sending poison-pill")
            self.request_queue.put_nowait(None)

        log.debug("cancel_worker: releasing worker")
        self.worker = None

    # ##########################################################################
    # plug-in selection
    # ##########################################################################
    def process_widgets(self, widgets, parent):
        for epf in widgets:
            if not PluginValidator.validate_field(epf):
                log.error("invalid EnlightenPluginField: %s", epf.name)
                continue

            # plugins are allowed exactly one pandas output
            if epf.datatype == "pandas":
                if self.panda_field:
                    log.error(f"ignoring extra pandas field {epf.name}")
                else:
                    self.panda_field = epf
                # no dynamic widget for pandas fields...they use the TableView
                continue
            elif epf.datatype == "radio":
                groupBox = QtWidgets.QGroupBox(f"{epf.name}")
                vbox = QtWidgets.QVBoxLayout()
                epf.group = groupBox
                epf.layout = vbox
                for option in epf.options:
                    epf.name = option
                    pfw = PluginFieldWidget(epf)
                    parent.append(pfw)
                continue

            log.debug(f"instantiating PluginFieldWidget {epf.name}")
            pfw = PluginFieldWidget(epf)
            parent.append(pfw)
            # old code left to be clear what parent was before dict
            # makes this easier to understand imo
            #self.plugin_field_widgets.append(pfw)

    ##
    # This may or may not be the first time this plugin has been selected, so
    # make sure the module is loaded, instantiated and we have its configuration,
    # then update the GUI accordingly.
    #
    # @note called by combo_module_callback
    def configure_gui_for_module(self, module_name):
        log.debug("configure_gui_for_module: module_name = %s", module_name)

        self.frame_control.setVisible(False)
        self.frame_fields.setVisible(False)
        self.clear_previous_layout()

        # if we just selected a module, we should not yet be connected, therefore
        # we can't and shouldn't be enabled
        self.cb_enabled.setChecked(False)
        self.cb_enabled.setEnabled(False)

        if module_name not in self.module_infos:
            log.error("configure_gui: invalid module")
            self.cb_connected.setEnabled(False)
            return False

        self.module_name = None
        module_info = self.module_infos[module_name]
        self.frame_control.setVisible(True)

        try:
            # import the module
            log.debug("importing the module")
            if not module_info.load():
                return False
            config = module_info.config

            # we're successfully initialized, so proceed
            self.module_name = module_name

            # satisfy dependencies
            if not self.satisfy_dependencies():
                log.error("failed to satisfy dependencies")
                return False

            # should we check config.has_other_graph?
            log.debug("configuring graph_pos")
            if config.has_other_graph:
                self.lb_graph_pos.setVisible(True)
                self.combo_graph_pos.setVisible(True)
                self.combo_graph_pos.setEnabled(True)
            else:
                self.lb_graph_pos.setVisible(False)
                self.combo_graph_pos.setVisible(False)
                self.combo_graph_pos.setEnabled(False)

            # set title
            log.debug("setting title")
            self.lb_title.setText(config.name)

            # set tooltip (really doesn't look that good)
            # if config.tooltip is not None:
            #     self.frame_control.setToolTip(config.tooltip)

            # delete any previously-displayed plugin widgets
            log.debug("clearing layout")
            self.clear_plugin_layout(self.plugin_fields_layout)

            # prepare to create the EnlightenPluginFields for this plugin
            log.debug("instantiating fields")
            self.panda_field = None
            self.plugin_field_widgets = []

            log.debug("populating vlayout")
            self.vlayout_fields.addLayout(self.plugin_fields_layout)

            added_group = []
            if type(config.fields) == dict:
                self.plugin_field_widgets = []
                log.debug("trying to add stack widget because dict for the fields")
                self.select_vbox = QtWidgets.QVBoxLayout()
                self.stacked_widget = QtWidgets.QStackedWidget()
                self.widget_selector = QtWidgets.QComboBox()
                self.widget_selector.activated[int].connect(self.stacked_widget.setCurrentIndex)
                for k, list_epf in config.fields.items():
                    self.widget_selector.addItem(str(k))
                    list_pfw = []
                    self.process_widgets(list_epf, list_pfw)
                    key_page = QtWidgets.QWidget()
                    key_page_layout = QtWidgets.QVBoxLayout()
                    for pfw in list_pfw:
                        # Not organizing values sent back to the plugin
                        # Just send all the field values as a flat list
                        self.plugin_field_widgets.append(pfw) 
                        key_page_layout.addLayout(pfw.get_display_element())
                    key_page.setLayout(key_page_layout)
                    self.stacked_widget.addWidget(key_page)

                self.select_vbox.addWidget(self.widget_selector)
                self.select_vbox.addWidget(self.stacked_widget)
                self.plugin_fields_layout.addLayout(self.select_vbox)
            else:
                log.debug(f"Non dict epf, performing standard layout")
                self.process_widgets(config.fields, self.plugin_field_widgets)

                # note these are PluginFieldWidgets, NOT EnlightenPluginFields
                log.debug("adding fields")
                for pfw in self.plugin_field_widgets:
                    if pfw.field_config.datatype == "radio":
                        group_box = pfw.field_config.group
                        layout = pfw.field_config.layout
                        if not group_box in added_group:
                            self.plugin_fields_layout.addWidget(group_box)
                            group_box.setLayout(layout)
                            added_group.append(group_box)
                        layout.addLayout(pfw.get_display_element())
                    else:
                        self.plugin_fields_layout.addLayout(pfw.get_display_element())

            self.frame_fields.setVisible(True)

            if self.panda_field:
                log.debug("creating output table")
                self.create_output_table()

            # configure graph series
            if config.series_names is not None and len(config.series_names) > 0:
                if not config.has_other_graph:

                    # note that these are all treated as lines 
                    # (EnlightenPluginConfiguration.graph_type pertains to graph_plugin)
                    log.debug("adding series to main graph")
                    for name in config.series_names:
                        # keep reference to curve objects so we can later delete them
                        log.info(f"adding curve on main graph: {name}")
                        self.create_graph_curves(name, self.graph_scope)

            # configure streaming support
            self.cb_enabled.setVisible(config.streaming)

            log.debug("done activating module %s", module_name)
        except:
            log.error(f"Error activating module {module_name}", exc_info=1)
            self.frame_control.setVisible(False)
            self.display_exception(
                f"An exception occurred while configuring the GUI for module {module_name}", 
                traceback.format_exc())
            # @todo self.unconnectable.add(module_name)
            return False

        log.debug("successfully reconfigured GUI for plugin %s", module_name)
        return True

    def get_plugin_fields(self):
        """Used by the plugin to programmatically change fields"""
        return self.plugin_field_widgets

    ##
    # Make it easy for plug-in authors to see exceptions when debugging their class.
    #
    # @todo move from QMessageBox to a custom dialog that's resizeable / larger
    def display_exception(self, summary, detail):
        log.critical(f"displaying exception to user: {summary}: {detail}")
        mb = QtWidgets.QMessageBox(
            QtWidgets.QMessageBox.Critical, 
            "ENLIGHTEN PluginController", 
            summary,
            parent = self.parent,
            flags = Qt.Widget)
        mb.setInformativeText(detail) # setDetailText has sizing issues
        mb.exec()

    def satisfy_dependencies(self):
        log.debug("satisfy_dependencies: start")

        # this is EnlightenPluginConfiguration
        config = self.get_current_configuration()
        if config is None or config.dependencies is None:
            return True

        # for enlighten.Configuration
        persist_section = f"Plugin_{config.name}"

        for dep in config.dependencies:
            log.debug(f"satisfying dependency {dep.name} of type {dep.dep_type}")

            if dep.dep_type == "existing_directory":
                prompt = dep.prompt if dep.prompt else "Please select an existing directory"
                self.marquee.info(prompt, persist=True, token="existing_directory")

                # create the dialog
                dialog = QtWidgets.QFileDialog(parent=self.parent, caption=prompt)
                dialog.setFileMode(QtWidgets.QFileDialog.Directory)
                dialog.setOption(QtWidgets.QFileDialog.ShowDirsOnly)

                # default to last selection 
                dialog.setDirectory(common.get_default_data_dir())
                if dep.persist:
                    last_dir = self.config.get(persist_section, dep.name)
                    if last_dir is not None and os.path.exists(last_dir):
                        dialog.setDirectory(last_dir)

                # get the user's choice
                value = dialog.getExistingDirectory()
                if value is None or len(value) == 0:
                    return False
                self.enlighten_info.dependencies[dep.name] = value

                # persist for next time
                if dep.persist:
                    self.config.set(persist_section, dep.name, value)
                self.marquee.clear(token="existing_directory")
            else:
                log.error(f"dependency {dep.name} has unsupported type {dep.dep_type}")
                return False

        return True

    # need to clear all depending the layout recursively
    # see https://stackoverflow.com/questions/4528347/clear-all-widgets-in-a-layout-in-pyqt
    def clear_plugin_layout(self, layout):
        if layout is None:
            return

        log.debug("clearing plugin layout")
        for i in reversed(range(layout.count())):
            layout_item = layout.takeAt(i)
            widget = layout_item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                self.clear_plugin_layout(layout_item.layout())

    def init_plugin_plot(self):
        log.debug("init_plugin_plot: start")
        config = self.get_current_configuration()
        if config is None:
            return

        self.plugin_plot= pyqtgraph.PlotWidget(name=f"{config.name}")
        if self.grid is not None and self.grid.enabled:
            self.plugin_plot.showGrid(True, True)
        self.combo_graph_pos.setVisible(True)
        self.lb_graph_pos.setVisible(True)
        self.plugin_plot_legend = self.plugin_plot.addLegend()

        self.graph_plugin = Graph(
            plot                = self.plugin_plot,
            generate_x_axis     = self.graph_scope.generate_x_axis,
            gui                 = self.graph_scope.gui,
            legend              = self.plugin_plot_legend,
            lock_marker         = True,  # let EPC.graph_type control this

            button_copy         = self.graph_scope.button_copy,
            button_invert       = self.graph_scope.button_invert,
            button_lock_axes    = self.graph_scope.button_lock_axes,
            button_zoom         = self.graph_scope.button_zoom,
            cb_marker           = self.graph_scope.cb_marker,
            combo_axis          = self.graph_scope.combo_axis,
            init_graph_axis     = False
        )

        # create curves for each series
        log.debug("creating curves for each series")
        if config.series_names is not None and config.has_other_graph:
            for name in config.series_names:
                self.create_graph_curves(name, self.graph_plugin)

        # configure x-axis
        if config.x_axis_label is not None:
            self.graph_plugin.set_x_axis_label(config.x_axis_label, locked=True)
        else:
            # no custom x-axis label provided, so whatever user has currently selected
            self.graph_plugin.update_axis_callback()

        # configure y-axis
        y_axis_label = "intensity (counts)" if config.y_axis_label is None else config.y_axis_label
        self.plugin_plot.setLabel(text=y_axis_label, axis="left")

    ##
    # Used to hold the output Pandas table, if one is provided
    def create_output_table(self):
        log.debug("creating output table widget")
        self.table_view = QtWidgets.QTableView()
        self.table_view.setAccessibleName("Pandas Output")

        # set stretch factor of scope to 1
        # tableview stretch defaults to 0, so it does not stretch
        self.layout_graphs.setRowStretch(1, 1)       

        self.layout_graphs.addWidget(self.table_view, 3, 0, 1, 3)
        self.layout_graphs.setRowMinimumHeight(3, 100)

    def create_graph_curves(self, name, graph):
        if name in self.plugin_curves.keys():
            log.info("Curve already exists, returning")
            return
        log.debug(f"creating curves for series {name}")
        config = self.get_current_configuration()
        if config is None:
            return

        if config.graph_type == 'line':
            log.debug("creating line curve")
            curve = graph.plot.plot(
                name = name,
                x    = [],
                y    = [],
                pen  = self.gui.make_pen())
        else:
            log.debug("creating xy curve")
            curve = graph.plot.plot(
                name       = name,
                x          = [],
                y          = [],
                pen        = None,
                symbol     = 'x',
                symbolPen  = self.gui.make_pen(),
                symbolSize = 12)

        self.plugin_curves[name] = curve

    # ##########################################################################
    # public methods
    # ##########################################################################

    def process_responses(self):
        while not self.response_queue.empty():
            response = self.response_queue.get_nowait()
            if response is not None:
                self.handle_response(response)
            else:
                log.critical("PluginController received an upstream poison-pill from %s", self.module_name)
                
                # self.marquee.error(f"Plug-in {self.module_name} encountered an error and shutdown")
                if self.worker is not None and self.worker.error_message is not None:
                    self.display_exception(f"{self.module_name} exception", self.worker.error_message)

                # go ahead and disconnect from the worker; don't bother
                # sending them a downstream pill, as they fed us one
                self.disconnect()
                return

    ##
    # Probably a controversial method...actually freeze the ENLIGHTEN GUI until 
    # the next plugin response is available.  Enforces a hard timeout of 1sec.
    # Probably we could do this in the background so the "GUI" doesn't free, but
    # ...we actually don't want to process any new spectra until this is resolved.
    #
    # @param orig_pr: the original ProcessedReading which led to this response, 
    #                 so we can fold response outputs into the original PR.
    #
    # @returns True if response received and processed within timeout
    def process_response_blocking(self, orig_pr):
        try:
            response = self.response_queue.get(block=True, timeout=10)
            self.handle_response(response, orig_pr)
            return True
        except:
            log.critical("exception blocking on response", exc_info=1)
            if self.worker is not None and self.worker.error_message is not None:
                self.display_exception(f"{self.module_name} exception", self.worker.error_message)
            self.disconnect()
            return False

    def get_current_settings(self):
        config = self.get_current_configuration()
        plugin_fields = { pfw.field_name: pfw.field_value for pfw in self.plugin_field_widgets }
        if type(config.fields) == dict:
            plugin_fields["active_page"] = self.widget_selector.currentText()
        return plugin_fields

    ##
    # Processes any queued responses, then sends the new request.
    #
    # Note that we make deep copies of both settings and the processed_reading, 
    # to minimize opportunities for bugs / exploits in plugins that could 
    # break ENLIGHTEN.  This is a performance hit, but oh well.
    #
    # @returns true if new EnlightenPluginRequest successfully sent to plugin
    def process_reading(self, processed_reading, settings, spec, manual=False):
        if processed_reading is None or settings is None:
            return False

        if not self.enabled and not manual:
            log.debug("neither enabled nor manual")
            return False

        config = self.get_current_configuration()
        if config is None:
            log.debug("missing configuration")
            return False

        # don't pass-down readings from unselected (background) spectrometers 
        # unless the plugin explicitly supports such
        device_id = processed_reading.device_id
        if device_id is not None:
            if not config.multi_devices and not self.multispec.is_selected(device_id):
                log.debug("plugin doesn't support multiple spectrometers")
                return False

        try:
            # never a good reason not to do this
            self.process_responses()

            # if we were fired by Controller upon receiving a new reading,
            # go no further unless we're still enabled
            if not manual and (not self.enabled or self.worker is None):
                log.debug("not manual and disabled/workerless, so stopping")
                return

            if config.is_blocking and self.blocking_request is not None:
                log.info("ignoring reading (plugin blocked on request_id %d)", self.blocking_request.request_id)
                return False

            # Note that here we make a deepcopy of the processed_reading, meaning 
            # that when we later get the response back, we no longer have a 
            # handle to the "original" processed_reading.  That makes it hard to 
            # pass-back "Measurement Metadata" in the response, and have a chance
            # of actually saving plugin-added metadata or columns in the final 
            # saved Measurement.

            log.debug("instantiating EnlightenPluginRequest")
            plugin_fields = self.get_current_settings()
            self.mut.lock() # avoid duplicate request_ids
            request = EnlightenPluginRequest(
                request_id          = self.next_request_id,
                spec                = spec,
                settings            = copy.deepcopy(settings),
                processed_reading   = copy.deepcopy(processed_reading),
                fields              = plugin_fields
            )
            self.next_request_id += 1
            self.mut.unlock()

            if config.is_blocking:
                log.debug("going to block on EnlightenPluginRequest %d", request.request_id)
                self.blocking_request = request

            log.debug("sending EnlightenPluginRequest %d", request.request_id)
            self.request_queue.put_nowait(request)

            # experimental: allow plugin to block ENLIGHTEN until response received
            if config.block_enlighten:
                if not self.process_response_blocking(processed_reading):
                    return False
            return True

        except: 
            log.error(f"Error with plugin request", exc_info=1)
            return False

    # ##########################################################################
    # processing EnlightenPluginResponses
    # ##########################################################################

    # release the block, if this is what we were waiting on
    def release_block(self, request):
        if self.blocking_request is not None \
                and self.blocking_request.request_id == request.request_id:
            log.debug("releasing block on request %d", request.request_id)
            self.blocking_request = None
        self.button_process.setEnabled(not self.enabled)

    ##
    # @todo split-out outputs, series into their own methods
    def handle_response(self, response, orig_pr=None):

        log.debug("handling response")

        config = self.get_current_configuration()
        if config is None:
            return
        try:
            if response is None:
                if self.worker.error_message is not None:
                    self.display_exception(f"Plugin {self.module_name} experienced an exception", self.worker.error_message)
                return

            request = response.request
            log.debug("handling response to request %d", request.request_id)

            if not PluginValidator.validate_response(response):
                log.error("invalid EnlightenPluginResponse")
                self.release_block(request)
                return

            ####################################################################
            # handle message                                                   #
            ####################################################################

            if response.message is not None:
                self.marquee.info(response.message)

            ####################################################################
            # handle outputs                                                   #
            ####################################################################

            outputs = response.outputs
            if outputs is not None:
                
                log.debug("plugin response has output")

                # handle scalar outputs
                for pfw in self.plugin_field_widgets:
                    epf = pfw.field_config
                    if epf.name in outputs and pfw.field_config.direction == "output":
                        pfw.update_value(outputs[epf.name])

                # handle Pandas output
                if self.panda_field and self.table_view:
                    dataframe = response.outputs.get(self.panda_field.name, None)
                    if dataframe is not None:
                        # log.debug(f"pandas dataframe {self.panda_field.name} = %s", dataframe)
                        model = TableModel(dataframe)
                        self.table_view.setModel(model)

                # handle functional-plugin Pandas output
                if "Table" in response.outputs.keys():
                    if not self.table_view:
                        self.create_output_table()

                    log.debug("functional-plugin using panda table")
                    dataframe = response.outputs["Table"]
                    model = TableModel(dataframe)
                    self.table_view.setModel(model)

            self.release_block(request)

            ####################################################################
            # handle graph series                                              #
            ####################################################################

            seriess = response.series
            if seriess is not None:
                log.debug("graphing series")

                # all plugin series are either on the main graph or the secondary
                # graph -- currently we don't support per-series configuration
                graph = self.graph_plugin if config.has_other_graph else self.graph_scope

                # determine default x-axis for a series, if none is provided
                x_from_label = None
                if config.x_unit is not None:
                    log.debug(f"took default x-axis from label ({config.x_unit})")
                    x_from_label = self.generate_x_axis(unit=config.x_unit)
                x_live = self.generate_x_axis()

                # plot each series to the selected graph; at this point it doesn't
                # matter if the plot is xy or line

                # first blank any missing series, this happens quickly, immediately blanking the graph
                to_remove = []
                for name in self.plugin_curves:
                    series = seriess.get(name, None)
                    if series is None:
                        log.debug(f"configured series {name} missing")
                        if name in self.plugin_curves:
                            graph.remove_curve(name)
                            to_remove.append(name)
                        else:
                            log.debug(f"configured series {name} missing curve?")
                
                # now perform the slower option of removing from configuration
                # this happens slowly, ~.2 sec per curve, enough that you would
                # see them being removed one by one if this was included in the
                # above loop
                for name in to_remove:
                    del self.plugin_curves[name]
                
                #del self.plugin_curves[name]

                # now graph every provided series (declared or otherwise)
                for name in sorted(seriess):
                    log.debug(f"graphing series {name}")
                    series = seriess.get(name, None)

                    if name not in self.plugin_curves:

                        # SB: functional plugins use exclusively undeclared curves

                        log.debug(f"found undeclared curve {name}...adding. in_legend={series.get('in_legend', True)}")
                        self.plugin_curves[name] = graph.add_curve(
                            name=name, 
                            pen=self.gui.make_pen(color=series.get("color")), 
                            in_legend=series.get("in_legend", True)
                        )

                    x_values = None
                    if isinstance(series, dict):
                        y_values = series.get('y', None)
                        if y_values is None:
                            log.error(f"series {name} missing y")
                            graph.set_data(self.plugin_curves[name], y=[], x=[])
                            continue
                        log.debug("taking x_values from dict")
                        x_values = series.get('x', None)
                    else:
                        y_values = series

                    if x_values is not None:
                        log.debug(f"x_values is {x_values[0]}..{x_values[-1]}")

                    if y_values == [] or y_values is None:
                        log.error(f"Received response with no y_values for series {name}")
                        continue
                        
                    if x_values is None:
                        # determine appropriate x-axis
                        log.debug("x_values is None, so determining appropriate x_axis")

                        if x_from_label is not None and len(y_values) == len(x_from_label):
                            # use default x-axis implied by x-axis label if sizing permits
                            x_values = x_from_label
                        elif config.x_axis_label is None and len(y_values) == len(x_live):
                            # if no label was provided and sizing fits, use live/selected axis
                            x_values = x_live
                        else:
                            # default to datapoints
                            x_values = np.array(list(range(len(y_values))), dtype=np.float32)

                    log.debug(f"updating curve {name}") # (x = %s, y = %s)", x_values, y_values)
                    try:
                        graph.set_data(self.plugin_curves[name], y=y_values, x=x_values)
                    except:
                        log.error(f"Failed to update curve {name}", exc_info=1)

            ####################################################################
            # handle metadata and overrides                                    #
            ####################################################################

            self.apply_overrides(orig_pr, response)

            ####################################################################
            # handle commands                                                  #
            ####################################################################

            self.apply_commands(response)

        except:
            log.error(f"error handling response", exc_info=1)

    def apply_overrides(self, orig_pr, response):
        if orig_pr is None:
            return

        orig_pr.plugin_metadata = response.metadata
        if response.overrides is None:
            return

        for name in response.overrides:
            value = response.overrides[name]
            if   name == "processed"            : orig_pr.processed            = value
            elif name == "recordable_dark"      : orig_pr.recordable_dark      = value
            elif name == "recordable_reference" : orig_pr.recordable_reference = value
            else:
                log.error(f"unsupported override: {name}")

    def apply_commands(self, response):
        if response.commands is None:
            return

        for setting, value in response.commands:
            log.debug(f"applying {setting}")
            self.multispec.change_device_setting(setting, value)

    ############################################################################
    # events                                                                   #
    ############################################################################

    ##
    # If there is a connected plugin, and if it has an events hash, and if that
    # hash has a 'save' callback, then relay the data.
    def events_factory_callback(self, measurement, event):
        log.debug(f"received Measurement from event {event}")

        if event == "pre-save" and self.enabled:
            measurement.set_plugin_name(self.module_name)

        config = self.get_current_configuration()
        if config is None or config.events is None:
            return

        callback = config.events.get(event, None)
        if callback is None:
            return

        log.debug("cloning measurement")
        m = measurement.clone()
        # log.debug("pickle.dumps: %s", pickle.dumps(m))

        log.debug(f"passing measurement to {callback}")
        callback(measurement = m)

    def export_event_callback(self, measurement):
        self.events_factory_callback(measurement, "export")

    ############################################################################
    # utility                                                                  #
    ############################################################################

    def get_current_module_info(self):
        if self.module_name is None or self.module_name not in self.module_infos:
            return
        return self.module_infos[self.module_name]

    def get_current_configuration(self):
        module_info = self.get_current_module_info()
        if module_info is None or not module_info.is_loaded():
            return
        return module_info.config

    def populate_combobox(self, cb, items, index=0):
        cb.clear()
        for i in items:
            cb.addItem(i)
        cb.setCurrentIndex(index)

    def clear_previous_layout(self):
        log.debug("clear_previous_layout: start")

        self.max_cols = 0
        self.max_rows = 0
        self.blocking_request = None
        self.request_queue = Queue()
        self.response_queue = Queue()
        self.clear_plugin_layout(self.plugin_fields_layout)
        self.layout_graphs.setRowMinimumHeight(3,0)

        log.debug("plugin curves = %s", self.plugin_curves)
        try:
            for curve in self.plugin_curves.keys():
                log.info(f"attempting to remove curve {curve}")
                self.plugin_curves[curve].setData([],[])
                self.graph_scope.remove_curve(self.plugin_curves[curve].name())
        except:
            log.error(f"While attempting to clear main graph of plugins encountered error", exc_info=1)

        try:
            if self.plugin_plot is not None:
                self.plugin_plot.deleteLater()
                self.plugin_plot = None
        except:
            log.error(f"While trying to clear plugin plot encountered error", exc_info=1)

        try:
            if self.table_view is not None:
                self.table_view.deleteLater()
                self.table_view = None
        except:
            log.error(f"While trying to clear table widget ran into error", exc_info=1)

        self.plugin_curves = {}

    def display_plugin_warning(self):
        suppress_cb = QCheckBox("Don't show again.", self.cb_connected)
        warn_msg = QMessageBox(self.cb_connected)
        warn_msg.setWindowTitle("Plugin Warning")
        warn_msg.setText("Plugins allow additional code to run. Verify that you trust the plugin and it is safe before running it.")
        warn_msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        warn_msg.setIcon(QMessageBox.Warning)
        warn_msg.setCheckBox(suppress_cb)
        clk_btn = warn_msg.exec_()
        plugin_ok = (clk_btn == QMessageBox.Ok)
        suppress_checked = warn_msg.checkBox().isChecked()
        return (plugin_ok, suppress_checked)
