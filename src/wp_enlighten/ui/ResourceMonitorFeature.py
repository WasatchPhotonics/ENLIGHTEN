import os
import gc
import psutil
import logging

from datetime import datetime

from wp_enlighten.EnlightenFeature import EnlightenFeature

log = logging.getLogger(__name__)

class ResourceMonitorFeature(EnlightenFeature):
    """
    This class was created a few years ago when we had a buried memory leak which
    only presented on Linux. Fear not, the leak was isolated and resolved (it was
    in wasatch.applog). However, we're keeping the class as it could be handy
    down the road.
    """

    UPDATE_RATE_SEC = 10

    def __init__(self, ctl):
        super().__init__(ctl)

        cfu = ctl.form.ui

        self.lb_growth       = cfu.label_process_growth_mb
        self.lb_size         = cfu.label_process_size_mb

        self.process_id = os.getpid()

        self.max_allowed_size = None
        self.initial_size = None
        self.last_memory_check_time = datetime.now()
        self.last_memory_check_result = True
        self.exit_code = 0
        self.is_parallels = None

    def copacetic(self):
        """ @returns True if we should keep running, False if shutdown advised. """
        now = datetime.now()

        if not self.check_runtime(now):
            self.exit_code = 2
            return False

        if not self.check_memory_usage(now):
            self.exit_code = 1
            return False

        return True

    def under_parallels(self):
        """
        @see https://ifnotnil.com/t/if-you-ever-need-to-know-if-your-running-on-parallels/1980
        """
        if self.is_parallels is None:
            self.is_parallels = False
            for proc in psutil.process_iter(['pid', 'name']):
                if "prl_cc.exe" in str(proc.info):
                    self.is_parallels = True
                    break
        return self.is_parallels

    def check_runtime(self, now):
        """ 
        @returns True (happy) if configured run time limit (in seconds) has not been exceeded.

        There is no caching of this value, since it's just a clock-check.
        """
        if self.ctl.run_sec > 0 and self.ctl.run_sec >= (datetime.now() - self.start_time).total_seconds():
            log.critical("exceeded configured runtime (%d sec)", self.ctl.run_sec)
            return False
        
        return True

    def check_memory_usage(self, now=None, label=None):
        """ 
        @returns True (happy) if memory GROWTH (not SIZE) is within configured limits.

        This value is only updated every UPDATE_RATE_SEC, regardless of how often
        the function is called.
        """
        if now is None:
            now = datetime.now()

        if label is None and (now - self.last_memory_check_time).total_seconds() < ResourceMonitorFeature.UPDATE_RATE_SEC:
            return self.last_memory_check_result

        gc.collect()
        self.last_memory_check_time = now
        size_in_bytes = psutil.Process(self.process_id).memory_info().rss

        # lazy-initialize this after one cycle, so things are settled
        if self.initial_size is None:

            log.info(f"initial_size {size_in_bytes} bytes")
            self.initial_size = size_in_bytes
            if self.ctl.max_memory_growth > 0:
                self.max_allowed_size = round(size_in_bytes * (1 + (0.01 * self.ctl.max_memory_growth)))
                log.info(f"max_allowed_size {self.max_allowed_size} bytes")

            self.last_memory_check_result = True

        else:

            formatted_size   = "{:,}MB".format(round(size_in_bytes                       / (1024 * 1024), 1))
            formatted_growth = "{:,}MB".format(round((size_in_bytes - self.initial_size) / (1024 * 1024), 1))
            self.lb_size  .setText(formatted_size)
            self.lb_growth.setText(formatted_growth)

            log.info(f"PID {self.process_id}, size_in_bytes {size_in_bytes}, growth {formatted_growth}, label {label}")

            # see if we've exceeded our maximum allowed memory size
            if self.max_allowed_size is not None and size_in_bytes > self.max_allowed_size:
                log.critical(f"exceeded max_allowed_size {formatted_size}")
                self.last_memory_check_result = False
            else:
                self.last_memory_check_result = True

        return self.last_memory_check_result
