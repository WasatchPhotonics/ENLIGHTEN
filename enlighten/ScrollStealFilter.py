import logging

import PySide2
from PySide2.QtCore import QObject, QEvent

log = logging.getLogger(__name__)

# see https://stackoverflow.com/questions/5821802/qspinbox-inside-a-qscrollarea-how-to-prevent-spin-box-from-stealing-focus-when
# and https://doc.qt.io/qtforpython/overviews/eventsandfilters.html
class ScrollStealFilter(QObject):
    def __init__(self, parent):
        super().__init__(parent)

    def eventFilter(self, o: QObject, e: QEvent):
        if e.type() == QEvent.Wheel and not o.hasFocus():
            e.ignore()
            return True
        return False
