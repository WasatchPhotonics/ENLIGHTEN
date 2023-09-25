import multiprocessing
from os import path
import platform
import argparse
import logging
import signal
import time
import sys
import os
import re

if "macOS" in platform.platform():
    import matplotlib
    import matplotlib.pyplot as plt
    matplotlib.use('TkAgg')

os.environ["BLINKA_FT232H"]="1" # used to allow SPI with FT232H

# Required runtime imports for compiled .exe (see qsvg4.dll in InnoSetup)
from PySide2 import QtGui, QtCore, QtWidgets, QtSvg, QtXml
from PySide2.QtWidgets import QSplashScreen
from PySide2.QtGui import QPixmap, QImageReader

from enlighten.ui.BasicWindow import BasicWindow
from enlighten import common
from wasatch.DeviceID import DeviceID
from wasatch   import applog

log = logging.getLogger(__name__)


def signal_handler(signal, frame):
    log.critical('Interrupted by Ctrl-C')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

##
# This class encapsulates processing of command-line arguments, instantiates a 
# Controller then passes control to the Qt framework.
#
class EnlightenApplication(object):

    def __init__(self,testing=False):
        self.app = QtWidgets.QApplication(["windows:dpiawareness=1"])

        self.parser = self.create_parser()
        self.controller = None
        self.args = None
        self.testing = testing
        self.exit_code = 0

    ## Parse command-line arguments
    def parse_args(self, argv):
        log.debug("Process args: %s", argv)
        self.args = self.parser.parse_args(argv)
        if self.args is None:
            return

        # As far as I can tell, we've always passed uppercase strings to 
        # logging.setLevel(), though this seems to imply that shouldn't work:
        # https://stackoverflow.com/a/15368084
        self.args.log_level = self.args.log_level.upper()

        # logfile directory
        dir_ = common.get_default_data_dir()
        if self.args.logfile is None:
            try:
                os.mkdir(dir_)
            except:
                pass 
            if os.path.isdir(dir_):
                self.args.logfile = os.path.join(dir_, "enlighten.log")

        return self.args

    ## Defines the command-line arguments and their defaults
    #
    def create_parser(self):
        parser = argparse.ArgumentParser(description="acquire from specified device, display line graph")
        parser.add_argument("--log-level",          type=str, default="info",       help="logging level",    choices=['debug', 'info', 'warning', 'error', 'critical'])
        parser.add_argument("--log-append",         action="store_true",            help="append to existing logfile")
        parser.add_argument("--logfile",            type=str,                       help="Explicit path for the logfile")
        parser.add_argument("--max-memory-growth",  type=int, default=0,            help="Automatically exit after this percent memory growth (0 for never, 100 = doubling)")
        parser.add_argument("--run-sec",            type=int, default=0,            help="Automatically exit after this many seconds (0 for never)")
        parser.add_argument("--serial-number",      type=str,                       help="only connect to specified serial number")
        parser.add_argument("--set-all-dfu",        action="store_true",            help="set spectrometers to DFU mode as soon as they connect")
        parser.add_argument("--stylesheet-path",    type=str,                       help="Path to CSS directory")
        parser.add_argument("--headless",           action="store_true",            help="Run Enlighten without GUI")
        parser.add_argument("--plugin",             type=str,                       help="Plugin name")
        return parser

    ##
    # Spawn a QApplication, instantiate a Controller (which will instantiate
    # the Form within the QApplication), then call the QApplication's exec_()
    # method (which will tick QWidgets defined by the form in an event loop until 
    # something generates an exit signal).
    def run(self):

        # instantiate form (a QMainWindow with named "MainWindow")
        # UI needs to be imported here in order to access qresources for the splash screen
        self.form = BasicWindow(title="ENLIGHTEN %s" % common.VERSION, headless=self.args.headless)

        pixmap = QPixmap(":/application/images/splash.png")
        pixmap = pixmap.scaled(pixmap.width()/2, pixmap.height()/2) # eyeballed, default seemed to take whole screen
        self.splash = QSplashScreen()
        self.splash.setPixmap(pixmap)
        self.splash.show()

        self.main_logger = applog.MainLogger(self.args.log_level, logfile=self.args.logfile, timeout_sec=5, enable_stdout=not self.testing, append=self.args.log_append)

        # This violates convention but Controller has so many imports that it takes a while to import
        # This needs to occur here because the Qt app needs to be made before the splash screen
        # So it has to occur in this function after both the app creation and splash screen creation
        from enlighten.Controller import Controller

        log.debug("platform = %s", platform.platform())

        # instantiate the enlighten.Controller
        self.controller = Controller(
            app               = self.app,
            log_level         = self.args.log_level,
            log_queue         = self.main_logger.log_queue,
            max_memory_growth = self.args.max_memory_growth,
            run_sec           = self.args.run_sec,
            serial_number     = self.args.serial_number,
            stylesheet_path   = self.args.stylesheet_path,
            set_all_dfu       = self.args.set_all_dfu,
            form              = self.form,
            splash            = self.splash,
            headless          = self.args.headless,
            autoload_plugin   = self.args.plugin)
        # This requires explanation.  This is obviously a Qt "connect" binding,
        # but Controller is not a Qt widget, and does not inherit from/extend 
        # anything.  What gives?  See Controller.create_signals, which actually
        # adds the controller.control_exit_signal attribute as a QObject with one
        # "exit" signal, which we here connect to its callback.  
        #
        # This could also have been achieved by giving the controller a handle to 
        # this "self" EnlightenApplication instance, so that controller could do 
        # the closeEvent() stuff internally (which is how we later refactored 
        # ConfirmWidget).
        #####
        # The sim_spec code is used for debugging with the test framework during peculiar issues
        #####
        self.controller.control_exit_signal.exit.connect(self.closeEvent)
        #sim_spec = DeviceID(label="MOCK:WP-00887:WP-00887-mock.json")
        #self.controller.connect_new(sim_spec)
        # pass off control to Qt to manage its objects until application shutdown
        self.splash.finish(self.controller.form)
        if not self.testing:
            self.app.exec_()

        if not self.testing:
            print("back from app.exec_")
            print("returning from EnlightenApplication.run with exit_code %d" % self.exit_code)
            return self.controller.exit_code

    ## Catch the exit signal from the control application, and call 
    #  QApplication Quit. 
    def closeEvent(self): 
        print("EnlightenApplication.closeEvent: received control_exit_signal")

        self.exit_code = self.controller.exit_code
        print("EnlightenApplication.closeEvent: exit_code %d" % self.exit_code)


        # shutdown the logger
        self.main_logger.close()
        time.sleep(1)

        # call applog.explicit_log_close() here?
        applog.explicit_log_close()

        # quit the QApplication (only need one of these, not sure which is better)
        print("EnlightenApplication.closeEvent: quitting app")
        self.app.quit()

        print("EnlightenApplication.closeEvent: exiting with exit_code %d" % self.exit_code)
        sys.exit(self.exit_code)

def main(argv):
    enlighten = EnlightenApplication()
    enlighten.parse_args(argv[1:])
    try:
        ec = enlighten.run()
    except SystemExit as exc:
        log.critical("Exception in Enlighten.main", exc_info=1)
        print("Exception in Enlighten.main: %s" % str(exc))
        ec = exc.code
    return ec

if __name__ == "__main__":
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1" 
    multiprocessing.freeze_support() # needed on Win32

    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)

    ec = main(sys.argv)
    print("Exiting main exit_code %d" % ec)
    sys.exit(ec)
