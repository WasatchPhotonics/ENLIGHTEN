from asyncio.windows_events import CONNECT_PIPE_INIT_DELAY
import logging

log = logging.getLogger(__name__)

from .HardwareCaptureControlFeature   import HardwareCaptureControlFeature
from .RamanShiftCorrectionFeature     import RamanShiftCorrectionFeature     # single-point correction
from .DetectorTemperatureFeature      import DetectorTemperatureFeature
from .HardwareFileOutputManager       import HardwareFileOutputManager
from .RamanIntensityCorrection        import RamanIntensityCorrection   # SRM
from .AccessoryControlFeature         import AccessoryControlFeature
from .LaserTemperatureFeature         import LaserTemperatureFeature
from .IntegrationTimeFeature          import IntegrationTimeFeature
from .AdvancedOptionsFeature          import AdvancedOptionsFeature
from .ExternalTriggerFeature          import ExternalTriggerFeature
from .ResourceMonitorFeature          import ResourceMonitorFeature
from .InterpolationFeature            import InterpolationFeature
from .ScanAveragingFeature            import ScanAveragingFeature
from .RegionControlFeature            import RegionControlFeature
from .ManufacturingFeature            import ManufacturingFeature
from .LaserControlFeature             import LaserControlFeature
from .HighGainModeFeature             import HighGainModeFeature
from .TransmissionFeature             import TransmissionFeature
from .MeasurementFactory              import MeasurementFactory
from .BaselineCorrection              import BaselineCorrection
from .VignetteROIFeature              import VignetteROIFeature
from .AbsorbanceFeature               import AbsorbanceFeature
from .StatusBarFeature                import StatusBarFeature
from .RamanModeFeature                import RamanModeFeature
from .StatusIndicators                import StatusIndicators
from .DespikingFeature                import DespikingFeature
from .ReferenceFeature                import ReferenceFeature
from .AreaScanFeature                 import AreaScanFeature
from .BatchCollection                 import BatchCollection
from .Authentication                  import Authentication
from .ImageResources                  import ImageResources
from .PageNavigation                  import PageNavigation
from .TakeOneFeature                  import TakeOneFeature
from .RichardsonLucy                  import RichardsonLucy
from .BatteryFeature                  import BatteryFeature
from .LoggingFeature                  import LoggingFeature
from .FocusListener                   import FocusListener
from .GainDBFeature                   import GainDBFeature
from .BoxcarFeature                   import BoxcarFeature
from .Configuration                   import Configuration
from .Measurements                    import Measurements
from .EEPROMEditor                    import EEPROMEditor
from .GuideFeature                    import GuideFeature
from .CloudManager                    import CloudManager
from .EEPROMWriter                    import EEPROMWriter
from .Stylesheets                     import Stylesheets
from .MockManager                     import MockManager
from .DarkFeature                     import DarkFeature
from .SaveOptions                     import SaveOptions
from .FileManager                     import FileManager
from .VCRControls                     import VCRControls
from .BLEManager                      import BLEManager
from .Clipboard                       import Clipboard
from .ModelInfo                       import ModelInfo
from .Multispec                       import Multispec
from .Marquee                         import Marquee
from .Colors                          import Colors
from .Sounds                          import Sounds
from .Cursor                          import Cursor
from .Graph                           import Graph
from .GUI                             import GUI

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

        self.obj = {}

    def header(self, s):
        log.debug("")
        log.debug("=" * len(s))
        log.debug(s)
        log.debug("=" * len(s))
        log.debug("")

    def create_first(self):
        """
        These are things needed early in the Controller's constructor 
        initialization, i.e. before the placeholders are populated.
        """
        ctl = self.controller
        sfu = ctl.form.ui

        ctl.multispec = None 

        self.header("instantiating Configuration")
        ctl.config = Configuration(
            button_save                 = sfu.pushButton_save_ini,
            lb_save_result              = sfu.label_save_ini_result)

        self.header("instantiating LoggingFeature")
        ctl.logging_feature = LoggingFeature(
            cb_verbose  = sfu.checkBox_verbose_logging,
            config      = ctl.config,
            level       = ctl.log_level,
            queue       = ctl.log_queue)

        self.header("instantiating Colors")
        ctl.colors = Colors(ctl.config)

        self.header("instantiating Stylesheets")
        ctl.stylesheets = Stylesheets(ctl.stylesheet_path)

        self.header("instantiating GUI")
        ctl.gui = GUI(
            colors                      = ctl.colors,
            config                      = ctl.config,
            form                        = ctl.form,
            stylesheets                 = ctl.stylesheets)

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
            bt_close                    = sfu.pushButton_marquee_close,
            form                        = ctl.form,
            frame                       = sfu.frame_drawer_white,
            inner                       = sfu.frame_drawer_black,
            label                       = sfu.label_drawer,
            stylesheets                 = ctl.stylesheets)

        self.header("instantiating FileManager")
        ctl.file_manager = FileManager(
            form                        = ctl.form,
            marquee                     = ctl.marquee)

        self.header("instantiating Clipboard")
        ctl.clipboard = Clipboard(
            clipboard                   = ctl.app.clipboard(),
            marquee                     = ctl.marquee)

        self.header("instantiating GuideFeature")
        ctl.guide = GuideFeature(
            bt_enable                   = sfu.pushButton_guide,
            gui                         = ctl.gui,
            marquee                     = ctl.marquee)

        self.header("instantiating BatteryFeature")
        ctl.battery_feature = BatteryFeature(
            lb_raw                      = sfu.label_battery_raw,
            lb_parsed                   = sfu.label_battery_parsed)

        self.header("instantiating Graph")
        ctl.graph = Graph(
            clipboard                   = ctl.clipboard,
            generate_x_axis             = ctl.generate_x_axis,
            gui                         = ctl.gui,
            hide_when_zoomed            = [ sfu.frame_new_save_col_holder, sfu.controlWidget ],
            rehide_curves               = ctl.rehide_curves,

            button_copy                 = sfu.pushButton_copy_to_clipboard,
            button_invert               = sfu.pushButton_invert_x_axis,
            button_lock_axes            = sfu.pushButton_lock_axes,
            button_zoom                 = sfu.pushButton_zoom_graph,
            cb_marker                   = sfu.checkBox_graph_marker,
            combo_axis                  = sfu.displayAxis_comboBox_axis,

            layout_scope_capture        = sfu.layout_scope_capture_graphs,
            stacked_widget_scope_setup  = sfu.stackedWidget_scope_setup_live_spectrum)

        self.header("instantiating Cursor")
        ctl.cursor = Cursor(
            button_dn                   = sfu.pushButton_cursor_dn,
            button_up                   = sfu.pushButton_cursor_up,
            cb_enable                   = sfu.checkBox_cursor_scope_enabled,
            ds_value                    = sfu.doubleSpinBox_cursor_scope,
            generate_x_axis             = ctl.generate_x_axis,
            graph                       = ctl.graph)

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
            model_info                  = ctl.model_info,
            reinit_callback             = ctl.initialize_new_device,
            stylesheets                 = ctl.stylesheets,
            eject_button                = sfu.pushButton_eject,
            controller_disconnect       = ctl.disconnect_device,

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

        self.header("instantiating StatusIndicators")
        ctl.status_indicators = StatusIndicators(
            multispec                   = ctl.multispec,
            stylesheets                 = ctl.stylesheets,

            button_hardware             = sfu.systemStatusWidget_pushButton_hardware,
            button_lamp                 = sfu.systemStatusWidget_pushButton_light,
            button_temperature          = sfu.systemStatusWidget_pushButton_temperature)

        self.header("instantiating HardwareFileOutputManager")
        ctl.hardware_file_manager = HardwareFileOutputManager(
            cb_output=sfu.checkBox_feature_file_capture,
            spin_timeout=sfu.spinBox_hardware_capture_timeout)

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

        self.header("instantiating VignetteROIFeature")
        ctl.vignette_roi = VignetteROIFeature(
            multispec                   = ctl.multispec)
        ctl.graph.vignette_roi = ctl.vignette_roi

        self.header("instantiating TransmissionFeature")
        ctl.transmission = TransmissionFeature(
            marquee                     = ctl.marquee,
            vignette_roi                = ctl.vignette_roi,
                                       
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
            vignette_roi                = ctl.vignette_roi)

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
            cb_csv                      = sfu.checkBox_save_csv,
            cb_spc                      = sfu.checkBox_save_spc,
            cb_dark                     = sfu.checkBox_save_dark,
            cb_excel                    = sfu.checkBox_save_excel,
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
            le_note                     = sfu.lineEdit_scope_capture_save_note,
            le_prefix                   = sfu.lineEdit_scope_capture_save_prefix,
            le_suffix                   = sfu.lineEdit_scope_capture_save_suffix,
            multispec                   = ctl.multispec,
            rb_by_col                   = sfu.radioButton_save_by_column,
            rb_by_row                   = sfu.radioButton_save_by_row)

        self.header("instantiating PageNavigation")
        ctl.page_nav = PageNavigation(
            graph                                  = ctl.graph,
            marquee                                = ctl.marquee,
            multispec                              = ctl.multispec,
            save_options                           = ctl.save_options,
            stylesheets                            = ctl.stylesheets,

            button_raman                           = sfu.pushButton_raman,
            button_non_raman                       = sfu.pushButton_non_raman,
            button_expert                          = sfu.pushButton_expert,
            combo_view                             = sfu.comboBox_view,
            stack_hardware                         = sfu.stackedWidget_hardware_setup_details,
            stack_main                             = sfu.stackedWidget_low,

            textEdit_log                           = sfu.textEdit_log,                      # todo move to LoggingFeature
            frame_transmission_options             = sfu.frame_transmission_options,        # todo move to TransmissionFeature

            update_feature_visibility              = ctl.update_feature_visibility,
            scroll_area                            = sfu.scrollArea_hsd,
            sfu                                    = sfu)

        self.header("instantiating MeasurementFactory")
        ctl.measurement_factory = MeasurementFactory(
            colors                      = ctl.colors,
            file_manager                = ctl.file_manager,
            focus_listener              = ctl.focus_listener,
            graph                       = ctl.graph,
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
            reprocess_callback          = ctl.reprocess)
        ctl.graph.measurements = ctl.measurements

        self.header("instantiating Authentication")
        ctl.authentication = Authentication(
            gui                         = ctl.gui,
            marquee                     = ctl.marquee,
            parent                      = ctl.form,

            button_login                = sfu.pushButton_admin_login,
            combo_view                 = sfu.comboBox_view,

            oem_widgets                 = [ sfu.pushButton_write_eeprom, sfu.pushButton_importEEPROM,
                                           sfu.pushButton_exportEEPROM, sfu.pushButton_restore_eeprom, sfu.pushButton_reset_fpga ],
            advanced_widgets            = [ sfu.doubleSpinBox_lightSourceWidget_excitation_nm,
                                            #sfu.label_virtual_spec, sfu.frame_virtual_spec,
                                            sfu.tabWidget_advanced_features ])

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
            vignette_roi                = ctl.vignette_roi,
            current_spectrometer        = ctl.current_spectrometer)

        self.header("instantiating RamanIntensityCorrection")
        ctl.raman_intensity_correction = RamanIntensityCorrection(
            cb_enable                   = sfu.checkBox_raman_intensity_correction,
            guide                       = ctl.guide,
            multispec                   = ctl.multispec,
            vignette_roi                = ctl.vignette_roi)

        self.header("instantiating LaserControlFeature")
        ctl.laser_control = LaserControlFeature(
            battery_feature             = ctl.battery_feature,
            eeprom_editor               = ctl.eeprom_editor,
            gui                         = ctl.gui,
            marquee                     = ctl.marquee,
            multispec                   = ctl.multispec,
            page_nav                    = ctl.page_nav,
            status_indicators           = ctl.status_indicators,
            raman_intensity_correction  = ctl.raman_intensity_correction,

            button_dn                   = sfu.pushButton_laser_power_dn,
            button_up                   = sfu.pushButton_laser_power_up,
            button_toggle               = sfu.pushButton_laser_toggle,
            combo_unit                  = sfu.comboBox_laser_power_unit,
            spinbox_excitation          = sfu.doubleSpinBox_lightSourceWidget_excitation_nm, # not EEPROMEditor
            spinbox_power               = sfu.doubleSpinBox_laser_power,
            slider_power                = sfu.verticalSlider_laser_power,
            guide                       = ctl.guide)

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
            cb_enabled     = sfu.checkBox_cloud_config_download_enabled,
            restore_button = sfu.pushButton_restore_eeprom,

            config         = ctl.config,
            eeprom_editor  = ctl.eeprom_editor)

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
            generate_x_axis             = ctl.generate_x_axis,
            guide                       = ctl.guide,
            multispec                   = ctl.multispec,
            page_nav                    = ctl.page_nav,
            vignette_roi                = ctl.vignette_roi,
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
            stackedWidget_scope_setup_dark_spectrum = sfu.stackedWidget_scope_setup_dark_spectrum,
            gui_make_pen                = ctl.gui.make_pen)

        self.header("instantiating ReferenceFeature")
        ctl.reference_feature = ReferenceFeature(
            generate_x_axis                                 = ctl.generate_x_axis,
            graph                                           = ctl.graph,
            gui                                             = ctl.gui,
            marquee                                         = ctl.marquee,
            measurement_factory                             = ctl.measurement_factory,
            multispec                                       = ctl.multispec,
            page_nav                                        = ctl.page_nav,
            save_options                                    = ctl.save_options,
            set_curve_data                                  = ctl.set_curve_data,
                                        
            button_clear                                    = sfu.pushButton_reference_clear,
            button_load                                     = sfu.pushButton_reference_load,
            button_store                                    = sfu.pushButton_reference_store,
            button_toggle                                   = sfu.pushButton_scope_toggle_reference,
            frame_setup                                     = sfu.frame_scopeSetup_spectra_reference_white,
            lb_timestamp                                    = sfu.label_reference_timestamp,
            stackedWidget_scope_setup_reference_spectrum    = sfu.stackedWidget_scope_setup_reference_spectrum,
            gui_make_pen                                    = ctl.gui.make_pen)

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
            multispec                   = ctl.multispec)

        self.header("instantiating IntegrationTimeFeature")
        ctl.integration_time_feature = IntegrationTimeFeature(
            bt_dn                       = sfu.pushButton_integration_time_ms_dn,
            bt_up                       = sfu.pushButton_integration_time_ms_up,
            multispec                   = ctl.multispec,
            slider                      = sfu.slider_integration_time_ms,
            spinbox                     = sfu.spinBox_integration_time_ms)

        self.header("instantiating GainDBFeature")
        ctl.gain_db_feature = GainDBFeature(
            bt_dn                       = sfu.pushButton_gain_dn,
            bt_up                       = sfu.pushButton_gain_up,
            label                       = sfu.label_gainWidget_title,
            multispec                   = ctl.multispec,
            slider                      = sfu.slider_gain,
            spinbox                     = sfu.doubleSpinBox_gain)

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

        ctl.despiking_feature = DespikingFeature(
            spin_tau                    = sfu.doubleSpinBox_tau_despike,
            spin_window                 = sfu.spinBox_window_despike)

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
            vignette_roi                = ctl.vignette_roi)
        ctl.measurement_factory.kia = ctl.kia_feature

        self.header("instantiating RichardsonLucy")
        ctl.richardson_lucy = RichardsonLucy(
            cb_enable                   = sfu.checkBox_richardson_lucy,
            config                      = ctl.config,
            generate_x_axis             = ctl.generate_x_axis,
            graph                       = ctl.graph,
            multispec                   = ctl.multispec,
            vignette_roi                = ctl.vignette_roi)

        self.header("instantiating ManufacturingFeature")
        ctl.mfg = ManufacturingFeature(
            bt_dfu                      = sfu.pushButton_mfg_dfu,
            multispec                   = ctl.multispec)

        self.header("instantiating HardwareCaptureControlFeature")
        ctl.hardware_control_feature = HardwareCaptureControlFeature(
            sfu                 = sfu,
            graph               = ctl.graph,
            laser_feature       = ctl.laser_temperature,
            detector_feature    = ctl.detector_temperature)

        self.header("instantiating PluginController")
        ctl.plugin_controller = PluginController(
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
            get_grid_display            = ctl.get_grid_display,

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

        self.header("instantiating AdvancedOptionsFeature")
        ctl.advanced_options = AdvancedOptionsFeature(
            cb_enable                   = sfu.checkBox_AdvancedOptions,
            cb_area_scan                = sfu.checkBox_AdvancedOptions_AreaScan,
            cb_baseline                 = sfu.checkBox_AdvancedOptions_BaselineCorrection,
            cb_post                     = sfu.checkBox_AdvancedOptions_PostProcessing,
            cb_region                   = sfu.checkBox_AdvancedOptions_Region,
            cb_tec                      = sfu.checkBox_AdvancedOptions_TECControl,
            cb_despike                  = sfu.checkBox_AdvancedOptions_Despike,
            config                      = ctl.config,
            fr_subopt                   = sfu.frame_AdvancedOptions_SubOptions,
            fr_area_scan                = sfu.frame_area_scan_widget,
            fr_baseline                 = sfu.frame_baseline_correction,
            fr_post                     = sfu.frame_post_processing,
            fr_tec                      = sfu.frame_tec_control,
            fr_region                   = sfu.frame_region_control,
            fr_despike                  = sfu.frame_despike_widget,
            multispec                   = ctl.multispec,
            stylesheets                 = ctl.stylesheets)
        ctl.baseline_correction.advanced_options = ctl.advanced_options

        self.header("instantiating HighGainModeFeature")
        ctl.high_gain_mode = HighGainModeFeature(
            cb_enabled                  = sfu.checkBox_high_gain_mode_enabled,
            multispec                   = ctl.multispec)

        self.header("instantiating RegionControlFeature")
        ctl.region_control = RegionControlFeature(
            cb_enabled                  = sfu.checkBox_region_enabled,
            multispec                   = ctl.multispec,
            spinbox                     = sfu.spinBox_region)

        ctl.mock_mgr = MockManager(
            cb_via_file = sfu.checkBox_virtual_from_file,
            combo_compound = sfu.comboBox_virtual_sample,
            combo_virtual = sfu.comboBox_default_virtual,
            connect_btn = sfu.pushButton_connect_virtual,
            connect_new = ctl.connect_new,
            lamp_btn = sfu.pushButton_virtual_lamp,
            disconnect = ctl.disconnect_device,
            multispec = ctl.multispec,
            gui = ctl.gui,
            label_or = sfu.label_virtual_or,
            label_sample = sfu.label_virtual_sample
            )

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
