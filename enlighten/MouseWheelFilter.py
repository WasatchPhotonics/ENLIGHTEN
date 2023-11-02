import logging

import PySide6
from PySide6.QtCore import QObject, QEvent

log = logging.getLogger(__name__)

class MouseWheelFilter(QObject):
    """
    This should be applied to QVerticalSlider widgets where you don't want the 
    mouse-wheel to affect the widget EVER (whether it's in focus or not).

    In contrast, ScrollStealFilter allows the mouse-wheel to change the widget
    after you've clicked to focus it (appropriate for QSpinBox, QDoubleSpinBox, 
    QComboBox etc).

    @see https://stackoverflow.com/questions/5821802/qspinbox-inside-a-qscrollarea-how-to-prevent-spin-box-from-stealing-focus-when
    @see https://doc.qt.io/qtforpython/overviews/eventsandfilters.html
    """
    def __init__(self, parent):
        super().__init__(parent)

    def eventFilter(self, o: QObject, e: QEvent):
        if e.type() == QEvent.Wheel:
            e.ignore()
            return True
        return False
