import logging

from enlighten import common

log = logging.getLogger(__name__)

from enlighten.data.ModelInfoFeature import ModelInfoFeature
from enlighten.device.AccessoryControlFeature import AccessoryControlFeature
from enlighten.device.AmbientTemperatureFeature import AmbientTemperatureFeature
from enlighten.device.BatteryFeature import BatteryFeature
from enlighten.device.DetectorTemperatureFeature import DetectorTemperatureFeature
from enlighten.device.EEPROMEditorFeature import EEPROMEditorFeature
from enlighten.device.EEPROMWriter import EEPROMWriter
from enlighten.device.ExternalTriggerFeature import ExternalTriggerFeature
from enlighten.device.GainDBFeature import GainDBFeature
from enlighten.device.HighGainModeFeature import HighGainModeFeature
from enlighten.device.IntegrationTimeFeature import IntegrationTimeFeature
from enlighten.device.LaserControlFeature import LaserControlFeature
from enlighten.device.LaserTemperatureFeature import LaserTemperatureFeature
from enlighten.device.LaserWatchdogFeature import LaserWatchdogFeature
from enlighten.device.MultispecFeature import MultispecFeature
from enlighten.EnlightenFeature import EnlightenFeature
from enlighten.factory.DFUFeature import DFUFeature
from enlighten.factory.FactoryStripChartFeature import FactoryStripChartFeature
from enlighten.file_io.ConfigurationFeature import ConfigurationFeature
from enlighten.file_io.FileManagerFeature import FileManagerFeature
from enlighten.file_io.HardwareFileOutputFeature import HardwareFileOutputFeature
from enlighten.file_io.LoggingFeature import LoggingFeature
from enlighten.measurement.AreaScanFeature import AreaScanFeature
from enlighten.measurement.MeasurementFactory import MeasurementFactory
from enlighten.measurement.Measurements import Measurements
from enlighten.measurement.SaveOptionsFeature import SaveOptionsFeature
from enlighten.network.BLEManagerFeature import BLEManagerFeature
from enlighten.network.CloudManagerFeature import CloudManagerFeature
from enlighten.Plugins.PluginControllerFeature import PluginControllerFeature
from enlighten.post_processing.AbsorbanceFeature import AbsorbanceFeature
from enlighten.post_processing.AutoRamanFeature import AutoRamanFeature
from enlighten.post_processing.BaselineCorrectionFeature import BaselineCorrectionFeature
from enlighten.post_processing.BoxcarFeature import BoxcarFeature
from enlighten.post_processing.DalaiRamanFeature import DalaiRamanFeature
from enlighten.post_processing.DarkFeature import DarkFeature
from enlighten.post_processing.ElectricalDarkCorrectionFeature import ElectricalDarkCorrectionFeature
from enlighten.post_processing.EtalonCorrectionFeature import EtalonCorrectionFeature
from enlighten.post_processing.HorizROIFeature import HorizROIFeature
from enlighten.post_processing.InGaAsCorrectionFeature import InGaAsCorrectionFeature
from enlighten.post_processing.InterpolationFeature import InterpolationFeature
from enlighten.post_processing.LibraryMatchingFeature import LibraryMatchingFeature
from enlighten.post_processing.PixelCalibrationFeature import PixelCalibrationFeature
from enlighten.post_processing.RamanIntensityCorrectionFeature import RamanIntensityCorrectionFeature
from enlighten.post_processing.ReferenceFeature import ReferenceFeature
from enlighten.post_processing.RichardsonLucyFeature import RichardsonLucyFeature
from enlighten.post_processing.ScanAveragingFeature import ScanAveragingFeature
from enlighten.post_processing.TakeOneFeature import TakeOneFeature
from enlighten.post_processing.TransmissionFeature import TransmissionFeature
from enlighten.scope.CursorFeature import CursorFeature
from enlighten.scope.GraphFeature import GraphFeature
from enlighten.scope.GridFeature import GridFeature
from enlighten.scope.PresetFeature import PresetFeature
from enlighten.scope.RamanShiftCorrectionFeature import RamanShiftCorrectionFeature
from enlighten.timing.BatchCollectionFeature import BatchCollectionFeature
from enlighten.ui.AuthenticationFeature import AuthenticationFeature
from enlighten.ui.ClipboardFeature import ClipboardFeature
from enlighten.ui.Colors import Colors
from enlighten.ui.CorrectionStatusFeature import CorrectionStatusFeature
from enlighten.ui.DidYouKnowFeature import DidYouKnowFeature
from enlighten.ui.FocusListener import FocusListener
from enlighten.ui.GuideFeature import GuideFeature
from enlighten.ui.GUIFeature import GUIFeature
from enlighten.ui.HelpFeature import HelpFeature
from enlighten.ui.ImageResources import ImageResources
from enlighten.ui.MarqueeFeature import MarqueeFeature
from enlighten.ui.PageNavigationFeature import PageNavigationFeature
from enlighten.ui.ReadingProgressBarFeature import ReadingProgressBarFeature
from enlighten.ui.ResourceMonitorFeature import ResourceMonitorFeature
from enlighten.ui.SoundEffectsFeature import SoundEffectsFeature
from enlighten.ui.StatusBarFeature import StatusBarFeature
from enlighten.ui.StatusIndicatorFeature import StatusIndicatorFeature
from enlighten.ui.StylesheetFeature import StylesheetFeature
from enlighten.ui.VCRControlsFeature import VCRControlsFeature

