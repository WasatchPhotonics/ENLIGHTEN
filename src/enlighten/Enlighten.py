import multiprocessing
from os import path
import platform
import argparse
import logging
import signal
import psutil
import time
import sys
import os
import re

if "macOS" in platform.platform():
    import matplotlib
    import matplotlib.pyplot as plt
    matplotlib.use('TkAgg')

os.environ["BLINKA_FT232H"]="1" # used to allow SPI with FT232H

from enlighten import common
from enlighten.ui.BasicWindow import BasicWindow
from enlighten.assets.uic_qrc import splashscreens_rc

from wasatch.DeviceID import DeviceID
from wasatch   import applog

if common.use_pyside2():
    from PySide2 import QtGui, QtCore, QtWidgets, QtSvg, QtXml
    from PySide2.QtWidgets import QSplashScreen
    from PySide2.QtGui import QPixmap, QImageReader
else:
    from PySide6 import QtGui, QtCore, QtWidgets, QtSvg, QtXml
    from PySide6.QtWidgets import QSplashScreen
    from PySide6.QtGui import QPixmap, QImageReader

log = logging.getLogger(__name__)

def signal_handler(signal, frame):
    log.critical('Interrupted by Ctrl-C')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

##
# This class encapsulates processing of command-line arguments, instantiates a
# Controller then passes control to the Qt framework.
#
class EnlightenApplication:

    def __init__(self,testing=False):
        self.app = QtWidgets.QApplication()

        self.parser = self.create_parser()
        self.controller = None
        self.args = None
        self.testing = testing
        self.exit_code = 0

    ## Parse command-line arguments
    def parse_args(self, argv):

        # SB: this doesn't show up anywhere bc logging is not yet configured
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
    def create_parser(self):
        parser = argparse.ArgumentParser(description="ENLIGHTEN %s" % common.VERSION,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

        parser.add_argument("--log-level",         type=str, default="info",      help="logging level", choices=['debug', 'info', 'warning', 'error', 'critical'])
        parser.add_argument("--log-append",        type=str, default="False",     help="append to existing logfile", choices=["False", "True", "LIMIT"])
        parser.add_argument("--logfile",           type=str,                      help="explicit path for the logfile")
        parser.add_argument("--max-memory-growth", type=int, default=0,           help="automatically exit after this percent memory growth (0 for never, 100 = doubling)")
        parser.add_argument("--max-thumbnails",    type=int,                      help="maximum number of thumbnails in measurement clipboard", default=os.environ.get("ENLIGHTEN_MAX_THUMBNAILS", 500))
        parser.add_argument("--run-sec",           type=int, default=0,           help="automatically exit after this many seconds (0 for never)")
        parser.add_argument("--serial-number",     type=str,                      help="only connect to specified serial number")
        parser.add_argument("--set-all-dfu",       action="store_true",           help="set spectrometers to DFU mode as soon as they connect")
        parser.add_argument("--stylesheet-path",   type=str,                      help="path to CSS directory")
        parser.add_argument("--window-state",      type=str, default="maximized", help="window initial state", choices=["normal", "maximized", "fullscreen", "minimized"])
        parser.add_argument("--plugin",            type=str,                      help="plugin name to start enabled")
        parser.add_argument("--password",          type=str,                      help="authentication password", default=os.environ.get("ENLIGHTEN_PASSWORD"))
        parser.add_argument("--start-batch",       action="store_true",           help="start a Batch Collection as soon as a spectrometer connects")

        return parser

    def run(self):
        # instantiate form (a QMainWindow with name "MainWindow")
        self.form = BasicWindow(title="ENLIGHTEN™ %s" % common.VERSION)

        pixmap = QPixmap(":/splashscreens/Enlighten-loading-90p.png")
        pixmap = pixmap.scaled(pixmap.width()/2, pixmap.height()/2)
        self.splash = QSplashScreen()
        self.splash.setPixmap(pixmap)
        self.splash.show()

        self.main_logger = applog.MainLogger(
            "DEBUG",    # we always start in debug logging to catch startup issues
            logfile=self.args.logfile,
            timeout_sec=5,
            enable_stdout=not self.testing,
            append_arg=str(self.args.log_append)
        )

        # now that we've configured the logger, redirect stdout to our logger
        # (so we can use Tensorflow without a console window)
        sys.stdout = common.FakeOutputHandle("FakeStdout")

        if "windows" in platform.platform().lower():
            enlightens = []
            for process in psutil.process_iter(['pid', 'name']):
                proc_pid = process.info['pid']
                proc_name = process.info['name']
                if "enlighten.exe" in proc_name.lower():
                    enlightens.append(f"pid {proc_pid} {proc_name}")
            if len(enlightens) > 1:
                log.critical(f"too many ENLIGHTENs, exiting: {enlightens}")
                common.msgbox("Too many ENLIGHTEN™s detected, exiting", title="ENLIGHTEN™ Tribble Detector", detail="\n".join(enlightens))
                return 1

        # This violates convention but Controller has so many imports that it 
        # takes a while to import. We're choosing to import it here, AFTER
        # displaying the splash screen, so you have something pretty to look at
        # while we load all those BusinessObjects.
        from enlighten.Controller import Controller

        log.debug("platform = %s", platform.platform())

        # instantiate the enlighten.Controller
        self.controller = Controller(
            app               = self.app,
            log_level         = self.args.log_level,
            log_queue         = self.main_logger.log_queue,
            max_memory_growth = self.args.max_memory_growth,
            max_thumbnails    = self.args.max_thumbnails,
            run_sec           = self.args.run_sec,
            serial_number     = self.args.serial_number,
            stylesheet_path   = self.args.stylesheet_path,
            set_all_dfu       = self.args.set_all_dfu,
            form              = self.form,
            splash            = self.splash,
            window_state      = self.args.window_state,
            start_batch       = self.args.start_batch,
            password          = self.args.password,
            plugin            = self.args.plugin)

        # This requires explanation.  This is obviously a Qt "connect" binding,
        # but Controller is not a Qt widget, and does not inherit from/extend
        # anything.  What gives?  See Controller.create_signals, which actually
        # adds the controller.control_exit_signal attribute as a QObject with one
        # "exit" signal, which we here connect to its callback.
        #
        # This could also have been achieved by giving the controller a handle to
        # this "self" EnlightenApplication instance, so that Controller could do
        # the closeEvent() stuff internally.
        self.controller.control_exit_signal.exit.connect(self.closeEvent)

        # The sim_spec code is used for debugging with the test framework during peculiar issues
        # sim_spec = DeviceID(label="MOCK:WP-00887:WP-00887-mock.json")
        # self.controller.connect_new(sim_spec)

        # pass off control to Qt to manage its objects until application shutdown
        self.splash.finish(self.controller.form)
        if not self.testing:
            if common.use_pyside2():
                self.app.exec_()
            else:
                self.app.exec()

        if not self.testing:
            print("back from app.exec")
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

    def hide_console(self):
        """
        This isn't needed on Win10 (where pyinstaller's --hide-console hide-early works,
        though not hide-late), but apparently is on Win11 (where hide-early doesn't work;
        not sure about hide-late).

        Calling for coverage on Win11.

        @see https://github.com/pyinstaller/pyinstaller/issues/7729#issuecomment-1605503018
        @see https://github.com/pyinstaller/pyinstaller/pull/7735
        """
        if sys.platform == 'win32':
            import ctypes
            import ctypes.wintypes

            # Get console window
            console_window = ctypes.windll.kernel32.GetConsoleWindow()
            if console_window:
                # Check if console is owned by this process...
                process_id = ctypes.windll.kernel32.GetCurrentProcessId()
                console_process_id = ctypes.wintypes.DWORD()
                ctypes.windll.user32.GetWindowThreadProcessId(console_window, ctypes.byref(console_process_id))
                console_process_id = console_process_id.value
                if process_id == console_process_id:
                    # ... and if it is, minimize it
                    ctypes.windll.user32.ShowWindow(console_window, 2)  # SW_SHOWMINIMIZED

    def chdir(self, script_path):
        """
        ENLIGHTEN loads various settings from its own enlighten/assets/
        example_code distribution, which it accesses through relative
        paths, and it can't find those if run from another directory.
        """
        if script_path.endswith(".py"):
            # run as "python path/to/scripts/enlighten.py", so want "path/to"
            root_dir = os.path.join(os.path.dirname(script_path), "..")
        else:
            # presumably some kind of compiled executable
            root_dir = os.path.dirname(script_path)

        log.debug(f"chdir to {root_dir}")
        try:
            os.chdir(root_dir)
        except:
            log.error(f"error changing to {root_dir}")

def main(argv):
    enlighten = EnlightenApplication()
    enlighten.parse_args(argv[1:])
    enlighten.chdir(script_path=argv[0])
    enlighten.hide_console()
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

    ec = main(sys.argv)
    print("Exiting main exit_code %d" % ec)
    sys.exit(ec)
