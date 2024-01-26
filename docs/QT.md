# Qt Notes

Just starting to take some notes on Qt issues as we migrate to Qt5 and try to 
clean up some long-standing Qt4 issues.

See also: [CSS notes](CSS.md)

# Re-usable Styling

The entire point of CSS is to be able to define styles once, and have them
automatically apply to hundreds or thousands of widgets.  Unfortunately, early
versions of ENLIGHTEN (going back to 1.0) featured horrible "copy-pasta" in
which the StyleSheet element of individual QFrames (and QLabels, and QSpinBoxes,
and...) was copy-pasted to each new widget.  When you opened enlighten_layout.ui,
this meant that the file was filled with tons of raw CSS inside &lt;styleSheet&gt;
elements.  It was very unmaintainable, inconsistent and unskinnable.

We are now using enlighten.css to style virtually everything in the UI.  The
total amount of formatting code is much smaller, and as a result it is faster to 
style new GUI components and the results are rendered much more consistently,
creating a better user experience.

## FrameShape and FrameShadow

For some reason, frameShape and frameShadow enums work in Designer (if referenced 
by their decimal integers), but don't affect the GUI when ENLIGHTEN is run -- 
don't know why.  That's unfortunate, as otherwise we could just use the Designer
to select different frameShape / frameShadow combinations, and not have to use
the comparatively klunky wpBox / wpGrad / etc workaround.

## Custom Properties

Unlike frameShape / frameShadow, these do work, both in ENLIGHTEN and Designer.  
I wasn't able to do equivalence or substring comparison on string Custom 
Properties, but I am able to simply check for the presence of a property.  
Therefore, I'm just using simple bools, and it doesn't even matter if they're 
assigned a value (they default false).

These are currently the primary way that re-usable CSS styles are applied quickly
and easily to large number of widgets.  Some of the most common Custom Properties
in use are wpBox, wpGrad and wpPanel.  You will find them defined at the bottom 
of enlighten.css.

They can be easily added in Qt Designer (just click the "+" button).  For some
reason, you don't see the affect on an element right after adding the property,
but if you quit Designer and re-open it, you'll see the styling applied.

The advantage of these of course is that every wpBox, wpGrad etc can be 
immediately restyled by changing the one definition in enlighten.css.

# PySide2 bugs

I have found a couple of PySide2 bugs, which cause problems in rendered Python 
code (i.e. ENLIGHTEN) which do NOT occur in the Designer (because they're not 
present in the XML).

Both of the following bugs probably relate to the same abstract item class.
Also, I suspect they've been fixed in Qt for Python 5.13.1 but I haven't 
confirmed.

## QTableWidget.horizontalHeaderItem

A new problem came up with pyside2-uic.  It looks like in TableWidgets, if two 
TableWidgets are within the same (don't know), pyside2-uic incorrectly numbers 
the horizontalHeaderItem.  I ended up working around this by populating the 
KnowItAll TableWidgets programmatically rather than via Designer (see 
enlighten.KnowItAll.Feature.init_tables).

## QComboBoxes

You need to populate these in code; PySide2 numbers them incorrectly in code 
generation.  Or rather, the FIRST QComboBox is rendered correctly 
(comboBox_view as it happens), but the item indexes of subsequent QComboList 
widgets continue the original sequence.
