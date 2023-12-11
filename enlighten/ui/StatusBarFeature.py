import numpy as np
import logging

from enlighten import common

if common.use_pyside2():
    from PySide2 import QtCore, QtWidgets, QtGui
    from PySide2.QtWidgets import QMenu
else:
    from PySide6 import QtCore, QtWidgets, QtGui
    from PySide6.QtWidgets import QMenu

log = logging.getLogger(__name__)

##
# This class encapsulates the horizontal status bar at the bottom of the 
# ENLIGHTEN Scope Capture screen.  It offers several real-time status fields
# providing metrics about the current spectrum and selected spectrometer,
# and has a pop-up menu allowing the user to select which fields they would
# like to display (especially useful on small screens).  Selections are 
# persisted across application sessions.
class StatusBarFeature:

    # ##########################################################################
    # initialization
    # ##########################################################################

    ##
    # Each "pair" represents two QLabels, containing the "name" and "value"
    # of a "Name: value" tuple in the rendered StatusBar.  Both are needed so we
    # can show/hide pairs, and there are two (rather than one) to simplify left-
    # justified names and right-justified values.
    def __init__(self,
            pair_min,
            pair_max,
            pair_mean,
            pair_area,
            pair_temp,
            pair_cursor,
            pair_count,

            config,
            multispec, 
            tool_button,
            generate_x_axis,
            parent,

            cursor,
            detector_temperature):

        self.config = config
        self.multispec = multispec
        self.tool_button = tool_button
        self.generate_x_axis = generate_x_axis
        self.parent = parent

        self.widgets = {}
        self.menu_order = []

        # ordered strings represent menu items as well as dict key
        for group in [ [ "Min",                  pair_min    ],
                       [ "Max",                  pair_max    ],
                       [ "Mean",                 pair_mean   ],
                       [ "Area",                 pair_area   ],
                       [ "Detector Temperature", pair_temp   ],
                       [ "Cursor Intensity",     pair_cursor ], 
                       [ "Spectrum Count",       pair_count  ] ]:
            (name, pair) = group
            self.menu_order.append(name)
            self.widgets[name] = pair

        # register for notifications from other business objects
        cursor.register_observer(self.cursor_updated)
        detector_temperature.register_observer(self.temp_updated)

        self.create_status_menu()

    ## 
    # initialize the pop-up menu allowing users to selectively dis/enable
    # individual key-value pairs on the StatusBar
    def create_status_menu(self):
        menu = QMenu(parent=self.parent) # inherit parent's stylesheet

        for name  in self.menu_order:
            action = menu.addAction(name)
            action.setCheckable(True)

            if self.config.has_option("StatusBar", name):
                enabled = self.config.get_bool("StatusBar", name)
            elif name in ["Area", "Spectrum Count"]:
                enabled = False
            else:                    
                enabled = True

            action.setChecked(enabled)
            self.show(name, enabled)

        menu.triggered.connect(self.toggle_option_visible)
        self.tool_button.setMenu(menu)

        # This line shouldn't be needed but the menu won't show up if it's not here
        self.tool_button.menu() 

    # ##########################################################################
    # Utility
    # ##########################################################################

    ## @return the "name" widget associated with that key (e.g. lb_min_name)
    def name(self, s):
        return self.widgets[s][0]

    ## @return the "value" widget associated with that key (e.g. lb_min_value)
    def value(self, s):
        return self.widgets[s][1]

    ## clear all values associated with the current spectrum
    def clear(self):
        for s in [ "Min", "Max", "Mean" ]:
            self.value(s).clear()

    ## show or hide all the widgets associated with a given key (and persist)
    def show(self, name, flag):
        if name in self.widgets:
            for widget in self.widgets[name]:
                widget.setVisible(flag)
            self.config.set("StatusBar", name, flag)

    # ##########################################################################
    # methods
    # ##########################################################################

    ## 
    # Update any fields we can get to from inside the class (not waiting on
    # external notifications).
    #
    # If we ever create a "ReadingProcessor" or something that handles all new
    # Reading objects, we could always subscribe to notifications from that (as
    # would Graph, KnowItAll, PluginManager etc).
    def update(self):
        spec = self.multispec.current_spectrometer()
        if spec is None:
            return self.clear()

        # latest reading
        pr = spec.app_state.processed_reading
        if pr is not None:

            # count
            self.value("Spectrum Count").setText(str(pr.session_count))

            # current spectrum
            spectrum = pr.get_processed()
            if spectrum is not None:
                self.value("Min").setText("%.2f" % np.min(spectrum))
                self.value("Max").setText("%.2f" % np.max(spectrum))
                self.value("Mean").setText("%.2f" % np.average(spectrum))

                x_axis = self.generate_x_axis(spec=spec, cropped=pr.is_cropped())
                if len(spectrum) != len(x_axis):
                    # can happen when EEPROM is in bad state, or we've set a DetectorROI etc
                    log.error("can't update: spectrum %d != x_axis %d", len(spectrum), len(x_axis))
                    return

                # area
                area = 0 if x_axis is None else np.trapz(spectrum, x_axis)
                self.value("Area").setText("%.3e" % area)

    # ##########################################################################
    # callbacks
    # ##########################################################################

    ## the user clicked a check-box on the QMenu, so show/hide that pair
    def toggle_option_visible(self, action):
        s = action.text()
        self.show(s, action.isChecked())

    ## receives a point from Cursor
    def cursor_updated(self, x, y):
        self.value("Cursor Intensity").setText("%.2f" % y)

    ## receives a temperature from DetectorTemperatureFeature
    def temp_updated(self, degC):
        self.value("Detector Temperature").setText("%-.2f °C" % degC)
