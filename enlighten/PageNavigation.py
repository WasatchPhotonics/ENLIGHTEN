import logging

from . import common

log = logging.getLogger(__name__)

##
# This class is not yet fully refactored.
class PageNavigation:

    def __init__(self,
            graph,
            marquee,
            multispec,
            save_options,
            stylesheets,

            combo_technique,
            button_details,
            button_logging,
            button_setup,
            button_capture,
            stack_hardware,
            stack_main,

            update_feature_visibility,
            scroll_area,
            textEdit_log,                       # todo move to LoggingFeature
            frame_transmission_options,         # todo move to TransmissionFeature
            sfu,
            ):

        self.graph              = graph
        self.marquee            = marquee
        self.multispec          = multispec
        self.save_options       = save_options
        self.stylesheets        = stylesheets
        self.sfu                = sfu
                                
        self.button_details     = button_details
        self.button_logging     = button_logging
        self.button_setup       = button_setup
        self.button_capture     = button_capture 
        self.combo_technique    = combo_technique
        self.stack_hardware     = stack_hardware 
        self.stack_main         = stack_main 

        self.frame_transmission_options = frame_transmission_options 
        self.update_feature_visibility = update_feature_visibility
        self.scroll_area = scroll_area
        self.textEdit_log = textEdit_log

        # all techniques default to setup except scope
        self.technique_operation_mode = {}
        for technique in list(common.Techniques):
            if technique == common.Techniques.SCOPE:
                self.technique_operation_mode[technique] = common.OperationModes.CAPTURE
            else:
                self.technique_operation_mode[technique] = common.OperationModes.SETUP
        self.current_technique = common.Techniques.SCOPE
        self.current_operation_mode = common.OperationModes.CAPTURE
        self.has_used_raman = False

        self.button_setup       .clicked            .connect(self.set_operation_mode_setup)
        self.button_capture     .clicked            .connect(self.set_operation_mode_capture)
        self.combo_technique    .currentIndexChanged.connect(self.update_technique_callback)
        self.button_details     .clicked            .connect(self.set_hardware_details_active)
        self.button_logging     .clicked            .connect(self.set_hardware_logging_active)

    def post_init(self):
        self.set_technique_scope()
        self.set_operation_mode_capture()

    # ##########################################################################
    # activity introspection
    # ##########################################################################

    def doing_scope_capture     (self): return self.get_main_page() == common.Pages.SCOPE_CAPTURE
    def doing_hardware_capture  (self): return self.get_main_page() == common.Pages.HARDWARE_CAPTURE
    def doing_hardware          (self): return self.current_technique == common.Techniques.HARDWARE
    def doing_scope             (self): return self.current_technique == common.Techniques.SCOPE
    def doing_raman             (self): return self.current_technique == common.Techniques.RAMAN
    def doing_transmission      (self): return self.current_technique == common.Techniques.TRANSMISSION
    def doing_absorbance        (self): return self.current_technique == common.Techniques.ABSORBANCE
    def using_transmission      (self): return self.current_technique in [ common.Techniques.TRANSMISSION, common.Techniques.ABSORBANCE ]
    def using_reference         (self): return self.current_technique in [ common.Techniques.TRANSMISSION, common.Techniques.ABSORBANCE ]

    def get_current_technique(self): 
        return self.current_technique

    def get_current_technique_name(self):
        return common.TechniquesHelper.get_pretty_name(self.current_technique)

    # ##########################################################################
    # Techniques
    # ##########################################################################

    # parameterized method provided for constructor; otherwise we use named
    # functions which better support callbacks
    def set_technique(self, technique):
        if technique == common.Techniques.HARDWARE     : return self.set_technique_hardware()
        if technique == common.Techniques.SCOPE        : return self.set_technique_scope()
        if technique == common.Techniques.RAMAN        : return self.set_technique_raman()
        if technique == common.Techniques.TRANSMISSION : return self.set_technique_transmission()
        if technique == common.Techniques.ABSORBANCE   : return self.set_technique_absorbance()

        log.error("set_technique: Unsupported technique: %s", technique)
        self.set_technique_scope()


    # called whenever the user changes the technique via the GUI combobox
    def update_technique_callback(self):
        self.current_technique = self.determine_current_technique()
        log.debug("update_technique_callback: current_technique now %d", self.current_technique)

        if self.doing_hardware():
            self.sfu.frame_hardware_capture_control_cb.show()
            self.sfu.label_hardware_capture_control.show()
        else:
            self.sfu.frame_hardware_capture_control_cb.hide()
            self.sfu.label_hardware_capture_control.hide()

        if self.doing_hardware()    : return self.set_technique_hardware()
        if self.doing_scope()       : return self.set_technique_scope()
        if self.doing_raman()       : return self.set_technique_raman()
        if self.doing_transmission(): return self.set_technique_transmission()
        if self.doing_absorbance()  : return self.set_technique_absorbance()
        
        log.error("update_technique_callback: unknown technique: %s", self.current_technique)
        self.set_technique_scope()

    def toggle_hardware_and_scope(self):
        if self.doing_hardware():
            self.set_technique_scope()
        else:
            self.set_technique_hardware()

    def set_technique_hardware(self):
        log.info("setting technique to hardware")
        self.set_technique_common(common.Techniques.HARDWARE)

    def set_technique_scope(self):
        self.set_technique_common(common.Techniques.SCOPE)
        self.graph.set_x_axis(common.Axes.WAVELENGTHS)
        self.graph.set_y_axis(common.Axes.COUNTS)

    def set_technique_raman(self):
        spec = self.multispec.current_spectrometer()
        if spec is None or not spec.settings.has_excitation():
            self.marquee.error("Raman mode requires an excitation wavelength")
            return self.set_technique_scope()

        self.set_technique_common(common.Techniques.RAMAN)
        self.graph.set_x_axis(common.Axes.WAVENUMBERS)
        self.graph.set_y_axis(common.Axes.COUNTS)

        # Per Dieter, Raman mode should default to APLS. Note that we don't
        # currently track settings (baseline correction, integration time, laser
        # enable etc) by technique, so baseline correction will REMAIN selected
        # if you change to Scope or Absorbance/etc...
        if not self.has_used_raman:
            self.has_used_raman = True
            self.save_options.force_wavenumber()
            if spec.app_state.has_dark() and not spec.app_state.baseline_correction_enabled:
                # persist this because we don't know how long they'll stay on the
                # Scope Setup screen
                #
                # Dieter says "not yet"
                #
                # self.marquee.info("Auto-enabling baseline correction", persist=True)
                # self.baseline_correction.reset(enable=True)
                pass

    def set_technique_transmission(self):
        self.set_technique_common(common.Techniques.TRANSMISSION)
        self.graph.set_x_axis(common.Axes.WAVELENGTHS)
        self.graph.set_y_axis(common.Axes.PERCENT)

    def set_technique_absorbance(self):
        self.set_technique_common(common.Techniques.ABSORBANCE)
        self.graph.set_x_axis(common.Axes.WAVELENGTHS)
        self.graph.set_y_axis(common.Axes.AU)

    def set_technique_common(self, technique):
        log.debug("set_technique_common: technique %d", technique)
        self.combo_technique.setCurrentIndex(technique)
        self.frame_transmission_options.setVisible(self.using_transmission())

        # switch to last-used operation mode for the given technique
        self.set_operation_mode(self.technique_operation_mode[technique])

        self.graph.reset_axes()

        # Business Objects
        self.update_feature_visibility()

    # ##########################################################################
    # Page Navigation: Operation Mode
    # ##########################################################################

    def set_hardware_details_active(self):
        self.stack_hardware.setCurrentIndex(0)
        self.stylesheets.apply(self.button_details, "tab_active")
        self.stylesheets.apply(self.button_logging, "tab_inactive")

    def set_hardware_logging_active(self):
        self.stack_hardware.setCurrentIndex(1)
        self.stylesheets.apply(self.button_details, "tab_inactive")
        self.stylesheets.apply(self.button_logging, "tab_active")

        self.scroll_to_top(self.scroll_area)
        self.scroll_to_top(self.textEdit_log)

    def scroll_to_top(self, widget):
        widget.verticalScrollBar().setValue(widget.verticalScrollBar().minimum())
        
    def set_main_page(self, page):
        self.stack_main.setCurrentIndex(page)

    def get_main_page(self):
        return self.stack_main.currentIndex()

    def set_operation_mode(self, mode):
        if mode == common.OperationModes.SETUP  : return self.set_operation_mode_setup()
        if mode == common.OperationModes.CAPTURE: return self.set_operation_mode_capture()

        log.error("Unsupported operation mode: %s", mode)
        self.set_operation_mode_capture()

    def set_operation_mode_setup(self):
        self.set_operation_mode_common(common.OperationModes.SETUP)
        if self.doing_hardware(): 
            self.set_main_page(common.Pages.HARDWARE_SETUP)
        else:
            self.set_main_page(common.Pages.SCOPE_SETUP)

    def set_operation_mode_capture(self):
        log.debug("set_operation_mode_capture")
        self.set_operation_mode_common(common.OperationModes.CAPTURE)
        if self.doing_hardware():
            self.set_main_page(common.Pages.HARDWARE_CAPTURE)
        else:
            self.set_main_page(common.Pages.SCOPE_CAPTURE)

    def set_operation_mode_common(self, mode):
        # cache the newly-set operation mode for the current technique, so the
        # next time we switch back to this technique we'll restore this mode
        self.technique_operation_mode[self.current_technique] = mode

        # This is used by doing_peakfinding()...generally setting operation mode
        # is fire-and-forget, but that's one case when we later want to
        # introspect and know what mode we're supposedly in.
        self.operation_mode = mode

        if self.doing_hardware():
            # Hardware technique, so buttons should be (setup, capture)
            if mode == common.OperationModes.SETUP:
                self.stylesheets.apply(self.button_setup, "left_rounded_active")
                self.stylesheets.apply(self.button_capture, "right_rounded_inactive")
            elif mode == common.OperationModes.CAPTURE:
                self.stylesheets.apply(self.button_setup, "left_rounded_inactive")
                self.stylesheets.apply(self.button_capture, "right_rounded_active")
            else:
                log.error("unknown operation mode (hardware technique): %s", mode)
        else:
            # Scope or other technique, so buttons should be (setup, capture)
            if mode == common.OperationModes.SETUP:
                self.stylesheets.apply(self.button_setup, "left_rounded_active")
                self.stylesheets.apply(self.button_capture, "right_rounded_inactive")
            elif mode == common.OperationModes.CAPTURE:
                self.stylesheets.apply(self.button_setup, "left_rounded_inactive")
                self.stylesheets.apply(self.button_capture, "right_rounded_active")
            else:
                log.error("unknown operation mode (scopish technique): %s", mode)

        # All connected spectrometers always share the same technique.  It's a
        # valid question if technique should then be stored in app_state, since
        # it's not really a per-spectrometer attribute, but adding for
        # consistency and convenience.
        self.multispec.set_app_state("technique_name", self.get_current_technique_name(), all=True)

    def determine_current_technique(self):
        label = self.combo_technique.currentText().lower()

        if label == "hardware": return common.Techniques.HARDWARE
        if label == "scope":    return common.Techniques.SCOPE
        if label == "raman":    return common.Techniques.RAMAN
        if "abs" in label:      return common.Techniques.ABSORBANCE
        if "trans"  in label:   return common.Techniques.TRANSMISSION

        log.error("unknown technique %s", label)
        return common.Techniques.HARDWARE
