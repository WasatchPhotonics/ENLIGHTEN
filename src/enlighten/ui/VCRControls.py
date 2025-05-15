import logging

from enlighten import util
from enlighten.util import unwrap

from enlighten.common import msgbox

log = logging.getLogger(__name__)

##
# Encapsulate the state, appearance and behavior of the seven VCR-style
# "Action Buttons" appearing along the top of the Scope Capture screen.
# 
# Those are divided into four conceptual "positions", being:
#
# Pos1  Pos2  Pos3            Pos4
# ----- ----- -----           -----
# Pause Save  Step            StepSave
# Play        StartCollection
# Stop
#
# Only 2-4 buttons shold ever be shown at one time.  No more than one button 
# from a given "position" can be shown at one time; the buttons within a position 
# are mutually exclusive. 
#
class VCRControls:

    def __init__(self, ctl):
        self.ctl = ctl
        cfu = ctl.form.ui

        self.bt_pause            = cfu.pushButton_scope_capture_pause
        self.bt_play             = cfu.pushButton_scope_capture_play
        self.bt_save             = cfu.pushButton_scope_capture_save
        self.bt_start_collection = cfu.pushButton_scope_capture_start_collection
        self.bt_step             = cfu.pushButton_scope_capture_step
        self.bt_step_save        = cfu.pushButton_scope_capture_step_save
        self.bt_stop             = cfu.pushButton_scope_capture_stop

        self.paused = False     # external callers should use is_paused()

        self.bt_pause           .clicked.connect(self.pause_callback)
        self.bt_play            .clicked.connect(self.play_callback)
        self.bt_save            .clicked.connect(self.save)
        self.bt_start_collection.clicked.connect(self.start_collection)
        self.bt_step            .clicked.connect(self.step)
        self.bt_step_save       .clicked.connect(self.step_save)
        self.bt_stop            .clicked.connect(self.stop)

        self.tooltips = {
            "pause":            "Stop continuous acquisition (ctrl-P)",
            "play":             "Start continuous acquisition (ctrl-P)",
            "save":             "Save the current spectra shown on-screen (ctrl-S)",
            "start_collection": "Start a batch collection",
            "step":             "Acquire one averaged measurement and stop",
            "step_save":        "Acquire one averaged measurement, save it and stop",
            "stop":             "Cancel the current operation"
        }

        self.callbacks = {} 
        for name in self.tooltips:
            self.callbacks[name] = set()

        self.bt_pause           .setToolTip(self.tooltips["pause"])
        self.bt_play            .setToolTip(self.tooltips["play"])
        self.bt_save            .setToolTip(self.tooltips["save"])
        self.bt_start_collection.setToolTip(self.tooltips["start_collection"])
        self.bt_step            .setToolTip(self.tooltips["step"])
        self.bt_step_save       .setToolTip(self.tooltips["step_save"])
        self.bt_stop            .setToolTip(self.tooltips["stop"])

        self.bt_play            .setWhatsThis("VCR-style play button to un-pause display of on-screen spectra")
        self.bt_save            .setWhatsThis("Saves a single measurement to disk and to the scrolling Clipboard along the left-hand side of the scope")
        self.bt_start_collection.setWhatsThis("When Batch Collection is enabled, this button starts a new batch")
        self.bt_stop            .setWhatsThis("Halt the current activity (such as a long-running Batch Collection)")
        self.bt_pause           .setWhatsThis(unwrap("""VCR-style pause button to freeze on-screen spectra (spectrometer 
                                                        silently continues free-running acquisition in background, but 
                                                        new spectra are neither displayed nor saved)"""))
        self.bt_step            .setWhatsThis(unwrap("""This button is only available when the spectrometer is "paused."

                                                        In normal operation, this button will take a single measurement, then
                                                        resume pause.
                                                        
                                                        When Auto-Raman is enabled, this button will take a single Auto-Raman
                                                        measurement. See the "What's This" help for Auto-Raman for more 
                                                        information."""))
        self.bt_step_save       .setWhatsThis(unwrap("""This button is only available when the spectrometer is "paused."

                                                        In normal operation, this button will take a single measurement, 
                                                        saving it to disk and the Clipboard, then resume pause.
                                                        
                                                        When Auto-Raman is enabled, this button will take a single Auto-Raman
                                                        measurement and save it to disk and the Clipboard. See the "What's 
                                                        This" help for Auto-Raman for more information."""))

        # always colorize stop
        self.ctl.gui.colorize_button(self.bt_stop, True)

        self.update_visibility()

    ############################################################################
    # Observers
    ############################################################################

    ## 
    # Register a callback function (or instance method) to a named VCRControls
    # event.
    #
    # @param event one of "stop", "play", "stop", "pause", "step", "step_save", 
    #              "start_collection"
    # @param callback function to be called when the named event occurs
    def register_observer(self, event, callback):
        if event not in self.callbacks:
            log.critical("VCRControls.register has no event %s", event)
            return
        log.debug("registering observer: %s -> %s", event, str(callback))
        self.callbacks[event].add(callback)

        self.update_visibility()

    ## Remove a registered callback for the named event.
    def unregister_observer(self, event, callback):
        if event not in self.callbacks:
            log.critical("VCRControls.unregister has no event %s", event)
        elif callback in self.callbacks[event]:
            log.debug("unregistering %s from event %s", str(callback), event)
            self.callbacks[event].remove(callback)
            self.update_visibility() # stop-button state depends on registration
        else:
            # Some potential observers only register callbacks when they need to
            # (i.e. BatchCollection), but unregister everything on shutdown for
            # safety.
            #
            # log.debug("VCRControls didn't have a registration from event %s to %s", event, str(callback))
            pass

    def _stop_enabled(self):
        return len(self.callbacks["stop"]) > 0

    # ##########################################################################
    # Button callbacks
    # ##########################################################################

    def pause_callback(self):
        self.pause()

    def play_callback(self):
        self.play()

    ## pause the current spectrometer
    def pause(self, spec=None): 
        log.debug("pause")
        self._set_paused(True, all_=self.ctl.multispec.locked, spec=spec)
        for callback in list(self.callbacks["pause"]):
            callback()
        self.update_visibility()

    ## set the current spectrometer to continuous acquisition
    def play(self, spec=None):
        log.debug("play")
        self._set_paused(False, all_=self.ctl.multispec.locked, spec=spec)
        for callback in list(self.callbacks["play"]):
            callback()
        self.update_visibility()

    ## 
    # If a long-running operation is in progress, cancel it by sending event
    # to each registered observer. 
    # 
    # Typically there would be just one registered observer for a Stop, but 
    # during a BatchCollection for instance, there can be two: 
    #
    # - the TakeOne instance is registered to stop its potentially multi-averaged 
    #   measurement
    # - the BatchCollection is registered to stop the Batch itself
    #  
    # A single click of the "stop" button should correctly stop both.
    def stop(self): 
        log.debug("stop")
        for callback in list(self.callbacks["stop"]):
            callback()

        # we essentially have a permanent hardcoded callback from stop -> scan_averaging, 
        # but it's not implemented in the list, as we don't want the callback to expire,
        # nor do we want it to trigger a state change in the sense of displaying
        # a permanent [stop] button
        if self.ctl.scan_averaging:
            self.ctl.scan_averaging.reset()

        # after the stop has been processed, clear all observers 
        # (each stop is a one-time event)
        self.callbacks["stop"] = set()

        self.update_visibility()

    ## send a "save" event to anyone registered for that
    def save(self): 
        log.debug("save")

        if len(self.callbacks["save"]) == 0:
            # this is one scenario where the save button does nothing
            # if this happens, it means the main save callback was unregistered
            msgbox("Fatal Error: Save button has no callback.", "Error")

        for callback in list(self.callbacks["save"]):
            callback()

        self.update_visibility()

    ## collect one measurement, then go back to paused
    def step(self, save=False, completion_callback=None, take_one_template=None):
        log.debug("step")

        # pass along any callback related to the completion of the TakeOne process
        self.ctl.take_one.start(save=save, completion_callback=completion_callback, template=take_one_template)

        # to be clear, these callbacks indicate the "step" button was clicked/fired, 
        # NOT that it is complete
        for callback in list(self.callbacks["step"]):
            log.debug(f"step: calling callback {callback}")
            callback()

        self.update_visibility()

    def step_save(self, completion_callback=None, take_one_template=None): 
        log.debug("step_save")
        self.step(save=True, completion_callback=completion_callback, take_one_template=take_one_template)
        for callback in list(self.callbacks["step_save"]):
            callback()
        self.update_visibility()

    def start_collection(self): 
        log.debug("start_collection")

        # testing: pause, if not already
        spec = self.ctl.multispec.current_spectrometer()
        if spec:
            paused = spec.app_state.paused
        else:
            paused = self.paused 
        if not paused:
            self.pause()
        # end testing

        for callback in list(self.callbacks["start_collection"]):
            callback()
        self.update_visibility()
        
    # ##########################################################################
    # public methods
    # ##########################################################################

    ##
    # There are basically 5 typical permutations of buttons (lowercase = disabled)
    #
    # \verbatim
    #                           Pos1    Pos2    Pos3    Pos4
    # Continuous Acquisition:   Pause   Save
    # Paused (normal):          Play    Save    Step    StepSave
    # TakeOne (averaging):      Stop    save    step    stepsave
    # Paused (BatchCollection): Play    Save    StartCol
    # Collecting Batch:         Stop    save    startcol
    # \endverbatim
    #
    # This is called externally by BatchCollection and probably others.
    def update_visibility(self):
        bc_enabled   = self.ctl.batch_collection is not None and self.ctl.batch_collection.enabled
        bc_running   = self.ctl.batch_collection is not None and self.ctl.batch_collection.running
        to_running   = self.ctl.take_one is not None and self.ctl.take_one.running
        stop_enabled = self._stop_enabled()
        paused       = self.is_paused()

        log.debug("update_visibility: BatchCollection enabled (%s) running (%s); TakeOne running (%s); stop enabled (%s); paused (%s)",
            bc_enabled, bc_running, to_running, stop_enabled, paused)

        # pos 1
        self.bt_stop.setVisible(stop_enabled)
        if stop_enabled:
            self.bt_play .setVisible(False)
            self.bt_pause.setVisible(False)
        else:
            self.bt_play .setVisible(paused)
            self.bt_pause.setVisible(not paused)

        # pos 2
        util.set_enabled(self.bt_save, not (bc_running or to_running), tooltip=self.tooltips["save"])

        # pos 3
        if bc_enabled:
            self.bt_step.setVisible(False)
            self.bt_start_collection.setVisible(True)
            util.set_enabled(self.bt_start_collection, not (bc_running or to_running), tooltip=self.tooltips["start_collection"])
        else:
            self.bt_start_collection.setVisible(False)
            self.bt_step.setVisible(True)
            util.set_enabled(self.bt_step, paused and not (bc_running or to_running), tooltip=self.tooltips["step"])

        # pos 4
        util.set_enabled(self.bt_step_save, paused and not (bc_enabled or to_running), tooltip=self.tooltips["step_save"])

    ##
    # Called by KnowItAll.Feature, ScanAveragingFeature etc.
    #
    # It's debatable whether this method belongs to VCRControls, as it's actually
    # querying Multispec, but...at the moment we're trying to consolidate pause/play
    # state here, so let's go with it.
    #
    # @return whether the current spectrometer is paused or not
    def is_paused(self, spec=None):
        if spec is None:
            spec = self.ctl.multispec.current_spectrometer()
        if spec is None or spec.app_state is None:
            return False

        return spec.app_state.paused

    ##
    # Called by Controller's ctrl-P shortcut
    def toggle(self):
        if self.is_paused():
            self.play()
        else:
            self.pause()

    # ##########################################################################
    # Private methods
    # ##########################################################################

    def _set_paused(self, flag, all_=False, spec=None):
        """
        Pause the current spectrometer (or all, if specified).

        This used to set free_running_mode downstream when Paused, telling 
        Wasatch.PY to stop endlessly reading spectra at the current integration 
        time. The reason for that was probably to minimize latency when 
        externally triggered, or perhaps just to minimize latency when resuming 
        "Play". At the moment, this is not "playing" well with SiG, due to 
        internal automatic sensor sleep modes, so I'm leaving the WrapperWorker
        in free_running_mode at all times. Arguably we could treat Hamamatsu
        and SiG separately, but I'm not doing that right now.

        @private
        """
        log.debug(f"_set_paused: {flag}")
        self.paused = flag

        if all_:
            for spec in self.ctl.multispec.get_spectrometers():
                spec.reset_acquisition_timeout()
                spec.app_state.paused = flag
            return

        if spec is None:
            spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return
        
        spec.app_state.paused = flag
        spec.reset_acquisition_timeout()
