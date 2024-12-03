import logging
from wasatch.TakeOneRequest import TakeOneRequest

log = logging.getLogger(__name__)

##
# Encapsulates the collection of one averaged spectrum (optionally saved), either
# from one spectrometer or all.
#
class TakeOneFeature:

    def __init__(self, ctl):
        self.ctl = ctl

        self.reset()

        self.observers = {}

    def reset(self):
        log.debug("resetting")

        self.running = False            # currently executing a TakeOne
        self.spec = None                # whether to TakeOne from one spectrometer or all
        self.save = False               # whether to save at the end
        self.completion_count = 0       # how many spectrometers we're taking "from"
        self.completion_callback = None # anything special after completion
        self.stop_callback = None       # in case subscriber needs to clean-up after a "Stop"

        # anyone waiting on the NEXT completion

        if self.ctl.vcr_controls:
            self.ctl.vcr_controls.unregister_observer("stop", self.stop)
            self.ctl.vcr_controls.update_visibility()
        self.ctl.scan_averaging.reset()

    def register_observer(self, event, callback):
        if event not in self.observers:
            self.observers[event] = set()
        self.observers[event].add(callback)

    ##
    # @param spec   which spectrometer to use, or None for all
    # @param save   whether to save the measurement at completion
    # @param completion_callback if provided, fire when done
    # @param template if provided, use as the TakeOneRequest template
    def start(self, spec=None, save=False, completion_callback=None, stop_callback=None, template=None):
        log.debug(f"starting (spec {spec}, save {save}, completion_callback {completion_callback}, template {template})")

        self.spec = spec
        self.save = save
        self.running = True
        self.completion_count = 0
        self.completion_callback = completion_callback
        self.stop_callback = stop_callback

        log.debug("registering VCRControls.stop -> self.stop")
        self.ctl.vcr_controls.register_observer("stop", self.stop)

        # note that we trigger callbacks before actually unpausing and sending 
        # the take_one, so subscribers can prepare themselves to "catch" / 
        # process the upcoming measurement
        if "start" in self.observers:
            for callback in self.observers["start"]:
                try:
                    callback()
                except:
                    log.critical("start: caught exception on observer callback {callback}", exc_info=1)

        take_one_request = TakeOneRequest(
            scans_to_average=self.ctl.scan_averaging.get_scans_to_average(), 
            template=template)

        if self.spec is None:
            self.ctl.multispec.set_app_state("take_one_request", take_one_request)
            self.ctl.multispec.change_device_setting("take_one_request", take_one_request)
        else:
            self.spec.app_state.take_one_request = take_one_request
            spec.change_device_setting("take_one_request", take_one_request)

        log.debug(f"done starting")

    def stop(self):
        log.debug("stopping")

        if self.running:
            if self.spec is None:
                self.ctl.multispec.change_device_setting("cancel_take_one")
                for spec in self.ctl.multispec.get_spectrometers():
                    spec.app_state.take_one_request = None
            else:
                self.spec.change_device_setting("cancel_take_one")
                self.spec.app_state.take_one_request = None

            self.pause(True)
        
        if self.stop_callback:
            log.debug(f"stop: notifying {self.stop_callback}")
            try:
                self.stop_callback()
            except:
                log.critical("stop: caught exception on stop callback {self.stop_callback}", exc_info=1)

        self.reset()

    ##
    # Accept a newly ProcessedReading from the Controller.  If the measurement is 
    # fully averaged, complete the TakeOne and optionally save.
    def process(self, processed_reading):
        if not self.running:
            log.debug("process: not running")
            return

        if processed_reading is None or processed_reading.reading is None:
            log.debug("process: no Reading")
            return

        log.debug("process: start")

        # did we get an averaged reading (completing a single TakeOne within a spectrometer?)
        reading = processed_reading.reading
        if not reading.averaged:
            log.debug("process: insufficiently averaged")
            return
        self.completion_count += 1

        # does this complete the overall TakeOne operation?
        log.debug("process: checking for completion")
        if self.check_complete():
            log.debug("process: calling complete")
            self.complete()
        else:
            log.debug("process: not yet complete")

    def check_complete(self):
        """ 
        TakeOne events should yield a response from every connected 
        spectrometer...see whether they've all called in. 
        """
        if self.spec is None:
            return self.completion_count >= self.ctl.multispec.count()
        else:
            return self.completion_count >= 1

    def complete(self):
        log.debug("complete: starting")
        self.pause(True)
        if self.save:
            log.debug("complete: saving")
            self.ctl.vcr_controls.save()

        # If you're wondering what the difference is between 
        # self.completion_callback and self.observers["complete"], well I guess 
        # I am too. The fundamental difference is that self.completion_callback 
        # gets cleared to None at the end of a TakeOneRequest (successful or 
        # otherwise), so that's essentially a one-shot callback hook. In contrast,
        # observers are persistent, and will be notified at the end of EVERY
        # TakeOneRequest (regardless of who generated it).
        #
        # We should probably enrich this pipeline by passing the TakeOneRequest 
        # (with request_id) to the callback function, so they can know (if they
        # care) "which" TakeOneRequest just completed (including perhaps "what 
        # kind" of request, requested by whom, etc).

        if self.completion_callback:
            log.debug(f"complete: notifying {self.completion_callback}")
            try:
                self.completion_callback()
            except:
                log.critical("complete: caught exception on completion callback {self.completion_callback}", exc_info=1)

        log.debug("complete: resetting")
        self.reset()

        if "complete" in self.observers:
            for callback in self.observers["complete"]:
                try:
                    callback()
                except:
                    log.critical("complete: caught exception on observer callback {callback}", exc_info=1)

        log.debug("complete: done")

    def pause(self, flag):
        if self.spec is None:
            self.ctl.multispec.set_app_state("paused", flag)
        else:
            self.spec.app_state.paused = flag
