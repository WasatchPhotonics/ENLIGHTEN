# CSS (Cascading StyleSheets)

Hints and suggestions on how to maintain the application's CSS stylesheets.

See also: [QT notes](QT.md)

# Stylesheets

There are three ways you can style an element:

1. via enlighten/assets/stylesheets/dark/enlighten.css (a secondary copy is
   embedded at the top of enlighten/assets/uic_qrc/enlighten_layout.ui, but you
   should edit the .css version)
2. via per-element stylesheets, applied within Qt Designer, and again stored 
   within enlighten_layout.ui
3. programmatically from Python, typically via the Stylesheets class which 
   provides access to enlighten/assets/stylesheets/dark

My goal is to use #1 as much as possible, fail-over to #3 when dynamic styling is 
required, and utilize #2 as little as possible.

Originally, ENLIGHTEN made heavy use of #2: ENLIGHTEN 1.6 had almost 400 
individually styled elements, some with fairly large multi-element stylesheets,
all showing a bewildering preponderance of copy-pasta.

The goal is for ENLIGHTEN 1.7.x to use _no_ per-element styles, and rely far
more heavily on #1.

# Dependencies

The stylesheet we use is tailored from 
[QDarkStyleSheet](https://github.com/ColinDuquesnoy/QDarkStyleSheet),
specifically commit c92d0c4c996e3e859134492e0f9f7f74bd0e12cd of:

- https://raw.githubusercontent.com/ColinDuquesnoy/QDarkStyleSheet/master/qdarkstyle/style.qss

# enlighten.css

I have extracted the stylesheet from enlighten_layout.ui, and put it in
stylesheets/dark as enlighten.css.

I've also updated scripts\rebuild_resources.sh to use XPath to copy the latest
enlighten.css into enlighten_layout.ui before running pyside2-uic.  That way
you can directly update and edit enlighten.css in a proper context-colored
editor, run it through lint-checkers, etc.  Also, it is automatically
updated into the .ui file so Qt Designer can see it as well.

More significantly, we're TRYING to "apply" enlighten.css to the MainWindow at
runtime via the Stylesheets class.  That means that end-users SHOULD be able to edit 
enlighten.css (and the other defaults/) to their hearts content, and their styles 
would automatically override the compiled-in stylesheet at execution.

I also added --stylesheet-path as a cmd-line option.

# Supported CSS Properties

Qt doesn't support all CSS properties (nor does any browser...)  A list of
supported properties is here:

- https://doc.qt.io/qt-5/stylesheet-reference.html#list-of-properties

Although...empirical testing suggests only these are actually working via PySide2?

- https://doc.qt.io/archives/qt-4.8/stylesheet-reference.html#list-of-properties

Nor does Qt seem to support CSS3 variables :-(

# Maintenance

After editing the CSS in enlighten.css, you need to re-run
scripts\rebuild_resources.sh to copy the new CSS into enlighten_layout.ui
so it can be seen in Qt Designer.  

EVENTUALLY, the enlighten.css stylesheet should be
[re-]applied to MainWindow at runtime, so edits to the .css can be seen
in ENLIGHTEN without re-running rebuild_resources.sh; but this isn't working
right now?

# Selectors

Normally you style CSS elements by classes.  I haven't had luck identifying
Qt widgets by class, but I have found that Qt "custom properties" can be used
as element selectors (see wpBox, wpPanel, wpGrad etc).

Also note that the styles as shown in Qt Designer are often _not_ what you see
in running the ENLIGHTEN executable!  I don't know if that would be resolved
if we moved to the Qt5 Designer, but it could be.

# Appearance Notes

Historically, ENLIGHTEN uses these sharp-looking panels with a thin white
frame (frame_FOO_white) enclosing a heavier dark frame (frame_FOO_black/shaded).
These are currently implemented with a frame with a wpBox property enclosing a
frame with a wpPanel or wpGrad property.

This means there are twice as many frames as there needs to be, as you'd THINK
there would be ways to put a thin white line around a heavier dark line using
CSS.  And there are: several ways, in fact.  But Qt's CSS rendering engine
doesn't seem to support the 'outline' property, nor the 'box-shadow' property,
and I couldn't figure out how to successfully create a .QFrame[wpPanel] :: after
shadow.
    
    MZ: Verify the above is still true in Qt5!

There are _programmatic_ ways to do shadows / edged panels in Qt, but that would
be comingling function and design, and wouldn't support skinning.  So anyway,
for now we have frame_FOO_white[wpBox] enclosing frame_FOO_black[wpGrad], etc.

Fix if you can.

# Dark Mode vs Light Mode

The current "dark mode" setting is stored in two objects within ENLIGHTEN.
The _boolean_ stating whether "Dark Mode is enabled" is in the GUI class.
The _string_ reflecting whether the current stylesheets are loaded from ./dark
or ./light is stored in the Stylesheets class.  The on-screen button letting
users toggle between modes is held by the GUI class, and it updates the 
Stylesheets class as needed.

I haven't found an easy way to toggle the background / foreground color of 
existing pyqtgraph plots.  There's a setBackgroundColor() command to change
the plot area itself, but not the axis region below and the left of the Graph:

    self.plot.plotItem.vb.setBackgroundColor('k' if dark_mode else 'w')

We could probably delete and recreate all the graphs, but that's too much
effort for now.  As a temporary solution, I persist the desired mode in
enlighten.ini and configure the graph defaults at the next launch.

    Dark       Light
    #383838 -> #19232D
    #F0F0F0 -> #19232D
    #787878 -> #FAFAFA
    #787878 -> #788d9c
    #14506e -> #daedff
    #148cd2 -> #73c7ff
    #32414B -> #C9CDD0

## Darkstyle

The default ENLIGHTEN color palette was tailored from this:

- https://github.com/ColinDuquesnoy/QDarkStyleSheet 

## Lightstyle

Tailored from this:

- https://raw.githubusercontent.com/ColinDuquesnoy/QDarkStyleSheet/master/qdarkstyle/light/lightstyle.qss

# Path Forward

## fewer default/

We should probably add a property for wpClickedButton, allowing us to do without
gray_gradient_button and red_gradient_button.

Would be even better if we could use string matches in property selectors like 
"benign" or "hazard"...
