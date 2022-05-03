import os
import logging

log = logging.getLogger(__name__)

## Encapsulates all the CSS stylesheets provided with the ENLIGHTEN distribution.
class Stylesheets(object):

    DEFAULT_SUBDIR = "enlighten/assets/stylesheets/default"

    def clear(self):
        self.css = None

    def __init__(self, path):
        self.css = {}
        self.load(path)

    ##
    # Load all the CSS stylesheets of the installed distribution into a dict, 
    # where the keys are the basename of each file (sans extension).
    def load(self, path):
        if path is None:
            path = Stylesheets.DEFAULT_SUBDIR

        log.debug("loading CSS from %s", path)
        for (_dirpath, _dirnames, filenames) in os.walk(path):
            for filename in sorted(filenames):
                if not filename.endswith(".css"):
                    continue

                basename = filename.replace(".css", "")
                pathname = os.path.join(path, filename)
                s = ""
                try:
                    with open(pathname, "r") as f:
                        s = f.read() # .strip("\n")
                    self.css[basename] = s
                    # log.debug("  loaded %s (%d bytes)", basename, len(s))
                except:
                    log.error("unable to load %s", pathname, exc_info=1)

    ## apply CSS to a widget (don't change widget if stylesheet not found)
    def apply(self, widget, name):
        css = self.get(name)
        if css is None:
            return

        try:
            # log.debug("applying stylesheet %s to widget %s", name, widget.objectName())
            widget.setStyleSheet(css)
        except:
            log.error("unable to apply stylesheet '%s'", name, exc_info=1)

    ## return a stylesheet by name (None on error)
    def get(self, name):
        if name in self.css:
            return self.css[name]
        log.critical("unknown stylesheet: %s", name)

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

