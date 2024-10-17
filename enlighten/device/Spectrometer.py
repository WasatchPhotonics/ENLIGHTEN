import datetime
import logging
import copy

import pyqtgraph

from enlighten.device.SpectrometerApplicationState import SpectrometerApplicationState
from enlighten.ui.Colors import Colors
from enlighten.scope.Cursor import AxisConverter
from enlighten import common

from wasatch.SpectrometerState     import SpectrometerState
from wasatch.AbstractUSBDevice     import AbstractUSBDevice
from wasatch.MockUSBDevice         import MockUSBDevice

log = logging.getLogger(__name__)

##
# Represents an individual Spectrometer within the set of connected spectrometers
# managed by Multispec.
#
# The fundamental justification for this class is to persist a reference to
# each connected spectrometer's SpectrometerSettings and 
# SpectrometerApplicationState objects.
#
# It is reasonable to ask whether ALL of SpectrometerApplicationState can be 
# moved in here.
#
# @par Architecture
#
# \verbatim
#                                       _______________         
#                                      |   Controller  |        
#                                      |_______________|        
#                   +---------------------------^--------------------+
#                  < >                                               |
#         __________v___________                                _____v_____
#        | WasatchDeviceWrapper | <------------.               | Multispec |
#        |______________________|               `              |___________|
#                   ^                           |                   < >
#                   | .wrapper_worker           |                    | .spectrometers{}
#            _______v_______                    |             _______v______
#           | WrapperWorker |                   `--- .device | Spectrometer |
#           |_______________|                                |______________|
#                   ^
#                   | .connected_device
#            _______v_______
#           | WasatchDevice |
#           |_______________|
#                   ^
#                   | .hardware
#     ______________v______________
#    | FeatureIdentificationDevice | .device --> usb.core.Device
#    |_____________________________|
#                   ^
#                   | .device_type
#          _________v_________
#         | AbstractUSBDevice |
#         |___________________|
#                  /_\ 
#                   |
#         +---------+-------+
#  _______v_______   _______v_______ 
# | MockUSBDevice | | RealUSBDevice |
# |_______________| |_______________|
#
# \endverbatim
#
# @note fair bit of Controller can probably be moved into here
# @note seems save to deepcopy and pass to plugins
# @todo consider moving to enlighten.device
class Spectrometer:
    
    def clear(self):
        self.device = None
        self.device_id = None
        self.label = None
        self.curve = None
        self.color = None
        self.app_state = None
        self.wp_model_info = None
        self.settings = None
        self.next_expected_acquisition_timestamp = None
        self.roi_region_left = None
        self.roi_region_right = None

    ##
    # @param device  a wasatch.WasatchDeviceWrapper.WasatchDeviceWrapper
    # @see wasatch.DeviceID.DeviceID
    def __init__(self, device, ctl):
        self.clear()

        self.device = device # a WasatchDeviceWrapper
        self.ctl = ctl

        self.device_id = self.device.device_id 
        self.settings = self.device.settings
        self.roi_region_left = None
        self.roi_region_right = None
        self.app_state = SpectrometerApplicationState(ctl, device_id=self.device_id)

        self.wp_model_info = ctl.model_info.get_by_model(self.settings.full_model())
        log.debug(f"best-guess ModelInfo: {self.wp_model_info}")

        # prefer EEPROM for FWHM, or lookup from model
        if self.settings.eeprom.avg_resolution > 0:
            self.fwhm = self.settings.eeprom.avg_resolution
            log.debug(f"using FWHM from EEPROM: {self.fwhm:.2f}")
        else:
            self.fwhm = ctl.model_info.model_fwhm.get_by_model(self.settings.full_model())
            log.debug(f"using FWHM from lookup table: {self.fwhm}")

        self.settings.eeprom_backup = copy.deepcopy(self.settings.eeprom)

        self.label = f"{self.settings.eeprom.serial_number} ({self.settings.full_model()})"
        self.converter = AxisConverter(ctl)

        self.closing = False

        log.debug(f"Spectrometer: instantiated {self.label} from {self.device_id}")

    def close(self):
        log.info(f"Spectrometer: closing {self.device_id}")
        self.closing = True
        try:
            self.device.disconnect()
        except Exception as e:
            log.error(f"Spectrometer either does not exist or already disconnected {e}")
        log.info(f"Spectrometer: closed {self.device_id}")

    def __str__(self):
        return str(self.device_id).replace("DeviceID", "Spectrometer Object")

    def __eq__(self, other):
        return str(self) == str(other)

    def __ne__(self, other):
        return str(self) != str(other)

    def __hash__(self):
        return hash(str(self))

    def has_excitation(self):
        return self.settings.eeprom.excitation_nm > 0

    ## @param unit should be cm, nm or px
    def get_fwhm(self, unit):
        unit = unit.lower()
        if unit not in ["cm", "nm", "px"]:
            log.error(f"invalid FWHM unit: {unit}")
            return

        # first get from EEPROM, if configured
        avg = self.settings.eeprom.avg_resolution

        # Assume Raman spectrometers are configured in wavenumber and others in wavelength.
        # If the matching unit was requested, return the configured value
        if avg is not None and avg > 0.0:
            if self.has_excitation():
                if unit == "cm":
                    return avg
            else:
                if unit == "nm":
                    return avg

        # Here we could try to convert the configured value from one unit to another, but
        # that could get hairy.  For now, fail-over to the hardcoded "model" setting if found.
        if self.wp_model_info is not None:
            return self.wp_model_info.get_fwhm(unit, int(round(self.settings.eeprom.slit_size_um, 0)))

    def get_image_pathname(self):

        def make_pathname(model):
            # this must correspond exactly to the paths specified in devices.rc 
            # and iterated in ImageResources
            return f":/spectrometers/images/devices/{model}.png"

        pathname = make_pathname("WP-785X-ILP")

        if self.wp_model_info is None:
            log.debug("get_image_pathname: no wp_model_info, so default")
            return pathname

        model = self.settings.full_model()
        log.debug("get_image_pathname: eeprom_model = [%s]", model)
        log.debug("get_image_pathname: wp_model_info =")
        if self.wp_model_info is not None:
            self.wp_model_info.dump()
            name = self.wp_model_info.name
            pathname = make_pathname(name)
            if self.ctl.image_resources.contains(pathname):
                log.debug(f"get_image_pathname: found {pathname}")
            else:
                log.debug(f"get_image_pathname: not found: {pathname}")

        log.debug(f"returning {pathname}")
        return pathname

    def is_acquisition_timeout(self):

        # kludges for SiG-VIS
        model = self.settings.eeprom.model
        if model is None:
            return False
        model = model.lower()
        if "sig" in model and "vis" in model:
            return False

        if self.next_expected_acquisition_timestamp is None:
            return False
        if self.settings.state.trigger_source == SpectrometerState.TRIGGER_SOURCE_EXTERNAL:
            return False
        return datetime.datetime.now() > self.next_expected_acquisition_timestamp

    ## Was disabled for awhile because experimental features like laser ramping 
    # and IMX overrides can cause long gaps between acquisitions, but bringing
    # back.
    def reset_acquisition_timeout(self):
        timeout_ms = self.settings.state.integration_time_ms * ( self.settings.state.scans_to_average + 2 ) + 10000
        if "BLE" in str(self.device_id): # BLE takes a while so give it even more
            timeout_ms += 10000
        future_time = datetime.datetime.now() + datetime.timedelta(milliseconds=timeout_ms)
        self.next_expected_acquisition_timestamp = future_time
        log.debug(f"reset_acquisition_timeout({self.device_id}): expecting next acquisition within {timeout_ms}  ms (by {future_time})")

    def send_alert(self, setting, value=True):
        if self.closing:
            return

        log.info(f"send_alert[{self.device.device_id}]: {setting} -> {value}")
        self.device.send_alert(setting, value)

    ## send commands to device subprocess via (name, value) pickleable tuples
    def change_device_setting(self, setting, value=0):
        if self.closing:
            return

        log.info(f"change_device_setting[{self.device.device_id}]: {setting} -> {value}")
        self.device.change_setting(setting, value)

    def is_mock(self) -> bool:
        return self.get_mock() is not None

    def get_mock(self) -> MockUSBDevice:
        device_type = self.get_device_type()
        if device_type:
            if isinstance(device_type, MockUSBDevice):
                return device_type

    def get_device_type(self) -> AbstractUSBDevice:
        try:
            return self.device.wrapper_worker.connected_device.hardware.device_type
        except:
            log.error(f"Spectrometer {self} doesn't seem to have an accessible device_type")

    ############################################################################
    # 
    #                             Horizontal ROI
    # 
    ############################################################################

    # It is debateable whether the "curtain" regions should "belong" to the
    # Graph, the Spectrometer or the HorizROIFeature. The ROI is very much per-
    # Spectrometer, and is "mastered" by that Spectrometer's SpectrometerSettings'
    # EEPROM. However, as a "visual" indicator, it is technically part of the
    # plot (Graph). However, we're encapsulating visualization / control / 
    # application / editing of the ROI to the HorizROIFeature.
    #
    # Part of the question is: will we ever want to show the ROI curtains for 
    # two spectrometers at the same time? If so, it makes sense to have those
    # regions "owned" by the Spectrometer. That's my current default approach,
    # as it seems to provide the most flexibility for the future.

    def init_curtains(self):

        # copy the pen color so we can lighten it without changing original
        region_color = Colors.QColor(self.color)
        region_color.setAlpha(20)

        if not self.settings.eeprom.has_horizontal_roi():
            self.roi_region_left = None
            self.roi_region_right = None
        else:
            # horizontal ROI is always in pixel space 
            roi = self.settings.eeprom.get_horizontal_roi()
            self.roi_region_left = pyqtgraph.LinearRegionItem((0, roi.start), 
                                                              pen = region_color,
                                                              brush = region_color,
                                                              movable = True,
                                                              swapMode = "block")
            self.roi_region_right = pyqtgraph.LinearRegionItem((roi.end, self.settings.eeprom.active_pixels_horizontal),
                                                              pen = region_color,
                                                              brush = region_color,
                                                              movable = True,
                                                              swapMode = "block")

            self.roi_region_left.sigRegionChangeFinished.connect(self.left_region_changed_callback)
            self.roi_region_right.sigRegionChangeFinished.connect(self.right_region_changed_callback)

            ####################################################################
            # this reaches into pyqtgraph.LinearRegionItem and does some stuff
            # we're probably not supposed to
            ####################################################################

            # lock the left-edge of the left region (always 0) 
            # and the right-edge of the right region (always 'pixels')
            self.roi_region_left.lines[0].setMovable(False)
            self.roi_region_right.lines[1].setMovable(False)

            # also, don't allow the "regions" (the curtain objects themselves) 
            # to be dragged left or right (just the inner edge of each)
            self.roi_region_left.movable = False
            self.roi_region_right.movable = False

    def update_curtains_editable(self):
        pass
    
    def left_region_changed_callback(self):
        (_, end) = self.roi_region_left.getRegion()

        pixel = self.get_new_pixel(end)
        if pixel is None:
            return
    
        log.debug(f"left_region_changed_callback: setting roi_horizontal_start to pixel {pixel} based on region end {end}")
        self.settings.eeprom.roi_horizontal_start = pixel
        self.ctl.horiz_roi.update_regions(spec=self, left_pixel=pixel)

    def right_region_changed_callback(self):
        (start, _) = self.roi_region_right.getRegion()

        pixel = self.get_new_pixel(start)
        if pixel is None:
            return
    
        log.debug(f"right_region_changed_callback: setting roi_horizontal_end to pixel {pixel} based on region start {start}")
        self.settings.eeprom.roi_horizontal_end = pixel
        self.ctl.horiz_roi.update_regions(spec=self, right_pixel=pixel)

    def get_x_from_pixel(self, px):
        x_axis = self.ctl.generate_x_axis(spec=self) 
        if x_axis is None:
            log.error(f"get_x_from_pixel: no x_axis from px {px}")
            return 0
        else:
            return x_axis[px]

    def get_new_pixel(self, x):
        """ 
        The user dragged the line, so lookup the x-coordinate in the Graph 
        axis (wl, wn etc) and convert back to pixels so we can update the 
        EEPROM's ROI 
        """
        x_axis = self.ctl.generate_x_axis(spec=self)
        if x_axis is None:
            return
    
        pixel = self.converter.convert(spec=self, old_axis=self.ctl.graph.current_x_axis, new_axis=common.Axes.PIXELS, x=x)
        if pixel is None:
            log.error(f"get_new_pixel: failed to convert x {x}")
            return None
    
        return min(max(round(pixel), 0), self.settings.pixels() - 1)

    def clear_graph(self):
        """ erase, but do not delete, this graph curve from the graph """
        self.ctl.graph.set_data(curve=self.curve)
