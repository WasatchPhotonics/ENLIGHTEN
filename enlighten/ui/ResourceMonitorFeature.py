import os
import gc
import psutil
import logging
import datetime

log = logging.getLogger(__name__)

class ResourceMonitorFeature:

    UPDATE_RATE_SEC = 5

    def __init__(self, ctl):
        self.ctl = ctl
        cfu = ctl.form.ui

        self.lb_growth       = cfu.label_process_growth_mb
        self.lb_size         = cfu.label_process_size_mb

        self.process_id = os.getpid()

        self.max_allowed_size = None
        self.initial_size = None
        self.last_memory_check = datetime.datetime.now()
        self.exit_code = 0

    ## @returns True if we should keep running, False if shutdown advised
    def copacetic(self):
        now = datetime.datetime.now()

        if not self.check_runtime(now):
            self.exit_code = 2
            return False

        if not self.check_memory_usage(now):
            self.exit_code = 1
            return False

        return True

    ## @returns True if copacetic
    def check_runtime(self, now):
        if self.ctl.run_sec > 0 and self.ctl.run_sec >= (datetime.datetime.now() - self.start_time).total_seconds():
            log.critical("exceeded configured runtime (%d sec)", self.ctl.run_sec)
            return False
        
        return True

    ## only check memory usage every 5sec
    #  @returns True if copacetic
    def check_memory_usage(self, now):
        if (now - self.last_memory_check).total_seconds() < ResourceMonitorFeature.UPDATE_RATE_SEC:
            return True

        gc.collect()
        self.last_memory_check = now
        size_in_bytes = psutil.Process(self.process_id).memory_info().rss

        # lazy-initialize this after one cycle, so things are settled
        if self.initial_size is None:
            log.info("initial_size = %d bytes", size_in_bytes)
            self.initial_size = size_in_bytes
            if self.ctl.max_memory_growth > 0:
                self.max_allowed_size = round(size_in_bytes * (1 + (0.01 * self.ctl.max_memory_growth)))
                log.info("max_alloweds_size = %d bytes", self.max_allowed_size)
            return True

        formatted_size   = "{:,}MB".format(round(size_in_bytes                       / (1024 * 1024), 1))
        formatted_growth = "{:,}MB".format(round((size_in_bytes - self.initial_size) / (1024 * 1024), 1))
        self.lb_size  .setText(formatted_size)
        self.lb_growth.setText(formatted_growth)

        log.info("PID %d memory = %d bytes (%s growth)", self.process_id, size_in_bytes, formatted_growth)

        # see if we've exceeded our maximum allowed memory size
        if self.max_allowed_size is not None and size_in_bytes > self.max_allowed_size:
            log.critical("exceeded max_allowed_size (%s)", formatted_size)
            return False

        return True
