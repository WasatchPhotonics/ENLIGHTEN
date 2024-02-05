import logging

from enlighten import common

if common.use_pyside2():
    from PySide2.QtCore import QObject, QEvent
else:
    from PySide6.QtCore import QObject, QEvent

log = logging.getLogger(__name__)

class ScrollStealFilter(QObject):
    """
    This should be applied to QSpinbox, QDoubleSpinBox and QComboBox objects
    where you want the mouse-wheel to be usable AFTER you've clicked to focus
    the widget, but should not trigger inadvertent events when you've simply
    "scrolled past" the widget within a QScrollArea.

    In contrast, MouseWheelFilter prevents the mouse-wheel from ever affecting
    the widget (appropriate for QVerticalSliders).

    @see https://stackoverflow.com/questions/5821802/qspinbox-inside-a-qscrollarea-how-to-prevent-spin-box-from-stealing-focus-when
    @see https://doc.qt.io/qtforpython/overviews/eventsandfilters.html
    """
    def __init__(self, parent):
        super().__init__(parent)

    def eventFilter(self, o: QObject, e: QEvent):
        if e.type() == QEvent.Wheel: # and not o.hasFocus():
            e.ignore()
            return True
        return False
