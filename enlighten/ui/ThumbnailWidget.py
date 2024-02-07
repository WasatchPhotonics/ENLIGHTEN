import pyqtgraph
from datetime import datetime
import logging

from enlighten import KnowItAll
from enlighten import common
from enlighten import util

if common.use_pyside2():
    from PySide2 import QtGui, QtCore, QtWidgets
else:
    from PySide6 import QtGui, QtCore, QtWidgets

log = logging.getLogger(__name__)

## 
# This class encapsulates the visual representation of a saved Measurement in
# the GUI's "saved spectra" column.  It includes a thumbnail pseudo-object (the 
# miniature raster of the spectra), as well as the Qt Widget which displays the
# Thumbnail and all the buttons and labels and CSS styling around it.
#
# It contains a reference to the main graph both so it can add and remove 
# itself to the graph as a visible trace, and also so it can determine the
# current x-axis unit.
#
# These objects are created by MeasurementFactory.
#
# Bizarrely, creation of the all-important thumbnail is still in MeasurementFactory?
class ThumbnailWidget(QtWidgets.QFrame):

    BUTTON_PADDING = 5
    BUTTON_Y    = 155

    OUTER_WIDTH = 190
    INNER_WIDTH = 188

    MIN_WIDTH = 160
    MAX_WIDTH = 170

    ## allows deep-copying of Measurements
    def __deepcopy__(self, memo):
        log.debug("blocking deep-copy")

    def __init__(self, 
            ctl,
            measurement,
            is_collapsed,
            graph):
        super(ThumbnailWidget, self).__init__()

        self.ctl            = ctl
        self.measurement    = measurement
        self.is_collapsed   = is_collapsed
        self.graph          = graph 

        log.debug(f"using graph {graph.name}")

        self.is_displayed  = False
        self.selected_color = None
        self.curve = None
        self.old_name = None
        self.last_editted = None

        ########################################################################
        # Widget styling
        ########################################################################

        # These styles are applied to the ThumbnailWidget itself, as a QWidget

        self.setProperty("wpBox", False)
        self.setMinimumWidth(ThumbnailWidget.OUTER_WIDTH)
        self.setMaximumWidth(ThumbnailWidget.OUTER_WIDTH)

        policy = QtWidgets.QSizePolicy()
        policy.setVerticalPolicy(QtWidgets.QSizePolicy.Fixed)
        self.setSizePolicy(policy)

        ########################################################################
        # Sub-frame
        ########################################################################

        # This sub-frame is colored black, and contains all the buttons and
        # graphic elements of the ThumbnailWidget.
        #
        # An alternate implementation would be to use a vertical layout for the 
        # label, body and button-bar (itself a horizontal layout).  Then we could 
        # just make things invisible and let the vertical layout collapse itself.

        self.frame = QtWidgets.QFrame()
        self.frame.setProperty("wpGrad", False)
        self.frame.setMinimumWidth(ThumbnailWidget.INNER_WIDTH)
        self.frame.setMaximumWidth(ThumbnailWidget.INNER_WIDTH)
        self.frame.setParent(self)
        self.frame.move(1, 1)

        ########################################################################
        # Button Bar
        ########################################################################

        self.buttons = QtWidgets.QFrame()
        self.buttons.setLayout(QtWidgets.QHBoxLayout())
        self.buttons.setMinimumWidth(ThumbnailWidget.INNER_WIDTH)
        self.buttons.setMaximumWidth(ThumbnailWidget.INNER_WIDTH)
        self.buttons.setParent(self)
        self.buttons.move(1, ThumbnailWidget.BUTTON_Y)
        self.buttons.setStyleSheet("background-color: transparent")

        ########################################################################
        # "Loading" thumbnail
        ########################################################################

        # When there are a lot of ThumbnailWidgets to render (say after loading
        # a bunch of saved spectra at once), the original intention was to 
        # stub each of them with a "Loading..." graphic until the actual spectra
        # could be re-rendered into a custom Thumbnail.  I'm not sure if this
        # even works right now, but that's what this is for.
        #
        # Oddly, the expand/collapse functions reference self.body, so perhaps
        # this is where the final Thumbnail goes as well?

        self.body = QtWidgets.QLabel("loading")
        # self.body.setPixmap(":/simulation/images/spectrums/thumbnail_loading.png")
        self.ctl.stylesheets.apply(self.body, "clear_border")
        self.body.move(12, 33)
        self.body.resize(162, 112)
        self.body.setScaledContents(True)
        self.body.setParent(self)

        ########################################################################
        # Editable Label
        ########################################################################

        self.le_name = self.create_label_widget()

        ########################################################################
        # Thumbnail control buttons
        ########################################################################

        # TODO: add a "..." drop-down menu of advanced functions, including
        # "choose color"
        add_id = self.should_add_id_button() 
        width = 31 if add_id else 35

        self.button_edit    = self.create_button(callback=self.rename_callback,     icon_name="pencil",        icon_size=(28, 28), size=(width, 30), tooltip="Rename measurement (ctrl-E for latest)")
        self.button_display = self.create_button(callback=self.display_callback,    icon_name="chart",         icon_size=(28, 28), size=(width, 30), tooltip="Toggle graph trace")
        self.button_color   = self.create_button(                                                              icon_size=(28, 28), size=(width, 30), tooltip="Set color", is_color=True)
        if add_id:
            self.button_id  = self.create_button(callback=self.id_callback,         icon_name="fingerprint",   icon_size=(28, 28), size=(width, 30), tooltip=KnowItAll.tooltip)
        else:
            self.button_id  = None
        self.button_trash   = self.create_button(callback=self.trash_callback,      icon_name="trash",         icon_size=(28, 28), size=(width, 30), tooltip="Delete measurement from disk")
        self.button_expand  = self.create_button(callback=self.expand_callback,     icon_name="down_triangle", icon_size=(10, 10), size=(15, 15), loc=(170,  15))

        self.button_color   .sigColorChanged    .connect(self.color_changed_callback)

        # self.button_edit.setAutoDefault(True) 

        ########################################################################
        # Tooltip
        ########################################################################

        self.generate_tooltip()

        ########################################################################
        # initial state
        ########################################################################

        if self.is_collapsed:
            self.collapse()
        else:
            self.expand()

        self.update_kia()

    # ##########################################################################
    # Creation
    # ##########################################################################

    def should_add_id_button(self):
        if not self.ctl.kia_feature.is_installed:
            log.debug("KIA not installed")
            return False

        # only add "identify" button to Raman measurements
        return self.measurement.technique and "raman" == self.measurement.technique.lower()

    ##
    # Called by MeasurementFactory to set the rendered thumbnail image
    def set_pixmap(self, pixmap):
        self.body.setPixmap(pixmap)

    def create_label_widget(self):
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setWeight(QtGui.QFont.Weight.Thin)
        font.setStyleHint(QtGui.QFont.StyleHint.SansSerif)
        font.setBold(False)

        policy = QtWidgets.QSizePolicy()
        policy.setHorizontalPolicy(QtWidgets.QSizePolicy.MinimumExpanding)

        le_name = QtWidgets.QLineEdit(self.measurement.label)
        self.ctl.stylesheets.apply(le_name, "clear_border")
        le_name.setSizePolicy(policy)
        le_name.setMinimumWidth(ThumbnailWidget.MIN_WIDTH)
        le_name.setMaximumWidth(ThumbnailWidget.MAX_WIDTH)
        le_name.move(10, 10)
        le_name.setFont(font)
        le_name.setParent(self)
        le_name.setReadOnly(True) 
        le_name.returnPressed.connect(self.rename_complete_callback) # consider using editingFinished() instead (supports loss-of-focus)

        return le_name

    # ##########################################################################
    # Utility
    # ##########################################################################

    ##
    # @warning we appear to be unable to write to our standard logger from 
    # within this class, presumably due to a conflict with Qt?
    def logMsg(self, msg):
        log.debug(msg)
        print("ThumbnailWidget: " + msg)

    def set_active(self, flag):
        self.is_displayed = flag
        self.ctl.gui.colorize_button(self.button_display, flag)

    def collapse(self):
        self.is_collapsed = True

        self.setMinimumHeight(40)
        self.setMaximumHeight(40)

        self.frame.setMinimumHeight(38)
        self.frame.setMaximumHeight(38)

        self.body.setVisible(False)
        # self.button_expand.setVisible(True)

    def expand(self):
        self.is_collapsed = False

        self.setMinimumHeight(200)
        self.setMaximumHeight(200)

        self.frame.setMinimumHeight(198)
        self.frame.setMaximumHeight(198)

        self.body.setVisible(True)
        # self.button_expand.setVisible(False)

    def create_button(self, 
            size=(30, 30), 
            icon_size=(20, 20), 
            icon_name=None,
            loc=None, 
            callback=None,
            tooltip=None,
            is_color=False):

        if is_color:
            button = pyqtgraph.ColorButton()
        else:
            button = QtWidgets.QPushButton()
            if icon_name is not None:
                icon = QtGui.QIcon()
                try:
                    icon.addPixmap(":/greys/images/grey_icons/%s.svg" % icon_name)
                    button.setIcon(icon)
                    button.setIconSize(QtCore.QSize(icon_size[0], icon_size[1]))
                except:
                    logMsg("ERROR: can't find icon_name " + icon_name)

        button.setParent(self)
        # button.resize(size[0], size[1])
        util.force_size(button, size[0], size[1])

        if loc is not None:
            button.move(loc[0], loc[1])
        else:
            self.buttons.layout().addWidget(button)

        if callback is not None:
            button.clicked.connect(callback)

        if tooltip is not None:
            button.setToolTip(tooltip)

        self.ctl.gui.colorize_button(button, False)

        return button

    # ##########################################################################
    # Callbacks
    # ##########################################################################

    def color_changed_callback(self, btn):
        self.selected_color = btn.color()
        if self.curve is not None:
            pen = pyqtgraph.mkPen(width=1, color=self.selected_color)
            self.curve.setPen(pen)

    # the user clicked the "thumbnail" icon, starting an ID operation
    def id_callback(self):
        self.ctl.kia_feature.enqueue_measurement(self.measurement)
        self.ctl.gui.colorize_button(self.button_id, True)

    # KIA finished the ID.  For lack of a clear reason to do otherwise, we have
    # the callback come back to the ThumbnailWidget object which originated the 
    # request.  However, high-level processing of the response is handled by
    # the Measurement, which has better visibility on what to do with the ID
    # declaration.  
    #
    # Note that the Measurement MAY elect to call this Thumbnail's rename() 
    # method to change the text field atop the widget...or it may not.
    def id_complete_callback(self):
        dm = self.measurement.declared_match
        if dm is not None:
            self.button_id.setToolTip("%s (score %.2f)" % (dm, dm.score))
        self.ctl.gui.colorize_button(self.button_id, False)

    def trash_callback(self):
        self.ctl.gui.colorize_button(self.button_trash, True)
        response = common.msgbox("Also delete measurement from disk?", buttons="Yes, No, Cancel")
        self.ctl.gui.colorize_button(self.button_trash, False)
        if response == "Cancel":
            return
        self.measurement.delete(from_disk=(response == "Yes"), update_parent=True)

    def display_callback(self):
        if self.is_displayed:
            self.remove_curve_from_graph()
        else:
            log.debug("display_callback: adding thumbnail trace to graph")
            self.add_curve_to_graph()

    ## the user clicked the "pencil" icon to edit the Thumbnail's label
    def rename_callback(self):

        if self.last_editted and (datetime.now() - self.last_editted).total_seconds() < 1:
            log.debug("rename: debouncing re-click intended to end edit")
            return
        
        # save old contents for comparison
        self.old_name = self.le_name.text()
        log.debug("rename: now editing")

        self.le_name.setReadOnly(False)
        self.ctl.stylesheets.apply(self.le_name, "edit_text")
        self.le_name.setFocus()
        self.le_name.selectAll()
        self.ctl.gui.colorize_button(self.button_edit, True)

        self.ctl.focus_listener.register(self.le_name, self.rename_complete_callback)

    def rename_complete_callback(self):
        """
        The user hit "return" after editting the Thumbnail's name, or otherwise
        moved focus to a different widget (or re-clicked the edit button), so 
        pass the new label up to the Measurement object.
        """
        log.debug("rename_complete: completing")
        self.last_editted = datetime.now()

        self.ctl.focus_listener.unregister(self.le_name)

        self.ctl.stylesheets.apply(self.le_name, "clear_border")
        self.button_edit.setFocus()
        self.le_name.setReadOnly(True)
        self.ctl.gui.colorize_button(self.button_edit, False)

        if self.le_name.text() != self.old_name:
            self.measurement.update_label(self.le_name.text(), manual=True)

    def expand_callback(self):
        if self.is_collapsed:
            self.expand()
        else:
            self.collapse()

    def toggle_thumbnail_expand_callback(self, thumbnail):
        cfu = self.form.ui
        layout = cfu.verticalLayout_scope_capture_save
        if layout.is_collapsed:
            if thumbnail.is_collapsed:
                thumbnail.expand()
            else:
                thumbnail.collapse()

    # ##########################################################################
    # Methods
    # ##########################################################################

    # this is called by Measurement AFTER Measurement decides that it's okay to
    # rename the Measurement
    def rename(self, label):
        self.le_name.setText(label)

    def update_kia(self):
        if self.button_id is not None:
            self.button_id.setEnabled(self.ctl.kia_feature and self.ctl.kia_feature.is_installed)

    ## Retain the thumbnail in the session, but remove its graphical trace from 
    # the chart.  This returns a bool so the clickable "toggle trace" button
    # can simply try to remove an existing trace as means of checking whether the
    # trace is currently shown on the graph or not.
    def remove_curve_from_graph(self):
        if self.measurement is not None:
            self.graph.remove_curve(measurement_id=self.measurement.measurement_id)
        else:
            self.graph.remove_curve(name=self.le_name.text())

        self.set_active(False)
        self.curve = None

    ##
    # @todo move some of this to Graph?
    def add_curve_to_graph(self):
        if self.curve is not None:
            return

        label = self.measurement.label
        pixels = self.measurement.settings.pixels()
        if self.measurement.plugin_name != "":
            log.debug(f"plugin trying to add save to plot")

        # take axis unit from Graph, then load axis values from Measurement
        if self.graph.current_x_axis == common.Axes.WAVELENGTHS:
            log.debug("axis is wavelengths so getting settings wavelengths")
            x_axis = self.measurement.processed_reading.get_wavelengths()
            log.debug(f"wavelengths len is {len(x_axis)}")
        elif self.graph.current_x_axis == common.Axes.WAVENUMBERS:
            log.debug("axis is wavenumbers so getting settings wavenumbers")
            x_axis = self.measurement.processed_reading.get_wavenumbers()
        else:
            log.debug("generating from pixels")
            x_axis = list(range(pixels))

        if x_axis is None:
            # maybe from a loaded file with insufficient data?
            log.debug("add_curve_to_graph: somehow have no x-axis?")
            return

        log.debug("add_curve_to_graph: generated x_axis of %d elements (%.2f to %.2f)", len(x_axis), x_axis[0], x_axis[-1])
        spectrum = self.measurement.processed_reading.get_processed()

        color = self.selected_color
        if color is None:
            # use named color if found in label
            color = self.ctl.colors.color_names.search(label)
        if color is None:
            color = self.ctl.colors.get_next_random()
        pen = pyqtgraph.mkPen(width=1, color=color)

        log.debug("add_curve_to_graph: adding name %s, %d y elements, %d x elements (%.2f to %.2f)",
            label, len(spectrum), len(x_axis), x_axis[0], x_axis[-1])

        try:
            self.curve = self.graph.add_curve(name=label, y=spectrum, x=x_axis, pen=pen, measurement=self.measurement)
        except:
            log.error("couldn't add Thumbnail trace to graph", exc_info=1)

        self.set_active(self.curve is not None)

    ## Called by Measurement.save_csv_file_by_row to prevent attempts to rename
    # spectra appended as lines to an existing file.
    def disable_edit(self):
        self.button_edit.setEnabled(False)

    ## Called by Measurement.save_csv_file_by_row to prevent attempts to delete
    # spectra appended as lines to an existing file. (All they can do is click
    # the eraser icon to remove the whole list, or click the trash icon on the
    # FIRST file to which other spectra were appended.)
    def disable_trash(self):
        self.button_trash.setVisible(False)

    def generate_tooltip(self):
        # quick stats in first line
        proc = self.measurement.processed_reading.get_processed()
        tt = f"Max {int(max(proc))}, Avg {int(sum(proc)/len(proc))}, Min {int(min(proc))}\n\n" if proc is not None else ""

        # followed by Measurement metadata
        metadata = self.measurement.get_all_metadata()
        for k in sorted(metadata):
            v = metadata[k]
            if v is not None:
                s = str(v)
                if len(s) > 0:
                    tt += f"{k}: {s}\n"
        # self.body.setToolTip(tt.strip())
        self.body.setWhatsThis(tt.strip())
        self.ctl.stylesheets.apply(self.body, "tooltip")
