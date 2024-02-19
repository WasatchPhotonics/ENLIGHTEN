import os
import logging

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
        """ Event handler for when theme combobox is changed (do NOT update the combobox again) """
        
        # for update_widgets to apply now
        self.theme = self.get_theme_list()[index]
        
        # for persistence on next restart
        self.ctl.config.set("theme", "theme", self.theme)
        log.debug(f"set_theme_combobox: theme now {self.theme}")

        self.update_widgets()

    def set_theme(self, theme):
        """ Programmatically set the theme (and make sure the settings combobox is updated) """
        cfu = self.ctl.form.ui

        # for update_widgets to apply now
        self.theme = theme
        
        # for persistence on next restart
        self.ctl.config.set("theme", "theme", theme)
        log.debug(f"set_theme: theme now {self.theme}")

        # make sure comboxbox matches set theme
        # cfu.comboBox_Theme.blockSignals(True)
        cfu.comboBox_Theme.setCurrentIndex(self.get_theme_list().index(theme))
        # cfu.comboBox_Theme.blockSignals(False)

        self.update_widgets()

    def set_dark_mode(self, flag):
        self.set_theme("dark" if flag else "light")

    def update_widgets(self):
        log.debug("update_widgets: start ---------------------")
        for widget, style_name in self.widget_last_style.items():
            self.apply(widget, style_name)
        log.debug("update_widgets: done ----------------------")

    ##
    # Load all the CSS stylesheets of the installed distribution into a dict, 
    # where the keys are the basename of each file (sans extension).
    def load(self, theme):
        path = os.path.join(self.path, theme)
        log.debug(f"loading CSS from {path}")
        for (_dirpath, _dirnames, filenames) in os.walk(path):
            for filename in sorted(filenames):
                if not filename.endswith(".css"):
                    continue

                basename = filename.replace(".css", "")
                pathname = os.path.join(path, filename)
                try:
                    with open(pathname, "r") as f:
                        s = f.read() 
                    self.css[theme][basename] = s
                    # log.debug("  loaded %s[%s] (%d bytes)", theme, basename, len(s))
                except:
                    log.error(f"unable to load {theme}[{pathname}]", exc_info=1)

    ## apply CSS to a widget (don't change widget if stylesheet not found)
    def apply(self, widget, style_name):
        css = self.get(style_name)
        if css is None:
            log.error("no CSS found for style_name {style_name}, theme {self.theme}")
            return

        widget_name = widget.objectName()
        old = widget.styleSheet()

        # This screws up ThumbnailWidgets...
        # if not widget_name or len(widget_name) == 0:
        #     log.error(f"widget [{widget_name}] has no name: {widget}")
        #     return

        if old == css:
            log.debug(f"{widget_name} already has stylesheet equivalent to {self.theme}[{style_name}]")
        else:
            log.debug(f"applying {self.theme}[{style_name}] to {widget_name}")
            widget.setStyleSheet(css)

        self.widget_last_style[widget] = style_name

    ## return a stylesheet by name (None on error)
    def get(self, style_name):
        if style_name in self.css[self.theme]:
            return self.css[self.theme][style_name]
        log.critical(f"unknown stylesheet: theme {self.theme}, style_name {style_name}")

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
