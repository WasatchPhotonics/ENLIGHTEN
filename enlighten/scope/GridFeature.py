import functools
import logging

log = logging.getLogger(__name__)

class GridFeature:

    def __init__(self, ctl):
        self.ctl = ctl
        cfu = ctl.form.ui

        self.button = cfu.pushButton_graphGrid
        self.plots = { "scope graph" : [ctl.graph, "plot"],
                       "plugin graph": [ctl.plugin_controller, "graph_plugin", "plot"] }

        self.enabled = False

        self.button.clicked.connect(self.toggle)
        self.button.setWhatsThis("Convenience shortcut to show or hide a grid on the main graph. You can fine-tune the grid by right-clicking on the graph.")

    def toggle(self):
        self.enabled = not self.enabled
        self.ctl.gui.colorize_button(self.button, self.enabled)

        # MZ: this is needlessly convoluted
        def resolve_graph_plot(head, attr):
            if head is not None and hasattr(head, attr):
                return getattr(head, attr)

        for name, obj_path in self.plots.items():
            plot = functools.reduce(resolve_graph_plot, obj_path)
            if plot is not None:
                plot.showGrid(self.enabled, self.enabled)
            else:
                log.error(f"{name} couldn't set grid")
