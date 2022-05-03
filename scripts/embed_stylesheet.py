#!/usr/bin/env python

import xml.etree.ElementTree as ET
import sys

def error(msg):
    print(msg)
    sys.exit(1)

# embed this stylesheet:
css_path = 'enlighten/assets/stylesheets/default/enlighten.css'

# into this Qt Designer file:
ui_path  = 'enlighten/assets/uic_qrc/enlighten_layout.ui'

# load CSS
css = None
try:
    with open(css_path, "r") as f:
        css = f.read()
except:
    error("Unable to read %s" % css_path)

# load .ui XML
try:
    tree = ET.parse(ui_path)
    root = tree.getroot()
except:
    error("Unable to parse XML from %s" % ui_path)

# find target element using XPath
#
# <ui version="4.0">
#  <widget class="QMainWindow" name="MainWindow">
#   <property name="styleSheet">
#    <string notr="true">
#     --> NEW CSS GOES HERE <--
element = root.find('./widget[@name="MainWindow"]/property[@name="styleSheet"]/string')
if element is None:
    error("Unable to find target node")

# overwrite element contents
element.text = css

# save updated .ui
try:
    tree.write(ui_path, encoding="UTF-8")
except:
    error("Unable to write %s" % ui_path)

print("Embedded %s" % css_path)
print("    into %s" % ui_path)
