import logging

from enlighten.EnlightenFeature import EnlightenFeature
from enlighten import common

if common.use_pyside2():
    from PySide2 import QtCore
else:
    from PySide6 import QtCore

log = logging.getLogger(__name__)

class CorrectionStatusFeature(EnlightenFeature):
    """
    Note that some of these may update outside of GUI events, so tick updates.

    Consider using QScrollArea.ensureWidgetVisible to auto-scroll ToolPalette to
    show a given feature if double-clicked.
    """

    def __init__(self, ctl):
        super().__init__(ctl)

        cfu = ctl.form.ui

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.tick)
        self.timer.setSingleShot(True)

        # mapping of each correction's "short name" to their EnlightenFeature
        features = { "raman_shift": ctl.raman_shift_correction,
                     "ingaas":      ctl.ingaas_correction,
                     "etalon":      ctl.etalon_correction,
                     "srm":         ctl.raman_intensity_correction,
                     "dalai":       ctl.dalai,
                     "baseline":    ctl.baseline_correction }
        
        # generate map of "short names" to everything we need to track
        self.corrections = {}
        for name, feature in features.items():
            callback = getattr(self, f"{name}_notification")
            self.corrections[name] = {
                "label_value": getattr(cfu, f"label_correction_status_{name}"),
                "label_name":  getattr(cfu, f"label_correction_status_{name}_label"),
                "callback": callback,
                "visible": True,
                "value": "OFF",
            }
            feature.register_observer(callback)

    def schedule_update(self):
        self.timer.start(10)

    def tick(self):
        for name, corr in self.corrections.items():
            lb_value = corr["label_value"]
            lb_name = corr["label_name"]
            visible = corr["visible"]
            value = corr["value"]

            lb_value.setText(value)
            lb_value.setVisible(visible)
            lb_name.setVisible(visible)

    ############################################################################
    # Callbacks
    ############################################################################

    def ingaas_notification(self, notification):
        log.error("ingaas not implemented")

    def etalon_notification(self, notification):
        log.error("etalon not implemented")

    def srm_notification(self, notification):
        log.error("srm not implemented")

    def dalai_notification(self, notification):
        log.error("dalai not implemented")

    def baseline_notification(self, notification):
        log.error("baseline not implemented")

    def raman_shift_notification(self, notification):
        corr = self.corrections["raman_shift"]

        corr["value"] = "ON" if notification["enabled"] else "OFF"
        corr["visible"] = notification["visible"]

        self.schedule_update()
