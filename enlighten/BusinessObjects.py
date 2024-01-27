import logging

from enlighten import common

if common.use_pyside2():
    from PySide2.QtGui import QColor
    from PySide2.QtCore import *
else:
    from PySide6.QtGui import QColor
    from PySide6.QtCore import *

log = logging.getLogger(__name__)

from enlighten.file_io.HardwareCaptureControlFeature import HardwareCaptureControlFeature
from enlighten.scope.RamanShiftCorrectionFeature import RamanShiftCorrectionFeature     # single-point correction
from enlighten.device.DetectorTemperatureFeature import DetectorTemperatureFeature
from enlighten.file_io.HardwareFileOutputManager import HardwareFileOutputManager
from enlighten.post_processing.RamanIntensityCorrection import RamanIntensityCorrection   # SRM
from enlighten.device.AccessoryControlFeature import AccessoryControlFeature
from enlighten.device.LaserTemperatureFeature import LaserTemperatureFeature
from enlighten.device.IntegrationTimeFeature import IntegrationTimeFeature
from enlighten.device.ExternalTriggerFeature import ExternalTriggerFeature
from enlighten.ui.ResourceMonitorFeature import ResourceMonitorFeature
from enlighten.post_processing.InterpolationFeature import InterpolationFeature
from enlighten.post_processing.ScanAveragingFeature import ScanAveragingFeature
from enlighten.device.RegionControlFeature import RegionControlFeature
from enlighten.device.ManufacturingFeature import ManufacturingFeature
from enlighten.device.LaserControlFeature import LaserControlFeature
from enlighten.device.HighGainModeFeature import HighGainModeFeature
from enlighten.post_processing.TransmissionFeature import TransmissionFeature
from enlighten.measurement.MeasurementFactory import MeasurementFactory
from enlighten.post_processing.BaselineCorrection import BaselineCorrection
from enlighten.post_processing.HorizROIFeature import HorizROIFeature
from enlighten.post_processing.AbsorbanceFeature import AbsorbanceFeature
from enlighten.ui.StatusBarFeature import StatusBarFeature
from enlighten.post_processing.RamanModeFeature import RamanModeFeature
from enlighten.ui.StatusIndicators import StatusIndicators
from enlighten.post_processing.ReferenceFeature import ReferenceFeature
from enlighten.measurement.AreaScanFeature import AreaScanFeature
from enlighten.timing.BatchCollection import BatchCollection
from enlighten.ui.Authentication import Authentication
from enlighten.scope.PresetFeature import PresetFeature
from enlighten.ui.ImageResources import ImageResources
from enlighten.ui.PageNavigation import PageNavigation
from enlighten.post_processing.TakeOneFeature import TakeOneFeature
from enlighten.post_processing.RichardsonLucy import RichardsonLucy
from enlighten.device.BatteryFeature import BatteryFeature
from enlighten.file_io.LoggingFeature import LoggingFeature
from enlighten.ui.FocusListener import FocusListener
from enlighten.device.GainDBFeature import GainDBFeature
from enlighten.post_processing.BoxcarFeature import BoxcarFeature
from enlighten.file_io.Configuration import Configuration
from enlighten.measurement.Measurements import Measurements
from enlighten.device.EEPROMEditor import EEPROMEditor
from enlighten.scope.GuideFeature import GuideFeature
from enlighten.network.CloudManager import CloudManager
from enlighten.device.EEPROMWriter import EEPROMWriter
from enlighten.ui.Stylesheets import Stylesheets
from enlighten.post_processing.DarkFeature import DarkFeature
from enlighten.measurement.SaveOptions import SaveOptions
from enlighten.scope.GridFeature import GridFeature
from enlighten.file_io.FileManager import FileManager
from enlighten.ui.VCRControls import VCRControls
from enlighten.ui.HelpFeature import HelpFeature
from enlighten.network.BLEManager import BLEManager
from enlighten.ui.Clipboard import Clipboard
from enlighten.data.ModelInfo import ModelInfo
from enlighten.device.Multispec import Multispec
from enlighten.ui.Marquee import Marquee
from enlighten.ui.Colors import Colors
from enlighten.ui.Sounds import Sounds
from enlighten.scope.Cursor import Cursor
from enlighten.scope.Graph import Graph
from enlighten.ui.GUI import GUI

from .KnowItAll.Feature               import Feature as KIAFeature
from .Plugins.PluginController        import PluginController

