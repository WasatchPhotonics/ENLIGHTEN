import os
import logging
import pyqtgraph

from datetime import datetime

from enlighten.EnlightenFeature import EnlightenFeature
from enlighten.timing.RollingDataSet import RollingDataSet
from enlighten import common

from PySide6.QtGui import QIcon, QFont
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QPushButton, QCheckBox, QFrame,QHBoxLayout, QLabel, QSizePolicy, QSpacerItem, QSpinBox, QVBoxLayout, QWidget, QStackedWidget

log = logging.getLogger(__name__)

class StripChartsFeature(EnlightenFeature):

    def __init__(self, ctl):
        super().__init__(ctl)

        cfu = ctl.form.ui

        self.layout_charts = cfu.layout_strip_charts
        self.parent = cfu.stackedWidget_hardware_capture_details_spectrum

        self.charts = {}

    def create_chart(self, name, window_sec=180, y_unit=None, warn_hi=None, warn_lo=None, format=None):
        chart = StripChart(self.ctl, name=name, window_sec=window_sec, y_unit=y_unit, warn_hi=warn_hi, warn_lo=warn_lo, format=format, parent=self.parent)
        self.charts[name] = chart

        # chart.layout.setParent(self.layout_charts)
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
    * a plot to graph the value over time

    We should be tracking these for:

    - detector temperature
    - laser temperature
    - µC temperature
    - battery charge level
    - battery temperature
    - battery IC temperature
    """
    
    def __init__(self, ctl, name, window_sec=180, y_unit=None, warn_hi=None, warn_lo=None, format=None, parent=None):
        self.ctl = ctl
        self.name = name
        self.y_unit = y_unit
        self.warn_hi = warn_hi
        self.warn_lo = warn_lo
        self.window_sec = window_sec
        self.format = format 
        self.parent = parent

        self.plot = None
        self.rds = RollingDataSet(size_seconds=window_sec)
        self.visible = True

        self.saving = False
        self.pathname = os.path.join(self.ctl.save_options.generate_today_dir(), f"{self.name}.txt")

        self.create_widgets()

    def create_widgets(self):
        """
        Detector Temperature    -15.01°C [x] Display [x] Save [v_180_sec_^] [Copy] [Clear]
         ________________________________________________________________________________
        |                                                                                |
        |                                                                                |
        |                                                                                |
        |________________________________________________________________________________|
        """
        self.layout = QVBoxLayout()

        font = QFont()
        font.setPointSize(10)
        font.setBold(True)

        # chart title
        self.lb_title = QLabel(self.parent)
        self.lb_title.setText(self.name)
        self.lb_title.setFont(font)

        # flexible spacer (push rest to right)
        horiz_spacer = QSpacerItem(2, 20, QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Minimum)

        # current value
        self.lb_value = QLabel(self.parent)
        self.lb_value.setFont(font)
        self.lb_value.setText("NA")

        # [x] Display
        self.cb_display = QCheckBox(self.parent)
        self.cb_display.setText("Display")
        self.cb_display.stateChanged.connect(self.display_callback)

        # [x] Save
        self.cb_save = QCheckBox(self.parent)
        self.cb_save.setText("Save")
        self.cb_save.stateChanged.connect(self.save_callback)

        # window size (seconds)
        self.sb_sec = QSpinBox(self.parent)
        self.sb_sec.setMinimum(10)
        self.sb_sec.setMaximum(3600)
        self.sb_sec.setValue(180)
        self.sb_sec.setSuffix(" sec")
        self.sb_sec.valueChanged.connect(self.sec_callback)

        # copy button
        self.pb_copy = self.make_icon_button("clipboard")
        self.pb_copy.clicked.connect(self.copy_callback)

        # clear button
        self.pb_clear = self.make_icon_button("eraser")
        self.pb_clear.clicked.connect(self.clear_callback)

        # now put all the above into a horizontal row
        hb = QHBoxLayout()
        hb.addWidget(self.lb_title)
        hb.addItem( horiz_spacer )
        hb.addWidget(self.lb_value)
        hb.addWidget(self.cb_display)
        hb.addWidget(self.cb_save)
        hb.addWidget(self.sb_sec)
        hb.addWidget(self.pb_copy)
        hb.addWidget(self.pb_clear)

        self.layout.addItem(hb)

        self.plot = pyqtgraph.PlotWidget(name = f"{self.name}Plot")
        self.plot.setLabel(axis="bottom", text="seconds")
        self.plot.setLabel(axis="left", text=self.y_unit)
        self.plot.invertX(True)
        self.plot.setMouseEnabled(x=False, y=False)
        self.curve = self.plot.plot([])

        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)

        sw = QStackedWidget(self.parent)
        sw.setSizePolicy(sizePolicy)
        sw.setMinimumSize(QSize(300, 300))
        sw.setMaximumSize(QSize(16777215, 300))
        sw.addWidget(self.plot)

        self.layout.addWidget(sw)

    def make_icon_button(self, icon_name):
        pb = QPushButton(self.parent)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(5)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(pb.sizePolicy().hasHeightForWidth())
        pb.setSizePolicy(sizePolicy)
        pb.setMinimumSize(QSize(16, 26))
        pb.setMaximumSize(QSize(30, 26))
        icon = QIcon()
        icon.addFile(f":/greys/images/grey_icons/{icon_name}.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        pb.setIcon(icon)
        pb.setIconSize(QSize(24, 24))
        return pb

    def add_value(self, value, spec=None):
        """
        todo maintain multiple RDS and curves for multiple connected spectrometers
        """
        now = datetime.now()

        # display latest value in chart header row
        text = self.format.format(value=value)
        self.lb_value.setText(text)

        # add to rolling dataset
        self.rds.add(value)

        # update graph
        x, y = self.rds.get_relative_to_now()
        self.curve.setData(y=y, x=x)

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
