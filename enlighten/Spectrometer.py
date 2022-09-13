import datetime
import logging
import copy

from .SpectrometerApplicationState import SpectrometerApplicationState

from wasatch.SpectrometerState    import SpectrometerState

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
# @note fair bit of Controller can probably be moved into here
# @note seems save to deepcopy and pass to plugins
class Spectrometer(object):
    
    def clear(self):
        self.device = None
        self.device_id = None
        self.label = None
        self.assigned_color = None
        self.curve = None
        self.app_state = None
        self.wp_model_info = None
        self.settings = None
        self.next_expected_acquisition_timestamp = None

    ##
    # @param device  a wasatch.WasatchDeviceWrapper.WasatchDeviceWrapper
    # @see wasatch.DeviceID.DeviceID
    def __init__(self, device, model_info):
        self.clear()

        self.device = device

        self.device_id = self.device.device_id 
        self.settings = self.device.settings
        self.app_state = SpectrometerApplicationState(self.device_id)

        self.wp_model_info = model_info.get_by_model(self.settings.full_model())
        log.debug(f"best-guess ModelInfo: {self.wp_model_info}")

        # prefer EEPROM for FWHM, or lookup from model
        if self.settings.eeprom.avg_resolution > 0:
            self.fwhm = self.settings.eeprom.avg_resolution
            log.debug("using FWHM from EEPROM: %f", self.fwhm)
        else:
            self.fwhm = model_info.model_fwhm.get_by_model(self.settings.full_model())
            log.debug("using FWHM from lookup table: %s", self.fwhm)

        self.settings.eeprom_backup = copy.deepcopy(self.settings.eeprom)

        self.label = "%s (%s)" % (self.settings.eeprom.serial_number, self.settings.full_model())

        self.closing = False

        log.debug("Spectrometer: instantiated %s from device %s", self.label, self.device_id)

    def close(self):
        log.info("Spectrometer: closing %s", self.device_id)
        self.closing = True
        try:
            self.device.disconnect()
        except Exception as e:
            log.error("Spectrometer either does not exist or already disconnected {e}")
        log.info("Spectrometer: closed %s", self.device_id)

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
            log.error("invalid fwhm unit: %s", unit)
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

    def get_image_pathname(self, resources):
        default = ':/spectrometers/images/devices/stroker.png'

        if self.wp_model_info is None or resources is None:
            log.debug("get_image_pathname: no wp_model_info, so default %s", default)
            return default

        eeprom_model = self.settings.full_model()
        log.debug("get_image_pathname: eeprom_model = [%s]", eeprom_model)
        log.debug("get_image_pathname: wp_model_info =")
        if self.wp_model_info is not None:
            self.wp_model_info.dump()

        # try to build up an exact match of NAME + COUPLING
        if eeprom_model is not None:
            likely = self.wp_model_info.name

            # image files don't include -SR, so just add nothing for that case
            if "-ER" in eeprom_model:
                likely += "-ER"

            if "-L" in eeprom_model:
                likely += "-L"
            elif "-F" in eeprom_model: # Freespace, not Fiber
                likely += "-FS"
            elif "-S" in eeprom_model: 
                likely += "-SMA"

            if "-OEM" in eeprom_model:
                likely += "-OEM"

            log.debug("get_image_pathname: likely [%s]", likely)
            pathname = ":/spectrometers/images/devices/%s.png" % likely
            if resources.contains(pathname):
                log.debug("get_image_pathname: likely %s", pathname)
                return pathname

        # okay, then try to find NAME with any COUPLING
        for coupling in [ 'SMA', 'FS', 'L' ]: 
            pathname = ":/spectrometers/images/devices/%s-%s.png" % (self.wp_model_info.name, coupling)
            if resources.contains(pathname):
                log.debug("get_image_pathname: best %s is %s", self.wp_model_info.name, pathname)
                return pathname
            log.debug("get_image_pathname: not found: %s", pathname)

        log.debug("get_image_pathname: gave up, so default %s", default)
        return default

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
        log.debug("reset_acquisition_timeout(%s): expecting next acquisition within %d ms (by %s)", self.device_id, timeout_ms, future_time)

    ## send commands to device subprocess via (name, value) pickleable tuples
    def change_device_setting(self, setting, value=0):
        if self.closing:
            return

        device_id = self.device.device_id
        log.info("change_device_setting[%s]: %s -> %s", device_id, setting, value)
        self.device.change_setting(setting, value)

