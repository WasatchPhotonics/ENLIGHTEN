import logging

from PySide6 import QtGui, QtCore, QtWidgets

log = logging.getLogger(__name__)

class ConfirmWidget(QtWidgets.QFrame):
    """
    Widget to display confirmation question when a ThumbnailWidget's trash 
    button is clicked. Each ThumbnailWidget has one of these, although it's 
    normally hidden.
    """
    def __init__(self, 
            callback_yes,
            parent,
            stylesheets,

            callback_no = None,
            message = "Delete from disk?"):
        super(ConfirmWidget, self).__init__()

        self.stylesheets = stylesheets

        self.setStyleSheet(self.stylesheets.get("clear_border"))
        self.setMinimumWidth(170)
        self.setMaximumWidth(170)
        self.setMinimumHeight(100)
        self.setMaximumHeight(100)

        self.setParent(parent)
        self.setVisible(False)

        # MZ: why is this a QPushButton vs QLabel?
        self.button_question = self.add_small_push_button(loc=(10, 25))
        self.button_question.setText(message)
        self.button_question.setMinimumWidth(135)
        self.button_question.setStyleSheet(self.stylesheets.get("red_text"))

        self.button_yes = self.add_small_push_button(icon_name="yes_xicon", size=(35, 30), icon_size=(28, 28), loc=(10, 55))
        self.button_yes.setMinimumWidth(65)
        self.button_yes.setText("Yes")
        self.button_yes.clicked.connect(callback_yes)

        self.button_no = self.add_small_push_button(icon_name="no_xicon", size=(35, 30), icon_size=(28, 28), loc=(80, 55))
        self.button_no.setMinimumWidth(65)
        self.button_no.setText("No")
        self.button_no.clicked.connect(self.default_callback_no if callback_no is None else callback_no)

    def default_callback_no(self):
        """ By default, just dismiss (hide) widget if user clicks No. """
        self.setVisible(False)

    def add_small_push_button(self, icon_name="default", size=(30, 30), icon_size=(20, 20), loc=None):
        """ @todo merge with ThumbnailWidget.create_button, move to util? """
        icon = QtGui.QIcon()
        icon.addPixmap(":/greys/images/grey_icons/%s.svg" % icon_name)

        # DO NOT add any whitespace in the string "qlineargradient(spread:pad":
        # https://www.qtcentre.org/threads/46371-QSS-qlineargradient-not-working-when-inserting-whitespaces
        style = """
            QPushButton:hover { border: 1px solid #78879b; color: silver; }
            QPushButton { border-color: rgb(0,0,0);}
            QPushButton { background-color: qlineargradient(spread:pad, 
                                                  x1:0.5, y1:1, 
                                                  x2:0.5, y2:0,
                                                  stop:0 rgba(67, 67, 67, 255),
                                                  stop:1 rgba(96, 96, 96, 255) ); 
                          border-radius: 5px; }
        """

        button = QtWidgets.QPushButton()
        button.setParent(self)
        button.setIcon(icon)
        button.resize(size[0], size[1])
        button.setIconSize(QtCore.QSize(icon_size[0], icon_size[1]))
        button.setStyleSheet(style)

        if loc is not None:
            button.move(loc[0], loc[1])

        return button
