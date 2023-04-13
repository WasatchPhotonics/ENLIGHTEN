import logging
import math

log = logging.getLogger(__name__)

class AbsorbanceFeature:
    """
    Computes absorbance using Beer's Law.

    Note that any required vignetting is performed within TransmissionFeature.

    @see [Beer-Lambert Law](https://en.wikipedia.org/wiki/Beer%E2%80%93Lambert_law)
    """

    ## above this it's likely bad data, based on current model performance 
    MAX_AU = 6.0    

    def __init__(self,
            marquee,
            transmission):

        self.marquee        = marquee                
        self.transmission   = transmission

    def process(self, processed_reading, settings, app_state) -> bool:
        """
        Computes absorbance from the current processed spectrum,
        then stores it back into 'processed.'

        @returns False if transmission can't be computed, or value exceeds MAX_AU
        @todo optimize with Numpy
        """
        pr = processed_reading

        if not self.transmission.process(pr, settings, app_state):
            log.error("can't compute absorbance w/o transmission")
            return False

        saturated = False
        absorbance = []
        trans = pr.get_processed()
        for t_perc in trans:
            au = 0
            t = t_perc / 100.0
            if t != 0:
                if t >= 0:
                    try:
                        au = -1.0 * math.log10(t)
                    except:
                        pass
                else:
                    au = AbsorbanceFeature.MAX_AU
                    saturated = True
            absorbance.append(au)

        pr.set_processed(absorbance)

        if saturated:
            self.marquee.error("absorbance out-of-range")
            return False # (even though we did update array for graphing)

        return True
