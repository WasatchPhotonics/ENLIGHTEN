import logging

from enlighten import common
from enlighten.ScrollStealFilter import ScrollStealFilter

log = logging.getLogger(__name__)

##
# This class is not yet fully refactored.
class PageNavigation:

    technique_callbacks = {
        common.Techniques.NONE: lambda self, tech: self.set_technique_common(common.Techniques.NONE),
        common.Techniques.EMISSION: lambda self, tech: self.set_technique_common(common.Techniques.EMISSION),
        common.Techniques.RAMAN: lambda self, tech: self.set_technique_common(common.Techniques.RAMAN),
        common.Techniques.REFLECTANCE_TRANSMISSION: lambda self, tech: self.set_technique_transmission(),
        common.Techniques.ABSORBANCE: lambda self, tech: self.set_technique_absorbance(),
        common.Techniques.COLOR: lambda self, tech: self.set_technique_common(common.Techniques.COLOR),
        common.Techniques.FLUORESCENCE: lambda self, tech: self.set_technique_common(common.Techniques.FLUORESCENCE),
        common.Techniques.RELATIVE_IRRADIANCE: lambda self, tech: self.set_technique_common(common.Techniques.RELATIVE_IRRADIANCE)
        }

    def __init__(self,
            graph,
            logging_feature,
            marquee,
            multispec,
            save_options,
            stylesheets,

            combo_view,
            button_raman,
            button_non_raman,
            button_expert,
            stack_main,

            update_feature_visibility,

            fr_transmission_options,
            fr_area_scan,
            fr_baseline,
            fr_post,
            fr_tec,
            fr_region,

            sfu,
            ):

        self.graph              = graph
        self.logging_feature    = logging_feature
        self.marquee            = marquee
        self.multispec          = multispec
        self.save_options       = save_options
        self.stylesheets        = stylesheets
        self.sfu                = sfu
                                
        self.button_raman       = button_raman
        self.button_non_raman   = button_non_raman
        self.button_expert      = button_expert
        self.combo_view         = combo_view
        self.stack_main         = stack_main 
        self.combo_technique    = self.sfu.technique_comboBox

        self.fr_transmission_options = fr_transmission_options
        self.fr_area_scan       = fr_area_scan
        self.fr_baseline        = fr_baseline
        self.fr_post            = fr_post
        self.fr_tec             = fr_tec
        self.fr_region          = fr_region
        
        self.update_feature_visibility = update_feature_visibility

        # self-register
        self.logging_feature.page_nav = self

        self.operation_mode = common.OperationModes.RAMAN
        self.current_view = -1
        self.has_used_raman = False
        self.current_technique = self.sfu.technique_comboBox.currentIndex()

        self.combo_technique.installEventFilter(ScrollStealFilter(self.combo_technique))

        self.button_raman           .clicked            .connect(self.set_operation_mode_raman)
        self.button_non_raman       .clicked            .connect(self.set_operation_mode_non_raman)
        self.button_expert          .clicked            .connect(self.set_operation_mode_expert)
        self.combo_view             .currentIndexChanged.connect(self.update_view_callback)
        self.combo_technique        .currentIndexChanged.connect(self.update_technique_callback)

    def post_init(self):
        self.graph.set_y_axis(common.Axes.COUNTS)

        # always start in scope view
        self.set_main_page(common.Pages.SCOPE)
        self.set_view(common.Views.SCOPE)

        self.sfu.frame_FactoryMode_Options.hide()
        self.set_operation_mode_non_raman()
        self.fr_transmission_options.hide()

    # ##########################################################################
    # activity introspection
    # ##########################################################################

    def doing_factory           (self): return self.current_view == common.Views.FACTORY
    def doing_settings          (self): return self.current_view == common.Views.SETTINGS
    def doing_hardware          (self): return self.current_view == common.Views.HARDWARE
    def doing_scope             (self): return self.current_view == common.Views.SCOPE
    def doing_log               (self): return self.current_view == common.Views.LOG

    def get_current_view(self): 
        return self.current_view

    def get_current_view_name(self):
        return common.ViewsHelper.get_pretty_name(self.current_view)

    # ##########################################################################
    # Views
    # ##########################################################################

    # parameterized method provided to ensure combo stays in sync
    def set_view(self, index):
        log.debug(f"set_view: changing combo index to {index}")
        self.combo_view.setCurrentIndex(index)

    def update_technique_callback(self):
        log.debug(f"technique callback triggered")
        self.current_technique = self.determine_current_technique()
        log.debug(f"setting to technique {self.current_technique}")
        callback = self.technique_callbacks.get(self.current_technique, None)
        if callback is not None:
            callback(self, self.current_technique)
        else:
            log.error("Determined technique was invalid for callback? Shouldn't be here.")

    # called whenever the user changes the view via the GUI combobox
    def update_view_callback(self):
        self.current_view = self.determine_current_view()
        log.debug("update_view_callback: current_view now %d", self.current_view)

        self.sfu.frame_FactoryMode_Options.setVisible(self.doing_factory())

        if self.doing_hardware()        : return self.set_view_hardware()
        if self.doing_factory()         : return self.set_view_factory()
        if self.doing_settings()        : return self.set_view_settings()
        if self.doing_scope()           : return self.set_view_scope()
        if self.doing_log()             : return self.set_view_logging()
        
        log.error("update_view_callback: unknown view: %s", self.current_view)
        self.set_view(common.Views.SCOPE)

    def toggle_hardware_and_scope(self):
        if self.doing_hardware():
            self.set_view(common.Views.SCOPE)
        else:
            self.set_view(common.Views.HARDWARE)

    def set_view_scope(self):
        log.debug("set_view_scope")
        if self.current_view != common.Views.SCOPE:
            self.set_view(common.Views.SCOPE)
            return

        self.set_view_common()
        self.set_main_page(common.Pages.SCOPE)

    def set_view_settings(self):
        log.debug("set_view_settings")
        if self.current_view != common.Views.SETTINGS:
            self.set_view(common.Views.SETTINGS)
            return

        self.set_view_common()
        self.set_main_page(common.Pages.SETTINGS)

    def set_view_hardware(self):
        log.debug("set_view_hardware")
        if self.current_view != common.Views.HARDWARE:
            self.set_view(common.Views.HARDWARE)
            return

        self.set_view_common()
        self.set_main_page(common.Pages.HARDWARE)

    def set_view_logging(self):
        log.debug("set_view_logging")
        if self.current_view != common.Views.LOG:
            self.set_view(common.Views.LOG)
            return

        self.set_view_common()
        self.set_main_page(common.Pages.LOG)

    def set_view_factory(self):
        log.debug("set_view_factory")
        if self.current_view != common.Views.FACTORY:
            self.set_view(common.Views.FACTORY)
            return

        self.set_view_common()
        self.set_main_page(common.Pages.FACTORY)

    def set_technique_transmission(self):
        self.graph.set_x_axis(common.Axes.WAVELENGTHS)
        self.graph.set_y_axis(common.Axes.PERCENT)
        self.set_technique_common(common.Techniques.REFLECTANCE_TRANSMISSION)

    def set_technique_absorbance(self):
        self.graph.set_x_axis(common.Axes.WAVELENGTHS)
        self.graph.set_y_axis(common.Axes.AU)
        self.set_technique_common(common.Techniques.ABSORBANCE)

    def update_view_shortcut(self):
        index = self.combo_view.currentIndex()
        tt = f"Ctrl-{index+1} shortcut" if index < common.Views.FACTORY else ""
        self.combo_view.setToolTip(tt)

     def is_expert(self):
         return self.operation_mode == common.OperationModes.EXPERT

    def set_view_common(self):
        self.update_view_shortcut()
        self.graph.reset_axes()
        self.update_feature_visibility()

    # ##########################################################################
    # Page Navigation: Operation Mode
    # ##########################################################################

    def set_main_page(self, index):
        log.debug(f"set_main_page: index {index}")
        self.stack_main.setCurrentIndex(index)

    def get_main_page(self):
        return self.stack_main.currentIndex()

    def doing_transmission      (self): return self.current_technique == common.Techniques.REFLECTANCE_TRANSMISSION
    def doing_absorbance        (self): return self.current_technique == common.Techniques.ABSORBANCE

    def using_transmission      (self): return self.current_technique in [ common.Techniques.REFLECTANCE_TRANSMISSION, common.Techniques.ABSORBANCE ]
    def using_reference         (self): return self.current_technique in [ common.Techniques.REFLECTANCE_TRANSMISSION, common.Techniques.ABSORBANCE ]

    def doing_raman(self):
        return self.operation_mode == common.OperationModes.RAMAN

    def doing_expert(self):
        return self.operation_mode == common.OperationModes.EXPERT

    def set_technique_absorbance(self):
        self.set_technique_common(common.Techniques.ABSORBANCE)
        self.graph.set_x_axis(common.Axes.WAVELENGTHS)
        self.graph.set_y_axis(common.Axes.AU)

    def set_technique_transmission(self):
        self.set_technique_common(common.Techniques.TRANSMISSION)
        self.graph.set_x_axis(common.Axes.WAVELENGTHS)
        self.graph.set_y_axis(common.Axes.PERCENT)

    def set_technique_common(self, technique):
        log.debug("set_technique_common: technique %d", technique)
        self.fr_transmission_options.setVisible(self.using_transmission())

        self.graph.reset_axes()

        self.current_technique = technique
        technique_name = common.TechniquesHelper.get_pretty_name(self.current_technique)
        # All connected spectrometers always share the same view.  It's a
        # valid question if view should then be stored in app_state, since
        # it's not really a per-spectrometer attribute, but adding for
        # consistency and convenience.
        self.multispec.set_app_state("technique_name", technique_name, all=True)

        # Business Objects
        self.update_feature_visibility()
    
    def set_operation_mode_raman(self):
        spec = self.multispec.current_spectrometer()
        if spec is None or not spec.settings.has_excitation():
            self.marquee.error("Raman mode requires an excitation wavelength")
            return self.set_operation_mode_non_raman()

        log.debug(f"raman mode operation set")

        self.graph.set_x_axis(common.Axes.WAVENUMBERS)
        self.graph.set_y_axis(common.Axes.COUNTS)
        self.operation_mode = common.OperationModes.RAMAN
        self.set_technique_common(common.Techniques.RAMAN)

        self.stylesheets.apply(self.button_raman, "left_rounded_active")
        self.stylesheets.apply(self.button_non_raman, "center_rounded_inactive")
        self.stylesheets.apply(self.button_expert, "right_rounded_inactive")
        self.hide_non_raman_technique()
        self.update_expert_widgets()

        # Per Dieter, Raman mode should default to APLS. Note that we don't
        # currently track settings (baseline correction, integration time, laser
        # enable etc) by view, so baseline correction will REMAIN selected
        # if you change to Scope or Absorbance/etc...
        if not self.has_used_raman:
            self.has_used_raman = True
            self.save_options.force_wavenumber()

    def set_operation_mode_non_raman(self):
        self.graph.set_x_axis(common.Axes.WAVELENGTHS)

        self.stylesheets.apply(self.button_raman, "left_rounded_inactive")
        self.stylesheets.apply(self.button_non_raman, "center_rounded_active")
        self.stylesheets.apply(self.button_expert, "right_rounded_inactive")

        self.operation_mode = common.OperationModes.NON_RAMAN

        self.update_feature_visibility()
        self.display_non_raman_technique()
        self.update_expert_widgets()

    def set_operation_mode_expert(self):
        log.debug("set_operation_mode_expert: start")
        self.stylesheets.apply(self.button_raman, "left_rounded_inactive")
        self.stylesheets.apply(self.button_non_raman, "center_rounded_inactive")
        self.stylesheets.apply(self.button_expert, "right_rounded_active")
        self.operation_mode = common.OperationModes.EXPERT
        self.update_feature_visibility()
        self.display_non_raman_technique()
        self.update_expert_widgets()

    def update_expert_widgets(self):
        is_ingaas = False
        has_cooling = False
        flag = self.doing_expert()

        spec = self.multispec.current_spectrometer()
        if spec is None:
            flag = False
        else:
            is_ingaas = spec.settings.is_ingaas()
            has_cooling = spec.settings.eeprom.has_cooling

        self.fr_post        .setVisible(flag)
        self.fr_baseline    .setVisible(flag)
        self.fr_tec         .setVisible(flag and has_cooling)
        self.fr_area_scan   .setVisible(flag and not is_ingaas)
        self.fr_region      .setVisible(False) # spec.settings.is_imx()

    def set_operation_mode_common(self, mode):
        # cache the newly-set operation mode for the current view, so the
        # next time we switch back to this view we'll restore this mode
        self.view_operation_mode[self.current_view] = mode

        # This is used by doing_peakfinding()...generally setting operation mode
        # is fire-and-forget, but that's one case when we later want to
        # introspect and know what mode we're supposedly in.
        self.operation_mode = mode

    def display_non_raman_technique(self):
        self.sfu.frame_TechniqueWidget.show()

    def hide_non_raman_technique(self):
        self.sfu.frame_TechniqueWidget.hide()

    def determine_current_technique(self):
        label = self.combo_technique.currentText().lower()
        if self.operation_mode == common.OperationModes.RAMAN:
            return common.Techniques.RAMAN
        else:
            if label == "emission":   return common.Techniques.EMISSION
            if label == "absorbance": return common.Techniques.ABSORBANCE
            if label == "trans/refl": return common.Techniques.REFLECTANCE_TRANSMISSION
        return common.Techniques.NONE

    def determine_current_view(self):
        label = self.combo_view.currentText().lower()

        if label == "hardware": return common.Views.HARDWARE
        if label == "scope":    return common.Views.SCOPE
        if label == "settings": return common.Views.SETTINGS
        if label == "log":      return common.Views.LOG
        if label == "factory":  return common.Views.FACTORY

        log.error("unknown view %s", label)
        return common.Views.HARDWARE