class BusinessObjects:
    """
    This is sort of an "extension class" to Controller, or a "partial class" in C#
    terms.  It's not really a separate object, so much as a place to encapsulate 
    one huge set of related functionality out of Controller.py, to make that
    already-huge class more navigable and maintainable.
    
    Consider having this maintain a list of all business objects, so Controller
    could call update_visibility() etc on all of them.
    """

    def __init__(self, controller):
        self.controller = controller
        self.clear()

    def header(self, s):
        log.debug("")
        log.debug("=" * len(s))
        log.debug(s)
        log.debug("=" * len(s))
        log.debug("")

        self.controller.splash.showMessage(s, alignment=Qt.AlignHCenter | Qt.AlignBottom, color=QColor("white"))
        self.controller.app.processEvents()

    def clear(self):
        """ Ensures objects can check for other's instantiation during start-up """
        ctl = self.controller

        ctl.absorbance = None
        ctl.accessory_control = None
        ctl.area_scan = None
        ctl.authentication = None
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
        ctl.hardware_control_feature = None
        ctl.hardware_file_manager = None
        ctl.help = None
        ctl.high_gain_mode = None
        ctl.horiz_roi = None
        ctl.image_resources = None
        ctl.integration_time_feature = None
        ctl.interp = None
        ctl.kia_feature = None
        ctl.laser_control = None
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
        ctl.raman_mode_feature = None
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
        ctl = self.controller
        sfu = ctl.form.ui

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
        ctl = self.controller
        sfu = ctl.form.ui

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

        self.header("instantiating StatusBarFeature")
        ctl.status_bar = StatusBarFeature(ctl)

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

        self.header("instantiating RamanIntensityCorrection")
        ctl.raman_intensity_correction = RamanIntensityCorrection(ctl)

        self.header("instantiating LaserControlFeature")
        ctl.laser_control = LaserControlFeature(ctl)

        self.header("instantiating LaserTemperatureFeature")
        ctl.laser_temperature = LaserTemperatureFeature(
            sfu                         = sfu,
            graph                       = ctl.graph,
            multispec                   = ctl.multispec,
            lb_degC                     = sfu.label_hardware_capture_details_laser_temperature,
            make_pen                    = ctl.gui.make_pen,
            clipboard                   = ctl.clipboard,
            hardware_file_manager       = ctl.hardware_file_manager)

        self.header("instantiating Sounds")
        ctl.sounds = Sounds(
            checkbox                    = sfu.checkBox_sound_enable,
            config                      = ctl.config,
            path                        = "enlighten/assets/example_data/sounds")

        self.header("instantiating ScanAveragingFeature")
        ctl.scan_averaging = ScanAveragingFeature(ctl)

        self.header("instantiating TakeOneFeature")
        ctl.take_one = TakeOneFeature(ctl)

        self.header("instantiating CloudManager")
        ctl.cloud_manager = CloudManager(
            cb_enabled                  = sfu.checkBox_cloud_config_download_enabled,
            restore_button              = sfu.pushButton_restore_eeprom,

            config                      = ctl.config,
            eeprom_editor               = ctl.eeprom_editor)

        self.header("instantiating VCRControls")
        ctl.vcr_controls = VCRControls(ctl)
        ctl.vcr_controls.register_observer("save", ctl.save_current_spectra)
        ctl.scan_averaging.complete_registrations()

        self.header("instantiating BaselineCorrection")
        ctl.baseline_correction = BaselineCorrection(ctl)

        self.header("instantiating DarkFeature")
        ctl.dark_feature = DarkFeature(ctl)

        self.header("instantiating ReferenceFeature")
        ctl.reference_feature = ReferenceFeature(
            graph                       = ctl.graph,
            gui                         = ctl.gui,
            marquee                     = ctl.marquee,
            measurement_factory         = ctl.measurement_factory,
            multispec                   = ctl.multispec,
            page_nav                    = ctl.page_nav,
            save_options                = ctl.save_options,
            set_curve_data              = ctl.set_curve_data,
                                        
            button_clear                = sfu.pushButton_reference_clear,
            button_load                 = sfu.pushButton_reference_load,
            button_store                = sfu.pushButton_reference_store,
            button_toggle               = sfu.pushButton_scope_toggle_reference,
            frame_setup                 = sfu.frame_scopeSetup_spectra_reference_white,
            lb_timestamp                = sfu.label_reference_timestamp,
            stacked_widget              = sfu.stackedWidget_scope_setup_reference_spectrum,
            gui_make_pen                = ctl.gui.make_pen)

        self.header("instantiating BatchCollection")
        ctl.batch_collection = BatchCollection(ctl)

        self.header("instantiating BoxcarFeature")
        ctl.boxcar = BoxcarFeature(ctl)

        self.header("instantiating IntegrationTimeFeature")
        ctl.integration_time_feature = IntegrationTimeFeature(ctl)

        self.header("instantiating GainDBFeature")
        ctl.gain_db_feature = GainDBFeature(ctl)

        self.header("instantiating BLEManager")
        ctl.ble_manager = BLEManager(
            marquee                     = ctl.marquee,
            ble_button                  = sfu.pushButton_bleScan,
            controller_connect          = ctl.connect_new,
            controller_disconnect       = ctl.disconnect_device,
            progress_bar                = sfu.readingProgressBar,
            multispec                   = ctl.multispec)

        self.header("instantiating RamanModeFeature")
        ctl.raman_mode_feature = RamanModeFeature(ctl)

        # TODO: refactor like PluginController
        self.header("instantiating KIAFeature")
        ctl.kia_feature = KIAFeature(
            baseline_correction         = ctl.baseline_correction,
            bt_alias                    = sfu.pushButton_id_results_make_alias,
            bt_benign                   = sfu.pushButton_id_results_flag_benign,
            bt_clear                    = sfu.pushButton_id_results_clear,
            bt_hazard                   = sfu.pushButton_id_results_flag_hazard,
            bt_id                       = sfu.pushButton_scope_id,
            bt_reset                    = sfu.pushButton_id_results_reset,
            bt_suppress                 = sfu.pushButton_id_results_suppress,
            cb_all                      = sfu.checkBox_kia_display_all_results,
            cb_enabled                  = sfu.checkBox_kia_enabled,
            cb_hazard                   = sfu.checkBox_kia_alarm_low_scoring_hazards,
            colors                      = ctl.colors,
            page_nav                    = ctl.page_nav,
            file_manager                = ctl.file_manager,
            frame_results               = sfu.frame_id_results_white,
            frame_side                  = sfu.frame_kia_outer,
            generate_x_axis             = ctl.generate_x_axis,
            get_last_processed_reading  = ctl.get_last_processed_reading,
            guide                       = ctl.guide,
            lb_logo                     = sfu.label_kia_logo,
            lb_name                     = sfu.label_kia_compound_name,
            lb_path                     = sfu.label_kia_install_path,
            lb_processing               = sfu.label_kia_processing,
            lb_score                    = sfu.label_kia_score,
            logging_feature             = ctl.logging_feature,
            marquee                     = ctl.marquee,
            measurements                = ctl.measurements,
            multispec                   = ctl.multispec,
            raman_intensity_correction  = ctl.raman_intensity_correction,
            sb_score_min                = sfu.spinBox_kia_score_min,
            sb_max_results              = sfu.spinBox_kia_max_results,
            sounds                      = ctl.sounds,
            stylesheets                 = ctl.stylesheets,
            table_recent                = sfu.tableWidget_id_match_recent,
            table_results               = sfu.tableWidget_id_match_results,
            vcr_controls                = ctl.vcr_controls,
            horiz_roi                   = ctl.horiz_roi)

        self.header("instantiating RichardsonLucy")
        ctl.richardson_lucy = RichardsonLucy(
            cb_enable                   = sfu.checkBox_richardson_lucy,
            config                      = ctl.config,
            graph                       = ctl.graph,
            multispec                   = ctl.multispec,
            horiz_roi                   = ctl.horiz_roi)

        self.header("instantiating ManufacturingFeature")
        ctl.mfg = ManufacturingFeature(
            bt_dfu                      = sfu.pushButton_mfg_dfu,
            multispec                   = ctl.multispec)

        self.header("instantiating HardwareCaptureControlFeature")
        ctl.hardware_control_feature = HardwareCaptureControlFeature(
            sfu                         = sfu,
            graph                       = ctl.graph,
            laser_feature               = ctl.laser_temperature,
            detector_feature            = ctl.detector_temperature)

        self.header("instantiating PluginController")
        ctl.plugin_controller = PluginController(
            ctl=ctl,
            colors                      = ctl.colors,
            config                      = ctl.config,
            generate_x_axis             = ctl.generate_x_axis,
            get_last_processed_reading  = ctl.get_last_processed_reading,
            get_settings                = ctl.settings,
            graph_scope                 = ctl.graph,
            gui                         = ctl.gui,
            marquee                     = ctl.marquee,
            measurement_factory         = ctl.measurement_factory,
            multispec                   = ctl.multispec,
            parent                      = ctl.form,
            save_options                = ctl.save_options,
            kia_feature                 = ctl.kia_feature,
            measurements_clipboard      = ctl.measurements,
            horiz_roi                   = ctl.horiz_roi,

            button_process              = sfu.pushButton_plugin_process,
            cb_connected                = sfu.checkBox_plugin_connected,
            cb_enabled                  = sfu.checkBox_plugin_enabled,
            combo_graph_pos             = sfu.comboBox_plugin_graph_pos,
            combo_module                = sfu.comboBox_plugin_module,
            frame_control               = sfu.frame_plugin_control,
            frame_fields                = sfu.frame_plugin_fields,
            layout_graphs               = sfu.layout_scope_capture_graphs,
            lb_graph_pos                = sfu.label_plugin_graph_pos,
            lb_title                    = sfu.label_plugin_title,
            lb_widget                   = sfu.label_plugin_widget,
            vlayout_fields              = sfu.verticalLayout_plugin_fields,
            measurements                = ctl.measurements)

        self.header("instantiating GridFeature")
        ctl.grid = GridFeature(
            button                      = sfu.pushButton_graphGrid,
            gui                         = ctl.gui,
            stylesheets                 = ctl.stylesheets,
            plots                       = {
                                            "scope graph" : [ctl.graph, "plot"],
                                            "plugin graph": [ctl.plugin_controller, "graph_plugin", "plot"],
                                          })
        ctl.plugin_controller.grid = ctl.grid

        self.header("instantiating AreaScanFeature")
        ctl.area_scan = AreaScanFeature(
            bt_save                     = sfu.pushButton_area_scan_save,
            cb_enable                   = sfu.checkBox_area_scan_enable,
            cb_fast                     = sfu.checkBox_area_scan_fast,
            frame_image                 = sfu.frame_area_scan_image,
            frame_live                  = sfu.frame_area_scan_live,
            graphics_view               = sfu.graphicsView_area_scan,
            gui                         = ctl.gui,
            layout_live                 = sfu.layout_area_scan_live,
            lb_current                  = sfu.label_area_scan_current_line,
            lb_frame_count              = sfu.label_area_scan_frame_count,
            marquee                     = ctl.marquee,
            multispec                   = ctl.multispec,
            progress_bar                = sfu.progressBar_area_scan,
            save_options                = ctl.save_options,
            sb_start                    = sfu.spinBox_area_scan_start_line,
            sb_stop                     = sfu.spinBox_area_scan_stop_line,
            sb_delay_ms                 = sfu.spinBox_area_scan_delay_ms,
            set_curve_data              = ctl.set_curve_data)

        self.header("instantiating RamanShiftCorrectionFeature")
        ctl.raman_shift_correction = RamanShiftCorrectionFeature(
            button                      = sfu.pushButton_ramanCorrection,
            cb_visible                  = sfu.checkBox_ramanCorrection_visible,
            combo                       = sfu.comboBox_ramanCorrection_compoundName,
            config                      = ctl.config,
            frame                       = sfu.frame_ramanCorrection_white,
            graph                       = ctl.graph,
            gui                         = ctl.gui,
            marquee                     = ctl.marquee,
            multispec                   = ctl.multispec,
            page_nav                    = ctl.page_nav)

        self.header("instantiating AccessoryControlFeature")
        ctl.accessory_control = AccessoryControlFeature(
            cb_display                  = sfu.checkBox_accessory_cont_strobe_display,
            cb_enable                   = sfu.checkBox_accessory_cont_strobe_enable,
            cb_fan                      = sfu.checkBox_accessory_fan,
            cb_lamp                     = sfu.checkBox_accessory_lamp,
            cb_shutter                  = sfu.checkBox_accessory_shutter,
            frame_cont_strobe           = sfu.frame_accessory_cont_strobe,
            frame_widget                = sfu.frame_accessory_widget,
            multispec                   = ctl.multispec,
            sb_freq_hz                  = sfu.spinBox_accessory_cont_strobe_freq_hz,
            sb_width_us                 = sfu.spinBox_accessory_cont_strobe_width_us)

        self.header("instantiating HighGainModeFeature")
        ctl.high_gain_mode = HighGainModeFeature(
            cb_enabled                  = sfu.checkBox_high_gain_mode_enabled,
            config                      = ctl.config,
            multispec                   = ctl.multispec)

        self.header("instantiating RegionControlFeature")
        ctl.region_control = RegionControlFeature(
            cb_enabled                  = sfu.checkBox_region_enabled,
            multispec                   = ctl.multispec,
            spinbox                     = sfu.spinBox_region)

        self.header("instantiating HelpFeature")
        ctl.help = HelpFeature(ctl)

        self.header("done with Business Object creation")

    def destroy(self):
        log.info("destroying business objects")
        ctl = self.controller

        # anything with external processes
        for feature in [ ctl.kia_feature,
                         ctl.plugin_controller ]:
            feature.disconnect()                        

        # anything with timers, observers etc
        for feature in [ ctl.marquee, 
                         ctl.guide ]:
            feature.stop()

        log.info("done destroying business objects")
