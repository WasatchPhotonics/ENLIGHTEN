import logging

from wasatch.ProcessedReading import ProcessedReading
from .RollingDataSet   import RollingDataSet

log = logging.getLogger(__name__)

##
# These are things that are very much ENLIGHTEN-specific and not generic
# enough to be in Wasatch.PY's SpectrometerState.  That class is for spectrometer
# state that "any" Python-based spectroscopy app is likely to need, and provided
# in a public class for common naming, re-use etc.  In contrast, this class
# is for things only ENLIGHTEN cares about, but need to be in a class so we can
# track them for multiple spectrometers.
#
# We might want to split this class in half, into "lightweight things we want to
# persist with Measurements" (dark/reference timestamps, reading_count, current 
# temperatures) and "heavyweight things we don't" (waterfall, historical 
# temperatures).
class SpectrometerApplicationState(object):

    def clear(self):
        self.device_id = None
        self.processed_reading = None
        self.dark                = None
        self.reference           = None
        self.dark_timestamp      = None
        self.reference_timestamp = None
        self.reference_is_dark_corrected = False
        self.reference_excitation = None
        self.reading_count = 0
        self.paused = False
        self.hidden = False
        self.waterfall = []
        self.missing_acquisition_timeout = None
        self.pending_disconnect = False
        self.baseline_correction_algo = None
        self.baseline_correction_enabled = False # MZ: is this used? should it be?
        self.spec_timeout_prompt_shown = False
        self.missed_reading_count = 0

        # to track separately from SpectrometerState, which is shared with Wasatch.PY thread
        self.laser_gui_firing = False 
        self.last_laser_toggle = None

        self.reset_rolling_data()

    def __init__(self, device_id):
        self.device_id = device_id
        self.clear()

    def dump(self):
        log.info("SpectrometerApplicationState:")
        log.info("  Device ID:                  %s", self.device_id)
        log.info("  Dark:                       %s (%s)", None if self.dark      is None else self.dark     [:5], self.dark_timestamp)
        log.info("  Reference:                  %s (%s)", None if self.reference is None else self.reference[:5], self.reference_timestamp)
        log.info("  Reference Dark-Corrected:   %s", self.reference_is_dark_corrected)
        log.info("  Reading Count:              %d", self.reading_count)
        log.info("  Paused:                     %s", self.paused)
        log.info("  Hidden:                     %s", self.hidden)
        log.info("  Waterfall:                  %s", None if self.waterfall is None else self.waterfall[:5])
        log.info("  Missing Acquisition Timeout:%s", self.missing_acquisition_timeout)
        log.info("  Pending Disconnect:         %s", self.pending_disconnect)
        log.info("  Laser Temperature:          %s", self.laser_temperature_data)
        log.info("  Laser GUI Firing:           %s", self.laser_gui_firing)
        log.info("  Last Laser Toggle:          %s", self.last_laser_toggle)
        log.info("  Detector Temperature:       %s", self.detector_temperatures_degC)
        log.info("  Detector Temperature Avg:   %s", self.detector_temperatures_degC_averaged)
        log.info("  Detector Temperature Disp:  %s", self.detector_temperatures_degC_averaged_display)
        log.info("  Secondary ADC Fast:         %s", self.secondary_adc_data_fast)
        log.info("  Secondary ADC Medium:       %s", self.secondary_adc_data_medium)
        log.info("  Secondary ADC Slow:         %s", self.secondary_adc_data_slow)
        log.info("  Baseline Correction Algo:   %s", self.baseline_correction_algo)
        log.info("  Baseline Correction Enabled:%s", self.baseline_correction_enabled)
        if self.processed_reading is not None:
            log.info("  Processed Reading:")
            self.processed_reading.dump()

    def has_dark(self):
        return self.dark is not None

    def has_reference(self):
        return self.reference is not None

    def clear_dark(self):
        self.dark = None
        self.dark_timestamp = None

    def clear_reference(self):
        self.reference = None
        self.reference_timestamp = None
        self.reference_is_dark_corrected = False
        self.reference_excitation = None

    ## @todo remove sfu (add setters for secondary adc windows)
    def reset_rolling_data(self, sfu=None, time_window=3, hotplug=True):
        # 1. raw data (all recent measurements, updated at a FAST rate)
        # 2. smoothed (use to display on-screen label at a MEDIUM rate)
        # 3. historical (on-screen graph trendline, updated at a SLOW rate)
        if not hotplug:
            return
        self.laser_temperature_data = RollingDataSet(time_window)
        self.battery_data = RollingDataSet(time_window)

        self.detector_temperatures_degC                  = RollingDataSet(time_window)
        self.detector_temperatures_degC_averaged         = RollingDataSet(time_window) # MZ: basically just slows down display graph rate
        self.detector_temperatures_degC_averaged_display = RollingDataSet(time_window)
        self.detector_temperature_degC_latest = None

        windows = (2, 2, 500)
        if sfu is not None:
            windows = (sfu.spinBox_secondary_adc_rolling_window_fast.value(),
                       sfu.spinBox_secondary_adc_rolling_window_medium.value(),
                       sfu.spinBox_secondary_adc_rolling_graph.value()) 

        self.secondary_adc_data_fast   = RollingDataSet(windows[0])
        self.secondary_adc_data_medium = RollingDataSet(windows[1])
        self.secondary_adc_data_slow   = RollingDataSet(windows[2])

    def update_rolling_data(self, window_value):

        self.battery_data.update_window(window_value)
        self.laser_temperature_data.update_window(window_value)
        self.detector_temperatures_degC.update_window(window_value)
        self.detector_temperatures_degC_averaged.update_window(window_value) 
        self.detector_temperatures_degC_averaged_display.update_window(window_value)

