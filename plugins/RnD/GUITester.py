import logging
from EnlightenPlugin import EnlightenPluginBase
log = logging.getLogger(__name__)

class GUITester(EnlightenPluginBase):

    def get_configuration(self):
        self.name = "GUI Tester"
        self.streaming = False
        self.process_requests = False

        self.field(name="frame_scope_status_bar_white", direction="input", datatype=bool, callback=self.frame_scope_status_bar_white_callback)
        self.field(name="frame_id_results_white", direction="input", datatype=bool, callback=self.frame_id_results_white_callback)
        self.field(name="page_scope_capture_details_spectrum", direction="input", datatype=bool, callback=self.page_scope_capture_details_spectrum_callback)
        self.field(name="stackedWidget_scope_capture_details_spectrum", direction="input", datatype=bool, callback=self.stackedWidget_scope_capture_details_spectrum_callback)

    def flip(self, w):
        w.setVisible(not w.isVisible())
    
    def frame_scope_status_bar_white_callback(self):
        self.flip(self.ctl.form.ui.frame_scope_status_bar_white)

    def frame_id_results_white_callback(self):
        self.flip(self.ctl.form.ui.frame_id_results_white)

    def page_scope_capture_details_spectrum_callback(self):
        self.flip(self.ctl.form.ui.page_scope_capture_details_spectrum)

    def stackedWidget_scope_capture_details_spectrum_callback(self):
        self.flip(self.ctl.form.ui.stackedWidget_scope_capture_details_spectrum_callback)
