import logging

from enlighten.EnlightenFeature import EnlightenFeature

log = logging.getLogger(__name__)

class UpdateCheckerFeature(EnlightenFeature):
    def __init__(self, ctl):
        super().__init__(ctl)
