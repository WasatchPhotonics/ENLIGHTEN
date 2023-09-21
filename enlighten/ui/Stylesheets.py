import os
import logging

log = logging.getLogger(__name__)

## 
# Encapsulates application of CSS stylesheets to Qt widgets.
class Stylesheets:

    # MZ: this will need to be prefixed by ctl.root_dir
    DEFAULT_PATH = "enlighten/assets/stylesheets"

    def clear(self):
        self.css = { "dark": {}, "light": {} }
        self.widget_last_style = {}

    def __init__(self, path=None):
        self.clear()

        self.path = path if path else self.DEFAULT_PATH
        self.set_dark_mode(True)

        self.load("dark")
        self.load("light")

    def set_dark_mode(self, flag):
        self.mode = "dark" if flag else "light"
        log.debug(f"mode now {self.mode}")
        self.update_widgets()

    def update_widgets(self):
        for widget, name in self.widget_last_style.items():
            self.apply(widget, name)

    ##
    # Load all the CSS stylesheets of the installed distribution into a dict, 
    # where the keys are the basename of each file (sans extension).
    def load(self, mode):
        path = self.path + "/" + mode
        log.debug(f"loading CSS from %s", path)
        for (_dirpath, _dirnames, filenames) in os.walk(path):
            for filename in sorted(filenames):
                if not filename.endswith(".css"):
                    continue

                basename = filename.replace(".css", "")
                pathname = os.path.join(path, filename)
                s = ""
                try:
                    with open(pathname, "r") as f:
                        s = f.read() 
                    self.css[mode][basename] = s
                    log.debug("  loaded %s[%s] (%d bytes)", mode, basename, len(s))
                except:
                    log.error("unable to load %s[%s]", mode, pathname, exc_info=1)

    ## apply CSS to a widget (don't change widget if stylesheet not found)
    def apply(self, widget, name):
        css = self.get(name)
        if css is None:
            return

        try:
            log.debug("applying stylesheet %s[%s] to widget %s", self.mode, name, widget.objectName())
            widget.setStyleSheet(css)
            self.widget_last_style[widget] = name
        except:
            log.error("unable to apply stylesheet '%s'", name, exc_info=1)

    ## return a stylesheet by name (None on error)
    def get(self, name):
        if name in self.css[self.mode]:
            return self.css[self.mode][name]
        log.critical("unknown stylesheet: %s[%s]", self.mode, name)

    ##
    # This was awkwardly designed, but allows a widget (including the Marquee)
    # to be marked "benign" (good), "hazard" (bad) or "neutral" (default).
    #
    # @param flag has three possible values: None (neutral), True (benign), False (hazard)
    def set_benign(self, widget, flag=None):
        if isinstance(flag, bool):
            if flag:
                self.apply(widget, "benign")
            else:
                self.apply(widget, "hazard")
        else:
            self.apply(widget, "panel")

