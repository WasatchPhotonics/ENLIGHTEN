import logging
import os

from enlighten import common

if common.use_pyside2():
    from PySide2 import QtCore, QtWidgets
else:
    from PySide6 import QtCore, QtWidgets

log = logging.getLogger(__name__)

##
# Encapsulate operations managing files, directory trees etc.
class FileManager:
    
    FILTER = "CSV (*.csv);;JSON (*.json);;SPC (*.spc);;ASC (*.asc)"

    def __init__(self, ctl):
        self.ctl = ctl

        self.files_to_load = []
        self.last_load_dir = common.get_default_data_dir()
        self.load_interval_ms = 10
        self.load_callback = None
        self.load_count = 0

        self.file_loader_timer = QtCore.QTimer()
        self.file_loader_timer.setSingleShot(True)
        self.file_loader_timer.timeout.connect(self.file_loader_tick)

    def save_dialog(self, filename=None, caption=None, dir_=None):
        """ Prompt user to navigate to a folder and enter a filename to save a single file. """
        if dir_ is None:
            dir_ = self.ctl.save_options.generate_today_dir()
        if filename is not None:
            dir_ = os.path.join(dir_, filename)
        result = QtWidgets.QFileDialog.getSaveFileName(parent=self.ctl.form, caption=caption, dir=dir_)
        return result[0]

    def get_pathname(self, caption="Select file to load", filter_=None):
        if filter_ is None:
            filter_ = FileManager.FILTER
        result = QtWidgets.QFileDialog.getOpenFileName(self.ctl.form, caption, self.last_load_dir, filter_)
        if result is None or len(result) < 1:
            return
        pathname = result[0]
        if pathname is None or len(pathname) == 0:
            return
        return pathname

    def get_directory(self):
        dialog = QtWidgets.QFileDialog(parent=self.ctl.form)
        dialog.setFileMode(QtWidgets.QFileDialog.Directory)
        dialog.setOption(QtWidgets.QFileDialog.ShowDirsOnly)
        return dialog.getExistingDirectory()
        
    ## not currently used
    def load_file(self, caption="Select file to load", filter_=None):
        if filter_ is None:
            filter_ = FileManager.FILTER
        pathname = self.get_pathname(caption, filter_)
        if pathname is None:
            return

        with open(pathname, "r") as f:
            return f.read()

    ## display a file selection dialog, let the user select one or more files, 
    # then load them up 
    def select_files_to_load(self, callback):
        self.load_count = 0

        result = QtWidgets.QFileDialog.getOpenFileNames(self.ctl.form, 
            "Select spectra to load", 
            self.last_load_dir,
            FileManager.FILTER)
        if result is None or len(result) == 0:
            return

        filenames = result[0] 
        if filenames is None or len(filenames) == 0:
            return

        self.load_callback = callback

        self.files_to_load = filenames
        log.debug("files_to_load: %s", self.files_to_load)

        # cache the selected directory
        self.last_load_dir = os.path.dirname(self.files_to_load[0])
        log.debug("last_load_dir = %s", self.last_load_dir)

        #self.progress_bar.setMaximum(len(self.files_to_load))
        #self.progress_bar.setValue(0)

        self.file_loader_timer.start(500)

    ## Pop off a filename, load it into the widget list, and update the progress bar. 
    def file_loader_tick(self):
        # are there more files to load?
        if not self.files_to_load:
            log.debug("finished loading files")
            #self.progress_bar.setVisible(False)
            self.ctl.marquee.info("loaded %d files" % self.load_count)
            return

        ########################################################################
        # load next file
        ########################################################################

        pathname = self.files_to_load.pop(0)
        log.info("Loading %s" % pathname)

        self.load_callback(pathname)

        self.load_count += 1
        #self.progress_bar.setValue(self.load_count)

        # schedule load of the next file
        log.debug("scheduling load of the next file")
        self.file_loader_timer.start(self.load_interval_ms)
