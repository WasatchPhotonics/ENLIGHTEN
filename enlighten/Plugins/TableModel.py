import logging

from enlighten import common

if common.use_pyside2():
    from PySide2 import QtCore
    from PySide2.QtCore import Qt
else:
    from PySide6 import QtCore
    from PySide6.QtCore import Qt

log = logging.getLogger(__name__)

##
# A custom QAbstractTableModel taking a Pandas DataFrame as input.
#
# @see https://www.mfitzp.com/tutorials/qtableview-modelviews-numpy-pandas/
class TableModel(QtCore.QAbstractTableModel):

    def __init__(self, df):
        super(TableModel, self).__init__()
        self._df = df

    def data(self, index, role):
        if role == Qt.DisplayRole:
            value = self._df.iloc[index.row(), index.column()]
            return str(value)

    def rowCount(self, index):
        return self._df.shape[0]

    def columnCount(self, index):
        return self._df.shape[1]

    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._df.columns[section])

            if orientation == Qt.Vertical:
                return str(self._df.index[section])

