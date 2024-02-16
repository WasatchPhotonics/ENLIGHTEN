##
# These utils are in enlighten (rather than Wasatch.PY) because they truly only 
# relate to the GUI for instance, explicitly reference Qt widgets).  Anything
# "generic" should really be in wasatch.utils. 

import logging
import numpy as np
import json
import sys
import re
import os

from collections import namedtuple
from decimal import Decimal

log = logging.getLogger(__name__)

################################################################################
# String Helpers
################################################################################

## join list, tossing any nulls / empty strings
def join_valid(delim, tokens):
    s = ""
    for tok in tokens:
        if tok is not None and len(tok) > 0:
            if len(s) > 0:
                s += delim + tok
            else:
                s = tok
    return s

## This made Chris Paul happy
def pluralize_spectra(count):
    if count == 0:
        return "no spectra"
    elif count == 1:
        return "1 spectrum"
    else:
        return "%d spectra" % count

def pluralize(count, singular, plural):
    return singular if count == 1 else plural

## @return whether any elements of set 1 appear in set 2
#  @todo could memoize if this ever became performance-critical
#  @todo best option would be to maintain sets in lowercase
def sets_intersect(s1, s2, case_insensitive=False):
    if case_insensitive:
        for i in s1:
            il = i.lower()
            for j in s2:
                if il == j.lower():
                    return True
    else:
        for s in s1:
            if s in s2:
                return True
    return False

def clean_list(a):
    if a is None:
        return
    if isinstance(a, np.ndarray):
        return a.tolist()
    return a 

def printable(s: str) -> str:
    """ bang (!) through tilde (~) """
    clean = ""
    if s is not None:
        for c in s:
            clean += c if 32 < ord(c) < 127 else "."
    return clean

def determine_encoding(pathname: str) -> str: 
    try:
        with open(pathname, "r", encoding="utf-8") as infile:
            line = infile.readline()
            #log.debug(f"determine_encoding: line [{line}] ({pathname})")
            return "utf-8-sig" if u'\ufeff' in line else "utf-8"
    except:
        # if it's not utf-8 or utf-8-sig we'll just assume it's using Central and Eastern Europe encoding
        return "iso8859_2"

def unwrap(s):
    result = None
    for line in s.split("\n"):
        line = line.strip()
        if line == "":
            if result:
                result += "\n\n"
            else:
                continue
        else:
            if result:
                if not result.endswith("\n"):
                    result += " "
                result += line
            else:
                result = line
    return result

def undent(s):
    result = ""
    for line in s.split("\n"):
        line = line.strip()
        if line == "":
            if result:
                result += "\n"
            else:
                continue
        else:
            if result:
                result += "\n"
            result += line
    return result

################################################################################
# File Helpers
################################################################################

## @todo move to FileManager
def find_file(filename, dirs):
    for directory in dirs:
        pathname = os.path.join(directory, filename)
        if os.path.exists(pathname):
            return pathname

## create a directory tree, optionally requiring user expansion (~),
#  without throwing exceptions
#
# @todo move to FileManager
def safe_mkdirp(directory):
    if os.path.exists(directory):
        return
    try:
        expanded = os.path.expanduser(directory)
        log.debug("creating %s", expanded)
        os.makedirs(expanded)
    except Exception:
        log.critical("can't create %s", directory, exc_info=1)

## 
# Some filenames are auto-populated from the on-screen labels used on 
# thumbnails and graph traces.  However, those labels may include characters
# that aren't valid (or wise) in filenames, like colon, slash, and backslash,
# so normalize those out.
def normalize_filename(filename):
    return re.sub(r'[:/\\]', '_', filename)

################################################################################
# Qt Helpers
################################################################################

## @see https://stackoverflow.com/a/46915601/11615696
def normalize_history(x, hi=65535.0):
    return (x - x.min()) / (np.ptp(x)) * hi

## @todo move to GUI
def incr_spinbox(spinbox):
    value = min(spinbox.maximum(), spinbox.value() + spinbox.singleStep())
    log.debug("incr_spinbox: changing from %d by %d to %d", spinbox.value(), spinbox.singleStep(), value)
    spinbox.setValue(value)

## @todo move to GUI
def decr_spinbox(spinbox):
    value = max(spinbox.minimum(), spinbox.value() - spinbox.singleStep())
    log.debug("decr_spinbox: changing from %d by %d to %d", spinbox.value(), spinbox.singleStep(), value)
    spinbox.setValue(value)

## @todo move to GUI
def apply_min_max(widget):
    if widget.value() > widget.maximum():
        widget.setValue(widget.maximum())
    elif widget.value() < widget.minimum():
        widget.setValue(widget.minimum())

