import numpy as np
import logging

from enlighten import common

if common.use_pyside2():
    from PySide2.QtWidgets import QMenu
else:
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

    @todo selectively show/hide trios which are inapplicable to the currently
          selected spectrometer (battery should be hidden unless has_battery)
    """

    # ##########################################################################
    # initialization
    # ##########################################################################

    def __init__(self, ctl):
        self.ctl = ctl
        cfu = ctl.form.ui
        
        self.widgets = {}
        self.menu_order = []

        # @todo: it would be a lot easier to maintain this feature if we 
        #        dynamically create these labels programmatically rather than 
        #        define them in enlighten_layout.ui
        for trio in [ [ "Min",                  cfu.label_StatusBar_min_name,           cfu.label_StatusBar_min_value ],
                      [ "Max",                  cfu.label_StatusBar_max_name,           cfu.label_StatusBar_max_value ],
                      [ "Mean",                 cfu.label_StatusBar_mean_name,          cfu.label_StatusBar_mean_value ],
                      [ "Area",                 cfu.label_StatusBar_area_name,          cfu.label_StatusBar_area_value ],
                      [ "Detector Temperature", cfu.label_StatusBar_detector_temp_name, cfu.label_StatusBar_detector_temp_value ],
                      [ "Laser Temperature",    cfu.label_StatusBar_laser_temp_name,    cfu.label_StatusBar_laser_temp_value ],
                      [ "Cursor Intensity",     cfu.label_StatusBar_cursor_name,        cfu.label_StatusBar_cursor_value ],
                      [ "Spectrum Count",       cfu.label_StatusBar_count_name,         cfu.label_StatusBar_count_value ],
                      [ "Battery",              cfu.label_StatusBar_battery_name,       cfu.label_StatusBar_battery_value ] ]:
            (name, label, value) = trio
            self.menu_order.append(name)
            self.widgets[name] = (label, value)

        # register for notifications from other business objects
        ctl.cursor.register_observer(self.cursor_updated)
        ctl.detector_temperature.register_observer(self.detector_temp_updated)
        ctl.laser_temperature.register_observer(self.laser_temp_updated)
        ctl.battery_feature.register_observer(self.battery_updated)

        self.create_status_menu()

    ## 
    # initialize the pop-up menu allowing users to selectively dis/enable
    # individual key-value pairs on the StatusBar
    def create_status_menu(self):
        menu = QMenu(parent=self.ctl.form) # inherit parent's stylesheet
        menu.setWhatsThis("Choose which fields to include on the Status Bar below the main scope.")

        for name in self.menu_order:
            action = menu.addAction(name)
            action.setCheckable(True)

            if self.ctl.config.has_option("StatusBar", name):
                enabled = self.ctl.config.get_bool("StatusBar", name)
            else:
                # these are disabled by default
                enabled = name not in [ "Area", "Spectrum Count", "Laser Temperature", "Battery" ]

            action.setChecked(enabled)
            self.show(name, enabled)

        menu.triggered.connect(self.toggle_option_visible)

        tool_button = self.ctl.form.ui.status_bar_toolButton
        tool_button.setMenu(menu)
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

    def update_visibility(self):
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return self.clear()

        for w in self.widgets["Battery"]:
            w.setVisible(spec.settings.eeprom.has_battery)

    ## 
    # Update any fields we can get to from inside the class (not waiting on
    # external notifications).
    #
    # If we ever create a "ReadingProcessor" or something that handles all new
    # Reading objects, we could always subscribe to notifications from that (as
    # would Graph, KnowItAll, PluginManager etc).
    # 
    # Called by the end of Controller.process_reading
    def process_reading(self, pr):
        if pr is None:
            return

        self.set("Spectrum Count", pr.reading.session_count)
        spectrum = pr.get_processed()

        if spectrum is not None:
            self.set("Min", f"{np.min(spectrum):.2f}")
            self.set("Max", f"{np.max(spectrum):.2f}")
            self.set("Mean", f"{np.average(spectrum):.2f}")

            x_axis = self.ctl.generate_x_axis(cropped=pr.is_cropped())
            if x_axis is None:
                # encountered when debugging XL cloud comms
                log.error(f"process_reading: can't compute area w/o x_axis") 
            elif len(spectrum) != len(x_axis):
                # can happen when EEPROM is in bad state, or we've set a DetectorROI etc
                log.error(f"process_reading: can't compute area (spectrum {len(spectrum)} != x_axis {len(x_axis)})")
            else:
                # note that unit will vary depending on x-axis
                area = 0 if x_axis is None else np.trapz(spectrum, x_axis)
                self.set("Area", f"{area:.3e}")

    # ##########################################################################
    # callbacks
    # ##########################################################################

    ## the user clicked a check-box on the QMenu, so show/hide that pair
    def toggle_option_visible(self, action):
        s = action.text()
        self.show(s, action.isChecked())

    def cursor_updated(self, x, y):
        self.set("Cursor Intensity", f"{y:.2f}")

    def detector_temp_updated(self, degC):
        self.set("Detector Temperature", f"{degC:-.2f} °C")

    def laser_temp_updated(self, s):
        if isinstance(s, float):
            s = f"{s:-.2f} °C"
        self.set("Laser Temperature", s)

    def battery_updated(self, perc, charging):
        spec = self.ctl.multispec.current_spectrometer()
        if spec and spec.settings.eeprom.has_battery:
            self.set("Battery", f"{perc:.2f}%")
        else:
            self.set("Battery", "none")
