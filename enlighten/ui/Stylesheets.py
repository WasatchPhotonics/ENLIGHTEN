import os
import logging

from enlighten.common import msgbox

log = logging.getLogger(__name__)

## 
# Encapsulates application of CSS stylesheets to Qt widgets.
class Stylesheets:

    DEFAULT_PATH = "enlighten/assets/stylesheets"

    def get_theme_list(self):
        return os.listdir(self.DEFAULT_PATH)

    def clear(self):
        self.css = {}
        for theme in self.get_theme_list():
            self.css.update({theme: {}})

            # populate settings dropdown with themes
            self.ctl.form.ui.comboBox_Theme.addItem(theme)

        self.widget_last_style = {}

    def __init__(self, ctl):
        self.ctl = ctl

        self.clear()
        path = self.ctl.stylesheet_path

        self.path = path if path else self.DEFAULT_PATH

        for theme in self.get_theme_list():
            self.load(theme)

        saved_theme = self.ctl.config.get("theme", "theme")
        if saved_theme in self.get_theme_list():
            self.set_theme(saved_theme)
        else:
            # default to dark if theme not on disk
            self.set_theme("dark")

        self.ctl.form.ui.comboBox_Theme.currentIndexChanged.connect(self.set_theme_combobox)

    def set_theme_combobox(self, index):
        """
        Event handler for when theme combobox is changed (do NOT update the combobox again)
        """
        
        # for update_widgets to apply now
        self.theme = self.get_theme_list()[index]
        
        # for persistence on next restart
        self.ctl.config.set("theme", "theme", self.theme)

        log.debug(f"mode now {self.theme}")
        self.update_widgets()

    def set_theme(self, theme):
        """
        Programmatically set the theme (and make sure the settings combobox is updated)
        """

        # for update_widgets to apply now
        self.theme = theme
        
        # for persistence on next restart
        self.ctl.config.set("theme", "theme", theme)

        log.debug(f"mode now {self.theme}")

        # make sure comboxbox matches set theme
        self.ctl.form.ui.comboBox_Theme.setCurrentIndex(self.get_theme_list().index(theme))

        self.update_widgets()

    def set_dark_mode(self, flag):
        self.set_theme("dark" if flag else "light")

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
            log.debug("applying stylesheet %s[%s] to widget %s", self.theme, name, widget.objectName())
            widget.setStyleSheet(css)
            self.widget_last_style[widget] = name
        except:
            log.error("unable to apply stylesheet '%s'", name, exc_info=1)

    ## return a stylesheet by name (None on error)
    def get(self, name):
        if name in self.css[self.theme]:
            return self.css[self.theme][name]
        log.critical("unknown stylesheet: %s[%s]", self.theme, name)

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

