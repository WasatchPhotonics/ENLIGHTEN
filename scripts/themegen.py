
### CONFIGURABLE ###

# this is a list of themes to generate
names = ["orange", "purple", "darkblue", "teal", "yellow", "pink", "blue"]

# this list corresponds to the names, it specifies the colors
colors = ["#e38914", "#9f1fd1", "#0a4ff0", "#03c2fc", "#fcba03", "#eb17bd", "#114ad1"]

# no need to use a dark tone when creating a dark theme it will be darkened

### BEGIN SOURCE ###

import shutil
import os
import colorsys

def hsv_to_hsl(hsv):
    """
    python hsv is given by the scale
        hue [0, 1), 
        sat [0, 1],
        val [0, 255]
    
    whereas css hsl is given by the scale 
        hue [0,360), 
        sat [0, 100],
        lum [0, 100]
    """
    h,s,v = hsv

    l = v - v*s/2
    if l in [0, 1]:
        s = 0
    else:
        s = (v-l)/min(l, 1-l)

    h *= 360
    s *= 100
    l *= 100

    return (h, s, l)

def get_hex(line):
    """
    given a line that starts with a hex color
    return the color and the rest of the line
    """
    i = 0

    # values part of color hex
    hexv = "0123456789abcdefABCDEF"

    # skip the '#'
    i += 1

    # will be populated with the color hex values (excluding the '#')
    srccolor = ""

    # skip three values (for short color code)
    for _ in range(3):
        srccolor += line[i]
        i += 1

    # skip up to three more (for long color code)
    if i < len(line) and line[i] in hexv:
        for _ in range(3):
            srccolor += line[i]
            i += 1

    # convert to long color code
    if len(srccolor) == 3:
        srccolor = srccolor[0]+srccolor[0]+srccolor[1]+srccolor[1]+srccolor[2]+srccolor[2]

    not_a_color = False
    for c in srccolor:
        if not c in hexv:
            not_a_color = True

    if not_a_color:
        return False

    p1 = int(srccolor[0:2], 16)/255
    p2 = int(srccolor[2:4], 16)/255
    p3 = int(srccolor[4:6], 16)/255

    return hsv_to_hsl(colorsys.rgb_to_hsv(p1, p2, p3)), line[i:]

def get_hsl(line):
    i = 0

    # skip "hsl("
    i += 4

    p1 = ""
    while line[i] != ",":
        p1 += line[i]
        i += 1

    # skip ','
    i += 1

    p2 = ""
    while line[i] != ",":
        p2 += line[i]
        i += 1

    # skip ','
    i += 1

    p3 = ""
    while line[i] != ")":
        p3 += line[i]
        i += 1

    # skip ")"
    i += 1

    # filter parameters
    p1 = p1.replace("%", "")
    p1 = int(p1)
    p2 = p2.replace("%", "")
    p2 = int(p2)
    p3 = p3.replace("%", "")
    p3 = int(p3)

    return (p1, p2, p3), line[i:]

def get_rgba(line):
    i = 0

    # skip "rgba("
    i += 5

    p1 = ""
    while line[i] != ",":
        p1 += line[i]
        i += 1

    p2 = ""
    while line[i] != ",":
        p2 += line[i]
        i += 1

    p3 = ""
    while line[i] != ")":
        p3 += line[i]
        i += 1

    # skip ")"
    i += 1

    p1 = int(p1)/255
    p2 = int(p2)/255
    p3 = int(p3)/255

    return hsv_to_hsl(colorsys.rgb_to_hsv(p1, p2, p3)), line[i:]

def process_color(line, target_hsl):
    """
    given the string line which may contain a color literal, such as #FFFFFF,
    replace the first occurence with the color transformed towards the target hue
    """

    out = ""

    # copy characters to out until a '#' is reached.
    i = 0
    while i < len(line):
        col = None

        if line[i] == '#' and get_hex(line[i:]):
            col, line = get_hex(line[i:])
            i = 0

        if line[i:i+4] == 'hsl(':
            col, line = get_hsl(line[i:])
            i = 0

        # not used for any noticable colors
        #if line[i:i+5] == 'rgba(':
        #    col, line = get_rgba(line[i:])
        #    i = 0

        if col:
            # col is given as an hsl integer tuple
            if col[2] > 90:
                # avoid darkening text for darkmodes
                out += f"hsl({target_hsl[0]}, {target_hsl[1]}%, {col[2]}%)"
            else:
                out += f"hsl({target_hsl[0]}, {target_hsl[1]}%, {(target_hsl[2]/100)*col[2]}%)"
        out += line[i]
        i += 1

    return out

def make_theme(name, color):
    target_hsl = get_hex(color)[0]

    # we use sourcedir as a reference, shades of gray will be converted to 
    # shades of the target color
    if name.startswith("dark"):
        sourcedir = "../enlighten/assets/stylesheets/dark"
    else:
        sourcedir = "../enlighten/assets/stylesheets/light"

    # first thing to do is create the folder for the new theme
    themesdir = "../enlighten/assets/stylesheets"
    newthemedir = themesdir + os.sep + name
    if not os.path.exists(newthemedir):
        shutil.copytree(sourcedir, newthemedir)
    else:
        print("Skipping already generated theme %s." % name)
        return

    # process enlighten.css line-by-line
    enlighten_css = newthemedir + os.sep + "enlighten.css"
    with open(enlighten_css, "rt") as e1:
        with open(enlighten_css+".tmp", "wt") as e2:
            line = e1.readline()
            while line:
                line = process_color(line, target_hsl)
                e2.write(line + "\n")
                line = e1.readline()

    # move enlighten.css.tmp into place
    shutil.move(enlighten_css+".tmp", enlighten_css)

if __name__ == "__main__":
    
    assert len(names) == len(colors)

    for i in range(len(names)):
        make_theme(names[i], colors[i])
