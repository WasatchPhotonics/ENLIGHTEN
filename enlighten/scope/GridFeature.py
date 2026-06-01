import logging

from enlighten.EnlightenFeature import EnlightenFeature
from enlighten.util import unwrap

log = logging.getLogger(__name__)

class GridFeature(EnlightenFeature):

    def __init__(self, ctl):
        super().__init__(ctl)

        cfu = ctl.form.ui

        self.button = cfu.pushButton_graphGrid

        self.enabled = False

        self.button.clicked.connect(self.toggle)

        self.button.setToolTip("show or hide graph grid")
        self.button.setWhatsThis(unwrap("""
                Convenience shortcut to show or hide a grid on the main graph. 
                You can fine-tune the grid by right-clicking on the graph. 

                This button was brought to you by Caleb ✌️"""))

    def toggle(self):
        self.enabled = not self.enabled
        self.ctl.gui.colorize_button(self.button, self.enabled)
        for graph in [ self.ctl.graph, self.ctl.alt_graph ]:
            graph.plot.showGrid(self.enabled, self.enabled)
