import logging

from enlighten import common

if common.use_pyside2():
    from PySide2.QtGui import QColor
    from PySide2.QtCore import Qt
else:
    from PySide6.QtGui import QColor
    from PySide6.QtCore import Qt

log = logging.getLogger(__name__)

from enlighten.KnowItAll.Feature import Feature as KIAFeature
from enlighten.Plugins.PluginController import PluginController
from enlighten.data.ModelInfo import ModelInfo
from enlighten.device.AccessoryControlFeature import AccessoryControlFeature
from enlighten.device.BatteryFeature import BatteryFeature
from enlighten.device.DetectorTemperatureFeature import DetectorTemperatureFeature
from enlighten.device.EEPROMEditor import EEPROMEditor
from enlighten.device.EEPROMWriter import EEPROMWriter
from enlighten.device.ExternalTriggerFeature import ExternalTriggerFeature
from enlighten.device.GainDBFeature import GainDBFeature
from enlighten.device.HighGainModeFeature import HighGainModeFeature
from enlighten.device.IntegrationTimeFeature import IntegrationTimeFeature
from enlighten.device.LaserControlFeature import LaserControlFeature
from enlighten.device.LaserWatchdogFeature import LaserWatchdogFeature
from enlighten.device.LaserTemperatureFeature import LaserTemperatureFeature
from enlighten.device.AmbientTemperatureFeature import AmbientTemperatureFeature
from enlighten.device.Multispec import Multispec
from enlighten.device.RegionControlFeature import RegionControlFeature
from enlighten.factory.DFUFeature import DFUFeature
from enlighten.factory.FactoryStripChartFeature import FactoryStripChartFeature
from enlighten.file_io.Configuration import Configuration
from enlighten.file_io.FileManager import FileManager
from enlighten.file_io.HardwareFileOutputManager import HardwareFileOutputManager
from enlighten.file_io.LoggingFeature import LoggingFeature
from enlighten.measurement.AreaScanFeature import AreaScanFeature
from enlighten.measurement.MeasurementFactory import MeasurementFactory
from enlighten.measurement.Measurements import Measurements
from enlighten.measurement.SaveOptions import SaveOptions
from enlighten.network.BLEManager import BLEManager
from enlighten.network.CloudManager import CloudManager
from enlighten.post_processing.AbsorbanceFeature import AbsorbanceFeature
from enlighten.post_processing.AutoRamanFeature import AutoRamanFeature
from enlighten.post_processing.BaselineCorrection import BaselineCorrection
from enlighten.post_processing.BoxcarFeature import BoxcarFeature
from enlighten.post_processing.DarkFeature import DarkFeature
from enlighten.post_processing.ElectricalDarkCorrectionFeature import ElectricalDarkCorrectionFeature
from enlighten.post_processing.HorizROIFeature import HorizROIFeature
from enlighten.post_processing.InterpolationFeature import InterpolationFeature
from enlighten.post_processing.PixelCalibration import PixelCalibration
from enlighten.post_processing.RamanIntensityCorrection import RamanIntensityCorrection
from enlighten.post_processing.ReferenceFeature import ReferenceFeature
from enlighten.post_processing.RichardsonLucy import RichardsonLucy
from enlighten.post_processing.ScanAveragingFeature import ScanAveragingFeature
from enlighten.post_processing.TakeOneFeature import TakeOneFeature
from enlighten.post_processing.TransmissionFeature import TransmissionFeature
from enlighten.scope.Cursor import Cursor
from enlighten.scope.Graph import Graph
from enlighten.scope.GridFeature import GridFeature
from enlighten.scope.PresetFeature import PresetFeature
from enlighten.scope.RamanShiftCorrectionFeature import RamanShiftCorrectionFeature
from enlighten.timing.BatchCollection import BatchCollection
from enlighten.ui.Authentication import Authentication
from enlighten.ui.Clipboard import Clipboard
from enlighten.ui.Colors import Colors
from enlighten.ui.DidYouKnowFeature import DidYouKnowFeature
from enlighten.ui.FocusListener import FocusListener
from enlighten.ui.GUI import GUI
from enlighten.ui.GuideFeature import GuideFeature
from enlighten.ui.HelpFeature import HelpFeature
from enlighten.ui.ImageResources import ImageResources
from enlighten.ui.Marquee import Marquee
from enlighten.ui.PageNavigation import PageNavigation
from enlighten.ui.ReadingProgressBar import ReadingProgressBar
from enlighten.ui.ResourceMonitorFeature import ResourceMonitorFeature
from enlighten.ui.Sounds import Sounds
from enlighten.ui.StatusBarFeature import StatusBarFeature
from enlighten.ui.StatusIndicators import StatusIndicators
from enlighten.ui.Stylesheets import Stylesheets
from enlighten.ui.VCRControls import VCRControls

