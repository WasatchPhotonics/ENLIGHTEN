import pyqtgraph

from collections import defaultdict
import logging
import re

from enlighten.device.Spectrometer import Spectrometer
from enlighten.ui.ScrollStealFilter import ScrollStealFilter

from wasatch.DeviceID import DeviceID
from wasatch.WasatchDeviceWrapper import WasatchDeviceWrapper

from enlighten import util

log = logging.getLogger(__name__)

##
# This class orchestrates ENLIGHTEN's simultaneous connection to multiple 
# spectrometers in parallel.
#
# For the first two years of its life (2016-2018), ENLIGHTEN could only connect
# to one spectrometer at a time.  Everything was hard-coded to assume a single
# spectrometer, and in many cases state was mastered in GUI widgets themselves,
# such that there was literally no place to store, for instance, the current
# integration time or laser enable status of a second spectrometer.
# 
# Refactoring such a fundamental aspect of the application was a big deal, so 
# this class was created to encapsulate the 1-to-many relationships.
#
# At some point I might rename this to be just "Spectrometers," in parallel with
# "Measurements" etc.
#
# It's worth considering whether to give Multispec a shutting_down flag, or a 
# callback to get it, but the tear-down process is sufficiently lightweight to
# just let it ride.
#
class Multispec:

    def __init__(self, ctl):
        self.ctl = ctl
        cfu = ctl.form.ui

        self.button_lock           = cfu.pushButton_multiSpec_lock
        self.check_autocolor       = cfu.checkBox_multiSpec_autocolor
        self.check_hide_others     = cfu.checkBox_multiSpec_hide_others
        self.combo_spectrometer    = cfu.comboBox_multiSpec
        self.frame_widget          = cfu.frame_multiSpecWidget
        self.layout_colors         = cfu.horizontalLayout_multiSpec_colors
        self.eject_button          = cfu.pushButton_eject

        # Essentially, these are widgets corresponding to SpectrometerState fields,
        # SpectrometerApplicationState fields, or change_device_setting() keys
        # which can therefore be "locked" in Multispec.  There is currently NO
        # CONNECTION in code between the widgets which "visually suggest they can
        # be locked" (via this list), and those which actually can be.
        self.lockable_widgets      = [ cfu.lightSourceWidget_shaded,    # includes LaserWatchdog
                                       cfu.detectorControlWidget_shaded,
                                       cfu.displayAxisWidget_shaded,
                                       cfu.scanAveragingWidget_shaded,
                                       cfu.boxcarWidget_shaded ]
        self.device_id = None
        self.ejected = set()
        self.spectrometers = {}
        self.in_process = {} # a dict of device_id to WasatchDeviceWrapper (may be None if "gave up")
        self.disconnecting = {}
        self.ignore = {}

        # There's a bunch of stuff here that I think would more cleanly go into 
        # SpectrometerApplicationState...
        self.strip_features = []
        self.spec_laser_temp_curves = {}
        self.spec_hardware_live_curves = {}
        self.spec_detector_temp_curves = {}
        self.spec_roi_curtains = {} 
        self.reset_spec_objs = {}
        self.spec_in_reset = defaultdict(int) # default of int() is 0
        self.spec_hardware_feature_curves = defaultdict(dict)

        # dict of serial_number to color - persisted in Multispec so that 
        # Spectrometers which disconnect and reconnect can easily re-acquire 
        # their previously-assigned color, and not confuse the user by shifting 
        # through a rainbow
        self.serial_colors = {} 

        # This refers to the Multispec feature of "locking" spectrometer state 
        # changes so that they apply to all connected spectrometers (or if 
        # "unlocked", only apply to the currently-selected spectrometer).
        # 
        # We need to generate a list of Features which support locking, and those
        # that don't / shouldn't.
        self.locked = False     

        self.hide_others = False

        self.reset_seen()
        self.combo_spectrometer.clear()
        self.button_color = self.add_color_button()

        # bindings
        self.check_autocolor    .stateChanged           .connect(self.check_callback)
        self.check_hide_others  .stateChanged           .connect(self.check_hide_others_callback)
        self.combo_spectrometer .currentIndexChanged    .connect(self.combo_callback)
        self.eject_button       .clicked                .connect(self.eject_current_spec)
        self.combo_spectrometer                         .installEventFilter(ScrollStealFilter(self.combo_spectrometer))
        self.button_lock        .clicked                .connect(self.lock_callback)
        self.button_color       .sigColorChanged        .connect(self.color_changed_callback)

        self.check_autocolor    .setWhatsThis("Automatically color-code on-screen graph traces according to hardware lid colors")
        self.check_hide_others  .setWhatsThis("Hide all connected spectrometers except the one currently selected")
        self.combo_spectrometer .setWhatsThis("Select one 'active' spectrometer from the list of currently connected devices")
        self.button_lock        .setWhatsThis("Apply setting changes (integration time, laser control, etc) to all connected spectrometers at once")
        self.button_color       .setWhatsThis("Manually select the graph color for this spectrometer.")
        self.eject_button       .setWhatsThis(util.unwrap("""
            Disconnect this spectrometer from software, such that ENLIGHTEN will
            no longer communicate with it until the program is re-launched or the
            device is re-enumerated"""))

        self.update_widget()

        log.debug("instantiated Multispec")

    ## @returns True if we're only looking for one spectrometer, and already found it
    def found_desired(self):
        return self.ctl.serial_number_desired is not None and self.count() > 0

    ## @returns True if we're only looking for one spectrometer, and this isn't it
    def reject_undesireable(self, device):
        if self.ctl.serial_number_desired is None:
            return False # we're not filtering, so don't reject

        if self.ctl.serial_number_desired == device.settings.eeprom.serial_number:
            return False # passed filter, so don't reject

        log.info("rejecting spectrometer (%s != %s)", self.ctl.serial_number_desired, device.settings.eeprom.serial_number)
        self.set_ignore(device.device_id)
        return True # failed filter

    def register_strip_feature(self, feature):
        """
        MZ: Whut?
        """
        self.strip_features.append(feature)

    ##
    # The Qt Designer doesn't let us emplace pyqtgraph objects (I think?), so
    # add this button at runtime.
    def add_color_button(self):
        button = pyqtgraph.ColorButton()
        util.force_size(button, width=30, height=26)
        self.ctl.gui.colorize_button(button, False)
        self.layout_colors.addWidget(button)
        return button

    ##
    # The user has manually selected a color for the current spectrometer, so 
    # save and apply it
    def color_changed_callback(self, btn):
        spec = self.current_spectrometer()
        if spec is None:
            return
        spec.color = btn.color()
        self.serial_colors[spec.settings.eeprom.serial_number] = spec.color
        self.update_spectrometer_colors()
        for feature in self.strip_features:
            feature.update_curve_color(spec)

    def update_color(self):
        spec = self.current_spectrometer()
        if spec is None:
            return
        if spec.color is not None:
            self.button_color.setColor(spec.color)

    def is_in_reset(self, device_id):
        return any([device_id == key for key in self.spec_in_reset.keys()])

    def set_in_reset(self, device_id):
        self.spec_in_reset[device_id] += 1
        self.reset_spec_objs[device_id] = self.spectrometers[device_id]
        del self.spectrometers[device_id]

    def reset_tries(self, device_id):
        return self.spec_in_reset[device_id]

    def clear_reset(self, device_id):
        try:
            self.spec_in_reset.pop(device_id)
        except:
            log.error("tried to pop device id {device_id} but couldn't find in reset dict")

    def have_any_in_process(self) -> bool:
        """
        @returns True if any in_process devices are honestly still in-process (i.e. not "gave up")
        @note I think there's a cleverer way to do this in Python now
        """
        for device_id in self.in_process:
            if self.in_process[device_id]:
                return True

    def have_any_andor(self) -> bool:
        """ 
        @note there may be a clever way to do this too
        """
        for device_id in self.in_process:
            if device_id.is_andor():
                return True
        for spec in self.get_spectrometers():
            if spec.device_id.is_andor():
                return True
        log.debug(f"have_any_andor: didn't find any")
        return False

    def set_in_process(self, device_id, device: WasatchDeviceWrapper):
        log.debug(f"set_in_process: {device_id} -> {device}")
        self.in_process[device_id] = device

    def set_gave_up(self, device_id):
        """
        Sets in_process value to None, indicating that we've given up trying to 
        connect to that device_id (it is permanently but inactively "in process").
        """
        self.in_process[device_id] = None
        log.debug("set_gave_up: %s", device_id)

    def set_ignore(self, device_id):
        log.debug("set_ignore: %s", device_id)
        self.ignore[device_id] = True

    def is_in_process(self, device_id) -> bool:
        """
        @returns True if in_process at all (including None, indicating "gave up")
        """
        return device_id in self.in_process 

    def is_ignore(self, device_id) -> bool:
        return device_id in self.ignore

    def is_gave_up(self, device_id) -> bool:
        return device_id in self.in_process and self.in_process[device_id] is None

    def remove_in_process(self, device_id):
        del self.in_process[device_id]

    def reset_seen(self):
        self.seen_colors = set() # '#abcdef' etc

    def set_disconnecting(self, device_id: str, status: bool) -> None:
        """
        Records that we are kicking off a spectrometer so
        Enlighten doesn't accidentally pick it up
        """
        try:
            if status:
                self.disconnecting[device_id] = True
            else:
                del self.disconnecting[device_id]
        except Exception as e:
            log.error(f"{e} trying to set disconnect status for {device_id}")

    def is_disconnecting(self, device_id: str) -> bool:
        return device_id in self.disconnecting.keys()

    def lock_callback(self):
        self.locked = not self.locked

        self.ctl.gui.colorize_button(self.button_lock, self.locked)
        if self.locked:
            css = self.ctl.stylesheets.get("multispec_locked")
        else:
            css = self.ctl.stylesheets.get("multispec_unlocked")

        for widget in self.lockable_widgets:
            widget.setStyleSheet(css)

    def check_hide_others_callback(self):
        self.update_hide_others()

    def check_ejected_unplugged(self, connected_devices: list[DeviceID]) -> None:
        """
        Goes through the set of ejected spectrometers and checks if they still appear
        in the list of connected devices. If they don't, this means a user ejected spec has
        been physically unplugged and should be removed from the set so the user can plug it back in
        """
        if len(self.ejected) == 0:
            return

        plugged_in = set(connected_devices)
        physically_unplugged = self.ejected.difference(plugged_in)
        self.ejected = {dev for dev in self.ejected if dev not in physically_unplugged}

    def check_spec_user_ejected(self, device_id: DeviceID) -> bool:
        return device_id in self.ejected

    def eject_current_spec(self):
        log.debug("user clicked eject")
        spec = self.current_spectrometer()
        if spec is None:
            return
        log.critical(f"user clicked eject on {spec}")
        self.ctl.disconnect_device(spec)
        self.ejected.add(spec.device.device_id)

    def update_hide_others(self):
        self.hide_others = self.check_hide_others.isChecked()

        if self.hide_others:
            for spec in self.get_spectrometers():
                if self.device_id != spec.device_id:
                    self.hide(spec)
                elif spec.app_state.hidden:
                    self.unhide(spec)
                else:
                    spec.curve.setPen(self.make_pen(spec))
        else:
            for spec in self.get_spectrometers():
                if spec.app_state.hidden or spec.curve is None:
                    self.unhide(spec)
                    spec.curve.setPen(self.make_pen(spec))
                else:
                    spec.curve.setPen(self.make_pen(spec))

    def hide(self, spec):
        if spec.app_state.hidden:
            return

        log.debug("hiding %s", spec.device_id)
        spec.app_state.hidden = True

        # now that we're adding device_id backreferences, could alternately delete by device_id
        self.ctl.graph.remove_curve(spec.label)

    def unhide(self, spec):
        if not spec.app_state.hidden:
            return

        log.debug("unhiding %s", spec.device_id)
        spec.app_state.hidden = False
        spec.curve = self.ctl.graph.add_curve(
            pen=self.make_pen(spec),
            name=spec.label,
            spec=spec)

    ##
    # Update the given SpectrometerState field for the current spectrometer,
    # or for all spectrometers if locking is enabled.
    def set_state(self, field, value):
        if self.locked:
            for spec in self.get_spectrometers():
                log.debug(f"{spec.label}: settings.state.{field} -> {value}")
                setattr(spec.settings.state, field, value)
        else:
            spec = self.current_spectrometer()
            if spec is not None:
                log.debug(f"{spec.label}: settings.state.{field} -> {value}")
                setattr(spec.settings.state, field, value)
                
    ##
    # Update the given SpectrometerApplicationState field for the current spectrometer,
    # or for all spectrometers if locking is enabled.
    def set_app_state(self, field, value, all_=False):
        if self.locked or all_:
            for spec in self.get_spectrometers():
                log.debug("%s: app_state.%s -> %s", spec.label, field, value)
                setattr(spec.app_state, field, value)
        else:
            spec = self.current_spectrometer()
            if spec is not None:
                log.debug("%s: app_state.%s -> %s", spec.label, field, value)
                setattr(spec.app_state, field, value)

    def get_spectrometers(self):
        try:
            specs = []
            for device_id in sorted(self.spectrometers, key=str):
                spec = self.spectrometers[device_id]
                if spec is not None:
                    specs.append(spec)
                else:
                    log.critical("get_spectrometers: None spectrometer for device_id %s", device_id)
            return specs
        except Exception as e:
            log.error(f"{e}")

    ## This function hopefully won't need to be retained, but is being added to analyze
    # a developmental bug in which apparently the same spectrometer connected twice, and
    # both instances continued to function :-(
    def get_clones(self, device_id):
        clones = []

        spec = self.get_spectrometer(device_id)
        if spec is None:
            log.error("Multispec.get_clones: can't find spectrometer %s", device_id)
            return clones

        for did in sorted(self.spectrometers, key=str):
            other = self.spectrometers[did]

            # skip the one we were passed
            if other is None or did == device_id:
                continue

            # look for clones (same serial number)
            if other.settings.eeprom.serial_number == spec.settings.eeprom.serial_number:
                clones.append(spec)

        return clones

    def any_has_excitation(self) -> bool:
        for device_id in sorted(self.spectrometers, key=str):
            if self.spectrometers[device_id].has_excitation():
                return True
        return False

    def get_spectrometer(self, device_id) -> Spectrometer:
        return self.spectrometers.get(device_id,None)

    def is_autocolor(self) -> bool:
        return self.check_autocolor.isChecked()

    def is_selected(self, device_id) -> bool:
        return device_id == self.device_id

    def is_connected(self, device_id) -> bool:
        return device_id in self.spectrometers

    def count(self) -> int:
        try:
            return len(self.spectrometers)
        except:
            log.error("error returning spec length")
            return 0

    def is_current_spectrometer(self, spec) -> bool:
        return self.device_id is not None and self.device_id == spec.device_id

    def current_spectrometer(self) -> Spectrometer:
        if self.device_id is None:
            return
    
        if self.device_id in self.spectrometers:
            return self.spectrometers[self.device_id]

        log.error(f"Multispec.current_spectrometer: can't find self.device_id {self.device_id} in spectrometers {self.spectrometers}")

    def update_widget(self):
        log.debug("update_widget start (%s)", self.device_id)
        multi = self.count() > 1

        self.frame_widget.setVisible(True)
        self.combo_spectrometer.setEnabled(multi)
        self.button_lock.setEnabled(multi)
        self.check_hide_others.setEnabled(multi)
        log.debug("update_widget end (%s)", self.device_id)

    def read_spec_object(self, device_id):
        log.debug(f"reading spec {device_id}")
        try:
            self.spectrometers[device_id] = self.reset_spec_objs[device_id]
            del self.reset_spec_objs[device_id]
            log.debug(f"after read specs are {self.spectrometers}")
        except Exception as e:
            log.error(f"error in read {e}")

    def add(self, device):
        device_id = device.device_id

        log.debug("Multispec.add: instantiating Spectrometer for device_id %s", device_id)
        spec = Spectrometer(device, self.ctl)

        log.debug("Multispec.add: adding to self.spectrometers: %s", device_id)
        self.spectrometers[device_id] = spec

        # This is within blockSignals because I don't want to recursively trigger
        # another call to initialize_new_device (which is presumably what trigger-
        # ed this call to add() in the first place).
        self.combo_spectrometer.blockSignals(True)
        self.combo_spectrometer.addItem(spec.label.replace(" ", "\n"))
        index = self.combo_spectrometer.count() - 1
        self.combo_spectrometer.setCurrentIndex(index)
        self.combo_spectrometer.blockSignals(False)
        
        # select the newly added device
        log.debug(f"Multispec.add: self.device_id now {device_id}")
        self.device_id = device_id

        ########################################################################
        # initialize graph trace
        ########################################################################

        # this is where the spectrometer's "normal" graph color is initialized
        # (whether or not "autocolor" is currently enabled)

        sn = spec.settings.eeprom.serial_number
        if sn in self.serial_colors:
            # this is a reconnection, so re-use previous color
            spec.color = self.serial_colors[sn]
        else:
            # assign a new color
            spec.color = self.choose_color(spec, ignore_auto=True)
            self.serial_colors[sn] = spec.color

        # now add to the curve, noting that autocolor may be in effect
        log.debug("Multispec.add: adding curve %s", spec.label)
        pen = self.make_pen(spec)
        spec.curve = self.ctl.graph.add_curve(
            pen=pen,
            name=spec.label,
            spec=spec)

        ########################################################################
        # initialize horizontal ROI "curtains"
        ########################################################################

        log.debug("add: calling init_curtains")
        spec.init_curtains()

        log.debug("add: calling update_regions")
        self.ctl.horiz_roi.update_regions(spec)

        log.debug("add: back from scary changed stuff")

        # done
        self.update_widget()

    def get_combo_index(self, spec) -> int:
        label = spec.label
        for index in range(self.combo_spectrometer.count()):
            this_label = self.combo_spectrometer.itemText(index).replace('\n', ' ', 1) # needed since \n added to avoid cutting off label in gui 
            log.debug(f"COMBO IDX checking {label} matches {index} {this_label}")
            if label == this_label:
                return index
        log.error("get_combo_index: failed to find %s", label)
        return -1

    def remove_all(self):
        log.debug("Multispec.removal_all: start")
        while self.count() > 0:
            spec = self.get_spectrometers()[0]
            self.remove(spec)

    ## @return success
    def remove(self, spec=None, silent=False) -> bool:
        if spec is None:
            # default to current
            spec = self.spectrometers[self.device_id]

        if spec.device_id not in self.spectrometers.keys():
            log.debug(f"Failed to find {spec} in {self.spectrometers.keys()}, returning")
            return False

        if spec is None:
            return False

        index = self.get_combo_index(spec)
        if index < 0:
            try:
                del self.spectrometers[self.device_id]
                log.error("Multispec.remove: can't find index")
                return False
            except Exception as e:
                log.error(f"Multispec.remove: failed to delete from spectrometers with error {e}")
                return False
        label = spec.label

        self.ctl.graph.remove_curve(label)
        self.ctl.graph.remove_roi_region(spec.roi_region_right)
        self.ctl.graph.remove_roi_region(spec.roi_region_left)

        # this should cause combo_callback to trigger, calling 
        # Controller.initialize_new_device and thus updating Multispec.device_id to 
        # a new value (or None)
        self.combo_spectrometer.removeItem(index)
        self.update_widget()
        
        if not self.count():
            self.reset_seen()

        del self.spectrometers[spec.device_id]

        return True

    # figure out which device_id was selected on the combobox
    def get_combo_device_id(self) -> DeviceID:
        index = self.combo_spectrometer.currentIndex()
        if index < 0:
            return 

        label = str(self.combo_spectrometer.itemText(index))
        log.debug("get_combo_device_id: label = %s index = %d", label, index)
        m = re.match(r'^\s*(.*)\s+\((.*)\)\s*$', label)
        if not m:
            log.error("get_combo_device_id: can't parse %s", label)
            return

        serial = m.group(1)
        model  = m.group(2)
        log.debug("get_combo_device_id: serial [%s], model [%s]", serial, model)

        for device_id in sorted(self.spectrometers, key=str):
            if serial == self.spectrometers[device_id].settings.eeprom.serial_number:
                return device_id 

        log.error("get_combo_device_id: can't find serial %s, model %s", serial, model)

    ## If the selected MultiSpec spectrometer changes, update affected objects
    def combo_callback(self):
        # get the device_id of the selected item in the comboBox
        device_id = self.get_combo_device_id()
        if device_id is None:
            log.debug("combo_callback: can't determine device_id (setting None)")
            self.device_id = None
            return 

        spec = self.spectrometers[device_id]
        if spec is None:
            log.error("combo_callback: selected non-existent spectrometer: %s", device_id)
            return

        # was this a real change?
        if device_id == self.device_id:
            log.info(self.spectrometers)
            log.debug("combo_callback[%s]: re-selected current spectrometer %s (no-op)", device_id, self.device_id)
            return

        log.info(f"combo_callback[{device_id}]: switching default device (now {device_id})")
        self.device_id = device_id

        # this is a no-op when shutting down
        self.ctl.initialize_new_device(spec.device)

        # update traces (make selected bold), so just use checkbox callback
        self.check_callback()

    # ##########################################################################
    # Pens and Colors
    # ##########################################################################

    def check_callback(self):
        self.update_spectrometer_colors()

    def update_spectrometer_colors(self):
        for spec in self.get_spectrometers():
            if spec is not None:
                spec.curve.setPen(self.make_pen(spec))

    def make_pen(self, spec):
        """
        @note that even though we determine color locally, we still pass the 
              widget back to make_pen to allow config-based configuration of 
              style, width etc
        @returns QPen
        """
        if self.is_autocolor():
            color = self.choose_color(spec)
        elif spec.color is None:
            color = self.choose_color(spec)
        else:
            color = spec.color

        try:
            pen = self.ctl.gui.make_pen(
                widget   = "scope", 
                selected = self.is_selected(spec.device_id),
                color    = color)
            return pen
        except:
            log.error("unable to generate pen", exc_info=1)

    def choose_color(self, spec, ignore_auto=False):
        if self.is_autocolor() and spec.wp_model_info is not None and not ignore_auto:
            return spec.wp_model_info.color
        elif spec.color is not None:
            return spec.color
        else:
            color = self.ctl.colors.get_by_widget("scope")
            while color in self.seen_colors:
                color = self.ctl.colors.get_next_random()
            self.seen_colors.add(color)
            return color

    ## send commands to device subprocess via (name, value) pickleable tuples
    def change_device_setting(self, setting, value=0, all_=False):
        try:
            if self.locked or all_:
                for spec in self.get_spectrometers():
                    spec.change_device_setting(setting, value)
                return

            spec = self.current_spectrometer()
            if spec is None:
                return

            spec.change_device_setting(setting, value)
        except Exception as e:
            log.error(e)

    def register_hardware_feature_curve(self, name, spec_id, curve):
        self.spec_hardware_feature_curves[name][spec_id] = curve

    def get_hardware_feature_curve(self, name, spec_id):
        return self.spec_hardware_feature_curves[name].get(spec_id, None)

    def remove_hardware_curve(self, name, spec_id):
        self.spec_hardware_feature_curves[name].pop(spec_id, None)

    def check_hardware_curve_present(self, name, spec_id) -> bool:
        return spec_id in self.spec_hardware_feature_curves[name]
