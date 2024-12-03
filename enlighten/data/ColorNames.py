import logging
import re

log = logging.getLogger(__name__)

class ColorNames:
    """
    These are colors we can reference by name in .ini files or elsewhere.
    
    The static ColorNames lookups have been extracted out of Colors, in part so 
    Configuration can "have" a ColorNames without needing a full Colors object
    (which itself currently requires a Configuration).
    
    @note all names are lowercase (comparisons are case-insensitive)
    
    @see http://htmlcolorcodes.com/color-names/
    """
    def clear(self):
        self.names = None
        self.names_by_length = None

    def __init__(self):
        self.names = {
            'aliceblue':            '#f0f8ff',
            'antiquewhite':         '#faebd7',
            'aqua':                 '#00ffff',
            'aquamarine':           '#7fffd4',
            'azure':                '#f0ffff',
            'beige':                '#f5f5dc',
            'bisque':               '#ffe4c4',
            'black':                '#000000',
            'blanchedalmond':       '#ffebcd',
            'blue':                 '#0000ff',
            'blueviolet':           '#8a2be2',
            'brown':                '#a52a2a',
            'burlywood':            '#deb887',
            'cadetblue':            '#5f9ea0',
            'chartreuse':           '#7fff00',
            'chocolate':            '#d2691e',
            'coral':                '#ff7f50',
            'cornflowerblue':       '#6495ed',
            'cornsilk':             '#fff8dc',
            'crimson':              '#dc143c',
            'cyan':                 '#00ffff',
            'darkblue':             '#00008b',
            'darkcyan':             '#008b8b',
            'darkgoldenrod':        '#b8860b',
            'darkgray':             '#a9a9a9',
            'darkgreen':            '#006400',
            'darkkhaki':            '#bdb76b',
            'darkmagenta':          '#8b008b',
            'darkolivegreen':       '#556b2f',
            'darkorange':           '#ff8c00',
            'darkorchid':           '#9932cc',
            'darkred':              '#8b0000',
            'darksalmon':           '#e9967a',
            'darkseagreen':         '#8fbc8b',
            'darkslateblue':        '#483d8b',
            'darkslategray':        '#2f4f4f',
            'darkturquoise':        '#00ced1',
            'darkviolet':           '#9400d3',
            'deeppink':             '#ff1493',
            'deepskyblue':          '#00bfff',
            'dimgray':              '#696969',
            'dodgerblue':           '#1e90ff',
            'firebrick':            '#b22222',
            'floralwhite':          '#fffaf0',
            'forestgreen':          '#228b22',
            'fuchsia':              '#ff00ff',
            'gainsboro':            '#dcdcdc',
            'ghostwhite':           '#f8f8ff',
            'gold':                 '#ffd700',
            'goldenrod':            '#daa520',
            'gray':                 '#808080',
            'green':                '#008000',
            'greenyellow':          '#adff2f',
            'honeydew':             '#f0fff0',
            'hotpink':              '#ff69b4',
            'indianred':            '#cd5c5c',
            'indigo':               '#4b0082',
            'ivory':                '#fffff0',
            'khaki':                '#f0e68c',
            'lavender':             '#e6e6fa',
            'lavenderblush':        '#fff0f5',
            'lawngreen':            '#7cfc00',
            'lemonchiffon':         '#fffacd',
            'lightblue':            '#add8e6',
            'lightcoral':           '#f08080',
            'lightcyan':            '#e0ffff',
            'lightgoldenrodyellow': '#fafad2',
            'lightgray':            '#d3d3d3',
            'lightgreen':           '#90ee90',
            'lightpink':            '#ffb6c1',
            'lightsalmon':          '#ffa07a',
            'lightseagreen':        '#20b2aa',
            'lightskyblue':         '#87cefa',
            'lightslategray':       '#778899',
            'lightsteelblue':       '#b0c4de',
            'lightyellow':          '#ffffe0',
            'lime':                 '#00ff00',
            'limegreen':            '#32cd32',
            'linen':                '#faf0e6',
            'magenta':              '#ff00ff',
            'maroon':               '#800000',
            'mediumaquamarine':     '#66cdaa',
            'mediumblue':           '#0000cd',
            'mediumorchid':         '#ba55d3',
            'mediumpurple':         '#9370db',
            'mediumseagreen':       '#3cb371',
            'mediumslateblue':      '#7b68ee',
            'mediumspringgreen':    '#00fa9a',
            'mediumturquoise':      '#48d1cc',
            'mediumvioletred':      '#c71585',
            'midnightblue':         '#191970',
            'mintcream':            '#f5fffa',
            'mistyrose':            '#ffe4e1',
            'moccasin':             '#ffe4b5',
            'navajowhite':          '#ffdead',
            'navy':                 '#000080',
            'oldlace':              '#fdf5e6',
            'olive':                '#808000',
            'olivedrab':            '#6b8e23',
            'orange':               '#ffa500',
            'orangered':            '#ff4500',
            'orchid':               '#da70d6',
            'palegoldenrod':        '#eee8aa',
            'palegreen':            '#98fb98',
            'paleturquoise':        '#afeeee',
            'palevioletred':        '#db7093',
            'papayawhip':           '#ffefd5',
            'peachpuff':            '#ffdab9',
            'peru':                 '#cd853f',
            'pink':                 '#ffc0cb',
            'plum':                 '#dda0dd',
            'powderblue':           '#b0e0e6',
            'purple':               '#800080',
            'rebeccapurple':        '#663399',
            'red':                  '#ff0000',
            'rosybrown':            '#bc8f8f',
            'royalblue':            '#4169e1',
            'saddlebrown':          '#8b4513',
            'salmon':               '#fa8072',
            'sandybrown':           '#f4a460',
            'seagreen':             '#2e8b57',
            'seashell':             '#fff5ee',
            'sienna':               '#a0522d',
            'silver':               '#c0c0c0',
            'skyblue':              '#87ceeb',
            'slateblue':            '#6a5acd',
            'slategray':            '#708090',
            'snow':                 '#fffafa',
            'springgreen':          '#00ff7f',
            'steelblue':            '#4682b4',
            'tan':                  '#d2b48c',
            'teal':                 '#008080',
            'thistle':              '#d8bfd8',
            'tomato':               '#ff6347',
            'turquoise':            '#40e0d0',
            'violet':               '#ee82ee',
            'wheat':                '#f5deb3',
            'white':                '#ffffff',
            'whitesmoke':           '#f5f5f5',
            'yellow':               '#ffff00',
            'yellowgreen':          '#9acd32',

            # from Nathan
            'enlighten_lightblue':  '#6666ff',
            'enlighten_magenta':    '#ff33aa',
            'enlighten_high_gray':  '#e7e7e7',
            'enlighten_blue':       '#0000ff',
            'enlighten_red':        '#ff0000',
            'enlighten_green':      '#1fd11f', # semi light-green
            'enlighten_dark_red':   '#660000', 
            'enlighten_light_gray': '#a7a7a7',
            'enlighten_faded_gray': '#272727',
            'enlighten_medium_blue':'#0000ff',
            'enlighten_dark_blue':  '#000099',

            # from Cicely
            'enlighten_teal':       '#27c0a1', # the teal 'I' in ENLIGHTEN logo
            'enlighten_cyan':       '#2994d3', # the cyan 'L' in ENLIGHTEN logo
            'enlighten_default':    '#27c0a1', # enlighten_teal (see Configuration)
            'enlighten_name_e1':    '#6758c5', # the 'E' in ENLIGHTEN (violet)
            'enlighten_name_n1':    '#4a5da9', # the 'N' in ENLIGHTEN (blue)
            'enlighten_name_l':     '#2994d3', # the 'L' in ENLIGHTEN (cyan)
            'enlighten_name_i':     '#27c0a1', # the 'I' in ENLIGHTEN (bluegreen)
            'enlighten_name_g':     '#60b34e', # the 'G' in ENLIGHTEN (green)
            'enlighten_name_h':     '#f7e842', # the 'H' in ENLIGHTEN (yellow)
            'enlighten_name_t':     '#f79a1c', # the 'T' in ENLIGHTEN (orange)
            'enlighten_name_e2':    '#f84f21', # the 'E' in ENLIGHTEN (orangered)
            'enlighten_name_n2':    '#cd242b', # the 'N' in ENLIGHTEN (red)

            'enlighten_benign':     '#007c3c', 
            'enlighten_hazard':     '#a60a0a',

            # These are the colors used in the ENLIGHTEN logo:
            #
            #          R    G    B
            #    E   103,  88, 197   violet
            #    N    74,  93, 169   blue
            #    L    41, 148, 211   enlighten_cyan
            #    I    39, 192, 161   enlighten_bluegreen
            #    G    96, 190,  78   green
            #    H   247, 232,  66   yellow
            #    T   247, 154,  28   orange
            #    E   248,  79,  33   orangered
            #    N   205,  36,  43   red
        }

        # maintain a list of names sorted "longest to shortest" so we can attempt
        # partial matches like "blue"
        self.names_by_length = list(self.names.keys())
        self.names_by_length.sort() 
        self.names_by_length.sort(key=len, reverse=True) 

    def has(self, name):
        try:
            return name.lower() in self.names
        except:
            return False

    def get(self, name):
        if isinstance(name, str) and re.match(r'^#([0-9a-f]{3}){1,2}$', name, re.IGNORECASE):
            return name

        try:
            s = name.lower()
            if s in self.names:
                return self.names[s]
        except:
            pass
        log.debug("color not found: %s", name)

    def search(self, label):
        try:
            for name in self.names_by_length:
                if re.search(name, label, re.IGNORECASE):
                    return self.names[name]
        except:
            pass
