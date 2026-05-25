import os
import logging
import pyqtgraph

from enlighten.EnlightenFeature import EnlightenFeature
from enlighten.timing.RollingDataSet import RollingDataSet
from enlighten import common

from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QPushButton, QCheckBox, QFrame,QHBoxLayout, QLabel, QSizePolicy, QSpacerItem, QSpinBox, QVBoxLayout, QWidget

log = logging.getLogger(__name__)

class StripChartsFeature(EnlightenFeature):

    def __init__(self, ctl):
        super().__init__(ctl)

        cfu = ctl.form.ui

        self.layout_charts = cfu.layout_strip_charts

        self.charts = {}

    def create_chart(self, name, window_sec=180, y_unit=None, warn_hi=None, warn_lo=None, fmt=None):
        chart = StripChart(self.ctl, name=name, window_sec=window_sec, y_unit=y_unit, warn_hi=warn_hi, warn_lo=warn_lo, fmt=fmt)
        self.charts[name] = chart

        chart.layout.setParent(self.layout_charts)
        self.layout_charts.addItem(chart.layout)

        return chart

class StripChart:
    """
    Each of these should instantiate and own:

    * a RollingDataSet to hold the data
    * a name
    * a spinBox to determine window age in sec
    * a checkbox to log data to a file
    * a checkbox to display the chart
    * a clipboard icon to copy data to the system clipboard
    * potentially, warn_hi and warn_lo thresholds to colorize
    - a plot to graph the value over time

    We should be tracking these for:

    - detector temperature
    - laser temperature
    - µC temperature
    - battery charge level
    - battery temperature
    - battery IC temperature
    """
    
    def __init__(self, ctl, name, window_sec=180, y_unit=None, warn_hi=None, warn_lo=None, fmt=None):
        self.ctl = ctl
        self.name = name
        self.y_unit = y_unit
        self.warn_hi = warn_hi
        self.warn_lo = warn_lo
        self.window_sec = window_sec
        self.format = fmt

        self.plot = None
        self.rds = RollingDataSet(size_seconds=window_sec)
        self.visible = True

        self.saving = False
        self.pathname = os.path.join(self.ctl.save_options.generate_today_dir(), f"{self.name}.txt")

        self.create_widgets()

    def create_widgets(self):
        self.layout = QVBoxLayout()
        parent = self.ctl.form

        lb = QLabel(parent)
        lb.setText(self.name)

        hs = QSpacerItem(40, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.cb_display = QCheckBox(parent)
        self.cb_display.setText("Display")
        self.cb_display.stateChanged.connect(self.display_callback)

        self.cb_save = QCheckBox(parent)
        self.cb_save.setText("Save")
        self.cb_save.stateChanged.connect(self.save_callback)

        self.sb_sec = QSpinBox(parent)
        self.sb_sec.setMinimum(10)
        self.sb_sec.setMaximum(3600)
        self.sb_sec.setValue(180)
        self.sb_sec.setPrefix(" sec")
        self.sb_sec.valueChanged.connect(self.sec_callback)

        self.pb_copy = QPushButton(parent)
        self.pb_copy.setMinimumSize(QSize(30, 26))
        icon = QIcon()
        icon.addFile(u":/greys/images/grey_icons/clipboard.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pb_copy.setIcon(icon)
        self.pb_copy.setIconSize(QSize(24, 24))
        self.pb_copy.clicked.connect(self.copy_callback)

        self.pb_clear = QPushButton(parent)
        self.pb_clear.setText("Clear")
        self.pb_clear.clicked.connect(self.clear_callback)

        hb = QHBoxLayout()
        hb.addWidget(lb)
        hb.addItem(hs)
        hb.addWidget(self.cb_display)
        hb.addWidget(self.cb_save)
        hb.addWidget(self.sb_sec)
        hb.addWidget(self.pb_copy)

        self.layout.addItem(hb)

        self.plot = pyqtgraph.PlotWidget(name = f"{self.name}Plot")
        self.plot.setLabel(axis="bottom", text="seconds")
        self.plot.setLabel(axis="left", text=self.y_unit)
        self.plot.invertX(True)
        self.plot.setMouseEnabled(x=False, y=False)
        self.curve = self.plot.plot([])

    def add_value(self, value, spec=None):
        """
        todo maintain multiple RDS and curves for multiple connected spectrometers
        """
        now = datetime.now()
        self.rds.add(value)

        # graph value
        x, y = self.rds.get_relative_to_now()
        self.curve.set_data(y=y, x=x)

        # write file
        if self.saving:
            with open(self.pathname, "a") as outfile:
                outfile.write(f"{now}, {value}\n")

    def set_warn_hi(self, hi):
        self.warn_hi = hi

    def set_warn_lo(self, lo):
        self.warn_lo = lo

    def save_callback(self):
        self.saving = self.cb_save.isChecked()

    def sec_callback(self):
        self.window_sec = self.sb_sec.value()
        self.rds = RollingDataSet(size_seconds=self.window_sec)

    def display_callback(self):
        self.set_visible(self.cb_display.isChecked())

    def clear_callback(self):
        self.rds.clear()

    def copy_callback(self):
        self.ctl.clipboard.copy_rds(self.rds)

    def set_visible(self, flag):
        self.visible = flag

    def get_latest(self):
        if self.rds.empty():
            return
        (_, value) = self.rds.latest()
        return value
