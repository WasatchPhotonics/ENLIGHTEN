import os
import logging
import datetime
import pyqtgraph
import numpy as np
import qimage2ndarray

from enlighten import util
from enlighten import common
from enlighten.ui.ScrollStealFilter import ScrollStealFilter

if common.use_pyside2():
    from PySide2 import QtCore, QtWidgets, QtGui
else:
    from PySide6 import QtCore, QtWidgets, QtGui

log = logging.getLogger(__name__)

class AreaScanFeature:
    """
    Implements a 2D "area scan," displaying the full detector rows and columns
    rather than the usual 1D vertically-binned spectrum.

    This feature is primarily for manufacturing use.  It is not currently 
    very robust or efficient.

    @par Fast Mode

    Early AreaScan implementations in firmware sent out a single line in response
    to a single ACQUIRE opcode; 64 ACQUIRE requests had to be sent to read-out an
    entire 64-row detector.  When in "Fast Area Scan Mode," the detector sends
    out all 64 lines (or the height of the detector) in response to a single
    ACQUIRE.

    @todo give Graph awareness of the four plugin locations (top, left, right, 
          bottom), so that other features can use them; have AreaScanFeature claim
          "top", so when in use, PluginController only allows left/right/bottom.
    """

    # ##########################################################################
    # Lifecycle
    # ##########################################################################

    def __init__(self,
            bt_save,
            cb_enable,
            cb_fast,
            frame_image,
            frame_live,
            graphics_view,
            gui,
            layout_live,
            lb_current,
            lb_frame_count,
            marquee,
            multispec,
            progress_bar,
            save_options,
            sb_start,
            sb_stop,
            sb_delay_ms,
            set_curve_data):

        self.bt_save            = bt_save
        self.cb_enable          = cb_enable
        self.cb_fast            = cb_fast
        self.frame_image        = frame_image
        self.frame_live         = frame_live
        self.graphics_view      = graphics_view
        self.gui                = gui
        self.layout_live        = layout_live
        self.lb_current         = lb_current
        self.lb_frame_count     = lb_frame_count
        self.marquee            = marquee
        self.multispec          = multispec
        self.progress_bar       = progress_bar
        self.save_options       = save_options
        self.sb_start           = sb_start
        self.sb_stop            = sb_stop
        self.sb_delay_ms        = sb_delay_ms
        self.set_curve_data     = set_curve_data

        self.data = None
        self.enabled = False
        self.visible = False
        self.start_line = 0
        self.stop_line = 63
        self.ignored = 0
        self.frame_count = 0
        self.delay_ms = self.sb_delay_ms.value()
        self.image = None
        self.name = "Area_Scan"
        self.last_received_time = None

        # create widgets we can't / don't pass in
        self.create_widgets()
        self.multispec.register_strip_feature(self)

        self.cb_fast.setChecked(True)
        self.progress_bar.setVisible(False)

        self.bt_save    .clicked        .connect(self.save_callback)
        self.cb_fast    .stateChanged   .connect(self.fast_callback)
        self.cb_enable  .stateChanged   .connect(self.enable_callback)
        self.sb_start   .valueChanged   .connect(self.roi_callback)
        self.sb_stop    .valueChanged   .connect(self.roi_callback)
        self.sb_delay_ms.valueChanged   .connect(self.delay_callback)

        self.progress_bar_timer = QtCore.QTimer()
        self.progress_bar_timer.timeout.connect(self.tick_progress_bar)
        self.progress_bar_timer.setSingleShot(True)

        self.update_from_gui()

        # disable scroll stealing
        for key, item in self.__dict__.items():
            if key.startswith("sb_"):
                item.installEventFilter(ScrollStealFilter(item))

    def create_widgets(self):
        log.debug("creating widgets")

        # QGraphicsScene used to hold the Area Scan image
        self.scene = QtWidgets.QGraphicsScene(parent=self.frame_image) 
        self.graphics_view.setScene(self.scene)
        #self.graphics_view.setViewportMargins(0, -20, 0, -20) # L, T, R, B

        # PyQtChart to hold the "summed" graph beneath
        # (why not just put graphicsscene atop scope chart...?)
        self.chart_live = pyqtgraph.PlotWidget(name="Area Scan Live")
        #self.curve_live = chart_live.plot([], pen=self.gui.make_pen(widget="area_scan_live"))
        self.layout_live.addWidget(self.chart_live)

    def add_spec_curve(self, spec):
        if self.multispec.check_hardware_curve_present(self.name, spec.device_id):
            log.info(f"Adding spec curve {spec} already present, returning")
            return
        curve = self.chart_live.plot([], pen=spec.curve.opts['pen'],name=str(spec.label))
        self.multispec.register_hardware_feature_curve(self.name, spec.device_id, curve)

    def remove_spec_curve(self, spec):
        log.info(f"spec removal from graph called for spec {spec}")
        if not self.multispec.check_hardware_curve_present(self.name, spec.device_id):
            log.info(f"Removing spec curve {spec} already deleted, returning")
            return

        cur_curve = self.multispec.get_hardware_feature_curve(self.name, spec.device_id)

        # remove current curve from graph
        for curve in self.chart_live.listDataItems():
            if curve.name() == cur_curve.name():
                self.chart_live.removeItem(curve)

        self.multispec.remove_hardware_curve(self.name, spec.device_id)
        log.info(f"finished removing spec {spec}")


    def disconnect(self):
        log.debug("disconnecting")
        spec = self.multispec.current_spectrometer()
        if spec is not None:
            if self.enabled and spec.settings.state.area_scan_enabled:
                self.cb_enable.setChecked(False)
        self.update_visibility()

    # ##########################################################################
    # public methods
    # ##########################################################################

    ## @todo mess with is_supported etc if appropriate
    def update_visibility(self):
        spec = self.multispec.current_spectrometer()
        if spec is None:
            return self.disable()

        self.frame_live.setVisible(not (self.enabled and spec.settings.is_imx()))

        roi = spec.settings.get_vertical_roi()
        if roi is not None:
            log.debug("initializing ROI %s", roi)
            self.sb_start.setValue(roi[0])
            self.sb_stop .setValue(roi[1])
        else:
            log.debug("spectrometer has no vertical ROI")
            self.sb_start.setValue(0)
            self.sb_stop .setValue(spec.settings.eeprom.active_pixels_vertical - 1)

        # Fast Area Scan not yet available on SiG
        if spec.settings.is_imx():
            self.cb_fast.setChecked(False)
            self.sb_start.setEnabled(True)
            self.sb_stop.setEnabled(True)
            self.sb_delay_ms.setEnabled(False)
        else:
            # Hamamatsu
            self.cb_fast.setChecked(True)
            self.sb_start.setEnabled(False)
            self.sb_stop.setEnabled(False)
        self.cb_fast.setEnabled(False)

        self.frame_count = 0 # could move to app_settings

    def process_reading(self, reading):
        log.debug(f"trying to process area scan read")
        if reading is None or reading.spectrum is None:
            return

        if not self.enabled:
            self.set_curve_data(self.multispec.get_hardware_feature_curve(self.name, reading.device_id), y=reading.spectrum, label="AreaScanFeature.process_reading")
            return

        if reading.area_scan_row_count < 1:
            return

        # check that we 
        spec = self.multispec.current_spectrometer()
        if spec is None:
            return self.disable()

        # if spec.settings.state.area_scan_enabled:
        #     log.debug("area scan enabled, but not for spec")
        #     return

        log.debug("process_reading")
        if spec.settings.state.area_scan_fast and reading.area_scan_data is not None:
            self.update_progress_bar()

            log.debug("rendering frame of area_scan_fast")
            self.data = None
            rows = len(reading.area_scan_data)
            for i in range(rows):
                spectrum = reading.area_scan_data[i]
                row = spectrum[0]
                spectrum[0] = spectrum[1]
                self.process_spectrum(spectrum, row=row)

            self.finish_update()

            # update the on-screen frame counter
            self.frame_count += 1
            self.lb_frame_count.setText(str(self.frame_count))
        else:
            # slow mode
            spectrum = reading.spectrum
            row = reading.area_scan_row_count
            log.debug(f"slow mode: using row {row} of spectrum {spectrum[:10]}")
            self.process_spectrum(spectrum, row=row)
            self.finish_update()

    # ##########################################################################
    # callbacks
    # ##########################################################################

    def delay_callback(self):
        """ the user changed the delay_ms spinner """
        spec = self.multispec.current_spectrometer()
        if spec is None:
            return self.disable()

        self.delay_ms = self.sb_delay_ms.value()
        if self.enabled:
            spec.change_device_setting("detector_offset", self.delay_ms)

    def roi_callback(self):
        """ the user changed the start/stop lines """
        spec = self.multispec.current_spectrometer()
        if spec is None:
            return self.disable()

        self.update_from_gui()

    def fast_callback(self):
        """ The user clicked "[x] fast" on the widget """
        spec = self.multispec.current_spectrometer()
        if spec is None:
            return self.disable()

        spec.settings.state.area_scan_fast = self.cb_fast.isChecked()
        spec.change_device_setting("area_scan_fast", spec.settings.state.area_scan_fast)

    def disable(self):
        log.debug("disabling area scan")
        self.enabled = False
        self.data = None
        self.last_received_time = None
        self.frame_image.setVisible(False)
        self.cb_enable.setChecked(False)

    def enable_callback(self):
        """ The user clicked "[x] enable" on the widget """
        spec = self.multispec.current_spectrometer()
        if spec is None:
            return self.disable()

        self.enabled = self.cb_enable.isChecked()

        # apply and reverse these in careful order
        if self.enabled:
            log.debug("enabling area scan")
            self.frame_image.setVisible(True)
            self.progress_bar.setVisible(True)
            spec.change_device_setting("detector_offset", self.delay_ms)
            spec.change_device_setting("area_scan_enable", True)
        else:
            spec.change_device_setting("area_scan_enable", False)
            spec.change_device_setting("detector_offset", spec.settings.eeprom.detector_offset)
            spec.settings.state.ignore_timeouts_for(sec=5)
            self.disable()

        self.update_visibility()

        # update sizing
        if self.enabled:
            self.update_from_gui()
            self.ignored = 0

    def save_callback(self):
        spec = self.multispec.current_spectrometer()
        if spec is None:
            return self.disable()

        today_dir = self.save_options.generate_today_dir()
        basename = "area-scan-%s-%s" % (datetime.datetime.now().strftime("%Y%m%d-%H%M%S"),
                                        spec.settings.eeprom.serial_number)

        # save image
        if self.image is not None:
            pathname_png = os.path.join(today_dir, basename + ".png")
            log.debug("saving qimage %s", pathname_png)
            self.image.save(pathname_png)

        # save table
        pathname_csv = os.path.join(today_dir, basename + ".csv")
        log.debug("saving csv %s", pathname_csv)
        np.savetxt(pathname_csv, self.data, fmt="%d", delimiter=",")

        # don't use .info, as Hardware Capture doesn't include the Drawer
        self.marquee.toast("saved %s" % basename)

    # ##########################################################################
    # private methods
    # ##########################################################################

    def update_from_gui(self):
        """ update the area scan parameters from the GUI widgets """
        spec = self.multispec.current_spectrometer()
        if spec is None:
            return self.disable()

        (old_start, old_stop) = (self.start_line, self.stop_line)
        self.start_line = self.sb_start.value()
        self.stop_line  = self.sb_stop.value()
        if self.start_line > self.stop_line:
            (self.start_line, self.stop_line) = (self.stop_line, self.start_line)

        if old_start != self.start_line or old_stop != self.stop_line:
            log.debug("applying new ROI (%d, %d)", self.start_line, self.stop_line)
            spec.change_device_setting("vertical_binning", (self.start_line, self.stop_line))
            self.resize()

    def update_progress_bar(self):
        """ we've updated the start/stop lines, so resize the image """
        if self.last_received_time is None:
            log.debug("update_progress_bar: initializing")
            self.last_received_time = datetime.datetime.now()
            return

        elapsed_ms = round(1000 * (datetime.datetime.now() - self.last_received_time).total_seconds())
        log.debug("update_progress_bar: elapsed = %d ms (estimate was %d)", elapsed_ms, self.progress_bar.maximum())
        if elapsed_ms > 5000:
            log.debug("update_progress_bar: ignoring overlong elapsed")
            self.last_received_time = datetime.datetime.now()
            return
    
        self.progress_bar.setVisible(True)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(elapsed_ms)
        self.progress_bar.setValue(1)
        self.progress_bar_timer.start(100)

        self.last_received_time = datetime.datetime.now()

    def tick_progress_bar(self):
        if not self.enabled:
            log.debug("tick_progress_bar: disabled so invisibling")
            self.progress_bar.setVisible(False)
            self.last_received_time = None
            return
        elif self.last_received_time is None:
            return
        elapsed_ms = round(1000 * (datetime.datetime.now() - self.last_received_time).total_seconds())
        self.progress_bar.setValue(elapsed_ms)
        self.progress_bar_timer.start(100)

    def process_spectrum(self, spectrum, row):
        width = len(spectrum)
        self.lb_current.setText(str(row))

        if row < self.start_line or row > self.stop_line:
            log.debug("ignoring area scan row %d (ROI %d, %d)", row, self.start_line, self.stop_line)
        else:
            if self.data is None:
                self.resize()

            index = row - self.start_line # absolute (detector) vs ROI (image)
            self.data[index] = spectrum

    def update_curve_color(self, spec):
        curve = self.multispec.get_hardware_feature_curve(self.name, spec.device_id)
        if curve == None:
            return
        curve.opts["pen"] = spec.color

    def resize(self):
        spec = self.multispec.current_spectrometer()
        if spec is None:
            return self.disable()

        data_h = self.stop_line - self.start_line + 1
        data_w = spec.settings.pixels()
        log.debug("resize: data_w = %d, data_h = %d (start %d, stop %d)", data_w, data_h, self.start_line, self.stop_line)
        self.data = np.zeros((data_h, data_w), dtype=np.float32)

        self.frame_image.setMinimumHeight(data_h + 40)
        self.graphics_view.setMinimumHeight(150)

        # if spec.settings.is_micro():
        #    self.image.move(0, 0)

    def finish_update(self):
        """
        @todo qimage2ndarray technically provides access to the existing QImage's 
              underlying data, so we could probably simply update the existing 
              QImage rather than make a whole new QPixmap.
        """
        if self.data is None:
            return

        # graph the rotated 2D array
        self.image = qimage2ndarray.array2qimage(self.data, normalize=True)
        pixmap = QtGui.QPixmap(self.image).scaledToWidth(self.frame_image.width())
        self.scene.clear() # @todo - anything leak here? need to deleteLater old pixmap?
        self.scene.addPixmap(pixmap)

        # vertically bin the on-screen image for the "live" spectrum
        total = np.sum(self.data, axis=0)
        self.set_curve_data(self.curve_live, total, label="AreaScanFeature.finish_update")
