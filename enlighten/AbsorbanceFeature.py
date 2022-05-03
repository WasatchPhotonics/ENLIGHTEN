import logging
import math

log = logging.getLogger(__name__)

##
# Thinking this doesn't need VignetteROI, because Transmission already does it.
class AbsorbanceFeature:

    ## above this it's bad data, because our spectrometers aren't this good
    MAX_AU = 6.0

    def __init__(self,
            marquee,
            transmission):

        self.marquee        = marquee                
        self.transmission   = transmission

    ## 
    # @returns True if successfully updated ProcessedReading
    # @todo update with numpy?
    def process(self, processed_reading, settings):
        pr = processed_reading

        if not self.transmission.process(pr, settings):
            log.error("can't compute absorbance w/o transmission")
            return False

        saturated = False
        absorbance = []
        trans = pr.get_processed()
        log.debug("trans = %s", trans[0:10])
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

        log.debug("absorbance = %s", absorbance[0:10])
        pr.set_processed(absorbance)

        if saturated:
            self.marquee.error("absorbance out-of-range")
            return False # (even though we did update array for graphing)

        return True
