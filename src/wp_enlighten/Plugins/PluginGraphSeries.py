import pyqtgraph
import logging

from . import util

log = logging.getLogger(__name__)

##
# THIS CLASS IS NOT DONE!
#
# We need to add an on-screen [x] checkbox and (color) button for every series a
# plugin adds to the main graph.
class PluginGraphSeries:

    def __init__(self, name, curve):
        self.button_color = self.add_color_button()

        self.cb_show            .stateChanged           .connect(self.show_callback)
        self.button_color       .sigColorChanged        .connect(self.color_callback)

    def add_color_button(self):
        button = pyqtgraph.ColorButton()
        util.force_size(button, width=30, height=26)
        # self.layout_colors.addWidget(button)
        return button