## @todo move to GUI
def set_min_max(widget, lo, hi, value=None):
    widget.blockSignals(True)
    widget.setMinimum(lo)
    widget.setMaximum(hi)
    widget.blockSignals(False)
    
    if value is not None:
        # will automatically check limits
        widget.setValue(value)
    else:
        # since we're not calling setValue and triggering the range
        # check that way, apply it manually
        apply_min_max(widget)

##
# @todo move to GUI
def get_combobox_item_index(combobox, name):
    for i in range(combobox.count()):
        if combobox.itemText(i) == name:
            return i
    return None

##
# @todo move to GUI
def add_combobox_item(combobox, name):
    currentIndex = get_combobox_item_index(combobox, name)
    if currentIndex is None:
        combobox.addItem(name)
    else:
        log.debug("declining to re-add %s to combobox (already at index %d)", name, currentIndex)

##
# @todo move to GUI
def remove_combobox_item(combobox, name):
    currentIndex = get_combobox_item_index(combobox, name)
    if currentIndex is not None:
        combobox.removeItem(currentIndex)
    else:
        log.debug("unable to remove %s (not found)", name)

##
# should be e.g. QtGui.QColor(0,125,0)  
# @todo replace with Colors
# @todo move to GUI
def set_table_row_color(table, row, color):
    for col in range(table.columnCount()):
        table.item(row, col).setBackground(color)

## 
# Enable or disable a QWidget, while simultaneous restoring or clearing its QToolTip.
#
# Normally you can't disable or hide a tooltip.  In this case, I would like to change
# the tooltip behavior for disabled widgets.
#
# @todo move to GUI
def set_enabled(w, flag, tooltip=None):
    w.setEnabled(flag)

    if tooltip:
        if flag:
            w.setToolTip(tooltip)
        else:
            w.setToolTip(None)

def force_size(widget, width, height):
    widget.setMinimumWidth(width)
    widget.setMaximumWidth(width)
    widget.setMinimumHeight(height)
    widget.setMaximumHeight(height)
    widget.setMaximumWidth(width)

def set_checkbox_quietly(cb, flag):
    cb.blockSignals(True)
    cb.setChecked(flag)
    cb.blockSignals(False)

# doesn't seem to do anything visible
# def set_benign(widget, flag=False):
#     if flag is None:
#         widget.setProperty("wpPanel",  True)
#         widget.setProperty("wpBenign", None)
#         widget.setProperty("wpHazard", None)
#     elif flag:
#         widget.setProperty("wpPanel",  None)
#         widget.setProperty("wpBenign", True)
#         widget.setProperty("wpHazard", None)
#     else:
#         widget.setProperty("wpPanel",  None)
#         widget.setProperty("wpBenign", None)
#         widget.setProperty("wpHazard", True)
#     log.debug("set_benign: widget = %s, flag = %s", widget.objectName(), flag)

################################################################################
# JSON helpers
################################################################################

##
# This didn't seem to work, but I'm not taking time to troubleshoot it now.
# Explore later as a way to minimize the number of dicts vs objects passed
# externally.
#
# @see https://stackoverflow.com/a/15882054/11615696
def json2obj(text): 
    return json.loads(text, object_hook=_json_object_hook)

def _json_object_hook(d): 
    return namedtuple('X', d.keys())(*d.values())

## Assuming JSON has been rendered with indentation, leave the dicts indented but 
#  flatten arrays to single lines.  Also, normalize NaN.
# 
# @note this is assuming arrays of numbers...if the input JSON includes arrays of
#       strings, and strings could contain ] characters, this would probably 
#       corrupt data.
def clean_json(s):
    pattern = r'^(.*)' + r'\[' + "[\n\r]+" + r'([^\]]+)' + r'\]' + r'(.*)$'
    pat = re.compile(pattern, flags=re.DOTALL)

    m = pat.match(s)
    while m is not None:
        array_contents = m.group(2).strip()
        contents_as_line = re.sub(",\s+", ", ", array_contents)
        new_list = "[ " + contents_as_line + " ]"
        s = m.group(1) + new_list + m.group(3)
        m = pat.match(s)

    # Java's JSON parser breaks on NaN...the spec is iffy
    return re.sub(r"\bNaN\b", "null", s)

##
# Recurse down a potentially nested structure of dicts and lists, converting
# every Decimal into a float.  Used to normalize results from AWS DynamoDB.
# (Is there a way to make boto default to this?)
def normalize_decimal(obj):
    if type(obj) is dict:
        for k, v in obj.items():
            if type(v) is Decimal:
                obj[k] = float(v)
            elif isinstance(v, (list, dict)):
                normalize_decimal(v)
    elif type(obj) is list:
        for i in range(len(obj)):
            if type(obj[i]) is Decimal:
                obj[i] = float(obj[i])
            elif isinstance(obj[i], (list, dict)):
                normalize_decimal(obj[i])

def python_version():
    return ".".join([str(x) for x in sys.version_info])
