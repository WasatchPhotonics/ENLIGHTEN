import os
import logging
import datetime
import pyqtgraph
import numpy as np
import qimage2ndarray

from PIL import Image, ImageStat

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

    In ALL of the following historical implementations, one pixel is "stomped" 
    by the firmware with the original line index to aid in visual reconstruction
    of the 2D image. Unless otherwise specified, that is pixel 0.

    @par Slow Mode (Legacy)

    Early AreaScan implementations in firmware sent out a single line in response
    to a single ACQUIRE opcode; 64 ACQUIRE requests had to be sent to read-out an
    entire 64-row detector. Each line came from a separate integration (one line
    per frame).

    @par Continuous Area Scan (IMX385)

    Once the firmware is set into Area Scan mode, the STM32 will stream an
    endless sequence of ACQUIRE signals into the FPGA. Each time the FPGA 
    receives one, it will read-out the next line to firmware and the host,
    wrapping-around when one frame completes and automatically beginning the
    next one. This continues until the spectrometer is taken out of Area Scan
    mode.

    @par Frame

    With IDS cameras, the vender drivers will automatically collect full-frame
    images from the camera, such that vertical binning is performed in software.
    On such devices, when Area Scan is enabled, Wasatch.PY will automatically
    include each full-frame image along with the vertically binned spectrum,
    so the image can be directly displayed in ENLIGHTEN.

    """

    # ##########################################################################
    # Lifecycle
    # ##########################################################################

    def __init__(self, ctl):
        self.ctl = ctl
        cfu = ctl.form.ui

        self.bt_save            = cfu.pushButton_area_scan_save
        self.cb_enable          = cfu.checkBox_area_scan_enable
        self.cb_normalize       = cfu.checkBox_area_scan_normalize
        self.cb_fit             = cfu.checkBox_area_scan_fit
        self.frame_image        = cfu.frame_area_scan_image
        self.frame_live         = cfu.frame_area_scan_live
        self.graphics_view      = cfu.graphicsView_area_scan
        self.layout_live        = cfu.layout_area_scan_live
        self.lb_elapsed         = cfu.label_area_scan_frame_elapsed
        self.lb_current         = cfu.label_area_scan_current_line
        self.lb_frame_count     = cfu.label_area_scan_frame_count
        self.progress_bar       = cfu.progressBar_area_scan
        self.sb_start           = cfu.spinBox_area_scan_start_line
        self.sb_stop            = cfu.spinBox_area_scan_stop_line
        self.sb_delay_ms        = cfu.spinBox_area_scan_delay_ms
        self.sb_step            = cfu.spinBox_area_scan_line_step

        self.data = None
        self.enabled = False
        self.visible = False
        self.normalize = True
        self.fit = True
        self.start_line = 0
        self.stop_line = 63
        self.ignored = 0
        self.frame_count = 0
        self.delay_ms = self.sb_delay_ms.value()
        self.image = None
        self.name = "Area_Scan"
        self.last_received_time = None
        self.last_line = 0
        self.last_elapsed_sec = 0
        self.curve_live = None
        self.frame_start = datetime.datetime.now()

        self.pen_start = self.ctl.gui.make_pen(color="green", width=2)
        self.pen_stop  = self.ctl.gui.make_pen(color="red", width=2)
        self.pen_line  = self.ctl.gui.make_pen(color="yellow")

        # create widgets we can't / don't pass in
        self.create_widgets()

        self.cb_fit.setChecked(True)
        self.cb_normalize.setChecked(True)
        self.progress_bar.setVisible(False)

        self.bt_save     .clicked        .connect(self.save_callback)
        self.cb_normalize.stateChanged   .connect(self.normalize_callback)
        self.cb_fit      .stateChanged   .connect(self.fit_callback)
        self.cb_enable   .stateChanged   .connect(self.enable_callback)
        self.sb_start    .valueChanged   .connect(self.roi_callback)
        self.sb_stop     .valueChanged   .connect(self.roi_callback)
        self.sb_delay_ms .valueChanged   .connect(self.delay_callback)
        self.sb_step     .valueChanged   .connect(self.step_callback)

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

        # PyQtChart to hold the "summed" graph beneath
        # (why not just put graphicsscene atop scope chart...?)
        self.chart_live = pyqtgraph.PlotWidget(name="Area Scan Live")
        self.curve_live = self.chart_live.plot([], pen=self.ctl.gui.make_pen(widget="area_scan_live"))
        self.layout_live.addWidget(self.chart_live)

    def disconnect(self):
        log.debug("disconnecting")
        spec = self.ctl.multispec.current_spectrometer()
        if spec is not None:
            if self.enabled and spec.settings.state.area_scan_enabled:
                self.cb_enable.setChecked(False)
        self.update_visibility()

    # ##########################################################################
    # public methods
    # ##########################################################################

    ## @todo mess with is_supported etc if appropriate
    def update_visibility(self):
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return self.disable()

        # self.frame_live.setVisible(not (self.enabled and spec.settings.is_imx()))
        self.frame_live.setVisible(True)

        roi = spec.settings.get_vertical_roi()
        if roi is not None:
            log.debug("initializing ROI %s", roi)
            self.sb_start.setValue(roi.start)
            self.sb_stop .setValue(roi.end)
        else:
            log.debug("spectrometer has no vertical ROI")
            self.sb_start.setValue(0)
            self.sb_stop .setValue(spec.settings.eeprom.active_pixels_vertical - 1)

        if spec.settings.is_imx():
            self.sb_start.setEnabled(True)
            self.sb_stop.setEnabled(True)
            self.sb_delay_ms.setEnabled(False)
        else:
            # Hamamatsu
            self.sb_start.setEnabled(False)
            self.sb_stop.setEnabled(False)

        self.frame_count = 0 # could move to app_settings

    def process_reading(self, reading):
        if reading is None:
            return

        if not self.enabled and reading.spectrum is not None:
            # area scan isn't running, so just update the "live" spectrum from 
            # the latest reading
            self.ctl.set_curve_data(self.curve_live, y=reading.spectrum)
            return

        if reading.area_scan_image is not None:
            self.process_reading_with_area_scan_image(reading)

    # ##########################################################################
    # callbacks
    # ##########################################################################

    def step_callback(self):
        """ the user changed the step spinner """
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return self.disable()

        spec.settings.state.area_scan_line_step = self.sb_step.value()
        spec.change_device_setting("area_scan_line_step", spec.settings.state.area_scan_line_step)

    def delay_callback(self):
        """ the user changed the delay_ms spinner """
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return self.disable()

        self.delay_ms = self.sb_delay_ms.value()
        if self.enabled:
            spec.change_device_setting("detector_offset", self.delay_ms)

    def roi_callback(self):
        """ the user changed the start/stop lines """
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return self.disable()

        self.update_from_gui()

    def normalize_callback(self):
        """ The user clicked "[x] normalize" on the widget """
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return self.disable()
        self.normalize = self.cb_normalize.isChecked()

    def fit_callback(self):
        """ The user clicked "[x] fit" on the widget """
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return self.disable()
        self.fit = self.cb_fit.isChecked()

    def disable(self):
        log.debug("disabling area scan")
        self.enabled = False
        self.data = None
        self.last_received_time = None
        self.frame_image.setVisible(False)
        self.cb_enable.setChecked(False)

    def enable_callback(self):
        """ The user clicked "[x] enable" on the widget """
        spec = self.ctl.multispec.current_spectrometer()
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
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return self.disable()

        today_dir = self.ctl.save_options.generate_today_dir()
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

        self.ctl.marquee.info("saved %s" % basename)

    # ##########################################################################
    # private methods
    # ##########################################################################

    def update_from_gui(self):
        """ update the area scan parameters from the GUI widgets """
        spec = self.ctl.multispec.current_spectrometer()
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
        self.lb_current.setText(str(row))

        if row < self.start_line or row > self.stop_line:
            log.debug("ignoring area scan row %d (ROI %d, %d)", row, self.start_line, self.stop_line)
        else:
            if self.data is None:
                self.resize()

            index = row - self.start_line # absolute (detector) vs ROI (image)
            self.data[index] = spectrum

    def process_reading_with_area_scan_image(self, reading):
        spectrum = reading.spectrum
        asi = reading.area_scan_image
        self.resize(area_scan_image=asi)

        if asi.pathname_png is not None:
            self.process_reading_with_area_scan_image_png(reading)
        elif asi.data is not None:
            self.process_reading_with_area_scan_image_data(reading)

        if reading.spectrum is not None:
            self.ctl.set_curve_data(self.curve_live, reading.spectrum)

    def process_reading_with_area_scan_image_data(self, reading):
        """ 
        We have received a Reading with an AreaScanImage with .data populated 
        (implicitly a NumPy array), such as generated on XS spectrometers from
        wasatch.FID.get_area_scan_xs.
        """
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return

        try:
            asi = reading.area_scan_image
            line_index = asi.line_index 
            data = asi.data
            h, w = data.shape

            # optionally normalize
            if self.normalize:
                lo = np.min(data)
                hi = np.max(data)
                data = (data - lo) / (hi - lo)
                data *= 65535
            data = data.astype(np.uint16)

            # generate QImage from source data
            self.image = QtGui.QImage(data, w, h, w*2, QtGui.QImage.Format_Grayscale16)
            qpixmap = QtGui.QPixmap.fromImage(self.image)

            self.scene.clear()
            self.scene.addPixmap(qpixmap)

            start = spec.settings.eeprom.roi_vertical_region_1_start
            stop  = spec.settings.eeprom.roi_vertical_region_1_end

            # add three horizontal marker lines ATOP the image to show bounds and progress
            log.debug(f"adding green/red lines at (start {start}, stop {stop}) on image (width {w}, height {h}), line_index {line_index}")
            margin = 15
            self.scene.addLine(-margin, start,      w + margin, start,      self.pen_start)
            self.scene.addLine(-margin, line_index, w + margin, line_index, self.pen_line) 
            self.scene.addLine(-margin, stop,       w + margin, stop,       self.pen_stop)

            # optionally scale entire QGraphicsView
            if self.fit:
                w_ratio = self.frame_image.width()  / self.scene.width()
                h_ratio = self.frame_image.height() / self.scene.height()
                ratio = min(w_ratio, h_ratio)
                if ratio < 1:
                    t = QtGui.QTransform()
                    t.scale(ratio, ratio)
                    self.graphics_view.setTransform(t)

            # display current line
            self.lb_current.setText(str(line_index))

            # display timing
            if line_index < self.last_line:
                self.last_elapsed_sec = (datetime.datetime.now() - self.frame_start).total_seconds()
                self.frame_start = datetime.datetime.now()
            elapsed_sec = (datetime.datetime.now() - self.frame_start).total_seconds()
            self.lb_elapsed.setText(f"{elapsed_sec:.2f} (last {self.last_elapsed_sec:.2f})")
            self.last_line = line_index

        except:
            log.error("failed to render AreaScanImage data", exc_info=1)

    def process_reading_with_area_scan_image_png(self, reading):
        """ we have received a Reading with an AreaScanImage with pathname_png populated """
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return

        asi = reading.area_scan_image
        try:
            if self.normalize:
                self.normalize_png(asi.pathname_png)
            qpixmap = QtGui.QPixmap(asi.pathname_png)
            self.scene.clear()
            self.scene.addPixmap(qpixmap)

            scale = 1
            if asi.height is not None and asi.height_orig is not None:
                scale = 1.0 * asi.height / asi.height_orig
                
            start_line = spec.settings.eeprom.roi_vertical_region_1_start
            stop_line = spec.settings.eeprom.roi_vertical_region_1_end

            self.scene.addLine(-10, scale*start_line, qpixmap.width() + 10, scale*start_line, self.pen_start)
            self.scene.addLine(-10, scale*stop_line,  qpixmap.width() + 10, scale*stop_line,  self.pen_stop)
        except:
            log.error("failed to display PNG", exc_info=1)

    def normalize_png(self, pathname_png):
        try:
            img = Image.open(pathname_png).convert('L')
            stat = ImageStat.Stat(img)
            mean_brightness = stat.mean[0]
            img_array = np.array(img)
            normalized_img_array = img_array / mean_brightness * 100 
            normalized_img = Image.fromarray(np.uint8(normalized_img_array))
            normalized_img.save(pathname_png)
        except Exception as ex:
            log.error(f"normalize_png: caught {ex}", exc_info=1)

    def update_curve_color(self, spec):
        """ Required callback for Multispec.strip_features? """
        curve = self.ctl.multispec.get_hardware_feature_curve(self.name, spec.device_id)
        if curve is None:
            return
        curve.opts["pen"] = spec.color

    def resize(self, area_scan_image=None):
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return self.disable()

        if area_scan_image is None:
            # data_h = self.stop_line - self.start_line + 1
            data_h = spec.settings.eeprom.active_pixels_vertical
            data_w = spec.settings.pixels()
        else:
            data_h = area_scan_image.height
            data_w = area_scan_image.width

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
        self.ctl.set_curve_data(self.curve_live, total)
