import functools
import logging

log = logging.getLogger(__name__)

class GridFeature:

    def __init__(self,
            button,
            gui,
            plots,
            stylesheets):

        self.button = button
        self.gui = gui
        self.plots = plots
        self.stylesheets = stylesheets

        self.enabled = False

        self.button.clicked.connect(self.toggle)

    def toggle(self):
        self.enabled = not self.enabled
        self.gui.colorize_button(self.button, self.enabled)

        def resolve_graph_plot(head, attr):
            if head != None and hasattr(head, attr):
                return getattr(head, attr)
            else:
                None

        for name, obj_path in self.plots.items():
            plot = functools.reduce(resolve_graph_plot, obj_path)
            if plot != None:
                plot.showGrid(self.enabled, self.enabled)
            else:
                log.error(f"{name} couldn't set grid")

