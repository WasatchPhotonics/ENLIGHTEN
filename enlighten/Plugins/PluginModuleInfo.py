import re
import os
import logging
import importlib.util

from .PluginValidator import PluginValidator

log = logging.getLogger(__name__)

##
# Encapsulates information about a specific ENLIGHTEN Plug-In (child of 
# PluginBaseClass). This is information at the "compiled .pyc bytecode" level, 
# and does not include (easily accessible) information about "what" the plug-in
# does, what fields it inputs or outputs, etc.  This is information about the
# code itself: the Python module, the Python class, and the final instantiated
# object.
#
# As a goal, we're trying to persist module information within ENLIGHTEN, so we
# don't have to re-initialize heavyweight plugins when switching between them.
#
# However, we're NOT bothering to persist the "GUI" side of these modules, i.e.
# pyqtgraph charts and curves, Qt widgets etc.
#
# @see https://stackoverflow.com/questions/67631/how-to-import-a-module-given-the-full-path
# @see https://docs.python.org/3/library/types.html#types.ModuleType
class PluginModuleInfo:

    def __init__(self, pathname, package, filename, ctl):
        
        self.pathname = pathname                                # /path/to/Foo.py
        self.package = package
        self.filename = filename

        (self.module_name, _) = os.path.splitext(self.filename) # Foo

        self.full_module_name = re.sub("/", ".", f"{package}.{self.module_name}")
        # log.debug(f"full module_name = {self.full_module_name}")

        # populated by load()
        self.module_specification = None    # Python importlib type
        self.module_obj = None              # the loaded module object
        self.class_obj = None               # e.g. Foo.Foo (the class within the module object)
        self.instance = None                # a single instance of Foo.Foo() 
        self.config = None                  # an instance of EnlightenPluginConfiguration
        self.name = None

        self.ctl = ctl

        log.debug("instantiated %s", str(self))

    ##
    # Import the selected Python module containing the plugin class.
    #
    # Loads and stores the imported "module object" (executable code containing 
    # one or more classes), instantiates the class, then loads the configuration.
    #
    # @returns True on success
    # @throws all kinds of exceptions, which we let PluginController catch so it
    #         can display them to the user / plugin author
    def load(self):
        
        # log.debug("loading %s", self.full_module_name)
        self.module_specification = importlib.util.spec_from_file_location(self.full_module_name, self.pathname)
        self.module_obj = importlib.util.module_from_spec(self.module_specification)
        self.module_specification.loader.exec_module(self.module_obj)
        self.class_obj = getattr(self.module_obj, self.module_name)
        self.name = self.full_module_name

        # log.debug("instantiating %s (%s)", self.module_name, self.class_obj)
        self.instance = self.class_obj(self.ctl)

        # An OOP plugin will return an object itself
        # A functional plugin will define its configuration via calls only and return None
        # The calls will generate instance.configuration_obj behind the scenes
        self.config = self.instance.get_configuration_obj()
        if self.config is None:
            log.error("unable to load configuration")
            return False

        if not PluginValidator.validate_config(self.config, self):
            log.error("invalid configuration")
            return False

        log.debug("loaded EnlightenPluginConfiguration { name %s, has_other_graph %s, x_axis %s, y_axis %s, is_blocking %s, graph_type %s }",
            self.config.name, self.config.has_other_graph, self.config.x_axis_label, self.config.y_axis_label, self.config.is_blocking, self.config.graph_type)
        return True

    def is_loaded(self):
        return self.config is not None

    def __str__(self):
        return "PluginModuleInfo { full_module_name %s, loaded %s, pathname %s }" % (
            self.full_module_name, 
            self.is_loaded(),
            self.pathname)
