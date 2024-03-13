import logging

from enlighten import common
from enlighten.ui.ScrollStealFilter import ScrollStealFilter

from enlighten.util import unwrap

log = logging.getLogger(__name__)

class PageNavigation:
    """
    This class encapsulates moving around different "screens" of ENLIGHTEN's GUI.
    In many cases, this is achieved by moving different QWidgets (QFrames) to the
    top of QStackedWidgets.

    This class also therefore maintains aspects of application state, as "what
    screen you're on" often affects ENLIGHTEN's understanding of "what you're 
    doing" and therefore what options and features should be enabled or disabled
    across the program.

    Starting with ENLIGHTEN 4.x, we tweaked / refined our nomenclature of how to 
    describe and visually select between different sets of features and operations.

    The current structure is that ENLIGHTEN has Views, Modes and Techniques.

    NB: Capturing in code because I'm thinking about it, but honestly this belongs
    in the ENLIGHTEN Manual if not already there.

    ----------------------------------------------------------------------------
    Views 
    ----------------------------------------------------------------------------

    A VIEW is essentially visual screen you're looking at providing information
    relevant to one conceptual aspect of the measurement system and process:

    - Scope: a large realtime spectral graph, with a "Clipboard" of saved
          Measurements to the left and a StatusBar at the bottom.
    - Settings: ENLIGHTEN application settings on how / where to save files,
          configure interpolation, perform BatchCollections etc.
    - Hardware: information about the currently selected spectrometer, 
          especially its EEPROM pages, but also firmware versions, battery, 
          temperature etc.
    - Log: a scrolling view of recent application log messages (basically a
          'tail' on EnlightenSpectra/enlighten.log)
    - Factory: a "hidden view" only available through a password where 
          Production and Manufacturing features are accessed.

    Views are mutually self-exclusive; you can only be looking at one at a time.
    They are selected via drop-down at the top of the screen.
    
    ----------------------------------------------------------------------------
    Modes
    ----------------------------------------------------------------------------

    Operation Modes are basically "sets of spectrometer features" and 
    "spectroscopic processing options" which logically go together, and are
    essentially based on the type of spectrometer connected and the types of
    spectroscopy usually performed with that model.

    It makes little sense to offer Absorbance or Color-processing features if
    a 785X-ILP spectrometer is connected, because most users would never use
    those features with that model.  It would similarly make little sense to
    offer Raman-related features (like Fire Laser or Raman Intensity Correction)
    if a VISNIRX was connected, because you would rarely use such features with
    that model.

    So Modes are essentially ways to logically group and guide users to "typical,
    reasonable, recommended" behaviors and options based on different types of
    spectrometer and spectroscopy.

    These are the modes currently offered:

    - Raman: all the things a Raman user would normally want to do, and nothing
          distracting / confusing that would get them into trouble.
    - Non-Raman: all the things typically done with non-Raman spectrometers
          (UVVIS, VIS, VISNIR, NIR1 etc).
    - Expert: ...okay, this is where it gets a litle weird.

    "Expert Mode" is provided for people who Know What They Are Doing and want
    All The Features.  Some of those features may or may not typically combined
    or used with a particular model, but these instruments are often used for
    Wild And Crazy R&D so Stop Coddling Me and Give Me the Buttons.

    So kind of in Expert Mode, we take the governors off and expose all the
    features...Raman, non-Raman, even some experimental stuff that even we're
    not completely sure how well it works or where it fits.

    Conceptually, Expert Mode is basically the union of Raman Mode and Non-Raman
    Mode and whatever else we've got going on that isn't hidden in the Factory
    View or in a plug-in.

    Operational Modes are selected via large buttons at the top of the screen
    that look like Tylenol capsules.

    ----------------------------------------------------------------------------
    Techniques
    ----------------------------------------------------------------------------

    There are many different spectroscopy techniques, most offering different 
    post-processing math options, different measurement sequences (e.g. whether
    they require a reference), different hardware features (laser, LED/broadband,
    etc).

    So like Modes, Techniques help inform ENLIGHTEN of what you're trying to do,
    and therefore what features to expose or recommend (or hide, to reduce
    training mistakes, unless the operator explicitly selects Expert Mode and
    the Wild Wild West).

    There is a definite point of equivocation here, in that "Raman" is arguably
    a Technique as well as a Mode. Or you may counter that "Raman" is more a
    family of techniques, including SERS, SERDS, SORS, SSE etc.

    At the moment, we're exposing a "Technique" selection box in the non-Raman
    Mode, but hiding it in the Raman Mode.

    @todo WE NEED to decide how to handle that more elegantly when in Expert
    Mode with a Raman spectrometer (probably by including Raman as a selectable
    Technique, and automatically setting that if transitioning to Expert "from"
    Raman Mode).
    """

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

    def __init__(self, ctl):
        self.ctl = ctl
        cfu = ctl.form.ui

                                
        self.button_raman       = cfu.pushButton_raman
        self.button_non_raman   = cfu.pushButton_non_raman
        self.button_expert      = cfu.pushButton_expert
        self.combo_view         = cfu.comboBox_view
        self.stack_main         = cfu.stackedWidget_low
        self.combo_technique    = cfu.technique_comboBox

        self.button_raman       .setWhatsThis("Switch to Raman mode, which enables Raman-relevant features in the Control Palette.")
        self.button_non_raman   .setWhatsThis("Switch to non-Raman mode, which hides Raman-only features while adding features for absorbance, reflectance etc.")
        self.combo_view         .setWhatsThis("Switch between various ENLIGHTEN views to access different types of product features.")
        self.combo_technique    .setWhatsThis("Select between various non-Raman techniques, each providing distinct spectral processing and options.")
        self.button_expert      .setWhatsThis(unwrap("""
            Enable access to all features and options, whether they seem relevant to your spectrometer or not.

            Also enables access to some 'experimental features' still in development. Intended for advanced users 
            who know what they are doing...use at your own risk."""))

        self.operation_mode = common.OperationModes.RAMAN
        self.current_view = -1 
        self.has_used_raman = False
        self.current_technique = self.combo_technique.currentIndex()

        self.observers = {}

        self.combo_technique.installEventFilter(ScrollStealFilter(self.combo_technique))

        self.button_raman           .clicked            .connect(self.set_operation_mode_raman)
        self.button_non_raman       .clicked            .connect(self.set_operation_mode_non_raman)
        self.button_expert          .clicked            .connect(self.set_operation_mode_expert)
        self.combo_view             .currentIndexChanged.connect(self.update_view_callback)
        self.combo_technique        .currentIndexChanged.connect(self.update_technique_callback)

    def post_init(self):
        self.ctl.graph.set_y_axis(common.Axes.COUNTS)

        # always start in scope view
        self.set_main_page(common.Pages.SCOPE)
        self.set_view(common.Views.SCOPE)

        self.ctl.form.ui.frame_FactoryMode_Options.hide()
        self.ctl.form.ui.frame_transmission_options.hide()        # todo move to TransmissionFeature
        self.set_operation_mode_non_raman()

    def register_observer(self, event, callback):
        if event not in self.observers:
            self.observers[event] = set()
        self.observers[event].add(callback)

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

        self.ctl.form.ui.frame_FactoryMode_Options.setVisible(self.doing_factory())

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
        self.ctl.graph.set_x_axis(common.Axes.WAVELENGTHS)
        self.ctl.graph.set_y_axis(common.Axes.PERCENT)
        self.set_technique_common(common.Techniques.REFLECTANCE_TRANSMISSION)

    def set_technique_absorbance(self):
        self.ctl.graph.set_x_axis(common.Axes.WAVELENGTHS)
        self.ctl.graph.set_y_axis(common.Axes.AU)
        self.set_technique_common(common.Techniques.ABSORBANCE)

    def update_view_shortcut(self):
        index = self.combo_view.currentIndex()
        tt = f"Ctrl-{index+1} shortcut" if index < common.Views.FACTORY else ""
        self.combo_view.setToolTip(tt)

    def is_expert(self):
         return self.operation_mode == common.OperationModes.EXPERT

    def set_view_common(self):
        self.update_view_shortcut()
        self.ctl.graph.reset_axes()

        # if everyone registered as observers, we could drop this...
        self.ctl.update_feature_visibility()

        if "view" in self.observers:
            for callback in self.observers["view"]:
                callback()

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
        return self.operation_mode in [common.OperationModes.RAMAN, common.OperationModes.EXPERT ]

    def doing_expert(self):
        return self.operation_mode == common.OperationModes.EXPERT

    def set_technique_absorbance(self):
        self.set_technique_common(common.Techniques.ABSORBANCE)
        self.ctl.graph.set_x_axis(common.Axes.WAVELENGTHS)
        self.ctl.graph.set_y_axis(common.Axes.AU)

    def set_technique_transmission(self):
        self.set_technique_common(common.Techniques.TRANSMISSION)
        self.ctl.graph.set_x_axis(common.Axes.WAVELENGTHS)
        self.ctl.graph.set_y_axis(common.Axes.PERCENT)

    def set_technique_common(self, technique):
        log.debug("set_technique_common: technique %d", technique)
        self.ctl.form.ui.frame_transmission_options.setVisible(self.using_transmission())

        self.ctl.graph.reset_axes()

        self.current_technique = technique
        technique_name = common.TechniquesHelper.get_pretty_name(self.current_technique)
        # All connected spectrometers always share the same view.  It's a
        # valid question if view should then be stored in app_state, since
        # it's not really a per-spectrometer attribute, but adding for
        # consistency and convenience.
        if self.ctl.multispec:
            self.ctl.multispec.set_app_state("technique_name", technique_name, all_=True)

        # Business Objects
        self.ctl.update_feature_visibility()
    
    def set_operation_mode_raman(self):
        spec = self.ctl.multispec.current_spectrometer() if self.ctl.multispec else None
        if spec is None or not spec.settings.has_excitation():
            if self.ctl.marquee:
                self.ctl.marquee.error("Raman mode requires an excitation wavelength")
            return self.set_operation_mode_non_raman()

        log.debug(f"raman mode operation set")

        self.ctl.graph.set_x_axis(common.Axes.WAVENUMBERS)
        self.ctl.graph.set_y_axis(common.Axes.COUNTS)
        self.operation_mode = common.OperationModes.RAMAN
        self.set_technique_common(common.Techniques.RAMAN)

        self.ctl.stylesheets.apply(self.button_raman, "left_rounded_active")
        self.ctl.stylesheets.apply(self.button_non_raman, "center_rounded_inactive")
        self.ctl.stylesheets.apply(self.button_expert, "right_rounded_inactive")
        self.hide_non_raman_technique()
        self.update_expert_widgets()

        if not self.has_used_raman and self.ctl.save_options:
            self.has_used_raman = True
            self.ctl.save_options.force_wavenumber()
        self.set_operation_mode_common()

    def set_operation_mode_non_raman(self):
        self.ctl.graph.set_x_axis(common.Axes.WAVELENGTHS)

        self.ctl.stylesheets.apply(self.button_raman, "left_rounded_inactive")
        self.ctl.stylesheets.apply(self.button_non_raman, "center_rounded_active")
        self.ctl.stylesheets.apply(self.button_expert, "right_rounded_inactive")

        self.operation_mode = common.OperationModes.NON_RAMAN

        self.ctl.update_feature_visibility()
        self.display_non_raman_technique()
        self.update_expert_widgets()
        self.set_operation_mode_common()

    def set_operation_mode_expert(self):
        log.debug("set_operation_mode_expert: start")
        self.ctl.stylesheets.apply(self.button_raman, "left_rounded_inactive")
        self.ctl.stylesheets.apply(self.button_non_raman, "center_rounded_inactive")
        self.ctl.stylesheets.apply(self.button_expert, "right_rounded_active")
        self.operation_mode = common.OperationModes.EXPERT
        self.ctl.update_feature_visibility()
        self.display_non_raman_technique()
        self.update_expert_widgets()
        self.set_operation_mode_common()

    def update_expert_widgets(self):
        is_ingaas = False
        has_cooling = False
        flag = self.doing_expert()
        cfu = self.ctl.form.ui

        spec = self.ctl.multispec.current_spectrometer() if self.ctl.multispec else None
        if spec is None:
            flag = False
        else:
            is_ingaas = spec.settings.is_ingaas()
            has_cooling = spec.settings.eeprom.has_cooling

        # todo: migrate all of these to register_observer("doing_expert") in 
        # their respective owning Business Objects
        cfu.frame_post_processing.setVisible(flag)
        cfu.frame_baseline_correction.setVisible(flag)
        # cfu.frame_tec_control.setVisible(flag and has_cooling)
        cfu.frame_area_scan_widget.setVisible(flag and not is_ingaas)
        cfu.frame_region_control.setVisible(False) # spec.settings.is_imx()

    def set_operation_mode_common(self):
        if "mode" in self.observers:
            for callback in self.observers["mode"]:
                callback()

    def display_non_raman_technique(self):
        self.ctl.form.ui.frame_TechniqueWidget.show()

    def hide_non_raman_technique(self):
        self.ctl.form.ui.frame_TechniqueWidget.hide()

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
