import logging

from PySide6 import QtGui, QtWidgets, QtCore
from PySide6.QtCore import Qt

from wasatch import utils as wasatch_utils

from enlighten.ScrollStealFilter import ScrollStealFilter

log = logging.getLogger(__name__)

##
# Creates an appropriate Qt GUI widget corresponding to a single input or output
# EnlightenPluginField, and manages the data updates between the plugin field
# and its GUI counterpart.
# 
# @note since this extends QWidget, we want to be careful creating attributes 
#       with names like .name, .value, .config or .widget that could override 
#       parent attributes
# @todo add QtWidgets.ComboBox
class PluginFieldWidget(QtWidgets.QWidget):

    ## class attribute
    datatype_to_widgets = {
        'string':   QtWidgets.QLineEdit,
        'int':      QtWidgets.QSpinBox,
        'float':    QtWidgets.QDoubleSpinBox,
        'radio':    QtWidgets.QRadioButton,
        'bool':     QtWidgets.QCheckBox,
        'button':   QtWidgets.QPushButton
    }

    # ##########################################################################
    # initialization
    # ##########################################################################

    ##
    # @param field_config is an EnlightenPluginField
    def __init__(self, config, ctl=None):
        super().__init__()

        self.field_config = config
        self.field_name   = config.name
        self.field_value  = config.initial

        # this will (after initUI) hold the QWidget used for input/output field values
        self.field_widget = None 

        # create the hbox and populate it with the name-value pair 
        # (note the hbox isn't yet added to a parent layout)
        self.hbox = self.initUI()

        # populate the field widget
        #
        # Overlooked something simple. Forgot to invoke the lambda from the 
        # dict. This does look much nicer with the change I made the output entry
        # likely isn't needed but I'm leaving it in case we want the option to add
        # output labels in the controller area on the right side.
        configure_widget = {
            "output":   lambda widget : widget.setText(str(self.field_value)),
            "float":    lambda widget : self.create_float_fields   (widget),
            "int":      lambda widget : self.create_int_fields     (widget), 
            "string":   lambda widget : self.create_string_fields  (widget),
            "bool":     lambda widget : self.create_bool_fields    (widget),
            "radio":    lambda widget : self.create_radio_fields   (widget),
            "button":   lambda widget : self.create_button_fields  (widget)
        }

        try:
            if config.direction == "output":
                configure_widget["output"](self.field_widget)
            else:
                configure_widget[config.datatype](self.field_widget)
        except Exception as e:
            log.error(f"Error, plugin {config.name} does not have a valid data type for connection.", exc_info=1)
            return

        if ctl and config.stylesheet:
            ctl.stylesheets.apply(self.field_widget, config.stylesheet)
        
    def initUI(self):

        # each "field" is actually expanded into a name-value pair
        hbox = QtWidgets.QHBoxLayout()

        # everything but buttons gets a label
        if self.field_config.datatype != "button":
            label = QtWidgets.QLabel(self)
            label.setText(self.field_name)
            label.setWordWrap(True)
            hbox.addWidget(label)

        if self.field_config.direction == "output":
            # create output widget
            self.field_widget = QtWidgets.QLabel(str(self.field_value))
        else:
            # create input widget
            if self.field_config.datatype != "radio":
                self.field_widget = PluginFieldWidget.datatype_to_widgets[self.field_config.datatype](self)
            else:
                self.field_widget = PluginFieldWidget.datatype_to_widgets[self.field_config.datatype]()

        if self.field_config.tooltip is not None:
            self.field_widget.setToolTip(self.field_config.tooltip)

        # add the pair
        hbox.addWidget(self.field_widget)
        return hbox

    def create_float_fields(self, widget):
        if self.field_value is None:
            self.field_value = float(self.field_config.minimum)
        widget.setRange(float(self.field_config.minimum), float(self.field_config.maximum))
        widget.setSingleStep(float(self.field_config.step))
        widget.setDecimals(int(self.field_config.precision))
        widget.setValue(float(self.field_value))
        widget.valueChanged.connect(lambda: self.update_value(self.field_widget.value()))
        widget.installEventFilter(ScrollStealFilter(widget))

    def create_int_fields(self, widget):
        if self.field_value is None:
            self.field_value = int(self.field_config.minimum)
        widget.setRange(int(self.field_config.minimum), int(self.field_config.maximum))
        widget.setSingleStep(int(self.field_config.step))
        widget.setValue(int(self.field_value))
        widget.valueChanged.connect(lambda: self.update_value(self.field_widget.value()))
        widget.installEventFilter(ScrollStealFilter(widget))

    def create_string_fields(self, widget):
        if self.field_value is None:
            self.field_value = ""

        widget.setText(self.field_value)
        widget.textChanged.connect(lambda: self.update_value(self.field_widget.text()))

    def create_radio_fields(self, widget):
        if self.field_value is None:
            self.field_value = False

        if isinstance(self.field_value, bool):
            widget.setChecked(self.field_value)
        widget.toggled.connect(lambda check: self.update_value(check))

    def create_bool_fields(self, widget):
        if self.field_value is None:
            self.field_value = False

        if isinstance(self.field_value, bool):
            widget.setChecked(self.field_value)
        widget.stateChanged.connect(lambda: self.update_value(self.field_widget.isChecked()))

    def create_button_fields(self, widget):
        widget.setText(self.field_name)
        widget.setMinimumHeight(30) 
        widget.pressed.connect(self.field_config.callback)

    # ##########################################################################
    # public methods
    # ##########################################################################

    def get_display_element(self):
        return self.hbox

    ##
    # The value of this PluginField has changed (whether by the user at the GUI,
    # for input fields, or via the latest Response from the plugin, for output
    # fields).  For output fields, update the new value to the QLabel.  For input
    # fields, grab the new value so we can pass it in the next Request.
    def update_value(self, value):
        log.debug(f"{self.field_name} -> {value}")
        if self.field_config.direction == "output":
            if value is None:
                value = ''
            if self.field_config.datatype == 'float':
                value = "%.*f" % (self.field_config.precision, float(value))
            self.field_widget.setText(str(value))
            self.field_value = value
            return

        # interesting decision: if a plugin passes None for an input field, we
        # retain the previous value; we do NOT clear the value
        if value is None:
            return

        self.field_value = value
        if self.field_config.datatype == 'string':
            self.field_widget.setText(str(value))
        elif self.field_config.datatype == "radio":
            self.field_widget.setChecked(wasatch_utils.to_bool(value))
        elif self.field_config.datatype == "bool":
            self.field_widget.setChecked(wasatch_utils.to_bool(value))
        elif self.field_config.datatype == 'int':
            self.field_widget.setValue(int(round(value)))
        elif self.field_config.datatype == 'float':
            self.field_widget.setValue(float(value))
