from PySide2 import QtCore, QtWidgets

import logging
import re
import os

from enlighten import common

log = logging.getLogger(__name__)

##
# Encapsulate operations managing files, directory trees etc.
class FileManager(object):
    
    FILTER = "CSV (*.csv);;JSON (*.json);;SPC (*.spc);;ASC (*.asc)"

    ##
    # @param form for QDialogs requiring a parent
    # @param marquee for displaying status information to the user
    def __init__(self,
            form,
            marquee):
        self.form           = form       
        self.marquee        = marquee
        #self.progress_bar   = progress_bar

        self.files_to_load = []
        self.last_load_dir = common.get_default_data_dir()
        self.load_interval_ms = 10
        self.load_callback = None
        self.load_count = 0

        self.file_loader_timer = QtCore.QTimer()
        self.file_loader_timer.setSingleShot(True)
        self.file_loader_timer.timeout.connect(self.file_loader_tick)

    def get_pathname(self, caption="Select file to load", filter=None):
        if filter is None:
            filter = FileManager.FILTER
        result = QtWidgets.QFileDialog.getOpenFileName(self.form, caption, self.last_load_dir, filter)
        if result is None or len(result) < 1:
            return
        pathname = result[0]
        if pathname is None or len(pathname) == 0:
            return
        return pathname

    def get_directory(self):
        dialog = QtWidgets.QFileDialog()
        dialog.setFileMode(QtWidgets.QFileDialog.Directory)
        dialog.setOption(QtWidgets.QFileDialog.ShowDirsOnly)
        return dialog.getExistingDirectory()
        
    ## not currently used
    def load_file(self, caption="Select file to load", filter=None):
        if filter is None:
            filter = FileManager.FILTER
        pathname = self.get_pathname(caption, filter)
        if pathname is None:
            return

        with open(pathname, "r") as f:
            return f.read()

    ## display a file selection dialog, let the user select one or more files, 
    # then load them up 
    def select_files_to_load(self, callback):
        self.load_count = 0

        result = QtWidgets.QFileDialog.getOpenFileNames(self.form, 
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
            self.marquee.info("loaded %d files" % self.load_count)
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