class BusinessObjects:
    """
    This is sort of an "extension class" to Controller, or a "partial class" in C#
    terms.  It's not really a separate object, so much as a place to encapsulate 
    one huge set of related functionality out of Controller.py, to make that
    already-huge class more navigable and maintainable.
    
    Consider having this maintain a list of all business objects, so Controller
    could call update_visibility() etc on all of them.
    """

    def __init__(self, ctl):
        self.ctl = ctl 
        self.clear()

    def header(self, msg):
        log.debug("")
        log.debug("=" * len(msg))
        log.debug(msg)
        log.debug("=" * len(msg))
        log.debug("")

        self.ctl.splash.showMessage(f"version {common.VERSION}\n\n{msg}\n", alignment=Qt.AlignHCenter | Qt.AlignBottom, color=QColor("#ccc"))
        self.ctl.app.processEvents()

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
        ctl.external_trigger = None
        ctl.file_manager = None
        ctl.focus_listener = None
        ctl.gain_db_feature = None
        ctl.graph = None
        ctl.grid = None
        ctl.gui = None
        ctl.guide = None
        ctl.factory_strip_feature = None
        ctl.hardware_file_manager = None
        ctl.help = None
        ctl.high_gain_mode = None
        ctl.horiz_roi = None
        ctl.image_resources = None
        ctl.integration_time_feature = None
        ctl.interp = None
        ctl.kia_feature = None
        ctl.laser_control = None
        ctl.laser_watchdog = None
        ctl.laser_temperature = None
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
        ctl.region_control = None
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

        self.header("instantiating Configuration")
        ctl.config = Configuration(ctl)

        self.header("instantiating Presets")
        ctl.presets = PresetFeature(ctl)

        self.header("instantiating LoggingFeature")
        ctl.logging_feature = LoggingFeature(ctl)

        self.header("instantiating Colors")
        ctl.colors = Colors(ctl.config)

        self.header("instantiating Stylesheets")
        ctl.stylesheets = Stylesheets(ctl)

        self.header("instantiating GUI")
        ctl.gui = GUI(ctl)

        self.header("instantiating PageNavigation")
        ctl.page_nav = PageNavigation(ctl)

    def create_rest(self):
        """
        Create the remaining business objects which allow us to encapsulate
        coherent sets of application functionality outside the Controller.
        
        This is called by Controller.__init__() after set_initial_state(), so you
        can assume that the GUI is configured and all widget placeholders have been
        populated.  No spectrometers will have connected at this time.
        """
        ctl = self.ctl
        cfu = ctl.form.ui

        self.header("instantiating ResourceMonitorFeature")
        ctl.resource_monitor = ResourceMonitorFeature(ctl)

        self.header("instantiating FocusListener")
        ctl.focus_listener = FocusListener(ctl)

        self.header("instantiating ModelInfo")
        ctl.model_info = ModelInfo(ctl)

        self.header("instantiating Marquee")
        ctl.marquee = Marquee(ctl)

        self.header("instantiating FileManager")
        ctl.file_manager = FileManager(ctl)

        self.header("instantiating Clipboard")
        ctl.clipboard = Clipboard(ctl)

        self.header("instantiating GuideFeature")
        ctl.guide = GuideFeature(ctl)

        self.header("instantiating Graph")
        ctl.graph = Graph(ctl, name="Scope")

        self.header("instantiating HardwareFileOutputManager")
        ctl.hardware_file_manager = HardwareFileOutputManager(ctl)

        self.header("instantiating Cursor")
        ctl.cursor = Cursor(ctl)

        self.header("instantiating ImageResources")
        ctl.image_resources = ImageResources()

        self.header("instantiating Multispec")
        ctl.multispec = Multispec(ctl)

        self.header("instantiating BatteryFeature")
        ctl.battery_feature = BatteryFeature(ctl)

        self.header("instantiating StatusIndicators")
        ctl.status_indicators = StatusIndicators(ctl)

        self.header("instantiating DetectorTemperatureFeature")
        ctl.detector_temperature = DetectorTemperatureFeature(ctl)

        self.header("instantiating HorizROIFeature")
        ctl.horiz_roi = HorizROIFeature(ctl)

        self.header("instantiating TransmissionFeature")
        ctl.transmission = TransmissionFeature(ctl)

        self.header("instantiating AbsorbanceFeature")
        ctl.absorbance = AbsorbanceFeature(ctl)

        self.header("instantiating InterpolationFeature")
        ctl.interp = InterpolationFeature(ctl)

        self.header("instantiating ExternalTriggerFeature")
        ctl.external_trigger = ExternalTriggerFeature(ctl)

        self.header("instantiating SaveOptions")
        ctl.save_options = SaveOptions(ctl)

        self.header("instantiating MeasurementFactory")
        ctl.measurement_factory = MeasurementFactory(ctl)

        self.header("instantiating Measurements")
        ctl.measurements = Measurements(ctl)

        self.header("instantiating Authentication")
        ctl.authentication = Authentication(ctl)

        self.header("instantiating EEPROMWriter")
        ctl.eeprom_writer = EEPROMWriter(ctl)

        self.header("instantiating EEPROMEditor")
        ctl.eeprom_editor = EEPROMEditor(ctl)

        self.header("instantiating LaserControlFeature")
        ctl.laser_control = LaserControlFeature(ctl)

        self.header("instantiating LaserWatchdogFeature")
        ctl.laser_watchdog = LaserWatchdogFeature(ctl)

        self.header("instantiating LaserTemperatureFeature")
        ctl.laser_temperature = LaserTemperatureFeature(ctl)

        self.header("instantiating AmbientTemperatureFeature")
        ctl.ambient_temperature = AmbientTemperatureFeature(ctl)

        self.header("instantiating ScanAveragingFeature")
        ctl.scan_averaging = ScanAveragingFeature(ctl)

        self.header("instantiating TakeOneFeature")
        ctl.take_one = TakeOneFeature(ctl)

        self.header("instantiating CloudManager")
        ctl.cloud_manager = CloudManager(ctl)

        self.header("instantiating VCRControls")
        ctl.vcr_controls = VCRControls(ctl)

        # need a more general way of handling these
        ctl.vcr_controls.register_observer("save", ctl.save_current_spectra)
        ctl.scan_averaging.complete_registrations()

        self.header("instantiating BaselineCorrection")
        ctl.baseline_correction = BaselineCorrection(ctl)

        self.header("instantiating DarkFeature")
        ctl.dark_feature = DarkFeature(ctl)

        self.header("instantiating ElectricalDarkCorrectionFeature")
        ctl.edc = ElectricalDarkCorrectionFeature(ctl)

        self.header("instantiating ReferenceFeature")
        ctl.reference_feature = ReferenceFeature(ctl)

        self.header("instantiating RamanIntensityCorrection")
        ctl.raman_intensity_correction = RamanIntensityCorrection(ctl)

        self.header("instantiating BatchCollection")
        ctl.batch_collection = BatchCollection(ctl)

        self.header("instantiating BoxcarFeature")
        ctl.boxcar = BoxcarFeature(ctl)

        self.header("instantiating IntegrationTimeFeature")
        ctl.integration_time_feature = IntegrationTimeFeature(ctl)

        self.header("instantiating GainDBFeature")
        ctl.gain_db_feature = GainDBFeature(ctl)

        self.header("instantiating AutoRamanFeature")
        ctl.auto_raman = AutoRamanFeature(ctl)

        # TODO: refactor like PluginController
        self.header("instantiating KIAFeature")
        ctl.kia_feature = KIAFeature(ctl)

        self.header("instantiating RichardsonLucy")
        ctl.richardson_lucy = RichardsonLucy(ctl)

        self.header("instantiating DFUFeature")
        ctl.dfu = DFUFeature(ctl)

        self.header("instantiating FactoryStripChartFeature")
        ctl.factory_strip_charts = FactoryStripChartFeature(ctl)

        self.header("instantiating PluginController")
        ctl.plugin_controller = PluginController(ctl)

        self.header("instantiating GridFeature")
        ctl.grid = GridFeature(ctl)

        self.header("instantiating AreaScanFeature")
        ctl.area_scan = AreaScanFeature(
            bt_save                     = cfu.pushButton_area_scan_save,
            cb_enable                   = cfu.checkBox_area_scan_enable,
            cb_fast                     = cfu.checkBox_area_scan_fast,
            frame_image                 = cfu.frame_area_scan_image,
            frame_live                  = cfu.frame_area_scan_live,
            graphics_view               = cfu.graphicsView_area_scan,
            gui                         = ctl.gui,
            layout_live                 = cfu.layout_area_scan_live,
            lb_current                  = cfu.label_area_scan_current_line,
            lb_frame_count              = cfu.label_area_scan_frame_count,
            marquee                     = ctl.marquee,
            multispec                   = ctl.multispec,
            progress_bar                = cfu.progressBar_area_scan,
            save_options                = ctl.save_options,
            sb_start                    = cfu.spinBox_area_scan_start_line,
            sb_stop                     = cfu.spinBox_area_scan_stop_line,
            sb_delay_ms                 = cfu.spinBox_area_scan_delay_ms,
            set_curve_data              = ctl.set_curve_data)

        self.header("instantiating RamanShiftCorrectionFeature")
        ctl.raman_shift_correction = RamanShiftCorrectionFeature(
            button                      = cfu.pushButton_ramanCorrection,
            cb_visible                  = cfu.checkBox_ramanCorrection_visible,
            combo                       = cfu.comboBox_ramanCorrection_compoundName,
            config                      = ctl.config,
            frame                       = cfu.frame_ramanCorrection_white,
            graph                       = ctl.graph,
            gui                         = ctl.gui,
            marquee                     = ctl.marquee,
            multispec                   = ctl.multispec,
            page_nav                    = ctl.page_nav)

        self.header("instantiating AccessoryControlFeature")
        ctl.accessory_control = AccessoryControlFeature(
            cb_display                  = cfu.checkBox_accessory_cont_strobe_display,
            cb_enable                   = cfu.checkBox_accessory_cont_strobe_enable,
            cb_fan                      = cfu.checkBox_accessory_fan,
            cb_lamp                     = cfu.checkBox_accessory_lamp,
            cb_shutter                  = cfu.checkBox_accessory_shutter,
            frame_cont_strobe           = cfu.frame_accessory_cont_strobe,
            frame_widget                = cfu.frame_accessory_widget,
            multispec                   = ctl.multispec,
            sb_freq_hz                  = cfu.spinBox_accessory_cont_strobe_freq_hz,
            sb_width_us                 = cfu.spinBox_accessory_cont_strobe_width_us)

        self.header("instantiating HighGainModeFeature")
        ctl.high_gain_mode = HighGainModeFeature(ctl)

        self.header("instantiating RegionControlFeature")
        ctl.region_control = RegionControlFeature(
            cb_enabled                  = cfu.checkBox_region_enabled,
            multispec                   = ctl.multispec,
            spinbox                     = cfu.spinBox_region)

        self.header("instantiating Sounds")
        ctl.sounds = Sounds(ctl)

        self.header("instantiating HelpFeature")
        ctl.help = HelpFeature(ctl)

        self.header("instantiating DidYouKnowFeature")
        ctl.did_you_know = DidYouKnowFeature(ctl)

        self.header("instantiating StatusBarFeature")
        ctl.status_bar = StatusBarFeature(ctl)

        self.header("instantiating ReadingProgressBar")
        ctl.reading_progress_bar = ReadingProgressBar(ctl)

        self.header("instantiating BLEManager")
        ctl.ble_manager = BLEManager(ctl)

        self.header("instantiating PixelCalibration")
        ctl.pixel_calibration = PixelCalibration(ctl)

        self.header("done with Business Object creation")

    def destroy(self):
        log.info("destroying business objects")

        # anything with external processes
        for feature in [ self.ctl.kia_feature,
                         self.ctl.plugin_controller ]:
            feature.disconnect()                        

        # anything with timers, observers etc
        for feature in [ self.ctl.marquee, 
                         self.ctl.guide ]:
            feature.stop()

        log.info("done destroying business objects")
