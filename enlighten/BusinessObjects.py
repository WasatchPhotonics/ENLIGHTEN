import logging
from PySide2.QtGui import QColor
from PySide2.QtCore import *

log = logging.getLogger(__name__)

from enlighten.file_io.HardwareCaptureControlFeature import HardwareCaptureControlFeature
from enlighten.scope.RamanShiftCorrectionFeature import RamanShiftCorrectionFeature     # single-point correction
from enlighten.scope.DetectorTemperatureFeature import DetectorTemperatureFeature
from enlighten.file_io.HardwareFileOutputManager import HardwareFileOutputManager
from enlighten.spectra_processes.RamanIntensityCorrection import RamanIntensityCorrection   # SRM
from enlighten.scope.AccessoryControlFeature import AccessoryControlFeature
from enlighten.scope.LaserTemperatureFeature import LaserTemperatureFeature
from enlighten.scope.IntegrationTimeFeature import IntegrationTimeFeature
from enlighten.scope.ExternalTriggerFeature import ExternalTriggerFeature
from enlighten.ui.ResourceMonitorFeature import ResourceMonitorFeature
from enlighten.spectra_processes.InterpolationFeature import InterpolationFeature
from enlighten.spectra_processes.ScanAveragingFeature import ScanAveragingFeature
from enlighten.scope.RegionControlFeature import RegionControlFeature
from enlighten.device.ManufacturingFeature import ManufacturingFeature
from enlighten.scope.LaserControlFeature import LaserControlFeature
from enlighten.scope.HighGainModeFeature import HighGainModeFeature
from enlighten.spectra_processes.TransmissionFeature import TransmissionFeature
from enlighten.measurement.MeasurementFactory import MeasurementFactory
from enlighten.spectra_processes.BaselineCorrection import BaselineCorrection
from enlighten.spectra_processes.HorizROIFeature import HorizROIFeature
from enlighten.spectra_processes.AbsorbanceFeature import AbsorbanceFeature
from enlighten.ui.StatusBarFeature import StatusBarFeature
from enlighten.scope.RamanModeFeature import RamanModeFeature
from enlighten.ui.StatusIndicators import StatusIndicators
from enlighten.scope.ReferenceFeature import ReferenceFeature
from enlighten.measurement.AreaScanFeature import AreaScanFeature
from enlighten.timing.BatchCollection import BatchCollection
from enlighten.device.Authentication import Authentication
from enlighten.ui.ImageResources import ImageResources
from enlighten.ui.PageNavigation import PageNavigation
from enlighten.spectra_processes.TakeOneFeature import TakeOneFeature
from enlighten.spectra_processes.RichardsonLucy import RichardsonLucy
from enlighten.device.BatteryFeature import BatteryFeature
from enlighten.file_io.LoggingFeature import LoggingFeature
from enlighten.ui.FocusListener import FocusListener
from enlighten.scope.GainDBFeature import GainDBFeature
from enlighten.spectra_processes.BoxcarFeature import BoxcarFeature
from enlighten.file_io.Configuration import Configuration
from enlighten.measurement.Measurements import Measurements
from enlighten.device.EEPROMEditor import EEPROMEditor
from enlighten.scope.GuideFeature import GuideFeature
from enlighten.network.CloudManager import CloudManager
from enlighten.device.EEPROMWriter import EEPROMWriter
from enlighten.ui.Stylesheets import Stylesheets
from enlighten.scope.DarkFeature import DarkFeature
from enlighten.measurement.SaveOptions import SaveOptions
from enlighten.scope.GridFeature import GridFeature
from enlighten.file_io.FileManager import FileManager
from enlighten.ui.VCRControls import VCRControls
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
        ctl.config = Configuration(
            button_save                 = sfu.pushButton_save_ini,
            lb_save_result              = sfu.label_save_ini_result)

        self.header("instantiating LoggingFeature")
        ctl.logging_feature = LoggingFeature(
            bt_copy     = sfu.pushButton_copy_log_to_clipboard,
            cb_paused   = sfu.checkBox_logging_pause,
            cb_verbose  = sfu.checkBox_verbose_logging,
            config      = ctl.config,
            level       = ctl.log_level,
            queue       = ctl.log_queue,
            te_log      = sfu.textEdit_log)

        self.header("instantiating Colors")
        ctl.colors = Colors(ctl.config)

        self.header("instantiating Stylesheets")
        ctl.stylesheets = Stylesheets(ctl.stylesheet_path)

        self.header("instantiating GUI")
        ctl.gui = GUI(
            colors                      = ctl.colors,
            config                      = ctl.config,
            form                        = ctl.form,
            stylesheet_path             = ctl.stylesheet_path,
            stylesheets                 = ctl.stylesheets,

            bt_dark_mode                = sfu.pushButton_dark_mode)

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
        ctl.resource_monitor = ResourceMonitorFeature(
            lb_growth                   = sfu.label_process_growth_mb,
            lb_size                     = sfu.label_process_size_mb,
            max_growth_perc             = ctl.max_memory_growth,
            run_sec                     = ctl.run_sec
        )

        self.header("instantiating FocusListener")
        ctl.focus_listener = FocusListener(app = ctl.app)

        self.header("instantiating ModelInfo")
        ctl.model_info = ModelInfo()

        self.header("instantiating Marquee")
        ctl.marquee = Marquee(
            app                         = ctl.app,
            bt_close                    = sfu.pushButton_marquee_close,
            form                        = ctl.form,
            frame                       = sfu.frame_drawer_white,
            inner                       = sfu.frame_drawer_black,
            label                       = sfu.label_drawer,
            stylesheets                 = ctl.stylesheets)
        ctl.gui.marquee = ctl.marquee

        self.header("instantiating FileManager")
        ctl.file_manager = FileManager(
            form                        = ctl.form,
            marquee                     = ctl.marquee)

        self.header("instantiating Clipboard")
        ctl.clipboard = Clipboard(
            clipboard                   = ctl.app.clipboard(),
            marquee                     = ctl.marquee)
        ctl.logging_feature.clipboard = ctl.clipboard

        self.header("instantiating GuideFeature")
        ctl.guide = GuideFeature(
            bt_enable                   = sfu.pushButton_guide,
            gui                         = ctl.gui,
            marquee                     = ctl.marquee)

        self.header("instantiating Graph")
        ctl.graph = Graph(ctl)

        self.header("instantiating HardwareFileOutputManager")
        ctl.hardware_file_manager = HardwareFileOutputManager(
            cb_output=sfu.checkBox_feature_file_capture,
            spin_timeout=sfu.spinBox_hardware_capture_timeout)

        self.header("instantiating Cursor")
        ctl.cursor = Cursor(ctl)

        self.header("instantiating ImageResources")
        ctl.image_resources = ImageResources()

        self.header("instantiating Multispec")
        ctl.multispec = Multispec(
            button_lock                 = sfu.pushButton_multiSpec_lock,
            check_autocolor             = sfu.checkBox_multiSpec_autocolor,
            check_hide_others           = sfu.checkBox_multiSpec_hide_others,
            colors                      = ctl.colors,
            combo_spectrometer          = sfu.comboBox_multiSpec,
            desired_serial              = ctl.serial_number_desired,
            frame_widget                = sfu.frame_multiSpecWidget,
            graph                       = ctl.graph,
            gui                         = ctl.gui,
            layout_colors               = sfu.horizontalLayout_multiSpec_colors,
            reinit_callback             = ctl.initialize_new_device,
            stylesheets                 = ctl.stylesheets,
            eject_button                = sfu.pushButton_eject,
            ctl                         = ctl,

			# Essentially, these are widgets corresponding to SpectrometerState fields,
            # SpectrometerApplicationState fields, or change_device_setting() keys
			# which can therefore be "locked" in Multispec.  There is currently NO
			# CONNECTION in code between the widgets which "visually suggest they can be locked"
            # (via this list), and those which actually can be.
            #
            # @todo pass in Features, not Widgets
            lockable_widgets            = [
                                             sfu.lightSourceWidget_shaded,
                                             sfu.detectorControlWidget_shaded,
                                             sfu.displayAxisWidget_shaded,
                                             sfu.scanAveragingWidget_shaded,
                                             sfu.boxcarWidget_shaded,
                                             sfu.temperatureWidget_shaded
                                          ]
        )
        for feature in [ ctl.cursor, ctl.config, ctl.gui ]:
            feature.multispec = ctl.multispec

        self.header("instantiating BatteryFeature")
        ctl.battery_feature = BatteryFeature(ctl)

        self.header("instantiating StatusIndicators")
        ctl.status_indicators = StatusIndicators(ctl)

        self.header("instantiating DetectorTemperatureFeature")
        ctl.detector_temperature = DetectorTemperatureFeature(
            graph                       = ctl.graph,
            multispec                   = ctl.multispec,
            status_indicators           = ctl.status_indicators,
            button_up                   = sfu.temperatureWidget_pushButton_detector_setpoint_up,
            button_dn                   = sfu.temperatureWidget_pushButton_detector_setpoint_dn,
            cb_enabled                  = sfu.checkBox_tec_enabled,
            lb_degC                     = sfu.label_hardware_capture_details_detector_temperature,
            lb_raw                      = sfu.label_ccd_temperature_raw,
            slider                      = sfu.verticalSlider_detector_setpoint_degC,
            spinbox                     = sfu.spinBox_detector_setpoint_degC,
            clear_btn                   = sfu.detector_temp_pushButton,
            sfu                         = sfu,
            gui                         = ctl.gui,
            clipboard                   = ctl.clipboard,
            hardware_file_manager       = ctl.hardware_file_manager)

        self.header("instantiating HorizROIFeature")
        ctl.horiz_roi = HorizROIFeature(ctl)

        self.header("instantiating TransmissionFeature")
        ctl.transmission = TransmissionFeature(
            marquee                     = ctl.marquee,
            horiz_roi                   = ctl.horiz_roi,
                                       
            cb_max_enable               = sfu.checkBox_enable_max_transmission,
            sb_max_perc                 = sfu.spinBox_max_transmission_perc)

        self.header("instantiating AbsorbanceFeature")
        ctl.absorbance = AbsorbanceFeature(
            marquee                     = ctl.marquee,
            transmission                = ctl.transmission)

        self.header("instantiating StatusBarFeature")
        ctl.status_bar = StatusBarFeature(
            pair_min                    = [ sfu.label_StatusBar_min_name,     sfu.label_StatusBar_min_value ],
            pair_max                    = [ sfu.label_StatusBar_max_name,     sfu.label_StatusBar_max_value ],
            pair_mean                   = [ sfu.label_StatusBar_mean_name,    sfu.label_StatusBar_mean_value ],
            pair_area                   = [ sfu.label_StatusBar_area_name,    sfu.label_StatusBar_area_value ],
            pair_temp                   = [ sfu.label_StatusBar_temp_name,    sfu.label_StatusBar_temp_value ],
            pair_cursor                 = [ sfu.label_StatusBar_cursor_name,  sfu.label_StatusBar_cursor_value ],
            pair_count                  = [ sfu.label_StatusBar_count_name,   sfu.label_StatusBar_count_value ],
                                       
            config                      = ctl.config,
            multispec                   = ctl.multispec,
            tool_button                 = sfu.status_bar_toolButton,
            generate_x_axis             = ctl.generate_x_axis,
            parent                      = ctl.form,
                                       
            cursor                      = ctl.cursor,
            detector_temperature        = ctl.detector_temperature)

        self.header("instantiating InterpolationFeature")
        ctl.interp = InterpolationFeature(
            config                      = ctl.config,
            cb_enabled                  = sfu.checkBox_save_interpolation_enabled,
            dsb_end                     = sfu.doubleSpinBox_save_interpolation_end,
            dsb_incr                    = sfu.doubleSpinBox_save_interpolation_incr,
            dsb_start                   = sfu.doubleSpinBox_save_interpolation_start,
            multispec                   = ctl.multispec,
            rb_wavelength               = sfu.radioButton_save_interpolation_wavelength,
            rb_wavenumber               = sfu.radioButton_save_interpolation_wavenumber,
            horiz_roi                   = ctl.horiz_roi)

        self.header("instantiating ExternalTriggerFeature")
        ctl.external_trigger = ExternalTriggerFeature(
            cb_enabled                  = sfu.checkBox_external_trigger_enabled,
            marquee                     = ctl.marquee,
            multispec                   = ctl.multispec)

        self.header("instantiating SaveOptions")
        ctl.save_options = SaveOptions(
            bt_location                 = sfu.pushButton_scope_setup_change_save_location,
            cb_all                      = sfu.checkBox_save_all,
            cb_allow_rename             = sfu.checkBox_allow_rename_files,
            cb_append                   = sfu.checkBox_save_data_append,
            cb_collated                 = sfu.checkBox_save_collated,
            cb_csv                      = sfu.checkBox_save_csv,
            cb_spc                      = sfu.checkBox_save_spc,
            cb_dark                     = sfu.checkBox_save_dark,
            cb_excel                    = sfu.checkBox_save_excel,
            cb_filename_as_label        = sfu.checkBox_save_filename_as_label,
            cb_json                     = sfu.checkBox_save_json,
            cb_load_raw                 = sfu.checkBox_load_raw,
            cb_pixel                    = sfu.checkBox_save_pixel,
            cb_raw                      = sfu.checkBox_save_raw,
            cb_reference                = sfu.checkBox_save_reference,
            cb_text                     = sfu.checkBox_save_text,
            cb_wavelength               = sfu.checkBox_save_wavelength,
            cb_wavenumber               = sfu.checkBox_save_wavenumber,
            config                      = ctl.config,
            file_manager                = ctl.file_manager,
            interp                      = ctl.interp,
            lb_location                 = sfu.label_scope_setup_save_location,
            le_label_template           = sfu.lineEdit_save_label_template,
            le_filename_template        = sfu.lineEdit_save_filename_template,
            le_note                     = sfu.lineEdit_scope_capture_save_note,
            le_prefix                   = sfu.lineEdit_scope_capture_save_prefix,
            le_suffix                   = sfu.lineEdit_scope_capture_save_suffix,
            multispec                   = ctl.multispec,
            rb_by_col                   = sfu.radioButton_save_by_column,
            rb_by_row                   = sfu.radioButton_save_by_row)

        self.header("instantiating PageNavigation")
        ctl.page_nav = PageNavigation(
            graph                       = ctl.graph,
            logging_feature             = ctl.logging_feature,
            marquee                     = ctl.marquee,
            multispec                   = ctl.multispec,
            save_options                = ctl.save_options,
            stylesheets                 = ctl.stylesheets,

            button_raman                = sfu.pushButton_raman,
            button_non_raman            = sfu.pushButton_non_raman,
            button_expert               = sfu.pushButton_expert,
            combo_view                  = sfu.comboBox_view,
            stack_main                  = sfu.stackedWidget_low,

            fr_transmission_options     = sfu.frame_transmission_options,        # todo move to TransmissionFeature
            fr_area_scan                = sfu.frame_area_scan_widget,
            fr_baseline                 = sfu.frame_baseline_correction,
            fr_post                     = sfu.frame_post_processing,
            fr_tec                      = sfu.frame_tec_control,
            fr_region                   = sfu.frame_region_control,

            update_feature_visibility   = ctl.update_feature_visibility,
            sfu                         = sfu)

        self.header("instantiating MeasurementFactory")
        ctl.measurement_factory = MeasurementFactory(
            colors                      = ctl.colors,
            file_manager                = ctl.file_manager,
            focus_listener              = ctl.focus_listener,
            graph                       = ctl.graph,
            plugin_graph                = ctl.get_plugin_graph,
            gui                         = ctl.gui,
            render_curve                = ctl.thumbnail_render_curve,
            render_graph                = ctl.thumbnail_render_graph,
            save_options                = ctl.save_options,
            stylesheets                 = ctl.stylesheets)

        self.header("instantiating Measurements")
        ctl.measurements = Measurements(
            button_erase                = sfu.pushButton_erase_captures,
            button_export               = sfu.pushButton_export_session,
            button_load                 = sfu.pushButton_scope_capture_load,
            button_resize               = sfu.pushButton_resize_captures,
            button_resort               = sfu.pushButton_resort_captures,
            factory                     = ctl.measurement_factory,
            file_manager                = ctl.file_manager,
            form                        = ctl.form,
            gui                         = ctl.gui,
            label_count                 = sfu.label_session_count,
            layout                      = sfu.verticalLayout_scope_capture_save,
            marquee                     = ctl.marquee,
            reprocess_callback          = ctl.reprocess,
            horiz_roi                   = ctl.horiz_roi)
        ctl.graph.measurements = ctl.measurements

        self.header("instantiating Authentication")
        ctl.authentication = Authentication(
            gui                         = ctl.gui,
            marquee                     = ctl.marquee,
            parent                      = ctl.form,

            button_login                = sfu.pushButton_admin_login,
            combo_view                  = sfu.comboBox_view,

            oem_widgets                 = [ sfu.pushButton_write_eeprom, sfu.pushButton_importEEPROM, sfu.pushButton_exportEEPROM, sfu.pushButton_restore_eeprom, sfu.pushButton_reset_fpga ],
            advanced_widgets            = [ sfu.tabWidget_advanced_features ])

        self.header("instantiating EEPROMWriter")
        ctl.eeprom_writer = EEPROMWriter(
            authentication              = ctl.authentication,
            button_save                 = sfu.pushButton_write_eeprom,
            marquee                     = ctl.marquee,
            multispec                   = ctl.multispec,
            reset_hardware_errors       = ctl.clear_response_errors)

        self.header("instantiating EEPROMEditor")
        ctl.eeprom_editor = EEPROMEditor(
            authentication              = ctl.authentication,
            bt_copy                     = sfu.pushButton_eeprom_clipboard,
            clipboard                   = ctl.clipboard,
            eeprom_writer               = ctl.eeprom_writer,
            image_resources             = ctl.image_resources,
            lb_digest                   = sfu.label_eeprom_digest,
            lb_product_image            = sfu.label_product_image,
            lb_serial                   = sfu.label_serial,
            multispec                   = ctl.multispec,
            sfu                         = sfu,
            stylesheets                 = ctl.stylesheets,
            update_gain_and_offset_callback = ctl.update_gain_and_offset,
            update_wavecal_callback     = ctl.update_wavecal,
            horiz_roi                   = ctl.horiz_roi,
            current_spectrometer        = ctl.current_spectrometer)

        self.header("instantiating RamanIntensityCorrection")
        ctl.raman_intensity_correction = RamanIntensityCorrection(
            cb_enable                   = sfu.checkBox_raman_intensity_correction,
            guide                       = ctl.guide,
            multispec                   = ctl.multispec,
            page_nav                    = ctl.page_nav,
            horiz_roi                   = ctl.horiz_roi)

        self.header("instantiating LaserControlFeature")
        ctl.laser_control = LaserControlFeature(ctl)

        self.header("instantiating LaserTemperatureFeature")
        ctl.laser_temperature = LaserTemperatureFeature(
            sfu                         = sfu,
            graph                       = ctl.graph,
            multispec                   = ctl.multispec,
            lb_degC                     = sfu.label_hardware_capture_details_laser_temperature,
            clear_btn                   = sfu.laser_temp_pushButton,
            make_pen                    = ctl.gui.make_pen,
            clipboard                   = ctl.clipboard,
            hardware_file_manager       = ctl.hardware_file_manager)

        self.header("instantiating Sounds")
        ctl.sounds = Sounds(
            checkbox                    = sfu.checkBox_sound_enable,
            config                      = ctl.config,
            path                        = "enlighten/assets/example_data/sounds")

        self.header("instantiating ScanAveragingFeature")
        ctl.scan_averaging = ScanAveragingFeature(
            bt_dn                       = sfu.pushButton_scan_averaging_dn,
            bt_up                       = sfu.pushButton_scan_averaging_up,
            multispec                   = ctl.multispec,
            spinbox                     = sfu.spinBox_scan_averaging,
            label                       = sfu.label_scan_averaging)

        self.header("instantiating TakeOneFeature")
        ctl.take_one = TakeOneFeature(
            multispec                   = ctl.multispec,
            scan_averaging              = ctl.scan_averaging)

        self.header("instantiating CloudManager")
        ctl.cloud_manager = CloudManager(
            cb_enabled                  = sfu.checkBox_cloud_config_download_enabled,
            restore_button              = sfu.pushButton_restore_eeprom,

            config                      = ctl.config,
            eeprom_editor               = ctl.eeprom_editor)

        self.header("instantiating VCRControls")
        ctl.vcr_controls = VCRControls(
            bt_pause                    = sfu.pushButton_scope_capture_pause,
            bt_play                     = sfu.pushButton_scope_capture_play,
            bt_save                     = sfu.pushButton_scope_capture_save,
            bt_start_collection         = sfu.pushButton_scope_capture_start_collection,
            bt_step                     = sfu.pushButton_scope_capture_step,
            bt_step_save                = sfu.pushButton_scope_capture_step_save,
            bt_stop                     = sfu.pushButton_scope_capture_stop,
            gui                         = ctl.gui,
            multispec                   = ctl.multispec,
            scan_averaging              = ctl.scan_averaging,
            take_one                    = ctl.take_one)
        ctl.vcr_controls.register_observer("save", ctl.save_current_spectra)
        ctl.scan_averaging.set_vcr_controls(ctl.vcr_controls)

        self.header("instantiating BaselineCorrection")
        ctl.baseline_correction = BaselineCorrection(
            cb_enabled                  = sfu.checkBox_baselineCorrection_enable,
            cb_show_curve               = sfu.checkBox_baselineCorrection_show,
            combo_algo                  = sfu.comboBox_baselineCorrection_algo,
            config                      = ctl.config,
            guide                       = ctl.guide,
            multispec                   = ctl.multispec,
            page_nav                    = ctl.page_nav,
            horiz_roi                   = ctl.horiz_roi,
            graph                       = ctl.graph)

        self.header("instantiating DarkFeature")
        ctl.dark_feature = DarkFeature(
            generate_x_axis             = ctl.generate_x_axis,
            gui                         = ctl.gui,
            marquee                     = ctl.marquee,
            measurement_factory         = ctl.measurement_factory,
            multispec                   = ctl.multispec,
            save_options                = ctl.save_options,
            set_curve_data              = ctl.set_curve_data,
            raman_intensity_correction  = ctl.raman_intensity_correction,
            button_clear                = sfu.pushButton_dark_clear,
            button_load                 = sfu.pushButton_dark_load,
            button_store                = sfu.pushButton_dark_store,
            button_toggle               = sfu.pushButton_scope_toggle_dark,
            lb_timestamp                = sfu.label_dark_timestamp,
            stacked_widget              = sfu.stackedWidget_scope_setup_dark_spectrum,
            gui_make_pen                = ctl.gui.make_pen)

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
        ctl.batch_collection = BatchCollection(
            config                        = ctl.config,
            dark_feature                  = ctl.dark_feature,
            factory                       = ctl.measurement_factory,
            laser_enable_callback         = ctl.laser_control.set_laser_enable,
            marquee                       = ctl.marquee,
            measurements                  = ctl.measurements,
            multispec                     = ctl.multispec,
            save_options                  = ctl.save_options,
            vcr_controls                  = ctl.vcr_controls,

            cb_enabled                    = sfu.checkBox_BatchCollection_enabled,
            cb_dark_before_batch          = sfu.checkBox_BatchCollection_dark_before_batch,
            cb_clear_before_batch         = sfu.checkBox_BatchCollection_clear_before_batch,
            cb_export_after_batch         = sfu.checkBox_BatchCollection_export_after_batch,
            lb_explain                    = sfu.label_BatchCollection_explain,
            rb_laser_manual               = sfu.radioButton_BatchCollection_laser_manual,
            rb_laser_spectrum             = sfu.radioButton_BatchCollection_laser_spectrum,
            rb_laser_batch                = sfu.radioButton_BatchCollection_laser_batch,
            spinbox_measurement_count     = sfu.spinBox_BatchCollection_measurement_count,
            spinbox_measurement_period_ms = sfu.spinBox_BatchCollection_measurement_period_ms,
            spinbox_batch_count           = sfu.spinBox_BatchCollection_batch_count,
            spinbox_batch_period_sec      = sfu.spinBox_BatchCollection_batch_period_sec,
            spinbox_laser_warmup_ms       = sfu.spinBox_BatchCollection_laser_warmup_ms,
            spinbox_collection_timeout    = sfu.spinBox_BatchCollection_collection_timeout,
            )

        self.header("instantiating BoxcarFeature")
        ctl.boxcar = BoxcarFeature(
            bt_dn                       = sfu.pushButton_boxcar_half_width_dn,
            bt_up                       = sfu.pushButton_boxcar_half_width_up,
            spinbox                     = sfu.spinBox_boxcar_half_width,
            
            multispec                   = ctl.multispec,
            page_nav                    = ctl.page_nav,
            )

        self.header("instantiating IntegrationTimeFeature")
        ctl.integration_time_feature = IntegrationTimeFeature(
            bt_dn                       = sfu.pushButton_integration_time_ms_dn,
            bt_up                       = sfu.pushButton_integration_time_ms_up,
            marquee                     = ctl.marquee,
            multispec                   = ctl.multispec,
            slider                      = sfu.slider_integration_time_ms,
            spinbox                     = sfu.spinBox_integration_time_ms)

        self.header("instantiating GainDBFeature")
        ctl.gain_db_feature = GainDBFeature(ctl = ctl)

        self.header("instantiating BLEManager")
        ctl.ble_manager = BLEManager(
            marquee                     = ctl.marquee,
            ble_button                  = sfu.pushButton_bleScan,
            controller_connect          = ctl.connect_new,
            controller_disconnect       = ctl.disconnect_device,
            progress_bar                = sfu.readingProgressBar,
            multispec                   = ctl.multispec)

        self.header("instantiating RamanModeFeature")
        ctl.raman_mode_feature = RamanModeFeature(
            bt_laser                    = sfu.pushButton_laser_toggle,
            cb_enable                   = sfu.checkBox_raman_mode_enable,
            multispec                   = ctl.multispec,
            page_nav                    = ctl.page_nav,
            vcr_controls                = ctl.vcr_controls)

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
        ctl.measurement_factory.kia = ctl.kia_feature

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
