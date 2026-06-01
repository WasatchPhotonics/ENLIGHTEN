from enighten.EnlightenFeature import EnlightenFeature

class DiagnosticFeature(EnlightenFeature):

    def __init__(self, ctl):
        super().__init__(ctl)

        self.cb_enable = cfu.checkBox_diagnostic_mode

        self.enabled = False

        self.cb_enable.stateChanged.connect(self.update_settings)

    def update_settings(self):
        self.enabled = self.cb_enable.isChecked()

        for spec in self.ctl.multispec.get_all_spectrometers():
            spec.settings.diagnostic_mode = self.enabled
