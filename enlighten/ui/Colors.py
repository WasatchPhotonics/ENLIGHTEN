import logging
import colorsys

from enlighten.data.ColorNames import ColorNames

log = logging.getLogger(__name__)

class Colors(object):
    """
    Encapsulate access to stateful / dynamic color information.
    
    The static ColorNames lookups have been extracted to a different class, in part 
    so Configuration can "have" a ColorNames without needing a full Colors object
    (which currently itself requires a Configuration).
    """
    def clear(self):
        self.config = None
        self.color_names = None

    def __init__(self, config):
        self.config = config

        # when generating "random" colors for things like saved thumbnail traces
        # and extra spectrometers of the same model, this is the last integral
        # value to be assigned
        self.rand_index = 0

        # this instance isn't used by local functions, but is made available to
        # anyone with a reference to this class
        self.color_names = ColorNames()

    def get_by_name(self, name):
        return self.color_names.get(name)

    def get_next_random(self) -> str:
        """
        Return the next random hue in sequence.
        
        There are various things we could do to allow lower-numbered random colors
        to be re-used after "releasing" (maintain lookup of hex color to originating
        index, etc), but none seem worthwhile at present.
        """
        self.rand_index += 1
        return self.int_color(self.rand_index)
        
    def int_color(self, index, hues=9, values=1, maxValue=255, minValue=150, maxHue=360, minHue=0, saturation=255, alpha=255) -> str:
        """
        This algorithm was borrowed from pyqtgraph.intColor().
        
        @see http://www.pyqtgraph.org/documentation/functions.html#pyqtgraph.intColor
        
        Originally we just used that function directly, but as it returns a 
        PySide.QtGui.QColor object, it couldn't be easily hashed / combined with
        simple hex RGB codes.
        """
        hues = int(hues)
        values = int(values)
        ind = int(index) % (hues * values)
        indh = ind % hues
        indv = ind // hues
        if values > 1:
            value = minValue + indv * ((maxValue-minValue) / (values-1))
        else:
            value = maxValue
        hue = minHue + (indh * (maxHue-minHue)) / hues

        # MZ added 
        hsv = (float(hue/255.0), float(saturation/255.0), float(value/255.0)) 
        rgb = colorsys.hsv_to_rgb(*hsv) 
        hexcolor = "#" + self.to_hex(rgb[0]) + self.to_hex(rgb[1]) + self.to_hex(rgb[2])
        # log.debug("int_color: index %d -> hsv(%s) -> rgb(%s) -> hex (%s)", index, hsv, rgb, hexcolor)
        return hexcolor

    def to_hex(self, x) -> str:
        """
        Converts 0.5 -> "7f"
        @param x should be a float in the range (0, 1)
        """
        scalar = min(1, max(0, x)) # force to range (0, 1)
        n = int(255 * scalar) & 0xff
        return "%02x" % n

    def get_by_widget(self, name):
        """
        @returns None if not configured (most have defaults tho)
        """
        return self.config.get("graphs", "%s_pen_color" % name)
