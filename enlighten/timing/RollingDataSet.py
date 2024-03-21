import logging
import numpy as np
from datetime import timedelta
from datetime import datetime as dt
from collections import deque

log = logging.getLogger(__name__)

##
# Encapsulates a "moving window" dataset such as used for detector temperature,
# laser temperature etc.
#
# @todo We may need to track these by timestamp, so that things like StatusIndicators
#       can base an LED's color on "all_within(-55C, 1C, window=10sec)" (more-or-less).
#       We need to be able to discriminate between the graph window size and the 
#       analytical / status window size.
class RollingDataSet:
    def __init__(self, size_seconds):
        self.data = deque()
        self.window_limit = timedelta(minutes=0, seconds=size_seconds, milliseconds=0)

    def __str__(self):
        return "RollingDataSet(size %d, latest %s)" % (self.size, self.latest())

    def add(self, value):
        if value and type(value) is list:
            values = value
        else:
            values = [ value ]

        for value in values:
            self.data.append((dt.now(),value))

        self.filter_limit()

    def filter_limit(self):
        if len(self.data) == 0:
            return
        while (dt.now()-self.data[0][0]) > self.window_limit:
            self.data.popleft()

    def __len__(self):
        return len(self.data)

    def full(self):
        return len(self.data) == self.size

    def empty(self):
        return len(self.data) == 0

    def average(self):
        return float(np.average(self.get_values()))

    def get_values(self):
        return [y for x,y in self.data]

    def get_relative_to_now(self):
        """ Return graphable x, y arrays by elapsed sec """
        now = dt.now()
        x = []
        y = []
        for k, v in self.data:
            x.append((now-k).total_seconds())
            y.append(v)
        return x, y

    def all_within(self, value, delta, window_sec=None) -> bool:
        now = dt.now()
        for k, v in self.data:
            if abs(value - v) > delta:
                if window_sec is not None:
                    if (now - k).total_seconds() > window_sec:
                        continue
                log.debug("all_within: at least one of %d elements not within delta %.2f of value %.2f", len(self.data), delta, value)
                return False
        return True

    def one_within(self, value, delta, window_sec=None):
        now = dt.now()
        for k, v in self.data:
            if abs(value - v) <= delta:
                if window_sec is not None:
                    if (now - k).total_seconds() > window_sec:
                        continue
                log.debug("one_within: at least one of %d elements within delta %.2f of value %.2f", len(self.data), delta, value)
                return True

    def latest(self):
        if len(self.data) > 0:
            return self.data[-1]
        else:
            return None

    def get_csv_data(self, source_attr, spec_label):
        data_strings = [f"{source_attr},{spec_label},{x},{y}" for x,y in self.data]
        csv_str = '\n'.join(data_strings)
        return csv_str

    def clear(self):
        self.data = deque()

    def update_window(self, size_seconds):
        self.window_limit = timedelta(minutes=0,seconds=size_seconds,milliseconds=000)
