import logging

log = logging.getLogger(__name__)

##
# Encapsulates the collection of one averaged spectrum (optionally saved), either
# from one spectrometer or all.
#
class TakeOneFeature(object):

    def __init__(self,
            multispec,
            scan_averaging):
        self.multispec      = multispec
        self.scan_averaging = scan_averaging

        # will be populated post-instantiation
        self.vcr_controls = None    

        self.reset()

    def reset(self):
        log.debug("resetting")

        self.running = False        # currently executing a TakeOne
        self.spec = None            # whether to TakeOne from one spectrometer or all
        self.save = False           # whether to save at the end
        self.completion_count = 0   # how many spectrometers we're taking "from"
        self.completion_callback = None # anything special after completion

        # anyone waiting on the NEXT completion

        if self.vcr_controls is not None:
            self.vcr_controls.unregister_observer("stop", self.stop)
            self.vcr_controls.update_visibility()
        self.scan_averaging.reset()

    ##
    # @param spec   which spectrometer to use, or None for all
    # @param save   whether to save the measurement at completion
    # @param completion_callback if provided, fire when done
    def start(self, spec=None, save=False, completion_callback=None):
        log.debug("starting")

        self.spec = spec
        self.save = save
        self.running = True
        self.completion_count = 0
        self.completion_callback = completion_callback

        self.vcr_controls.register_observer("stop", self.stop)
        self.pause(False)

        if self.spec is None:
            self.multispec.change_device_setting("take_one", True)
        else:
            self.spec.change_device_setting("take_one", True)

    def stop(self):
        log.debug("stopping")

        if self.running:
            if self.spec is None:
                self.multispec.change_device_setting("cancel_take_one")
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

        # did we get an averaged reading (completing a single TakeOne within a spectrometer?)
        reading = processed_reading.reading
        if not reading.averaged:
            return
        self.completion_count += 1

        # does this complete the overall TakeOne operation?
        if self.check_complete():
            self.complete()

    def check_complete(self):
        if self.spec is None:
            return self.completion_count >= self.multispec.count()
        else:
            return self.completion_count >= 1

    def complete(self):
        self.pause(True)
        if self.save:
            self.vcr_controls.save()

        if self.completion_callback:
            self.completion_callback()

        self.reset()

    def pause(self, flag):
        if self.spec is None:
            self.multispec.set_app_state("paused", flag)
        else:
            self.spec.app_state.paused = flag
            
