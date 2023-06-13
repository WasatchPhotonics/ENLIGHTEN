from PySide2 import QtCore, QtGui

import datetime
import logging

from enlighten import util
from enlighten.ScrollStealFilter import ScrollStealFilter

log = logging.getLogger(__name__)

class BatchCollection(object):
    """
    This class encapsulates batch collection, which is the automated collection
    of a series of 'measurement_count' Step-And-Save events at a period of
    'measurement_period_ms', captured to disk using the configured SaveOptions.
    
    This sequence is normally triggered when the VCRControls' "Start Collection"
    button is clicked, and is implemented as a timed series of clicks to the
    VCRControls' "Step and Save" button.
    
    It is assumed that the scope will be paused at the beginning of a Batch
    Collection, and left on pause at the end.
    
    @par History
    
    Earlier implementations of BatchCollection left the spectrometer in free-
    running mode, and simply timed a sequence of "Save" events running in
    parallel to the ongoing stream of spectra continually rendered to the scope.
    
    As a result, the beginning of ACQUISITIONS were not synchronized to the
    beginning of each batch "step", and the "save event" was not specifically
    tied to the END of an acquisition started within the step.
    
    There were many things wrong with this approach, which are partially remedied
    by the new VCRControl's encapsulated "Step and Save" functionality.

    Note that there is still a question of synchronization between when the
    software requests a spectrum (sends ACQUIRE to the microcontroller and
    FPGA), and when the commanded integration actually begins, due to the
    "free-running" modes internally implemented within the firmware to keep
    the detector pixels clear and the sensor in a ready state.
    
    @par Process Mode
    
    In so-called "process mode" (intended for 24/7 process line control systems),
    batches themselves can be indefinitely iterated if 'batch_count' is zero.
    
    For process environments, the enlighten.ini Configuration setting
    "batch.start_on_connect = True" will initiate a continuous sequence of batches
    upon first spectrometer connection.
    
    To be clear, the word "process" here has nothing to do with OS kernels or
    threads, and relates to continuous-measurement industrial environments.
    
    @par Multispec
    
    The original concept was just to "collect X spectra in a row".  The evolving
    concept is more like "at a period of Y ms, virtually click the 'Step and Save'
    button a total of X times".
    
    Therefore, the number of spectrometers connected, and the individual
    integration times of those spectrometers, becomes irrelevant: the
    measurement_period_ms determines the interval between Step-and-Save events, and
    the and the number of events, rather than the number of spectra saved, is the
    count.
    
    @par Untimed Collections
    
    Some users don't wish to impose fixed timing, and just want to collect and save
    measurement_count spectra at the defined integration time.
    
    Although this is the "easier" challenge than "clock ticked" collections, it has
    its own complications.  For instance, if there are multiple spectrometers connected
    with different integration times in effect, and save_all_spectrometers is checked,
    the measurements will occur at different times, and the collections won't end together.
    
    Therefore, if measurement_period_ms is ZERO, this class will not run any internal
    timers, but will simply collect "measurement_count" spectra from each contributing
    spectrometer. In this use-case, Controller.attempt_reading() calls
    BatchCollection.consider_for_save(), circumventing the QTimers.
    
    @par Laser Control
    
    There are three use-cases:
    
    - MANUAL: means the user is manually controlling the laser (if there
      is one), so don't worry about it
    - BATCH: turn the laser on at the beginning of a batch (count 0),
      off at the end (measurement_count)
    - SPECTRUM: turn the laser on at the beginning of a measurement (each
      count), off after.
    
    The three modes are exposed in the configuration file as:
    
    \code
      laser_mode = manual | batch | spectrum
    \endcode
    
    If multiple spectrometers are connected, the laser commands (like acquisition
    triggers) are sent to each.
    
    Note that laser_spectrum timing is implemented within Wasatch.PY, so that the
    laser on/off and timing can occur within the "spectrometer thread" during a
    single acquisition event.  On the contrary, laser_batch is implemented here
    within BatchCollection.
    
    @par Dark
    
    It's clearly useful to be able to take a fresh dark at the start of each
    batch, and that has been implemented.
    
    However, another customer requested the ability to take a dark before each
    measurement within a batch (presumably with laser mode "Spectrum"), and that's
    a bit more tricky.  Right now "spectrum" laser mode is controlled inside
    Wasatch.PY, so for each measurement we'd have to disable the driver's laser mode,
    TakeOne dark, set the dark, then re-enable laser mode, and take the measurement.
    That's not much better than having manual control of the laser from this
    process, which is what we were trying to avoid, as it doesn't really allow
    fine-grained control over warmup time.
    
    For now, I'm following in the architectural path of pushing somewhat more
    functionality down into Wasatch.PY, and letting the driver provide BOTH the
    dark and the laser control around the Reading.  We won't be performing dark
    subtraction within the driver, but adding a .dark attribute to the Reading
    which ENLIGHTEN can register and store upon receipt.
    """
    def __init__(self,
            config,
            dark_feature,
            factory,
            laser_enable_callback,
            marquee,
            measurements,
            multispec,
            save_options,
            vcr_controls,

            cb_enabled,
            cb_dark_before_batch,
            cb_clear_before_batch,
            cb_export_after_batch,
            lb_explain,
            rb_laser_manual,
            rb_laser_spectrum,
            rb_laser_batch,
            spinbox_measurement_count,
            spinbox_measurement_period_ms,
            spinbox_batch_count,
            spinbox_batch_period_sec,
            spinbox_laser_warmup_ms,
            spinbox_collection_timeout):

        self.config                         = config
        self.dark_feature                   = dark_feature
        self.factory                        = factory
        self.laser_enable_callback          = laser_enable_callback
        self.marquee                        = marquee
        self.measurements                   = measurements
        self.multispec                      = multispec
        self.save_options                   = save_options
        self.vcr_controls                   = vcr_controls

        self.cb_enabled                     = cb_enabled
        self.cb_dark_before_batch           = cb_dark_before_batch
        self.cb_clear_before_batch          = cb_clear_before_batch
        self.cb_export_after_batch          = cb_export_after_batch
        self.lb_explain                     = lb_explain
        self.rb_laser_manual                = rb_laser_manual
        self.rb_laser_spectrum              = rb_laser_spectrum
        self.rb_laser_batch                 = rb_laser_batch
        self.spinbox_measurement_count      = spinbox_measurement_count
        self.spinbox_measurement_period_ms  = spinbox_measurement_period_ms
        self.spinbox_batch_count            = spinbox_batch_count
        self.spinbox_batch_period_sec       = spinbox_batch_period_sec
        self.spinbox_laser_warmup_ms        = spinbox_laser_warmup_ms
        self.spinbox_collection_timeout     = spinbox_collection_timeout

        # if true, save each measurement for each spectrometer (when timing is
        # disabled and we're just counting down measurements)
        self.save_count_by_device_id = {}

        # This is the timer we use to kick-off BatchCollection measurements with
        # an acquisition delay.  To be clear, this timer is used to tick
        # individual measurements WITHIN ONE BATCH.
        self.timer_measurement = QtCore.QTimer()
        self.timer_measurement.setSingleShot(True)
        self.timer_measurement.timeout.connect(self.tick_measurement)

        # this is a separate timer used to schedule multiple batches 
        self.timer_batch = QtCore.QTimer()
        self.timer_batch.setSingleShot(True)
        self.timer_batch.timeout.connect(self.start_batch)

        # initial settings
        self.current_measurement_count = 1
        self.current_batch_count = 1
        self.running = False  # enabled and started
        self.current_batch_start_time = None
        self.next_batch_start_time = None
        self.next_tick_start_time = None
        self.start_on_connect = False
        self.dark_before_batch = False
        self.laser_mode = "manual"
        self.clear_before_batch = False
        self.export_after_batch = False
        self.collection_start_time = None

        # set initial values before binding callbacks
        self.init_from_config()

        # binding
        self.cb_enabled                    .stateChanged .connect(self.update_from_widgets)
        self.cb_dark_before_batch          .stateChanged .connect(self.update_from_widgets)
        self.cb_clear_before_batch         .stateChanged .connect(self.update_from_widgets)
        self.cb_export_after_batch         .stateChanged .connect(self.update_from_widgets)
        self.rb_laser_manual               .toggled      .connect(self.update_from_widgets)
        self.rb_laser_spectrum             .toggled      .connect(self.update_from_widgets)
        self.rb_laser_batch                .toggled      .connect(self.update_from_widgets)
        self.spinbox_measurement_count     .valueChanged .connect(self.update_from_widgets)
        self.spinbox_measurement_period_ms .valueChanged .connect(self.update_from_widgets)
        self.spinbox_batch_count           .valueChanged .connect(self.update_from_widgets)
        self.spinbox_batch_period_sec      .valueChanged .connect(self.update_from_widgets)
        self.spinbox_laser_warmup_ms       .valueChanged .connect(self.update_from_widgets)
        self.spinbox_collection_timeout    .valueChanged .connect(self.update_from_widgets)

        # disable scroll stealing
        for key, item in self.__dict__.items():
            if key.startswith("cb_") or key.startswith("rb_") or key.startswith("spinbox_"):
                item.installEventFilter(ScrollStealFilter(item))

        # now perform one update
        self.update_from_widgets()

        # register with VCRButtons
        self.vcr_controls.batch_collection = self
        self.vcr_controls.register_observer("start_collection", self.start_collection)

    def init_from_config(self):
        log.debug("init_from_config")
        s = "batch"

        self.start_on_connect = self.config.get_bool(s, "start_on_connect")
        self.cb_enabled.setChecked(self.config.get_bool(s, "enabled"))
        self.cb_dark_before_batch.setChecked(self.config.get_bool(s, "dark_before_batch"))
        self.cb_clear_before_batch.setChecked(self.config.get_bool(s, "clear_before_batch"))
        self.cb_export_after_batch.setChecked(self.config.get_bool(s, "export_after_batch"))

        if self.config.has_option(s, "measurement_count"):
            measure_count = self.config.get_int(s, "measurement_count") 
            self.spinbox_measurement_count.setValue(measure_count)

        if self.config.has_option(s, "measurement_period_ms"):
            self.spinbox_measurement_period_ms.setValue(self.config.get_int(s, "measurement_period_ms"))

        if self.config.has_option(s, "batch_period_sec"):
            self.spinbox_batch_period_sec.setValue(self.config.get_int(s, "batch_period_sec"))

        if self.config.has_option(s, "laser_warmup_ms"):
            self.spinbox_laser_warmup_ms.setValue(self.config.get_int(s, "laser_warmup_ms"))

        if self.config.has_option(s, "batch_count"):
            self.spinbox_batch_count.setValue(self.config.get_int(s,"batch_count"))

        # defaults
        self.laser_mode = "manual"
        self.rb_laser_manual.setChecked(True)

        # laser mode
        if self.config.has_option(s, "laser_mode"):
            self.laser_mode = self.config.get(s, "laser_mode").lower()
            log.debug("init_from_config: laser_mode %s", self.laser_mode)
            if self.laser_mode == "batch":
                self.rb_laser_batch.setChecked(True)
            elif self.laser_mode == "spectrum":
                self.rb_laser_spectrum.setChecked(True)

    def update_from_widgets(self):

        # update state from widgets
        self.enabled               = self.cb_enabled.isChecked()
        self.dark_before_batch     = self.cb_dark_before_batch.isChecked()
        self.clear_before_batch    = self.cb_clear_before_batch.isChecked()
        self.export_after_batch    = self.cb_export_after_batch.isChecked()
        self.measurement_count     = self.spinbox_measurement_count.value()
        self.measurement_period_ms = self.spinbox_measurement_period_ms.value()
        self.batch_count           = self.spinbox_batch_count.value()
        self.batch_period_sec      = self.spinbox_batch_period_sec.value()
        self.laser_warmup_ms       = int(self.spinbox_laser_warmup_ms.value())

        if self.rb_laser_spectrum.isChecked():
            self.laser_mode = "spectrum"
        elif self.rb_laser_batch.isChecked():
            self.laser_mode = "batch"
        else: # elif self.rb_laser_manual.isChecked():
            self.laser_mode = "manual"

        # update config from state
        s = "batch"
        for name in [ "enabled", "dark_before_batch", "clear_before_batch", "export_after_batch",
                      "measurement_count", "measurement_period_ms", "batch_count", "batch_period_sec",
                      "laser_warmup_ms", "start_on_connect", "laser_mode" ]:
            self.config.set(s, name, getattr(self, name))

        # todo: have BatchCollection support observers and events, so VCRControls
        #       can register for an "enable" event
        self.vcr_controls.update_visibility()

        self.update_explanation()

    def update_explanation(self):
        """ Generates the ToolTip on "Explain This." """
        if not self.enabled:
            s = "Batch Collection is <b>Disabled</b>."
        else:
            s = "<p>Because Batch Collection is <b>Enabled</b>, a new ⏩ button will be added to the Scope Controls. "
            s += "Clicking this will start a new Batch Collection.</p>"

            if self.spinbox_collection_timeout.value() == 0:
                s += "<p>The following collection will not timeout and will complete based on the end of batch collection and measurement count.<\p>"
            else:
                s += f"<p>The following collection will timeout after {self.spinbox_collection_timeout.value()} seconds. After a complete measurement if the timeout is reached, the batch will complete and export then the collection will stop.</p>"

            if self.batch_count == 0:
                s += "<p>The following batch will run in an endless loop, because <b>Batch Count</b> is zero.</p>"
            else:
                s += f"<p>The following batch will be run {self.batch_count} times, per <b>Batch Count</b>. "
                s += f"Successive batches will be timed to <i>start</i> {self.batch_period_sec}sec apart (<b>Batch Period</b>).</p>"

            s += f"<p>Each batch will collect {self.measurement_count} measurements (<b>Measurement Count</b>). "
            s += "The measurements will all be acquired at the current integration time. "
            s += f"The measurements will be spaced to <i>start</i> {self.measurement_period_ms}ms apart (<b>Measurement Period</b>).</p>"

            if self.laser_mode == "manual":
                s += "<p>The laser will not be automatically turned on or off during the collection (<b>Laser Mode Manual</b>).</p>"
            else:
                s += f"<p>The laser will be automatically turned on at the beginning of each {self.laser_mode} (<b>Laser Mode</b>). "
                if self.dark_before_batch:
                    s += "Before turning the laser, a fresh dark will be taken. "
                s += f"After the laser is turned on, it will be allowed to stabilize for {self.laser_warmup_ms}ms (<b>Laser Warmup</b>). "
                s += f"The laser will be automatically turned off at the end of each {self.laser_mode}.</p>"

            if self.clear_before_batch:
                s += "<p>The save bar will be cleared at the <i>start</i> of each new batch.</p>"
            if self.export_after_batch:
                s += "<p>At the end of each batch, the save bar will be automatically exported.</p>"

        self.lb_explain.setToolTip(f"<html><body>{s}</body></html>")

    # ##########################################################################
    # Runtime Loop
    # ##########################################################################

    def start_collection(self):
        """ Someone clicked the "Start Collection" button in VCRButtons. """
        if not self.enabled:
            self.stop() # just to be safe
            return False

        self.vcr_controls.register_observer("stop", self.vcr_stop)
        #self.vcr_controls.register_observer("save", self.save_complete)
        self.collection_start_time = datetime.datetime.now()
        if self.spinbox_collection_timeout.value() != 0:
            self.collection_timeout = self.collection_start_time + datetime.timedelta(seconds=self.spinbox_collection_timeout.value())
        else:
            self.collection_timeout = None

        if not self.running:
            log.info("starting")

            # initialize driver-level laser auto_triggering and dark collection
            if self.laser_mode == "spectrum":
                log.debug("starting laser_mode '%s', so setting acquisition_laser options", self.laser_mode)
                self.multispec.change_device_setting("acquisition_laser_trigger_delay_ms", self.laser_warmup_ms)
                self.multispec.change_device_setting("acquisition_laser_trigger_enable", True)
                if self.dark_before_batch:
                    self.multispec.change_device_setting("acquisition_take_dark_enable", True)

            else:
                log.debug("starting laser_mode '%s', so disabling acquisition_laser options", self.laser_mode)
                self.multispec.change_device_setting("acquisition_laser_trigger_delay_ms", 0)
                self.multispec.change_device_setting("acquisition_laser_trigger_enable", False)
                self.multispec.change_device_setting("acquisition_take_dark_enable", False)

            self.running = True

        else:
            # restart in-process collection
            log.info("restarting")

        self.current_batch_count = 0

        self.start_batch()
        return True

    def start_batch(self):
        label = util.pluralize(self.measurement_count, "measurement", "measurements")
        self.marquee.info("Starting batch %d/%d (%d %s)" % (
            self.current_batch_count + 1, self.batch_count, self.measurement_count, label), persist=True)

        if self.clear_before_batch:
            self.measurements.erase_all()

        self.current_measurement_count = 0
        self.current_batch_start_time = datetime.datetime.now()
        self.save_count_by_device_id = {}
        self.first_tick = True

        # we should only be ABLE to start a batch if we're paused, but...just to be sure:
        self.vcr_controls.pause(all=self.save_options.save_all_spectrometers())

        # Compute "next start time" now, at the beginning of the batch,
        # because it's defined as a PERIOD (start-to-start), not a DELAY.
        # Do this regardless of whether we think there will be more batches or not.
        self.next_batch_start_time = datetime.datetime.now() + datetime.timedelta(seconds=self.batch_period_sec)
        log.debug("next batch would start at %s", self.next_batch_start_time)

        if self.dark_before_batch and self.laser_mode == "batch":
            self.marquee.info("generating pre-laser batch dark", persist=True)
            self.vcr_controls.step(completion_callback=self.start_batch_post_dark)
        else:
            self.start_batch_post_dark()

    def start_batch_post_dark(self):
        if self.dark_before_batch:
            log.debug("saving the new dark before enabling laser")
            self.dark_feature.store()

        # default to processing first tick immediately
        sleep_ms = 0

        # if we're not in manual laser mode, initialize laser for the batch
        if self.laser_mode == "batch":
            self.laser_enable_callback(True, all=self.save_options.save_all_spectrometers())
            sleep_ms = self.laser_warmup_ms
            if sleep_ms > 0:
                self.marquee.info("warming up laser", persist=True)
        elif self.laser_mode == "spectrum":
            # This is debatable, but seems safest.  Since we're going to be
            # turning the laser on and off for each individual acquisition,
            # it should probably default to "off" before the first acquisition.
            #
            # To be doubly safe, we're turning off ALL lasers, regardless of
            # whether we're in "save_all" or not.
            self.laser_enable_callback(False, all=True)

        log.debug("scheduling first tick in %d ms", sleep_ms)
        self.timer_measurement.start(sleep_ms)

    ##
    # Tempting to render SaveOptions.label_template in here...not sure how that 
    # would fly with multiple spectrometers.  More to the point, label_template
    # is rendered on individual Measurement objects, and the BatchCollection
    # class, odd as it seems, doesn't actually have a reference to any of the 
    # Measurement objects it causes to be collected.  They're all automated by
    # raising step_save events in VCRControls, which doesn't itself hold any
    # references so can't even send one back through the completion event.
    # I don't think we can easily do this right now, perhaps for good reason.
    def generate_export_filename(self, now):
        filename = "Batch"

        prefix = self.save_options.prefix()
        if prefix:
            filename += "-" + prefix
        filename += "-" + now.strftime("%Y%m%d-%H%M%S")

        suffix = self.save_options.suffix()
        if suffix:
            filename += "-" + suffix

        if self.batch_count > 1:
            filename += f"-{self.current_batch_count}-of-{self.batch_count}"
        filename = util.normalize_filename(filename)
        log.debug(f"export filename = {filename}")
        return filename

    def complete_batch(self):
        now = datetime.datetime.now()
        self.current_batch_count += 1
        log.debug("completed batch %d/%d (laser_mode %s)", self.current_batch_count, self.batch_count, self.laser_mode)

        self.timer_measurement.stop()

        if self.laser_mode == "batch":
            log.debug("disabling laser")
            self.laser_enable_callback(False, all=True)

        self.marquee.info("batch of %d measurements complete" % self.measurement_count, persist=True)
        self.current_batch_start_time = None

        # batches end in paused state
        save_all = self.save_options.save_all_spectrometers()
        self.vcr_controls.pause(all=save_all)

        # export if requested
        if self.export_after_batch:
            filename = self.generate_export_filename(now)
            self.measurements.export_session(filename=filename)

        # If the batch ends after the timeout then stop
        if self.collection_timeout is not None and now > self.collection_timeout:
            log.info("timeout is reached, ending collection process")
            self.stop()
            return

        # stop if we're doing a fixed number, and we met that number
        if self.batch_count > 0 and self.batch_count <= self.current_batch_count:
            self.stop()
            return

        # either batch_count is negative (loop forever), or we're not there yet,
        # so keep going

        # compute HOW LONG until the next batch should start (the "when" was 
        # determined in start_batch)
        if now >= self.next_batch_start_time:
            log.info("starting next batch immediately")
            self.start_batch()
        else:
            sleep_ms = (self.next_batch_start_time - now).total_seconds() * 1000
            log.info("starting next batch in %d ms", sleep_ms)
            self.marquee.info("next batch @ %s" % self.next_batch_start_time.strftime('%H:%M:%S'), persist=True)
            self.timer_batch.start(sleep_ms)
            
    def vcr_stop(self):
        self.factory.label_suffix = None
        self.stop()

    def stop(self):
        log.debug("stopping")
        self.running = False
        self.timer_measurement.stop()
        self.timer_batch.stop()
        self.vcr_controls.unregister_observer("save", self.save_complete)
        self.vcr_controls.unregister_observer("stop", self.vcr_stop)
        self.current_batch_start_time = None

        self.multispec.change_device_setting("acquisition_laser_trigger_delay_ms", 0)
        self.multispec.change_device_setting("acquisition_laser_trigger_enable", False)
        self.multispec.change_device_setting("acquisition_take_dark_enable", False)

    def tick_measurement(self):
        """ At each tick of the Batch timer, initiate a Step And Save event. """
        if not self.running:
            return

        # don't take a measurement and end the batch if timeout occurred
        if self.collection_timeout is not None and datetime.datetime.now() > self.collection_timeout:
            log.info(f"collection timeout reach, not performing next measurement and completing batch. measurement count is {self.measurement_count}")
            self.complete_batch()
            return

        # if user unchecked "enabled", stop
        if not self.enabled:
            self.stop()
            return

        self.factory.label_suffix = "B%d %d-of-%d" % (self.current_batch_count + 1, self.current_measurement_count + 1, self.measurement_count)

        # compute (but don't yet schedule) next start-time now, so that the
        # measurement period can be "start-to-start"
        self.next_tick_start_time = datetime.datetime.now() + datetime.timedelta(milliseconds=self.measurement_period_ms)

        # when this event completes, VCRControls will call our save_complete method
        self.vcr_controls.step_save(self.save_complete)

    def save_complete(self):
        """ A VCRControls "step_save" event has completed. """
        if not self.running:
            return

        # if user unchecked "enabled", stop
        if not self.enabled:
            self.stop()
            return

        self.current_measurement_count += 1
        log.info("measurement %d/%d (batch %d/%d)",
            self.current_measurement_count, self.measurement_count,
            self.current_batch_count, self.batch_count)

        if self.current_measurement_count >= self.measurement_count:
            self.complete_batch()
            return

        self.marquee.info(
            "saved %s of %s (batch %d)" % (self.current_measurement_count, self.measurement_count, self.current_batch_count + 1),
            persist=True)

        if self.next_tick_start_time is None:
            return

        # schedule the next measurement event
        now = datetime.datetime.now()
        sleep_ms = 0
        if now < self.next_tick_start_time:
            sleep_ms = max(0, (self.next_tick_start_time - now).total_seconds() * 1000)
        self.timer_measurement.start(sleep_ms)
