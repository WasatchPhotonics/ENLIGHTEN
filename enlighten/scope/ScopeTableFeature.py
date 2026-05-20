import logging

from enlighten import common
from enlighten.EnlightenFeature import EnlightenFeature
from enlighten.data.TableModel import TableModel

if common.use_pyside2():
    from PySide2 import QtWidgets, QtCore
    from PySide2.QtCore import Qt
else:
    from PySide6 import QtWidgets, QtCore
    from PySide6.QtCore import Qt

log = logging.getLogger(__name__)

class ScopeTableFeature(EnlightenFeature):

    ROW = 3

    def __init__(self, ctl):
        super().__init__(ctl)

        cfu = ctl.form.ui

        # note this is the same grid layout used by enlighten.scope.Graph
        self.layout = cfu.layout_scope_capture_graphs

        self.visible = False
        self.table_view = None

        self.hide()

    def set_dataframe(self, dataframe):
        """ This creates and shows the table if not already created and visible, then fills the data """
        if not self.visible:
            self.create_table_view()
            self.visible = True

        model = TableModel(dataframe)
        self.table_view.setModel(model)

    def hide(self):
        """ This hides the table by destroying everything. It's cheap to recreate via set_dataframe. """
        if not self.visible:
            return

        if self.table_view is not None:
            self.table_view.deleteLater()
            self.table_view = None

        # do we need to grab and clear the item at self.layout.itemAtPosition(self.ROW, 0)?

        self.layout.setRowMinimumHeight(self.ROW, 0)
        self.visible = False

    def create_table_view(self):
        log.debug("creating output table widget")
        self.table_view = QtWidgets.QTableView()
        self.table_view.setAccessibleName("Pandas Output")

        header = self.table_view.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

        # TableView added to row 4 of 3-row Top-Bot-Lft-Rgt, spanning all 3 cols
        #
        # For clarity, that is TWO rows beneath ctl.graph and ctl.alt_graph, 
        # leaving an extra row in case we need to stack graphs vertically at some
        # point.
                                                  #          row  col
                                                  # row col span span
        self.layout.addWidget(self.table_view, self.ROW,  0,   1,   3) 
        self.layout.setRowStretch(self.ROW, 0)
        self.layout.setRowMinimumHeight(self.ROW, 100)

    def add_copy_dataframe_to_clipboard_button(self):
        if False:
            b = QtWidgets.QPushButton()
            b.setText("Copy to Clipboard")
            b.setMinimumHeight(30) 
            b.pressed.connect(self.copy_dataframe_to_clipboard)
            b.setToolTip("Copy table to Clipboard")

            hbox = QtWidgets.QHBoxLayout()
            hbox.addWidget(b)

            self.plugin_fields_layout.addLayout(hbox)

    def copy_dataframe_to_clipboard(self):
        if self.dataframe is not None:
            self.ctl.clipboard.copy_dataframe(self.dataframe)
