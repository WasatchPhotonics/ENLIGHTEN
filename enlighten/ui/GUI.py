import logging
import pyqtgraph
from PySide6 import QtGui

from enlighten.ui.TimeoutDialog import TimeoutDialog
from enlighten import common

from wasatch import utils as wasatch_utils

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

    def __init__(self, 
            colors,
            config,
            form,
            stylesheet_path,
            stylesheets,

            bt_dark_mode):

        self.colors       = colors
        self.config       = config
        self.form         = form
        self.stylesheets  = stylesheets

        self.bt_dark_mode = bt_dark_mode

        self.multispec = None
        self.dark_mode = True 
        self.marquee = None # post-construction

        # apply ENLIGHTEN application stylesheet found in configured directory
        self.stylesheets.apply(self.form, "enlighten") 

        self.bt_dark_mode.clicked.connect(self.dark_mode_callback)

        self.init_graph_color()

    def init_graph_color(self):
        self.dark_mode = self.config.get_bool(self.SECTION, "dark_mode", default=True)

        colors = ('w', 'k') if self.dark_mode else ('k', 'w')
        pyqtgraph.setConfigOption('foreground', colors[0])
        pyqtgraph.setConfigOption('background', colors[1])
        self.update_theme()

    def dark_mode_callback(self):
        self.dark_mode = not self.dark_mode
        self.config.set(self.SECTION, "dark_mode", self.dark_mode)

        if self.marquee:
            self.marquee.info(f"Graphs will use {'dark' if self.dark_mode else 'light'} backgrounds when ENLIGHTEN restarts.")

        self.update_theme()

    def update_theme(self):
        sfu = self.form.ui

        self.stylesheets.set_dark_mode(self.dark_mode)

        if self.dark_mode:
            self.bt_dark_mode.setToolTip("Seek the light!")
        else:
            self.bt_dark_mode.setToolTip("Embrace the dark!")

        path = ":/application/images/enlightenLOGO"
        if not self.dark_mode:
            path += "-light"
        path += ".png"

        pixmap = QtGui.QPixmap(path)
        sfu.label_application_logo.setPixmap(pixmap)

    def colorize_button(self, button, flag):
        if button is None:
            return

        if wasatch_utils.truthy(flag):
            self.stylesheets.apply(button, "red_gradient_button")
        else:
            self.stylesheets.apply(button, "gray_gradient_button")

    ##
    # @param widget: allows enlighten.ini to override color/style for named widgets
    def make_pen(self, widget=None, color=None, selected=False):
        if color is None and widget is not None:
            color = self.colors.get_by_widget(widget)
        
        # passed color may be a name
        if color is not None:
            named_color = self.colors.get_by_name(color)
            if named_color is not None:
                color = named_color

        if color is None:
            color = self.colors.get_next_random()

        style = self.config.get(self.SECTION, f"{widget}_pen_style")
        width = int(self.config.get(self.SECTION, f"{widget}_pen_width"))
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

        self.form.setWindowTitle(title)
