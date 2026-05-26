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
    """ 
    """

    def __init__(self, ctl):
        super().__init__(ctl)

        cfu = ctl.form.ui

        self.layout_charts = cfu.layout_strip_charts
        self.parent = cfu.stackedWidget_hardware_capture_details_spectrum

        self.charts = {}

    def create_chart(self, name, window_sec=180, y_unit=None, warn_hi=None, warn_lo=None, format=None, process_reading_callback=None):
        chart = StripChart(self.ctl, name=name, window_sec=window_sec, y_unit=y_unit, warn_hi=warn_hi, warn_lo=warn_lo, format=format, parent=self.parent, process_reading_callback=process_reading_callback)
        self.charts[name] = chart

        # chart.layout.setParent(self.layout_charts)
        self.layout_charts.addItem(chart.layout)

        return chart

    def process_reading(self, spec, reading):
        """ We have received a new Reading from a Spectrometer, so process it for every chart  """
        for name, chart in self.charts.items():
            callback = chart.process_reading_callback
            if callback is not None:
                callback(spec, reading)

class StripChart:
    
    def __init__(self, ctl, name, window_sec=180, y_unit=None, warn_hi=None, warn_lo=None, format=None, parent=None, process_reading_callback=None):
        self.ctl = ctl
        self.name = name
        self.y_unit = y_unit
        self.warn_hi = warn_hi
        self.warn_lo = warn_lo
        self.window_sec = window_sec
        self.format = format 
        self.parent = parent
        self.process_reading_callback = process_reading_callback

        self.plot = None
        self.visible = True

        self.spec_data = {} # hash from serial to curve and RollingDataSet 

        self.saving = False

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
        self.cb_display.setChecked(True)
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
        # todo: add legend

        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)

        self.stacked_widget = QStackedWidget(self.parent)
        self.stacked_widget.setSizePolicy(sizePolicy)
        self.stacked_widget.setMinimumSize(QSize(300, 300))
        self.stacked_widget.setMaximumSize(QSize(16777215, 300))
        self.stacked_widget.addWidget(self.plot)

        self.layout.addWidget(self.stacked_widget)

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

    def add_value(self, spec, value):
        """
        todo maintain multiple RDS and curves for multiple connected spectrometers
        """
        sn = spec.settings.eeprom.serial_number
        if sn not in self.spec_data:
            self.spec_data[sn] = { 
                "RDS": RollingDataSet(size_seconds=self.window_sec),
                "curve": self.plot.plot([]),
                "pathname": os.path.join(self.ctl.save_options.generate_today_dir(), f"{self.name}-{sn}.txt")
            }

        rds = self.spec_data[sn]["RDS"]
        curve = self.spec_data[sn]["curve"]
        now = datetime.now()

        # display latest value in chart header row
        text = self.format.format(value=value)
        self.lb_value.setText(text)

        # add to rolling dataset
        rds.add(value)

        # update graph
        x, y = rds.get_relative_to_now()
        curve.setData(y=y, x=x)

        # write file
        if self.saving:
            pathname = self.spec_data[sn]["pathname"]
            with open(pathname, "a") as outfile:
                outfile.write(f"{now}, {value}\n")

    def set_warn_hi(self, hi):
        self.warn_hi = hi

    def set_warn_lo(self, lo):
        self.warn_lo = lo

    def save_callback(self):
        self.saving = self.cb_save.isChecked()

    def sec_callback(self):
        self.window_sec = self.sb_sec.value()
        for sn in self.spec_data:
            self.spec_data[sn]["RDS"].update_window(self.window_sec)

    def display_callback(self):
        self.set_visible(self.cb_display.isChecked())

    def clear_callback(self):
        for sn in self.spec_data:
            self.spec_data[sn]["RDS"].clear()

    def copy_callback(self):
        cols = []
        longest = -1
        for sn in self.spec_data:
            rds = self.spec_data["RDS"]
            x, y = rds.get_relative_to_now()
            cols.append(x)
            cols.append(y)
            longest = max(longest, x)

        s = ""
        for i in range(longest):
            row = []
            for col in cols:
                if i < len(col):
                    row.append(col[i])
                else:
                    row.append("")
            s += "\t".join(row) + "\n"

        self.ctl.app.clipboard().setText(s)

    def set_visible(self, flag):
        if flag is None:
            # this can happen during Controller initialization
            flag = False
        self.visible = flag
        self.cb_display.setChecked(flag)

        # MZ: this is "greying-out" the graph, but not recapturing the space :-(
        # solution is probably to nest StackedWidget in a Frame, and hide the Frame
        self.stacked_widget.setVisible(flag)
