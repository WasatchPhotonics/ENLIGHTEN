import logging

from enlighten.EnlightenFeature import EnlightenFeature
from enlighten import common

if common.use_pyside2():
    from PySide2 import QtCore, QtGui
else:
    from PySide6 import QtCore, QtGui

log = logging.getLogger(__name__)

class CorrectionStatusFeature(EnlightenFeature):
    """
    Note that some of these may update outside of GUI events, so tick updates.

    Consider using QScrollArea.ensureWidgetVisible to auto-scroll ToolPalette to
    show a given feature if double-clicked.
    """

    ON = "ON"
    OFF = "off"

    def __init__(self, ctl):
        super().__init__(ctl)

        cfu = ctl.form.ui

        self.bt_minimize = cfu.pushButton_correction_status_minimize
        self.frame = cfu.frame_correction_status_1

        self.minimized = False

        self.bt_minimize.clicked.connect(self.minimize_callback)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.tick)
        self.timer.setSingleShot(True)

        # mapping of each correction's "short name" to their EnlightenFeature
        features = { "raman_shift": ctl.raman_shift_correction,
                     "ingaas":      ctl.ingaas_correction,
                     "etalon":      ctl.etalon_correction,
                     "srm":         ctl.raman_intensity_correction,
                     "edc":         ctl.edc,
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
                "value": self.OFF,
                "tooltip": None
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
            tt = corr["tooltip"]

            lb_value.setText(value)
            lb_value.setVisible(visible)
            lb_name.setVisible(visible)
            lb_value.setToolTip(tt)

    ############################################################################
    # Callbacks
    ############################################################################

    def minimize_callback(self):
        self.minimized = not self.minimized
        self.frame.setVisible(not self.minimized)

        tri = "up" if self.minimized else "down"
        icon = f":/greys/images/grey_icons/{tri}_triangle.svg"
        self.bt_minimize.setIcon(QtGui.QIcon(icon))

    def edc_notification(self):
        corr = self.corrections["edc"]
        corr["visible"] = self.ctl.edc.visible
        corr["value"] = self.ON if self.ctl.edc.enabled else self.OFF
        self.schedule_update()

    def ingaas_notification(self):
        corr = self.corrections["ingaas"]
        corr["visible"] = self.ctl.ingaas_correction.visible
        corr["value"] = self.ON if self.ctl.ingaas_correction.enabled else self.OFF
        self.schedule_update()

    def etalon_notification(self):
        corr = self.corrections["etalon"]
        corr["visible"] = self.ctl.etalon_correction.visible
        corr["value"] = self.ON if self.ctl.etalon_correction.enabled else self.OFF
        self.schedule_update()

    def srm_notification(self):
        corr = self.corrections["srm"]
        corr["value"] = self.ON if self.ctl.raman_intensity_correction.enabled else self.OFF
        corr["visible"] = self.ctl.raman_intensity_correction.is_supported()
        self.schedule_update()

    def dalai_notification(self):
        log.error("dalai not implemented")

    def baseline_notification(self):
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return
        enabled = spec.app_state.baseline_correction_enabled
        corr = self.corrections["baseline"]
        corr["value"] = self.ON if enabled else self.OFF
        corr["visible"] = True
        corr["tooltip"] = self.ctl.baseline_correction.current_algo_name if enabled else None
        self.schedule_update()

    def raman_shift_notification(self, notification):
        """ RamanShiftCorrectionFeature sends notifications with dict value """
        corr = self.corrections["raman_shift"]
        enabled = notification["enabled"]
        corr["value"] = self.ON if enabled else self.OFF
        corr["visible"] = notification["visible"]
        corr["tooltip"] = f"{notification['shift']:0.2f}cm⁻¹" if enabled else None
        self.schedule_update()
