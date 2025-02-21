import os
import sys
import copy
import shutil
import logging
import pyqtgraph
import traceback
import numpy as np

from time import sleep
from queue import Queue

from .PluginFieldWidget import PluginFieldWidget
from .PluginModuleInfo  import PluginModuleInfo
from .PluginValidator   import PluginValidator
from .PluginWorker      import PluginWorker
from .TableModel        import TableModel

from enlighten import common
from enlighten.scope.Graph import Graph
from enlighten.ui.ScrollStealFilter import ScrollStealFilter

# this is in ../../plugins
from EnlightenPlugin import EnlightenPluginRequest

if common.use_pyside2():
    from PySide2 import QtWidgets, QtCore
    from PySide2.QtCore import Qt
else:
    from PySide6 import QtWidgets, QtCore
    from PySide6.QtCore import Qt

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

    SECTION = "plugins"

    # ##########################################################################
    # initialization
    # ##########################################################################

    def clear(self):
        self.plugin_plot      = None  # a pyqtgraph chart for displaying returned plugin arrays or strip charts
        self.graph_plugin     = None  # second enlighten.ui.Graph object associated with self.plugin_chart
        self.table_view       = None  # where panda_field gets displayed
        self.panda_field      = None  # if the plugin provided an export of type "pandas", this points to it
        self.dataframe        = None  # cache for copy button

        self.module_infos     = None  # will hold and cache all the metadata (PluginModuleInfo) about each plugin we know about
        self.module_name      = None  # the string module name of the selected plugin

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
        self.autoload = None
        self.use_other_graph = True # not yet used

    def __init__(self, ctl):
        self.ctl = ctl
        cfu = ctl.form.ui

        log.debug("instantiating PluginController")
        self.clear()

        # widgets
        self.button_process             = cfu.pushButton_plugin_process
        self.cb_connected               = cfu.checkBox_plugin_connected
        self.combo_graph_pos            = cfu.comboBox_plugin_graph_pos
        self.combo_module               = cfu.comboBox_plugin_module
        self.frame_control              = cfu.frame_plugin_control
        self.frame_fields               = cfu.frame_plugin_fields
        self.layout_graphs              = cfu.layout_scope_capture_graphs
        self.lb_graph_pos               = cfu.label_plugin_graph_pos
        self.lb_title                   = cfu.label_plugin_title
        self.lb_widget                  = cfu.label_plugin_widget
        self.vlayout_fields             = cfu.verticalLayout_plugin_fields

        # start up check examples exist
        self.directory = common.get_default_data_dir()
        self.create_plugins_folder()

        # initialize GUI
        self.frame_control.setVisible(False)
        self.plugin_fields_layout = QtWidgets.QVBoxLayout()
        self.vlayout_fields.addLayout(self.plugin_fields_layout)
        self.combo_graph_pos.setVisible(False)
        self.combo_graph_pos.setEnabled(False)
        self.button_process.setEnabled(False)
        self.cb_connected.setEnabled(False)
        self.cb_connected.setChecked(False)
        self.combo_graph_pos.setCurrentIndex(0) # bottom

        # configure our search directories
        self.plugin_dirs = [
            "plugins",                                              # (for developers running from source)
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
        self.combo_module.currentIndexChanged.connect(self.combo_module_callback)
        self.combo_graph_pos.currentIndexChanged.connect(self.graph_pos_callback)

        # filter scroll-steal
        for combo in [ self.combo_module, self.combo_graph_pos ]:
            combo.installEventFilter(ScrollStealFilter(combo))

        self.timer = QtCore.QTimer() 
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.tick)

        self.ctl.page_nav.register_observer("mode", self.update_field_visibility)

    def start(self, ms):
        """
        The PluginController doesn't normally have an internal event loop (it's 
        mostly ticked by Controller.tick_status).

        However, occasionally it needs events which occur in the GUI thread, so
        widgets can be updated. This is for that.
        """
        self.timer.start(ms)

    def stop(self):
        self.timer.stop()

    def tick(self):
        if self.autoload:
            module = self.autoload
            self.autoload = None
            self.force_load_plugin(module)

        self.timer.start(1000) # 1Hz

    def create_plugins_folder(self):
        """Create the plugins folder if it does not exist"""
        log.debug(f"starting plugin stub")
        plugin_dst = os.path.join(self.directory, "plugins")
        if os.path.exists(plugin_dst):
            log.debug(f"plugin destination exists. Assumming created so not stubbing")
            return
        os.mkdir(plugin_dst)

        cwd = os.getcwd()
        plugin_src = os.path.join(cwd, "plugins")

        if os.path.exists(plugin_src):
            plugin_src_items = os.listdir(plugin_src)
            log.debug(f"in search items {plugin_src} found items {plugin_src_items}")
            shutil.copytree(plugin_src, plugin_dst, dirs_exist_ok=True)
        else:
            log.error(f"couldn't find plugin src {plugin_src} so not creating stub")

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
                try:
                    filename = os.path.basename(file)
                    package = os.path.basename(folder)
                    if filename.endswith('.py') and filename != "EnlightenPlugin.py" and not filename.startswith("_"):
                        # log.debug(f"find_all_plugins:   package {package}, filename {filename}, file {file}") # package Demo, filename BlockNullOdd.py
                        module_info = PluginModuleInfo(pathname=file, package=package, filename=filename, ctl=self.ctl)
                        full_module_name = module_info.full_module_name
                        if full_module_name not in module_infos:
                            log.debug(f"    added module {full_module_name}")
                            module_infos[full_module_name] = module_info
                        else:
                            log.debug("    skipping duplicate module_name %s", full_module_name)
                except Exception as e:
                    log.error(f"problem accessing file {file} of {e}")
                    continue
        return module_infos

    def populate_plugin_list(self):
        # log.debug("populating plugin list")
        previous_selection = self.ctl.config.get(self.SECTION, "selected_plugin")
        self.combo_module.clear()
        self.combo_module.addItem("Select a plugin")
        found = False
        for module_name in sorted(self.module_infos):
            # log.debug("adding %s", module_name)
            self.combo_module.addItem(module_name)
            if module_name == previous_selection:
                found = True

        if found:
            self.combo_module.setCurrentText(previous_selection)
            self.combo_module_callback()

    def disconnect(self):
        log.debug("disconnecting current worker")
        self.cancel_worker()

    def force_load_plugin(self, module_name):
        if module_name not in self.module_infos:
            log.error(f"unable to autoload unknown plugin: {module_name}")
            return
        
        log.debug(f"autoloading {module_name}")
        self.combo_module.setCurrentText(module_name)
        self.cb_connected.setChecked(True)
        self.connected_callback() # .clicked doesn't respond to programmatic changes

        # autoloaded plugins can't be disabled
        self.combo_module.setEnabled(False)
        self.cb_connected.setEnabled(False)

    # ##########################################################################
    # callbacks
    # ##########################################################################

    ##
    # The user just selected a different plugin.  Don't do anything drastic at
    # this point, just allow them to connect if a valid module was chosen.
    def combo_module_callback(self):
        module_name = self.combo_module.currentText()
        if module_name not in self.module_infos:
            log.error(f"user selected unknown plugin {module_name}")
            self.cb_connected.setEnabled(False)
            return

        log.debug(f"user selected plugin {module_name}")
        self.cb_connected.setEnabled(True)
        self.cb_connected.setChecked(False) # should be in this state anyway

        self.ctl.config.set(self.SECTION, "selected_plugin", module_name)

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

        self.hide_widget()

        if module_name not in self.module_infos:
            log.error(f"connected_callback: user somehow attempted to connect to invalid module {module_name}")
            self.cb_connected.setEnabled(False)
            self.cb_connected.setChecked(False)
            return

        connected = self.cb_connected.isChecked()
        warn_suppress = self.ctl.config.get("plugins", "suppress_warning", default=False)

        if not warn_suppress and connected:
            result = self.ctl.gui.msgbox_with_checkbox(
                title="Plugin Warning", 
                text="Plugins allow external code to run. Verify that you trust the plugin and it is safe before running it.",
                checkbox_text="Don't show again")

            if not result["ok"]:
                self.cb_connected.setChecked(False)
                return

            if result["checked"]:
                self.ctl.config.set("plugins", "suppress_warning", True)

        if connected:
            log.debug("connected_callback: we just connected")
            self.ctl.marquee.info(f"Connecting to plug-in {module_name}...", immediate=True)

            log.debug("connected_callback: reconfiguring GUI for %s", module_name)
            if not self.configure_gui_for_module(module_name):
                log.error("connected_callback: unable to configure GUI for module, disconnecting")
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

            connected_ok = False
            try:
                connected_ok = self.run_worker()
            except:
                # if this has good info, would be worth popping-up a MsgBox
                log.error("connected_callback: exception spawning PluginWorker", exc_info=1)

            if not connected_ok:
                log.error("connected_callback: failed to run worker, disconnecting")
                self.cb_connected.setChecked(False)
                self.do_post_disconnect()
                return

            module_config = self.get_current_configuration()
            streaming = module_config.streaming
            log.debug(f"connected_callback: streaming defaulting to {streaming}")
            if module_config.auto_enable is not None and isinstance(module_config.auto_enable, bool) and not module_config.auto_enable:
                log.debug(f"connected_callback: something set auto_enable {module_config.auto_enable}, so disabling streaming")
                streaming = False

            log.debug(f"connected_callback: streaming {module_config.streaming}, auto_enable {module_config.auto_enable}")
            if streaming:
                # this plugin should receive "streaming" inputs from ENLIGHTEN
                log.debug("connected_callback: enabling streaming")
                self.button_process.setVisible(False)
                self.enabled = True
            elif module_config.process_requests:
                # allow the user to enable the plugin
                log.debug("connected_callback: not streaming")
                self.button_process.setVisible(True)
                self.button_process.setEnabled(True)
                self.enabled = False
            else:
                log.debug("connected_callback: not processing requests")
                self.button_process.setVisible(False)
                self.enabled = False

            # for some reason, this doesn't work from within configure_gui_for_module
            self.graph_pos_callback()

            log.debug("connected_callback: successfully connected")
        else:
            log.debug("we just disconnected")
            self.do_post_disconnect()

        log.debug("connected_callback: done")

    def do_post_disconnect(self):
        log.debug("do_post_disconnect: start")
        self.button_process.setEnabled(False)
        self.combo_graph_pos.setEnabled(False)
        self.combo_module.setEnabled(True)
        self.cancel_worker()
        self.clear_previous_layout()
        log.debug("do_post_disconnect: done")

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

        if   pos == "top"   : self.layout_graphs.addWidget(self.plugin_plot, 0, 1)
        elif pos == "bottom": self.layout_graphs.addWidget(self.plugin_plot, 2, 1)
        elif pos == "left"  : self.layout_graphs.addWidget(self.plugin_plot, 1, 0)
        elif pos == "right" : self.layout_graphs.addWidget(self.plugin_plot, 1, 2)

    ##
    # The user clicked the "process" button on the control panel indicating
    # "please process the current spectra".
    def button_process_callback(self):
        log.debug("user pressed process button")

        if self.config.multi_devices:
            for spec in self.ctl.multispec.get_spectrometers():
                if spec is not None and spec.app_state is not None:
                    pr = spec.app_state.processed_reading
                    if pr is not None:
                        self.button_process.setEnabled(False)
                        self.process_reading(pr, spec.settings, spec, manual=True)
        else:
            spec = self.ctl.multispec.current_spectrometer()
            if spec is not None and spec.app_state is not None:
                pr = spec.app_state.processed_reading
                if pr is not None:
                    self.button_process.setEnabled(False)
                    self.process_reading(pr, spec.settings, spec, manual=True)

    # ##########################################################################
    # PluginWorker
    # ##########################################################################

    def run_worker(self):
        if self.worker is not None:
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
            module_info     = module_info)

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

    def process_widgets(self, widgets, container):
        for epf in widgets:
            if not PluginValidator.validate_field(epf):
                log.error(f"invalid EnlightenPluginField {epf.name}")
                continue

            # plugins are allowed exactly one pandas output
            if epf.datatype == "pandas":
                if self.panda_field:
                    log.error(f"ignoring extra pandas field {epf.name}")
                else:
                    log.debug(f"process_widgets: panda_field = {epf.name}")
                    self.panda_field = epf
                # no dynamic widget for pandas fields...they use the TableView
                continue
            elif epf.datatype == "radio":
                # MZ: considering removing support for these in preference for 
                # the new "combobox" datatype
                groupBox = QtWidgets.QGroupBox(epf.name)
                vbox = QtWidgets.QVBoxLayout()
                epf.group = groupBox
                epf.layout = vbox
                for choice in epf.choices:
                    epf.name = choice
                    pfw = PluginFieldWidget(epf, self.ctl)
                    container.append(pfw)
                continue

            log.debug(f"instantiating PluginFieldWidget with EnlightenPluginField {epf}")
            pfw = PluginFieldWidget(epf, self.ctl)
            container.append(pfw)

    def hide_widget(self):
        self.frame_control.setVisible(False)
        self.frame_fields.setVisible(False)
        self.clear_previous_layout()

    ##
    # This may or may not be the first time this plugin has been selected, so
    # make sure the module is loaded, instantiated and we have its configuration,
    # then update the GUI accordingly.
    #
    # @note called by combo_module_callback
    def configure_gui_for_module(self, module_name):
        log.debug("configure_gui_for_module: module_name = %s", module_name)

        self.hide_widget()

        if module_name not in self.module_infos:
            log.error(f"configure_gui_for_module: invalid module {module_name}")
            self.cb_connected.setEnabled(False)
            return False

        self.module_name = None
        module_info = self.module_infos[module_name]
        self.frame_control.setVisible(True)

        try:
            # import the module
            log.debug("configure_gui_for_module: importing the module")
            if not module_info.load():
                return False
            config = module_info.config

            # we're successfully initialized, so proceed
            self.module_name = module_name

            log.debug("configure_gui_for_module: configuring graph")
            self.show_plugin_graph(config.has_other_graph)

            # set title
            log.debug("configure_gui_for_module: setting title")
            self.lb_title.setText(config.name)

            # set tooltip (really doesn't look that good)
            # if config.tooltip is not None:
            #     self.frame_control.setToolTip(config.tooltip)

            # delete any previously-displayed plugin widgets
            log.debug("configure_gui_for_module: clearing layout")
            self.clear_plugin_layout(self.plugin_fields_layout)

            # prepare to create the EnlightenPluginFields for this plugin
            log.debug("configure_gui_for_module: instantiating fields")
            self.dataframe = None
            self.panda_field = None
            self.plugin_field_widgets = []

            log.debug("configure_gui_for_module: populating vlayout")
            self.vlayout_fields.addLayout(self.plugin_fields_layout)

            added_group = []
            log.debug(f"configure_gui_for_module: Non dict epf, performing standard layout")
            self.process_widgets(config.fields, self.plugin_field_widgets) # sets panda_field

            # note these are PluginFieldWidgets, NOT EnlightenPluginFields
            for pfw in self.plugin_field_widgets:
                log.debug(f"configure_gui_for_module: adding pfw {pfw.field_name}")
                if pfw.field_config.datatype == "radio":
                    group_box = pfw.field_config.group
                    layout = pfw.field_config.layout
                    if group_box not in added_group:
                        self.plugin_fields_layout.addWidget(group_box)
                        group_box.setLayout(layout)
                        added_group.append(group_box)
                    layout.addLayout(pfw.get_display_element())
                else:
                    item = pfw.get_display_element()
                    self.plugin_fields_layout.addLayout(item)

            # configure initial visibility
            self.update_field_visibility()

            if self.panda_field:
                # pandas ignores Expert visibility
                log.debug("configure_gui_for_module: creating output table")
                self.create_output_table()
                self.add_copy_dataframe_to_clipboard_button()

            # configure graph series
            if config.series_names is not None and len(config.series_names) > 0:
                # there are no Expert graphs or series
                if not config.has_other_graph:

                    # note that these are all treated as lines 
                    # (EnlightenPluginConfiguration.graph_type pertains to graph_plugin)
                    log.debug("configure_gui_for_module: adding series to main graph")
                    for name in config.series_names:
                        # keep reference to curve objects so we can later delete them
                        log.info(f"configure_gui_for_module: adding curve on main graph: {name}")
                        self.create_graph_curves(name, self.ctl.graph)

            log.debug("configure_gui_for_module: done activating module %s", module_name)
        except:
            log.error(f"configure_gui_for_module: Error activating module {module_name}", exc_info=1)
            self.frame_control.setVisible(False)
            self.display_exception(
                f"An exception occurred while configuring the GUI for module {module_name}", 
                traceback.format_exc())
            # @todo self.unconnectable.add(module_name)
            return False

        log.debug("configure_gui_for_module: successfully reconfigured GUI for plugin %s", module_name)
        return True

    def add_copy_dataframe_to_clipboard_button(self):
        if not self.panda_field:
            return

        log.debug("adding CopyDataframeToClipboard button")
        hbox = QtWidgets.QHBoxLayout()
        item = QtWidgets.QPushButton()
        item.setText("Copy to Clipboard")
        item.setMinimumHeight(30) 
        item.pressed.connect(self.copy_dataframe_to_clipboard)
        item.setToolTip("Copy table to Clipboard")
        hbox.addWidget(item)
        self.plugin_fields_layout.addLayout(hbox)
        log.debug("add CopyDataframeToClipboard done")

    def copy_dataframe_to_clipboard(self):
        if self.dataframe is not None:
            self.ctl.clipboard.copy_dataframe(self.dataframe)
        
    def show_plugin_graph(self, flag):
        """
        @todo it would be neat if plugins themselves could toggle 
              self.use_other_graph, but we'd need to move existing 
              curves between graphs/legends via self.plugin_curves
        """
        log.debug(f"show_plugin_graph: flag {flag}")
        self.use_plugin_graph = flag
        self.lb_graph_pos.setVisible(flag)
        self.combo_graph_pos.setVisible(flag)
        self.combo_graph_pos.setEnabled(flag)

    def get_plugin_fields(self):
        """Used by the plugin to programmatically change fields"""
        return self.plugin_field_widgets

    def update_field_visibility(self):
        visible_count = 0
        for pfw in self.plugin_field_widgets:
            if pfw.update_visibility():
                visible_count += 1
        self.frame_fields.setVisible(visible_count > 0)

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
            parent = self.ctl.form,
            flags = Qt.Widget)
        mb.setInformativeText(detail) # setDetailText has sizing issues
        mb.exec()

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

        self.plugin_plot = pyqtgraph.PlotWidget(name=f"{config.name}")
        if self.ctl.grid is not None and self.ctl.grid.enabled:
            self.plugin_plot.showGrid(True, True)
        self.combo_graph_pos.setVisible(config.has_other_graph)
        self.lb_graph_pos.setVisible(config.has_other_graph)
        self.plugin_plot_legend = self.plugin_plot.addLegend()

        self.graph_plugin = Graph(
            ctl                 = self.ctl,
            name                = f"Plugin {config.name}",

            plot                = self.plugin_plot,
            legend              = self.plugin_plot_legend,
            lock_marker         = True,  # let EPC.graph_type control this
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

        header = self.table_view.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

        self.layout_graphs.addWidget(self.table_view, 3, 0, 1, 3)
        self.layout_graphs.setRowMinimumHeight(3, 100)
        self.layout_graphs.setRowStretch(3, 0)

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
                pen  = self.ctl.gui.make_pen())
        else:
            log.debug("creating xy curve")
            curve = graph.plot.plot(
                name       = name,
                x          = [],
                y          = [],
                pen        = None,
                symbol     = 'x',
                symbolPen  = self.ctl.gui.make_pen(),
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
                
                if self.worker is not None and self.worker.error_message is not None:
                    self.display_exception(f"{self.module_name} exception", self.worker.error_message)

                # go ahead and disconnect from the worker; don't bother
                # sending them a downstream pill, as they fed us one
                self.disconnect()
                return

    ##
    # Probably a controversial method...actually freeze the ENLIGHTEN GUI until 
    # the next plugin response is available. Enforces a hard timeout of 1sec.
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
        if isinstance(config.fields, dict):
            plugin_fields["active_page"] = self.widget_selector.currentText()
        log.debug(f"get_current_settings: plugin_fields = {plugin_fields}")
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
            if not config.multi_devices and not self.ctl.multispec.is_selected(device_id):
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

            log.debug("instantiating EnlightenPluginRequest")
            plugin_fields = self.get_current_settings()

            self.mut.lock() # avoid duplicate request_ids
            # Send COPIES of SpectrometerSettings and the ProcessedReading,
            # to reduce opportunities for plugin bugs to screw-up ENLIGHTEN.
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

            # allow plugin to block ENLIGHTEN until response received
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
        if (self.blocking_request is not None and 
                self.blocking_request.request_id == request.request_id):
            log.debug("releasing block on request %d", request.request_id)
            self.blocking_request = None
        self.button_process.setEnabled(not self.enabled)

    ##
    # @todo split-out outputs, series into their own methods
    def handle_response(self, response, orig_pr=None):

        log.debug("handle_response: start")

        config = self.get_current_configuration()
        if config is None:
            return
        try:
            if response is None:
                if self.worker.error_message is not None:
                    self.display_exception(f"Plugin {self.module_name} experienced an exception", self.worker.error_message)
                return

            request = response.request
            log.debug(f"handle_response: request {request.request_id}")

            if not PluginValidator.validate_response(response):
                log.error("handle_response: invalid EnlightenPluginResponse")
                self.release_block(request)
                return

            ####################################################################
            # handle message                                                   #
            ####################################################################

            if response.message is not None:
                if "error" in response.message.lower():
                    self.ctl.marquee.error(response.message, period_sec=5)
                else:
                    self.ctl.marquee.info(response.message, period_sec=5)

            ####################################################################
            # handle outputs                                                   #
            ####################################################################

            outputs = response.outputs
            if outputs is not None:
                
                log.debug("handle_response: plugin response has output")

                # handle scalar outputs
                for pfw in self.plugin_field_widgets:
                    epf = pfw.field_config
                    if epf.name in outputs and pfw.field_config.direction == "output":
                        pfw.update_value(outputs[epf.name])

                # handle Pandas output
                model = None
                if self.panda_field and self.table_view:
                    dataframe = response.outputs.get(self.panda_field.name, None)
                    if dataframe is not None:
                        # log.debug(f"pandas dataframe {self.panda_field.name} = %s", dataframe)
                        model = TableModel(dataframe)
                        self.table_view.setModel(model)
                        self.dataframe = dataframe

                # handle functional-plugin Pandas output
                if "Table" in response.outputs.keys():
                    if not self.table_view:
                        self.create_output_table()

                    log.debug("handle_response: functional-plugin using panda table")
                    dataframe = response.outputs["Table"]
                    model = TableModel(dataframe)
                    self.table_view.setModel(model)
                    self.dataframe = dataframe

            self.release_block(request)

            ####################################################################
            # handle graph series                                              #
            ####################################################################

            seriess = response.series
            if seriess is not None:
                log.debug("handle_response: graphing seriess")

                # all plugin series are either on the main graph or the secondary
                # graph -- currently we don't support per-series configuration
                graph = self.graph_plugin if (config.has_other_graph and self.use_other_graph) else self.ctl.graph

                # determine default x-axis for a series, if none is provided
                x_from_label = None
                if config.x_unit is not None:
                    log.debug(f"handle_response: took default x-axis from label ({config.x_unit})")
                    x_from_label = self.ctl.generate_x_axis(unit=config.x_unit)
                x_live = self.ctl.generate_x_axis()

                # plot each series to the selected graph; at this point it doesn't
                # matter if the plot is xy or line

                # first blank any missing series, this happens quickly, immediately blanking the graph
                to_remove = []
                for name in self.plugin_curves:
                    # log.debug(f"handle_response: found existing curve {name}")
                    series = seriess.get(name, None)
                    if series is None:
                        log.debug(f"handle_response: configured series {name} missing")
                        if name in self.plugin_curves:
                            # log.debug(f"handle_response: removing curve {name}")
                            graph.remove_curve(name)
                            to_remove.append(name)
                        else:
                            log.debug(f"handle_response: configured series {name} missing curve?")
                
                # now perform the slower option of removing from configuration
                # this happens slowly, ~.2 sec per curve, enough that you would
                # see them being removed one by one if this was included in the
                # above loop
                for name in to_remove:
                    # log.debug(f"handle_response: deleting curve {name}")
                    del self.plugin_curves[name]
                
                # now graph every provided series (declared or otherwise)
                for name in sorted(seriess):
                    log.debug(f"handle_response: graphing series {name}")
                    series = seriess.get(name, None)

                    if name not in self.plugin_curves:

                        # SB: functional plugins use exclusively undeclared curves

                        log.debug(f"handle_response: found undeclared curve {name}...adding. in_legend={series.get('in_legend', True)}")
                        self.plugin_curves[name] = graph.add_curve(
                            name=name, 
                            pen=self.ctl.gui.make_pen(color=series.get("color")), 
                            in_legend=series.get("in_legend", True))

                    x_values = None
                    if isinstance(series, dict):
                        y_values = series.get('y', None)
                        if y_values is None:
                            log.error(f"handle_response: series {name} missing y")
                            graph.set_data(self.plugin_curves[name], y=[], x=[])
                            continue
                        # log.debug("handle_response: taking x_values from dict")
                        x_values = series.get('x', None)
                    else:
                        y_values = series

                    # if x_values is not None:
                    #     log.debug(f"handle_response: x_values is {x_values[0]}..{x_values[-1]}")

                    if y_values == [] or y_values is None:
                        log.error(f"handle_response: eceived response with no y_values for series {name}")
                        continue
                        
                    if x_values is None:
                        # determine appropriate x-axis
                        # log.debug("handle_response: x_values is None, so determining appropriate x_axis")

                        if x_from_label is not None and len(y_values) == len(x_from_label):
                            # use default x-axis implied by x-axis label if sizing permits
                            x_values = x_from_label
                        elif config.x_axis_label is None and len(y_values) == len(x_live):
                            # if no label was provided and sizing fits, use live/selected axis
                            x_values = x_live
                        else:
                            # default to datapoints
                            x_values = np.array(list(range(len(y_values))), dtype=np.float32)

                    # log.debug(f"handle_response: updating curve {name}") # (x = %s, y = %s)", x_values, y_values)
                    try:
                        graph.set_data(self.plugin_curves[name], y=y_values, x=x_values)
                    except:
                        log.error(f"handle_response: Failed to update curve {name}", exc_info=1)

            ####################################################################
            # handle metadata and overrides                                    #
            ####################################################################

            self.apply_overrides(orig_pr, response)

            ####################################################################
            # handle commands                                                  #
            ####################################################################

            self.apply_commands(response)

            ####################################################################
            # handle signals                                                   #
            ####################################################################

            # MZ: I am 100% confident there is a better way to do this. I'm
            # starting by seeing if this does what I want.

            self.apply_signals(response) 

        except:
            log.error(f"handle_response: caught exception", exc_info=1)

    def apply_overrides(self, orig_pr, response):
        if orig_pr is None:
            return

        orig_pr.plugin_metadata = response.metadata
        if response.overrides is None:
            return

        for name in response.overrides:
            value = response.overrides[name]
            if name == "processed": 
                orig_pr.set_processed(value)
            elif name == "recordable_dark": 
                orig_pr.recordable_dark = value
            elif name == "recordable_reference": 
                orig_pr.recordable_reference = value
            else:
                log.error(f"unsupported override: {name}")

    def apply_commands(self, response):
        if response.commands is None:
            return

        for setting, value in response.commands:
            log.debug(f"applying {setting}")
            self.ctl.multispec.change_device_setting(setting, value)

    def apply_signals(self, response):
        if response.signals is None:
            return

        for signal in response.signals:
            log.debug(f"applying signal: {signal}")
            eval(signal)

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
                self.ctl.graph.remove_curve(self.plugin_curves[curve].name())
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

    def get_active_graph(self):
        module_info = self.get_current_module_info()
        if module_info and module_info.config:
            return self.graph_plugin if module_info.config.has_other_graph else self.ctl.graph
        return self.ctl.graph
