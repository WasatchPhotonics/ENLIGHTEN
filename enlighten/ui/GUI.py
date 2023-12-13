import logging
import pyqtgraph

from enlighten import common

if common.use_pyside2():
    from PySide2 import QtGui
    from PySide2.QtWidgets import QMessageBox, QCheckBox, QDialog, QLineEdit, QDialogButtonBox, QVBoxLayout, QLabel
else:
    from PySide6 import QtGui
    from PySide6.QtWidgets import QMessageBox, QCheckBox, QDialog, QLineEdit, QDialogButtonBox, QVBoxLayout, QLabel

log = logging.getLogger(__name__)

##
# This is currently holding "GUI Utility" methods, but may grow to encapsulate
# more and more of the actual ENLIGHTEN GUI as we continue to prise functionality
# out of Controller.  
#
# Should probably end up "owning" Graph, Stylesheets etc, and be the single 
# object passed to classes which need those functions.
#
# Also provides the "skinning / themes" feature (dark/light-mode etc).
#
class GUI(object):

    SECTION = "graphs"

    def __init__(self, ctl):
        
        self.ctl = ctl

        self.multispec = None
        self.theme = self.ctl.config.get("theme", "theme")

        # apply ENLIGHTEN application stylesheet found in configured directory
        self.ctl.stylesheets.apply(self.ctl.form, "enlighten") 

        self.ctl.form.ui.pushButton_dark_mode.clicked.connect(self.dark_mode_callback)

        self.init_graph_color()
        self.update_theme()

    def init_graph_color(self, init=True):
        """
        call with init=True if this is being done before the graph widget was added to the scene
        otherwise call with init=False to repopulate the graph widget, forcing background color update
        """

        colors = ('w', 'k') if self.theme.startswith("dark") else ('k', 'w')
        pyqtgraph.setConfigOption('foreground', colors[0])
        pyqtgraph.setConfigOption('background', colors[1])

        if not init:
            # reset widgets so background color changes immediately
            self.ctl.graph.populate_scope_setup()
            self.ctl.graph.populate_scope_capture()

            # this is only a partial fix of #108, to finish it out
            # reinstantiate all instances of pyqtgraph.PlotWidget

            # that includes 
            # - Measurement Thumbnail Renderer
            # - AreaScanFeature
            # - DarkFeature (not to be confused with dark/light theme, this is dark as in Dark Measurement)
            # - DetectorTemperatureFeature
            # - LaserTemperatureFeature
            # - ReferenceFeature

            # it should be fairly easy to reference these using self.ctl...

    def dark_mode_callback(self):

        # toggle darkness
        self.theme = 'dark' if not (self.theme.startswith("dark")) else 'light'

        self.init_graph_color(False)
        self.update_theme()

    def update_theme(self):
        sfu = self.ctl.form.ui

        self.ctl.stylesheets.set_theme(self.theme)

        if self.theme.startswith("dark"):
            self.ctl.form.ui.pushButton_dark_mode.setToolTip("Seek the light!")
        else:
            self.ctl.form.ui.pushButton_dark_mode.setToolTip("Embrace the dark!")

        path = ":/application/images/enlightenLOGO"
        if not self.theme.startswith("dark"):
            path += "-light"
        path += ".png"

        pixmap = QtGui.QPixmap(path)
        sfu.label_application_logo.setPixmap(pixmap)

    def colorize_button(self, button, flag):
        if button is None:
            return

        if flag:
            self.ctl.stylesheets.apply(button, "red_gradient_button")
        else:
            self.ctl.stylesheets.apply(button, "gray_gradient_button")

    ##
    # @param widget: allows enlighten.ini to override color/style for named widgets
    def make_pen(self, widget=None, color=None, selected=False):
        if color is None and widget is not None:
            color = self.ctl.colors.get_by_widget(widget)
        
        # passed color may be a name
        if color is not None:
            named_color = self.ctl.colors.get_by_name(color)
            if named_color is not None:
                color = named_color

        if color is None:
            color = self.ctl.colors.get_next_random()

        style = self.ctl.config.get(self.SECTION, f"{widget}_pen_style")
        width = int(self.ctl.config.get(self.SECTION, f"{widget}_pen_width"))
        if selected and self.multispec is not None and self.multispec.count() > 1 and not self.multispec.hide_others:
            width = int(width * 2)

        return pyqtgraph.mkPen(color=color, width=width, style=style)

    def update_window_title(self, spec):
        ver   = common.VERSION
        model = spec.settings.full_model()
        sn    = spec.settings.eeprom.serial_number
        cnt   = self.multispec.count()

        title = f"ENLIGHTEN {ver}: {model} [{sn}]"

        if cnt > 1:
            title += " (+%d)" % (cnt - 1)

        self.ctl.form.setWindowTitle(title)

    def msgbox_with_checkbox(self, title, text, checkbox_text):
        cb = QCheckBox(checkbox_text, self.ctl.form)
        dialog = QMessageBox(self.ctl.form)
        dialog.setWindowTitle(title)
        dialog.setText(text)
        dialog.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        dialog.setIcon(QMessageBox.Warning)
        dialog.setCheckBox(cb)
        result = dialog.exec_()

        return { 
            "ok": result == QMessageBox.Ok,
            "checked": dialog.checkBox().isChecked()
        }

    def msgbox_with_lineedit_and_checkbox(self, title, label_text, lineedit_text, checkbox_text, checkbox_checked=False):
        dialog = QDialog(parent=self.ctl.form)
        dialog.setModal(True)
        dialog.setWindowTitle(title)
        dialog.setSizeGripEnabled(True)

        lb = QLabel(label_text, parent=dialog)

        le = QLineEdit(parent=dialog)
        le.setText(lineedit_text)

        cb = QCheckBox(checkbox_text, parent=dialog)
        cb.setChecked(checkbox_checked)

        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bb.accepted.connect(dialog.accept)
        bb.rejected.connect(dialog.reject)

        vb = QVBoxLayout(dialog)
        vb.addWidget(lb)
        vb.addWidget(le)
        vb.addWidget(cb)
        vb.addWidget(bb)

        result = dialog.exec_()
        return {
            "ok": result,
            "checked": cb.isChecked(),
            "lineedit": le.text() 
        }
