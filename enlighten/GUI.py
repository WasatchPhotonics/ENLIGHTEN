import logging
import pyqtgraph

from . import common 

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
class GUI(object):

    def __init__(self, 
            colors,
            config,
            form,
            stylesheets):

        self.colors      = colors
        self.config      = config
        self.form        = form
        self.stylesheets = stylesheets

        self.multispec = None

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

        style = self.config.get("graphs", f"{widget}_pen_style")
        width = int(self.config.get("graphs", f"{widget}_pen_width"))
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
