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

        self.running = False        # currently executing a TakeOne
        self.spec = None            # whether to TakeOne from one spectrometer or all
        self.save = False           # whether to save at the end
        self.completion_count = 0   # how many spectrometers we're taking "from"
        self.completion_callback = None # anything special after completion

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
    def start(self, spec=None, save=False, completion_callback=None, template=None):
        log.debug(f"starting (spec {spec}, save {save}, completion_callback {completion_callback}, template {template})")

        self.spec = spec
        self.save = save
        self.running = True
        self.completion_count = 0
        self.completion_callback = completion_callback

        log.debug("registering VCRControls.stop -> self.stop")
        self.ctl.vcr_controls.register_observer("stop", self.stop)

        # note that we trigger callbacks before actually unpausing and sending 
        # the take_one, so subscribers can prepare themselves to "catch" / 
        # process the upcoming measurement
        if "start" in self.observers:
            for callback in self.observers["start"]:
                callback()

        avg = self.ctl.scan_averaging.get_scans_to_average()

        if self.ctl.auto_raman.enabled:
            take_one_request = self.ctl.auto_raman.generate_take_one_request(template=template)
        else:
            log.debug(f"start: avg {avg}")
            take_one_request = TakeOneRequest(scans_to_average=avg, template=template)

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
            else:
                self.spec.change_device_setting("cancel_take_one")
            self.pause(True)
        
        self.reset()

    ##
    # Accept a newly ProcessedReading from the Controller.  If the measurement is 
    # fully averaged, complete the TakeOne and optionally save.
    def process(self, processed_reading):
        if not self.running or \
                processed_reading is None or \
                processed_reading.reading is None:
            return

        log.debug("process: start")

        # did we get an averaged reading (completing a single TakeOne within a spectrometer?)
        reading = processed_reading.reading
        if reading.averaged_count < 1:
            return
        self.completion_count += 1

        # does this complete the overall TakeOne operation?
        log.debug("process: checking for completion")
        if self.check_complete():
            log.debug("process: calling complete")
            self.complete()

    def check_complete(self):
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

        if self.completion_callback:
            log.debug(f"complete: notifying {self.completion_callback}")
            self.completion_callback()

        log.debug("complete: resetting")
        self.reset()

        if "complete" in self.observers:
            for callback in self.observers["complete"]:
                callback()

        log.debug("complete: done")

    def pause(self, flag):
        if self.spec is None:
            self.ctl.multispec.set_app_state("paused", flag)
        else:
            self.spec.app_state.paused = flag
            