class BusinessObjects:
    """
    This is sort of an "extension class" to Controller, or a "partial class" in C#
    terms.  It's not really a separate object, so much as a place to encapsulate 
    one huge set of related functionality out of Controller.py, to make that
    already-huge class more navigable and maintainable.
    """

    def __init__(self, ctl):
        self.ctl = ctl 
        self.clear()

    def clear(self):
        """ Ensures objects can check for other's instantiation during start-up """
        ctl = self.ctl

        ctl.absorbance = None
        ctl.accessory_control = None
        ctl.area_scan = None
        ctl.authentication = None
        ctl.auto_raman = None
        ctl.baseline_correction = None
        ctl.batch_collection = None
        ctl.battery_feature = None
        ctl.ble_manager = None
        ctl.boxcar = None
        ctl.clipboard = None
        ctl.cloud_manager = None
        ctl.colors = None
        ctl.config = None
        ctl.cursor = None
        ctl.dark_feature = None
        ctl.detector_temperature = None
        ctl.eeprom_editor = None
        ctl.eeprom_writer = None
        ctl.etalon_correction = None
        ctl.external_trigger = None
        ctl.factory_strip_feature = None
        ctl.file_manager = None
        ctl.focus_listener = None
        ctl.gain_db_feature = None
        ctl.graph = None
        ctl.grid = None
        ctl.gui = None
        ctl.guide = None
        ctl.hardware_file_manager = None
        ctl.help = None
        ctl.high_gain_mode = None
        ctl.horiz_roi = None
        ctl.image_resources = None
        ctl.ingaas_correction = None
        ctl.integration_time_feature = None
        ctl.interp = None
        ctl.laser_control = None
        ctl.laser_temperature = None
        ctl.laser_watchdog = None
        ctl.library_matching = None
        ctl.logging_feature = None
        ctl.marquee = None
        ctl.measurement_factory = None
        ctl.measurements = None
        ctl.mfg = None
        ctl.model_info = None
        ctl.multispec = None
        ctl.page_nav = None
        ctl.plugin_controller = None
        ctl.raman_intensity_correction = None
        ctl.raman_shift_correction = None
        ctl.reference_feature = None
        ctl.resource_monitor = None
        ctl.richardson_lucy = None
        ctl.save_options = None
        ctl.scan_averaging = None
        ctl.sounds = None
        ctl.status_bar = None
        ctl.status_indicators = None
        ctl.stylesheets = None
        ctl.take_one = None
        ctl.transmission = None
        ctl.vcr_controls = None

    def create_first(self):
        """
        These are things needed early in the Controller's constructor 
        initialization, i.e. before the placeholders are populated.
        """
        ctl = self.ctl

        ctl.config              = ConfigurationFeature(ctl)
        ctl.presets             = PresetFeature(ctl)
        ctl.logging_feature     = LoggingFeature(ctl)
        ctl.colors              = Colors(ctl.config)
        ctl.stylesheets         = StylesheetFeature(ctl)
        ctl.gui                 = GUIFeature(ctl)
        ctl.page_nav            = PageNavigationFeature(ctl)

    def create_rest(self):
        """
        Create the remaining business objects which allow us to encapsulate
        coherent sets of application functionality outside the Controller.
        
        This is called by Controller.__init__() after set_initial_state(), so you
        can assume that the GUI is configured and all widget placeholders have been
        populated. No spectrometers will have connected at this time.
        """
        ctl = self.ctl
        cfu = ctl.form.ui

        ctl.resource_monitor            = ResourceMonitorFeature(ctl)
        ctl.focus_listener              = FocusListener(ctl)
        ctl.model_info                  = ModelInfoFeature(ctl)
        ctl.marquee                     = MarqueeFeature(ctl)
        ctl.file_manager                = FileManagerFeature(ctl)
        ctl.clipboard                   = ClipboardFeature(ctl)
        ctl.guide                       = GuideFeature(ctl)
        ctl.graph                       = GraphFeature(ctl, name="Scope")
        ctl.hardware_file_manager       = HardwareFileOutputFeature(ctl)
        ctl.cursor                      = CursorFeature(ctl)
        ctl.image_resources             = ImageResources()
        ctl.multispec                   = MultispecFeature(ctl)
        ctl.battery_feature             = BatteryFeature(ctl)
        ctl.status_indicators           = StatusIndicatorFeature(ctl)
        ctl.detector_temperature        = DetectorTemperatureFeature(ctl)
        ctl.horiz_roi                   = HorizROIFeature(ctl)
        ctl.transmission                = TransmissionFeature(ctl)
        ctl.absorbance                  = AbsorbanceFeature(ctl)
        ctl.interp                      = InterpolationFeature(ctl)
        ctl.external_trigger            = ExternalTriggerFeature(ctl)
        ctl.save_options                = SaveOptionsFeature(ctl)
        ctl.measurement_factory         = MeasurementFactory(ctl)
        ctl.measurements                = Measurements(ctl)
        ctl.authentication              = AuthenticationFeature(ctl)
        ctl.eeprom_writer               = EEPROMWriter(ctl)
        ctl.eeprom_editor               = EEPROMEditorFeature(ctl)
        ctl.laser_control               = LaserControlFeature(ctl)
        ctl.laser_watchdog              = LaserWatchdogFeature(ctl)
        ctl.laser_temperature           = LaserTemperatureFeature(ctl)
        ctl.ambient_temperature         = AmbientTemperatureFeature(ctl)
        ctl.scan_averaging              = ScanAveragingFeature(ctl)
        ctl.take_one                    = TakeOneFeature(ctl)
        ctl.cloud_manager               = CloudManagerFeature(ctl)

        ctl.vcr_controls = VCRControlsFeature(ctl)
        ctl.vcr_controls.register_observer(ctl.save_current_spectra, "save")
        ctl.scan_averaging.complete_registrations()

        ctl.baseline_correction         = BaselineCorrectionFeature(ctl)
        ctl.dark_feature                = DarkFeature(ctl)
        ctl.edc                         = ElectricalDarkCorrectionFeature(ctl)
        ctl.reference_feature           = ReferenceFeature(ctl)
        ctl.raman_intensity_correction  = RamanIntensityCorrectionFeature(ctl)
        ctl.batch_collection            = BatchCollectionFeature(ctl)
        ctl.boxcar                      = BoxcarFeature(ctl)
        ctl.integration_time_feature    = IntegrationTimeFeature(ctl)
        ctl.gain_db_feature             = GainDBFeature(ctl)
        ctl.auto_raman                  = AutoRamanFeature(ctl)
        ctl.richardson_lucy             = RichardsonLucyFeature(ctl)
        ctl.dfu                         = DFUFeature(ctl)
        ctl.factory_strip_charts        = FactoryStripChartFeature(ctl)
        ctl.plugin_controller           = PluginControllerFeature(ctl)
        ctl.grid                        = GridFeature(ctl)
        ctl.area_scan                   = AreaScanFeature(ctl)
        ctl.etalon_correction           = EtalonCorrectionFeature(ctl)
        ctl.ingaas_correction           = InGaAsCorrectionFeature(ctl)
        ctl.raman_shift_correction      = RamanShiftCorrectionFeature(ctl)
        ctl.accessory_control           = AccessoryControlFeature(ctl)
        ctl.high_gain_mode              = HighGainModeFeature(ctl)
        ctl.sounds                      = SoundEffectsFeature(ctl)
        ctl.help                        = HelpFeature(ctl)
        ctl.did_you_know                = DidYouKnowFeature(ctl)
        ctl.status_bar                  = StatusBarFeature(ctl)
        ctl.reading_progress_bar        = ReadingProgressBarFeature(ctl)
        ctl.ble_manager                 = BLEManagerFeature(ctl)
        ctl.pixel_calibration           = PixelCalibrationFeature(ctl)
        ctl.library_matching            = LibraryMatchingFeature(ctl)
        ctl.dalai                       = DalaiRamanFeature(ctl)
        ctl.correction_status           = CorrectionStatusFeature(ctl)

    def destroy(self):
        log.info("destroying business objects")

        # anything with external processes
        for feature in [ self.ctl.plugin_controller ]:
            feature.disconnect()                        

        # anything with timers, observers etc
        for feature in [ self.ctl.marquee, 
                         self.ctl.guide,
                         self.ctl.library_matching ]:
            feature.stop()

        log.info("done destroying business objects")
