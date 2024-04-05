import logging
import pyqtgraph

from enlighten import common

if common.use_pyside2():
    from PySide2 import QtGui
    from PySide2.QtWidgets import QMessageBox, QCheckBox, QDialog, QLineEdit, QDialogButtonBox, QVBoxLayout, QLabel, QTextEdit
else:
    from PySide6 import QtGui
    from PySide6.QtWidgets import QMessageBox, QCheckBox, QDialog, QLineEdit, QDialogButtonBox, QVBoxLayout, QLabel, QTextEdit

log = logging.getLogger(__name__)

class GUI:
    """
    This is currently holding "GUI Utility" methods, but may grow to encapsulate
    more and more of the actual ENLIGHTEN GUI as we continue to prise functionality
    out of Controller.  
    
    Should probably end up "owning" Graph, Stylesheets etc, and be the single 
    object passed to classes which need those functions.
    
    Also provides the "skinning / themes" feature (dark/light-mode etc).
    """

    SECTION = "graphs"

    def __init__(self, ctl):
        self.ctl = ctl
        cfu = ctl.form.ui

        self.theme = self.ctl.config.get("theme", "theme")
        log.debug(f"init: theme {self.theme}")

        # apply ENLIGHTEN application stylesheet found in configured directory
        self.ctl.stylesheets.apply(self.ctl.form, "enlighten") 

        cfu.pushButton_dark_mode.clicked.connect(self.dark_mode_callback)
        cfu.pushButton_dark_mode.setWhatsThis("Toggles between 'dark mode' (default) and 'light mode'")

        self.init_graph_color()
        self.update_theme()

    def init_graph_color(self, init=True):
        """
        Call with init=True if this is being done BEFORE the graph widget was 
        added to the scene, otherwise call with init=False to repopulate the 
        graph widget, forcing background color update.
        """
        colors = ('w', 'k') if self.theme.startswith("dark") else ('k', 'w')
        pyqtgraph.setConfigOption('foreground', colors[0])
        pyqtgraph.setConfigOption('background', colors[1])

        if not init:

            # reset widgets so background color changes immediately
            # MZ: I think this overwrites existing curve objects...?
            if False:
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
        log.debug(f"dark_mode_callback: theme was {self.theme}")
        self.theme = 'dark' if not (self.theme.startswith("dark")) else 'light'
        log.debug(f"dark_mode_callback: theme now {self.theme}")

        self.init_graph_color(False) 
        
        self.update_theme()
        log.debug("dark_mode_callback: done")

    def update_theme(self):
        log.debug(f"update_theme: start ({self.theme})")
        self.ctl.stylesheets.set_theme(self.theme)

        cfu = self.ctl.form.ui
        if self.theme.startswith("dark"):
            cfu.pushButton_dark_mode.setToolTip("Seek the light!")
        else:
            cfu.pushButton_dark_mode.setToolTip("Embrace the dark!")

        path = ":/application/images/enlightenLOGO"
        if not self.theme.startswith("dark"):
            path += "-light"
        path += ".png"

        log.debug(f"logo {path}")
        pixmap = QtGui.QPixmap(path)
        cfu.label_application_logo.setPixmap(pixmap)
        log.debug("update_theme: done")

    def colorize_button(self, button, flag, tristate=False):
        if button is None:
            return

        if tristate and flag is None:
            self.ctl.stylesheets.apply(button, "orange_gradient_button")
        elif flag:
            self.ctl.stylesheets.apply(button, "red_gradient_button")
        else:
            self.ctl.stylesheets.apply(button, "gray_gradient_button")
    
    def make_pen(self, widget=None, color=None, selected=False):
        """ @param widget: allows enlighten.ini to override color/style for named widgets """
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
        if selected and self.ctl.multispec and self.ctl.multispec.count() > 1 and not self.ctl.multispec.hide_others:
            width = int(width * 2)

        return pyqtgraph.mkPen(color=color, width=width, style=style)

    def update_window_title(self, spec):
        ver   = common.VERSION
        model = spec.settings.full_model()
        sn    = spec.settings.eeprom.serial_number
        cnt   = self.ctl.multispec.count()

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
            "ok": result == QMessageBox.Ok, # note we don't use QDialogButtonBox
            "checked": dialog.checkBox().isChecked()
        }

    def msgbox_with_lineedit(self, title, label_text, lineedit_text):
        dialog = QDialog(parent=self.ctl.form)
        dialog.setModal(True)
        dialog.setWindowTitle(title)
        dialog.setSizeGripEnabled(True)

        lb = QLabel(label_text, parent=dialog)

        le = QLineEdit(parent=dialog)
        le.setText(lineedit_text)

        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bb.accepted.connect(dialog.accept)
        bb.rejected.connect(dialog.reject)

        vb = QVBoxLayout(dialog)
        vb.addWidget(lb)
        vb.addWidget(le)
        vb.addWidget(bb)

        result = dialog.exec_()
        log.debug(f"msgbox_with_lineedit: result = {result}")

        retval = {
            "ok": result == QDialog.Accepted,
            "lineedit": le.text() 
        }
        log.debug(f"msgbox_with_lineedit: retval = {retval}")

        return retval

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
            "ok": result == QDialog.Accepted,
            "checked": cb.isChecked(),
            "lineedit": le.text() 
        }

    def msgbox_with_textedit(self, title, label_text, textedit_text):
        dialog = QDialog(parent=self.ctl.form)
        dialog.setModal(True)
        dialog.setWindowTitle(title)
        dialog.setSizeGripEnabled(True)

        lb = QLabel(label_text, parent=dialog)

        te = QTextEdit(parent=dialog)
        te.setText(textedit_text)
        te.setReadOnly(True)

        vb = QVBoxLayout(dialog)
        vb.addWidget(lb)
        vb.addWidget(te)

        dialog.exec_()
        # no return value, this is "display-only"
