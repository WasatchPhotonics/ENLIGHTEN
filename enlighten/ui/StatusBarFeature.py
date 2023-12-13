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

class StatusBarFeature:
    """
    This class encapsulates the horizontal status bar at the bottom of the 
    ENLIGHTEN Scope Capture screen.  It offers several real-time status fields
    providing metrics about the current spectrum and selected spectrometer,
    and has a pop-up menu allowing the user to select which fields they would
    like to display (especially useful on small screens).  Selections are 
    persisted across application sessions.
    """

    # ##########################################################################
    # initialization
    # ##########################################################################

    def __init__(self, ctl):
        self.ctl = ctl

        sfu = ctl.form.ui
        self.widgets = {}
        self.menu_order = []
        for trio in [ [ "Min",                  sfu.label_StatusBar_min_name,     sfu.label_StatusBar_min_value ],
                      [ "Max",                  sfu.label_StatusBar_max_name,     sfu.label_StatusBar_max_value ],
                      [ "Mean",                 sfu.label_StatusBar_mean_name,    sfu.label_StatusBar_mean_value ],
                      [ "Area",                 sfu.label_StatusBar_area_name,    sfu.label_StatusBar_area_value ],
                      [ "Detector Temperature", sfu.label_StatusBar_temp_name,    sfu.label_StatusBar_temp_value ],
                      [ "Cursor Intensity",     sfu.label_StatusBar_cursor_name,  sfu.label_StatusBar_cursor_value ],
                      [ "Spectrum Count",       sfu.label_StatusBar_count_name,   sfu.label_StatusBar_count_value ] ]:
            (name, label, value) = trio
            self.menu_order.append(name)
            self.widgets[name] = (label, value)

        # register for notifications from other business objects
        ctl.cursor.register_observer(self.cursor_updated)
        ctl.detector_temperature.register_observer(self.temp_updated)

        self.create_status_menu()

    ## 
    # initialize the pop-up menu allowing users to selectively dis/enable
    # individual key-value pairs on the StatusBar
    def create_status_menu(self):
        menu = QMenu(parent=self.ctl.form) # inherit parent's stylesheet

        for name in self.menu_order:
            action = menu.addAction(name)
            action.setCheckable(True)

            if self.ctl.config.has_option("StatusBar", name):
                enabled = self.ctl.config.get_bool("StatusBar", name)
            elif name in ["Area", "Spectrum Count"]:
                enabled = False
            else:                    
                enabled = True

            action.setChecked(enabled)
            self.show(name, enabled)

        menu.triggered.connect(self.toggle_option_visible)

        tool_button = self.ctl.form.ui.status_bar_toolButton
        tool_button.setMenu(menu)

        # This line shouldn't be needed but the menu won't show up if it's not here
        tool_button.menu() 

    # ##########################################################################
    # Utility
    # ##########################################################################

    ## @return the "name" widget associated with that key (e.g. lb_min_name)
    def name(self, s):
        if s in self.widgets:
            return self.widgets[s][0]

    ## @return the "value" widget associated with that key (e.g. lb_min_value)
    def value(self, s):
        if s in self.widgets:
            return self.widgets[s][1]

    ## clear all values associated with the current spectrum
    def clear(self):
        for s in [ "Min", "Max", "Mean" ]:
            value = self.value(s)
            if value:
                value.clear()

    ## show or hide all the widgets associated with a given key (and persist)
    def show(self, name, flag):
        if name in self.widgets:
            for widget in self.widgets[name]:
                widget.setVisible(flag)
            self.ctl.config.set("StatusBar", name, flag)

    def set(self, name, v):
        value = self.value(name)
        if value:
            value.setText(str(v))
        
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
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return self.clear()

        # latest reading
        pr = spec.app_state.processed_reading
        if pr is not None:

            # count
            self.set("Spectrum Count", pr.session_count)

            # current spectrum
            spectrum = pr.get_processed()
            if spectrum is not None:
                self.set("Min", f"{np.min(spectrum):.2f}")
                self.set("Max", f"{np.max(spectrum):.2f}")
                self.set("Mean", f"{np.average(spectrum):.2f}")

                x_axis = self.ctl.generate_x_axis(spec=spec, cropped=pr.is_cropped())
                if len(spectrum) != len(x_axis):
                    # can happen when EEPROM is in bad state, or we've set a DetectorROI etc
                    log.error("can't update: spectrum %d != x_axis %d", len(spectrum), len(x_axis))
                    return

                # area
                area = 0 if x_axis is None else np.trapz(spectrum, x_axis)
                self.set("Area", f"{area:.3e}")

    # ##########################################################################
    # callbacks
    # ##########################################################################

    ## the user clicked a check-box on the QMenu, so show/hide that pair
    def toggle_option_visible(self, action):
        s = action.text()
        self.show(s, action.isChecked())

    ## receives a point from Cursor
    def cursor_updated(self, x, y):
        self.set("Cursor Intensity", f"{y:.2f}")

    ## receives a temperature from DetectorTemperatureFeature
    def temp_updated(self, degC):
        self.set("Detector Temperature", f"{degC:-.2f} °C")
