import sys
import time
import random
import pytest
import logging
import threading
from PySide2 import QtCore
from PySide2.QtTest import QTest

from enlighten import common
import scripts.Enlighten as enlighten
from wasatch.MockUSBDevice import MockUSBDevice
from conftest import wait_until, create_sim_spec, disconnect_spec

log = logging.getLogger(__name__)

class TestGUI:

    ############
    # Test Cases
    ############

    # description: tests that the window title is ENLIGHTEN
    # author: Evan Dort
    def test_tile(self,app):
        assert "ENLIGHTEN" in app.controller.form.windowTitle()

    # description: release test that the first page is the scope technique and spectra is set to play
    # author: Evan Dort
    @pytest.mark.release
    def test_init_tech_and_play(self,app):
        curr_tech = app.controller.page_nav.current_technique
        paused = app.controller.vcr_controls.is_paused()
        assert curr_tech == common.Techniques.SCOPE and not paused

    # description: test that changing the axis combo box changes the graph axes
    # author: Evan Dort
    def test_axis_change(self,app):
        @wait_until(timeout=1000)
        def check():
            return str(app.controller.graph.plot.getPlotItem().getAxis('bottom').labelString()) 
        res = check()
        # label string is written in HTML, so 'in' needs to be used
        if not common.AxesHelper.get_pretty_name(common.Axes.WAVELENGTHS) in res:
            assert False, f"graph name not properly initialized to wavelengths, it was {res}"
        app.controller.graph.combo_axis.setCurrentIndex(2)
        app.controller.graph.update_axis_callback()
        res = check()
        assert common.AxesHelper.get_pretty_name(common.Axes.WAVENUMBERS) in res

    # description: test that initially the advanced options are hidden from the user
    # author: Evan Dort
    def test_hidden_advanced(self,app):
        option_frame = app.controller.form.ui.frame_AdvancedOptions_SubOptions.isHidden()
        tec_control = not app.controller.form.ui.checkBox_AdvancedOptions_TECControl.isVisible()
        baseline_corr = not app.controller.form.ui.checkBox_AdvancedOptions_BaselineCorrection.isVisible()
        area_scan = not app.controller.form.ui.checkBox_AdvancedOptions_AreaScan.isVisible()
        post_process = not app.controller.form.ui.checkBox_AdvancedOptions_PostProcessing.isVisible()
        assert option_frame and tec_control and baseline_corr and area_scan and post_process

    # description: test that the sub options become visible when the advanced options is checked
    # author: Evan Dort
    def test_enable_hidden_advanced(self,app):
        option_cb = app.controller.form.ui.checkBox_AdvancedOptions
        option_cb.click() 
        @wait_until(timeout=7000)
        def check():
            sub_opt = app.controller.advanced_options.fr_subopt.isVisible()
            if sub_opt:
                return True
        res = check()
        assert res == True

    # description: test that initially box car smoothing is 0
    # author: Evan Dort
    def test_boxcar_init(self,app):
        sim_spec = create_sim_spec(app,"WP-00887","WP-00887-mock.json")
        boxcar_spin = app.controller.form.ui.spinBox_boxcar_half_width
        boxcar_spin_val = boxcar_spin.value()
        assert boxcar_spin_val == 0
        disconnect_spec(app,sim_spec)

    # desscription: test that clicking the boxcar buttons increments the boxcar value
    # author: Evan Dort
    def test_boxcar_gui(self,app):
        sim_spec = create_sim_spec(app,"WP-00887","WP-00887-mock.json")
        sim_spec.single_reading = True
        spec_obj = app.controller.multispec.get_spectrometer(sim_spec)
        spec_obj.settings.state.boxcar_half_width = 2
        box_up = app.controller.form.ui.pushButton_boxcar_half_width_up
        boxcar_spin = app.controller.form.ui.spinBox_boxcar_half_width
        boxcar_spin_val = boxcar_spin.value()
        inc_num = random.randint(1,5)
        for i in range(inc_num):
            QTest.mouseClick(box_up,QtCore.Qt.LeftButton)
        gui_match = boxcar_spin.value() == boxcar_spin_val + inc_num
        assert gui_match
        disconnect_spec(app,sim_spec)

    # description: test that clicking the scan average button increments the value
    # author: Evan Dort
    def test_scan_avg(self,app):
        sim_spec = create_sim_spec(app,"WP-00887","WP-00887-mock.json")
        scan_avg_spin = app.controller.form.ui.spinBox_scan_averaging
        scan_avg_up = app.controller.form.ui.pushButton_scan_averaging_up
        init_avg_val = scan_avg_spin.value()
        inc_num = random.randint(1,5)
        for i in range(inc_num):
            QTest.mouseClick(scan_avg_up, QtCore.Qt.LeftButton)
        gui_match = scan_avg_spin.value() == init_avg_val + inc_num
        avg_label_visible = app.controller.form.ui.label_scan_averaging.isHidden()
        assert init_avg_val == 1 and gui_match and avg_label_visible
        disconnect_spec(app,sim_spec)

    # description: test that the initial laser unit is in mW
    # author: Evan Dort
    def test_laser_default_mW(self,app):
        sim_spec = create_sim_spec(app,"WP-00887","WP-00887-mock.json")
        cb_laser_unit = app.controller.form.ui.comboBox_laser_power_unit
        assert cb_laser_unit.currentText() == "milliwatts (mW)"
        disconnect_spec(app,sim_spec)

    # description: test that clicking the invert button changes the graph state
    # author: Evan Dort
    def test_invert_x_axis(self,app):
        app.controller.form.ui.pushButton_invert_x_axis.click()
        graph_state = app.controller.graph.plot.getPlotItem().getViewBox().getState()
        assert graph_state["xInverted"]

    # description: test that clicking the lock buttons changes the graph state
    # author: Evan Dort
    def test_lock_axes(self,app):
        btn_lock_ax = app.controller.form.ui.pushButton_lock_axes
        graph_state = app.controller.graph.plot.getPlotItem().getViewBox().getState()
        initial_unlock = graph_state["autoRange"] != [False, False]
        btn_lock_ax.click()
        graph_state = app.controller.graph.plot.getPlotItem().getViewBox().getState()
        locked = graph_state["autoRange"] == [False, False]
        btn_lock_ax.click()
        assert initial_unlock and locked

    # description: test that default graph state is to scale axes
    # author: Evan Dort
    def test_default_graph_axes_scale(self,app):
        btn_lock_ax = app.controller.form.ui.pushButton_lock_axes
        graph_state = app.controller.graph.plot.getPlotItem().getViewBox().getState()
        initial_unlock = graph_state["autoRange"] != [False, False]
        assert initial_unlock

    # description: test that the cursor is initially false and made visible by clicking the gui button
    # author: Evan Dort
    def test_graph_cursor(self,app):
        cursor = app.controller.cursor
        init_visible = cursor.cursor.isVisible()
        app.controller.form.ui.checkBox_cursor_scope_enabled.click()
        visible = cursor.cursor.isVisible()
        assert not init_visible and visible

    # description: test that clicking the gui element shows the point markers
    # author: Evan Dort
    def test_graph_markers(self,app):
        sim_spec = create_sim_spec(app,"WP-00887","WP-00887-mock.json")
        spec_obj = app.controller.multispec.get_spectrometer(sim_spec)
        btn_markers = app.controller.form.ui.checkBox_graph_marker
        btn_markers.click()
        assert spec_obj.curve.opts["symbol"] is not None
        disconnect_spec(app,sim_spec)






