import logging

from enlighten.EnlightenFeature import EnlightenFeature
from enlighten.data.TableModel import TableModel

log = logging.getLogger(__name__)

class ScopeTableFeature(EnlightenFeature):

    ROW = 3

    def __init__(self, ctl):
        super().__init__(ctl)

        cfu = ctl.form.ui

        # note this is the same grid layout used by enlighten.scope.Graph
        self.layout           = cfu.layout_scope_capture_graphs

        self.clear()

        self.create_table_view()

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

    def set_visible(self, flag):
        if flag:
            self.layout_graphs.setRowMinimumHeight(self.ROW, 100)
        else:
            self.layout_graphs.setRowMinimumHeight(self.ROW, 0)

    def clear(self):
        self.model = None
        self.dataframe = None
        self.table_view.setModel(None)

    def set_dataframe(self, dataframe):
        self.dataframe = dataframe
        self.model = TableModel(self.dataframe)
        self.table_view.setModel(self.model)
