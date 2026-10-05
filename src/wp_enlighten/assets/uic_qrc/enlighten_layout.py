# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'enlighten_layout.ui'
##
## Created by: Qt User Interface Compiler version 6.11.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractScrollArea, QAbstractSpinBox, QApplication, QCheckBox,
    QComboBox, QDoubleSpinBox, QFormLayout, QFrame,
    QGraphicsView, QGridLayout, QGroupBox, QHBoxLayout,
    QLabel, QLayout, QLineEdit, QMainWindow,
    QProgressBar, QPushButton, QRadioButton, QScrollArea,
    QSizePolicy, QSlider, QSpacerItem, QSpinBox,
    QSplitter, QStackedWidget, QTabWidget, QTextEdit,
    QToolButton, QVBoxLayout, QWidget)
import grey_icons_rc
import throbbers_rc
import spectrums_rc
import devices_rc
import darkstyle_icons_rc
import enlighten_icons_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1470, 924)
        MainWindow.setMinimumSize(QSize(0, 0))
        icon = QIcon()
        icon.addFile(u":/application/images/EnlightenIcon.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setStyleSheet(u"/* START: enlighten/assets/stylesheets/default/enlighten.css \n"
"\n"
"   See README_CSS.md for notes.\n"
"\n"
"   borrowed from: https://github.com/ColinDuquesnoy/QDarkStyleSheet \n"
"   original: https://raw.githubusercontent.com/ColinDuquesnoy/QDarkStyleSheet/master/qdarkstyle/style.qss\n"
"             (c92d0c4c996e3e859134492e0f9f7f74bd0e12cd)\n"
"*/\n"
"\n"
"/* QDarkStyleSheet -----------------------------------------------------------\n"
"\n"
"This is the main style sheet, the palette has eight colors.\n"
"\n"
"It is based on three selecting colors, three greyish (background) colors\n"
"plus three whitish (foreground) colors. Each set of widgets of the same\n"
"type have a header like this:\n"
"\n"
"    ------------------\n"
"    GroupName --------\n"
"    ------------------\n"
"\n"
"And each widget is separated with a header like this:\n"
"\n"
"    QWidgetName ------\n"
"\n"
"This makes more easy to find and change some css field. The basic\n"
"configuration is described bellow.\n"
"\n"
"    BACKGROUND"
                        " -----------\n"
"\n"
"        Light  #4D 54 5B   #50 5F 69 (unpressed)\n"
"        Normal #31 36 3B   #32 41 4B (border, disabled, pressed, checked, toolbars, menus)\n"
"        Dark   #23 26 29   #19 23 2D (background)  -&gt; 38 38 38\n"
"\n"
"    FOREGROUND -------------\n"
"                         \n"
"        Light  #EF F0 F1   #F0 F0 F0 (texts/labels)\n"
"        Normal             #AA AA AA (not used yet)\n"
"        Dark   #50 5F 69   #78 78 78 (disabled texts)\n"
"                         \n"
"    SELECTION --------------\n"
"                         \n"
"        Light  #17 9A E0   #14 8C D2 (selection/hover/active)\n"
"        Normal #33 75 A3   #14 64 A0 (selected)\n"
"        Dark   #18 46 5D   #14 50 6E (selected disabled)\n"
"\n"
"If a stranger configuration is required because of a bugfix or anything\n"
"else, keep the comment on the line above so nobody changes it, including the\n"
"issue number.\n"
"\n"
"*/\n"
"/*\n"
"\n"
"See Qt documentation:\n"
"\n"
"  - https://doc.qt.io/qt-5/stylesheet.ht"
                        "ml\n"
"  - https://doc.qt.io/qt-5/stylesheet-reference.html\n"
"  - https://doc.qt.io/qt-5/stylesheet-examples.html\n"
"\n"
"--------------------------------------------------------------------------- */\n"
"/* QWidget ----------------------------------------------------------------\n"
"--------------------------------------------------------------------------- */\n"
"\n"
"* {\n"
"  padding: 0px;\n"
"  margin: 0px;\n"
"  border: 0px;\n"
"  border-style: none;\n"
"  border-image: none;\n"
"  outline: 0;\n"
"}\n"
"\n"
"QWidget {\n"
"  background-color: #383838;\n"
"  color: hsl(0, 0%, 60%);\n"
"  border: none;\n"
"  padding: 0px;\n"
"  selection-background-color: hsl(0, 0%, 70%);\n"
"  selection-color: #F0F0F0;\n"
"}\n"
"\n"
"QWidget:disabled {\n"
"  color: #787878;\n"
"  selection-background-color: #14506E;\n"
"  selection-color: #787878;\n"
"}\n"
"\n"
"QWidget::item:selected {\n"
"    color: #eee;\n"
"    background-color: hsl(0, 0%, 70%);\n"
"}\n"
"\n"
"/*\n"
"    QWidget::item:hover {\n"
"      background-co"
                        "lor: #148CD2;\n"
"      color: #32414B;\n"
"    }\n"
"*/\n"
"\n"
"/* QMainWindow ------------------------------------------------------------\n"
"This adjusts the splitter in the dock widget, not qsplitter\n"
"https://doc.qt.io/qt-5/stylesheet-examples.html#customizing-qmainwindow\n"
"--------------------------------------------------------------------------- */\n"
"\n"
"QMainWindow::separator {\n"
"  background-color: #ccc;\n"
"  border: none;\n"
"  spacing: 0;\n"
"  padding: 2px;\n"
"}\n"
"\n"
"QMainWindow::separator:hover {\n"
"  background-color: hsl(0, 0%, 60%);\n"
"  border: 0px solid #148CD2;\n"
"}\n"
"\n"
"QMainWindow::separator:horizontal {\n"
"  width: 5px;\n"
"  margin-top: 2px;\n"
"  margin-bottom: 2px;\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/toolbar_separator_vertical.png\");\n"
"}\n"
"\n"
"QMainWindow::separator:vertical {\n"
"  height: 5px;\n"
"  margin-left: 2px;\n"
"  margin-right: 2px;\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/toolbar_separator_horizontal.png\");\n"
""
                        "}\n"
"\n"
"/* QToolTip ---------------------------------------------------------------\n"
"https://doc.qt.io/qt-5/stylesheet-examples.html#customizing-qtooltip\n"
"--------------------------------------------------------------------------- */\n"
"\n"
"QToolTip {\n"
"  background-color: #ffc;\n"
"  border: 1px solid #828200;\n"
"  color: #828200;\n"
"  padding: 5px;\n"
"  opacity: 1;\n"
"}\n"
"\n"
"/* QStatusBar -------------------------------------------------------------\n"
"https://doc.qt.io/qt-5/stylesheet-examples.html#customizing-qstatusbar\n"
"--------------------------------------------------------------------------- */\n"
"\n"
"QStatusBar {\n"
"  border: 1px solid #32414B;\n"
"  background: #32414B;\n"
"}\n"
"\n"
"QStatusBar QLabel {\n"
"  background-color: transparent;\n"
"  border: none;\n"
"}\n"
"\n"
"/* QCheckBox --------------------------------------------------------------\n"
"https://doc.qt.io/qt-5/stylesheet-examples.html#customizing-qcheckbox\n"
"-----------------------------------------------"
                        "---------------------------- */\n"
"\n"
"QCheckBox {\n"
"  background-color: transparent;\n"
"  color: #F0F0F0;\n"
"  spacing: 4px;\n"
"  padding-top: 4px;\n"
"  padding-bottom: 4px;\n"
"}\n"
"\n"
"QCheckBox:focus {\n"
"  border: none;\n"
"}\n"
"\n"
"QCheckBox QWidget:disabled {\n"
"  background-color: #383838;\n"
"  color: #787878;\n"
"}\n"
"\n"
"QCheckBox::indicator {\n"
"  margin-left: 4px;\n"
"  height: 16px;\n"
"  width: 16px;\n"
"}\n"
"\n"
"QCheckBox::indicator:unchecked {\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/checkbox_unchecked.png\");\n"
"}\n"
"\n"
"QCheckBox::indicator:unchecked:hover, QCheckBox::indicator:unchecked:focus, QCheckBox::indicator:unchecked:pressed {\n"
"  border: none;\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/checkbox_unchecked_focus.png\");\n"
"}\n"
"\n"
"QCheckBox::indicator:unchecked:disabled {\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/checkbox_unchecked_disabled.png\");\n"
"}\n"
"\n"
"QCheckBox::indicator:checked {\n"
"  image: url(\":/qss_ico"
                        "ns/images/darkstyle_icons/checkbox_checked.png\");\n"
"}\n"
"\n"
"QCheckBox::indicator:checked:hover, QCheckBox::indicator:checked:focus, QCheckBox::indicator:checked:pressed {\n"
"  border: none;\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/checkbox_checked_focus.png\");\n"
"}\n"
"\n"
"QCheckBox::indicator:checked:disabled {\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/checkbox_checked_disabled.png\");\n"
"}\n"
"\n"
"QCheckBox::indicator:indeterminate {\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/checkbox_indeterminate.png\");\n"
"}\n"
"\n"
"QCheckBox::indicator:indeterminate:disabled {\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/checkbox_indeterminate_disabled.png\");\n"
"}\n"
"\n"
"QCheckBox::indicator:indeterminate:focus, QCheckBox::indicator:indeterminate:hover, QCheckBox::indicator:indeterminate:pressed {\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/checkbox_indeterminate_focus.png\");\n"
"}\n"
"\n"
"/* QGroupBox ---------------------------------------------"
                        "-----------------\n"
"https://doc.qt.io/qt-5/stylesheet-examples.html#customizing-qgroupbox\n"
"--------------------------------------------------------------------------- */\n"
"\n"
"QGroupBox {\n"
"  font-weight: bold;\n"
"  border: 1px solid #666;\n"
"  border-radius: 4px;\n"
"  padding: 4px;\n"
"  margin-top: 16px;\n"
"}\n"
"\n"
"QGroupBox::title {\n"
"  subcontrol-origin: margin;\n"
"  subcontrol-position: top left;\n"
"  left: 3px;\n"
"  padding-left: 3px;\n"
"  padding-right: 5px;\n"
"  padding-top: 8px;\n"
"  padding-bottom: 16px;\n"
"}\n"
"\n"
"QGroupBox::indicator {\n"
"  margin-left: 2px;\n"
"  height: 12px;\n"
"  width: 12px;\n"
"}\n"
"\n"
"QGroupBox::indicator:unchecked:hover, QGroupBox::indicator:unchecked:focus, QGroupBox::indicator:unchecked:pressed {\n"
"  border: none;\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/checkbox_unchecked_focus.png\");\n"
"}\n"
"\n"
"QGroupBox::indicator:unchecked:disabled {\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/checkbox_unchecked_disabled.p"
                        "ng\");\n"
"}\n"
"\n"
"QGroupBox::indicator:checked:hover, QGroupBox::indicator:checked:focus, QGroupBox::indicator:checked:pressed {\n"
"  border: none;\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/checkbox_checked_focus.png\");\n"
"}\n"
"\n"
"QGroupBox::indicator:checked:disabled {\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/checkbox_checked_disabled.png\");\n"
"}\n"
"\n"
"/* QRadioButton -----------------------------------------------------------\n"
"https://doc.qt.io/qt-5/stylesheet-examples.html#customizing-qradiobutton\n"
"--------------------------------------------------------------------------- */\n"
"\n"
"QRadioButton {\n"
"  background-color: #383838;\n"
"  color: #F0F0F0;\n"
"  spacing: 4px;\n"
"  padding: 0px;\n"
"  border: none;\n"
"}\n"
"\n"
"QRadioButton:focus {\n"
"  border: none;\n"
"}\n"
"\n"
"QRadioButton:disabled {\n"
"  background-color: #383838;\n"
"  color: #787878;\n"
"  border: none;\n"
"}\n"
"\n"
"QRadioButton QWidget {\n"
"  background-color: #383838;\n"
"  color: "
                        "#F0F0F0;\n"
"  spacing: 0px;\n"
"  padding: 0px;\n"
"  border: none;\n"
"}\n"
"\n"
"QRadioButton::indicator {\n"
"  border: none;\n"
"  margin-left: 4px;\n"
"  height: 16px;\n"
"  width: 16px;\n"
"}\n"
"\n"
"QRadioButton::indicator:unchecked {\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/radio_unchecked.png\");\n"
"}\n"
"\n"
"QRadioButton::indicator:unchecked:hover, QRadioButton::indicator:unchecked:focus, QRadioButton::indicator:unchecked:pressed {\n"
"  border: none;\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/radio_unchecked_focus.png\");\n"
"}\n"
"\n"
"QRadioButton::indicator:unchecked:disabled {\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/radio_unchecked_disabled.png\");\n"
"}\n"
"\n"
"QRadioButton::indicator:checked {\n"
"  border: none;\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/radio_checked.png\");\n"
"}\n"
"\n"
"QRadioButton::indicator:checked:hover, QRadioButton::indicator:checked:focus, QRadioButton::indicator:checked:pressed {\n"
"  border: none;\n"
"  image"
                        ": url(\":/qss_icons/images/darkstyle_icons/radio_checked_focus.png\");\n"
"}\n"
"\n"
"QRadioButton::indicator:checked:disabled {\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/radio_checked_disabled.png\");\n"
"}\n"
"\n"
"/* QMenuBar ---------------------------------------------------------------\n"
"https://doc.qt.io/qt-5/stylesheet-examples.html#customizing-qmenubar\n"
"--------------------------------------------------------------------------- */\n"
"\n"
"QMenuBar {\n"
"  background-color: #32414B;\n"
"  padding: 2px;\n"
"  border: 1px solid #383838;\n"
"  color: #F0F0F0;\n"
"}\n"
"\n"
"QMenuBar:focus {\n"
"  border: 1px solid #148CD2;\n"
"}\n"
"\n"
"QMenuBar::item {\n"
"  background: transparent;\n"
"  padding: 4px;\n"
"}\n"
"\n"
"QMenuBar::item:selected {\n"
"  padding: 4px;\n"
"  background: transparent;\n"
"  border: 0px solid #32414B;\n"
"}\n"
"\n"
"QMenuBar::item:pressed {\n"
"  padding: 4px;\n"
"  border: 0px solid #32414B;\n"
"  background-color: #148CD2;\n"
"  color: #F0F0F0;\n"
"  margin-bo"
                        "ttom: 0px;\n"
"  padding-bottom: 0px;\n"
"}\n"
"\n"
"/* QMenu ------------------------------------------------------------------\n"
"https://doc.qt.io/qt-5/stylesheet-examples.html#customizing-qmenu\n"
"--------------------------------------------------------------------------- */\n"
"\n"
"QMenu {\n"
"    background-color: #363636;\n"
"    color: #fff;\n"
"}\n"
"\n"
"/*\n"
"QMenu::separator {\n"
"  height: 1px;\n"
"  background-color: hsl(0, 0%, 60%);\n"
"  color: #F0F0F0;\n"
"}\n"
"\n"
"QMenu::icon {\n"
"  margin: 0px;\n"
"  padding-left: 4px;\n"
"}\n"
"\n"
"QMenu::item {\n"
"  background-color: #32414B;\n"
"  padding: 4px 24px 4px 24px;\n"
"  border: 1px transparent #32414B;\n"
"  color: pink;\n"
"}\n"
"*/\n"
"\n"
"QMenu::item:selected {\n"
"    background-color: #404040;\n"
"}\n"
"\n"
"/*\n"
"QMenu::indicator {\n"
"  width: 12px;\n"
"  height: 12px;\n"
"  padding-left: 6px;\n"
"}\n"
"\n"
"QMenu::indicator:non-exclusive:unchecked {\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/checkbox_unchecked.png\""
                        ");\n"
"}\n"
"\n"
"QMenu::indicator:non-exclusive:unchecked:selected {\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/checkbox_unchecked_disabled.png\");\n"
"}\n"
"\n"
"QMenu::indicator:non-exclusive:checked {\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/checkbox_checked.png\");\n"
"}\n"
"\n"
"QMenu::indicator:non-exclusive:checked:selected {\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/checkbox_checked_disabled.png\");\n"
"}\n"
"\n"
"QMenu::indicator:exclusive:unchecked {\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/radio_unchecked.png\");\n"
"}\n"
"\n"
"QMenu::indicator:exclusive:unchecked:selected {\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/radio_unchecked_disabled.png\");\n"
"}\n"
"\n"
"QMenu::indicator:exclusive:checked {\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/radio_checked.png\");\n"
"}\n"
"\n"
"QMenu::indicator:exclusive:checked:selected {\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/radio_checked_disabled.png\");\n"
"}\n"
"\n"
"QMenu:"
                        ":right-arrow {\n"
"  margin: 5px;\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/arrow_right.png\");\n"
"  height: 12px;\n"
"  width: 12px;\n"
"}\n"
"*/\n"
"\n"
"/* QAbstractItemView ------------------------------------------------------\n"
"https://doc.qt.io/qt-5/stylesheet-examples.html#customizing-qcombobox\n"
"--------------------------------------------------------------------------- */\n"
"\n"
"QAbstractItemView {\n"
"  alternate-background-color: #383838;\n"
"  color: #F0F0F0;\n"
"  border: 1px solid #32414B;\n"
"  border-radius: 4px;\n"
"}\n"
"\n"
"QAbstractItemView QLineEdit {\n"
"  padding: 2px;\n"
"}\n"
"\n"
"/* QAbstractScrollArea ----------------------------------------------------\n"
"https://doc.qt.io/qt-5/stylesheet-examples.html#customizing-qabstractscrollarea\n"
"--------------------------------------------------------------------------- */\n"
"\n"
"QAbstractScrollArea {\n"
"  background-color: #383838;\n"
"  border: 1px solid #333;\n"
"  border-radius: 4px;\n"
"  padding: 2px;\n"
"  m"
                        "in-height: 1.25em;\n"
"  color: #F0F0F0;\n"
"}\n"
"\n"
"QAbstractScrollArea:disabled {\n"
"  color: #787878;\n"
"}\n"
"\n"
"\n"
"/* QScrollArea ------------------------------------------------------------\n"
"--------------------------------------------------------------------------- */\n"
"\n"
"QScrollArea QWidget QWidget:disabled {\n"
"  background-color: #383838;\n"
"}\n"
"\n"
"QScrollArea\n"
"{\n"
"    border: none;\n"
"}\n"
"\n"
"/* QScrollBar -------------------------------------------------------------\n"
"https://doc.qt.io/qt-5/stylesheet-examples.html#customizing-qscrollbar\n"
"--------------------------------------------------------------------------- */\n"
"\n"
"QScrollBar:horizontal {\n"
"  height: 16px;\n"
"  margin: 2px 16px 2px 16px;\n"
"  border: 1px solid #333;\n"
"  border-radius: 4px;\n"
"  background-color: #383838;\n"
"}\n"
"\n"
"QScrollBar:vertical {\n"
"  background-color: #383838;\n"
"  width: 16px;\n"
"  margin: 16px 2px 16px 2px;\n"
"  border: 1px solid #333;\n"
"  border-radius: 4px;"
                        "\n"
"}\n"
"\n"
"QScrollBar::handle:horizontal {\n"
"  background-color: #787878;\n"
"  border: 1px solid #333;\n"
"  border-radius: 4px;\n"
"  min-width: 8px;\n"
"}\n"
"\n"
"QScrollBar::handle:horizontal:hover { }\n"
"\n"
"QScrollBar::handle:vertical {\n"
"  background-color: #787878;\n"
"  border: 1px solid #333;\n"
"  min-height: 8px;\n"
"  border-radius: 4px;\n"
"}\n"
"\n"
"QScrollBar::handle:vertical:hover { }\n"
"\n"
"QScrollBar::add-line:horizontal {\n"
"  margin: 0px 0px 0px 0px;\n"
"  border-image: url(\":/qss_icons/images/darkstyle_icons/arrow_right_disabled.png\");\n"
"  height: 12px;\n"
"  width: 12px;\n"
"  subcontrol-position: right;\n"
"  subcontrol-origin: margin;\n"
"}\n"
"\n"
"QScrollBar::add-line:horizontal:hover, QScrollBar::add-line:horizontal:on {\n"
"  border-image: url(\":/qss_icons/images/darkstyle_icons/arrow_right.png\");\n"
"  height: 12px;\n"
"  width: 12px;\n"
"  subcontrol-position: right;\n"
"  subcontrol-origin: margin;\n"
"}\n"
"\n"
"QScrollBar::add-line:vertical {\n"
"  margin"
                        ": 3px 0px 3px 0px;\n"
"  border-image: url(\":/qss_icons/images/darkstyle_icons/arrow_down_disabled.png\");\n"
"  height: 12px;\n"
"  width: 12px;\n"
"  subcontrol-position: bottom;\n"
"  subcontrol-origin: margin;\n"
"}\n"
"\n"
"QScrollBar::add-line:vertical:hover, QScrollBar::add-line:vertical:on {\n"
"  border-image: url(\":/qss_icons/images/darkstyle_icons/arrow_down.png\");\n"
"  height: 12px;\n"
"  width: 12px;\n"
"  subcontrol-position: bottom;\n"
"  subcontrol-origin: margin;\n"
"}\n"
"\n"
"QScrollBar::sub-line:horizontal {\n"
"  margin: 0px 3px 0px 3px;\n"
"  border-image: url(\":/qss_icons/images/darkstyle_icons/arrow_left_disabled.png\");\n"
"  height: 12px;\n"
"  width: 12px;\n"
"  subcontrol-position: left;\n"
"  subcontrol-origin: margin;\n"
"}\n"
"\n"
"QScrollBar::sub-line:horizontal:hover, QScrollBar::sub-line:horizontal:on {\n"
"  border-image: url(\":/qss_icons/images/darkstyle_icons/arrow_left.png\");\n"
"  height: 12px;\n"
"  width: 12px;\n"
"  subcontrol-position: left;\n"
"  subcontrol-or"
                        "igin: margin;\n"
"}\n"
"\n"
"QScrollBar::sub-line:vertical {\n"
"  margin: 3px 0px 3px 0px;\n"
"  border-image: url(\":/qss_icons/images/darkstyle_icons/arrow_up_disabled.png\");\n"
"  height: 12px;\n"
"  width: 12px;\n"
"  subcontrol-position: top;\n"
"  subcontrol-origin: margin;\n"
"}\n"
"\n"
"QScrollBar::sub-line:vertical:hover, QScrollBar::sub-line:vertical:on {\n"
"  border-image: url(\":/qss_icons/images/darkstyle_icons/arrow_up.png\");\n"
"  height: 12px;\n"
"  width: 12px;\n"
"  subcontrol-position: top;\n"
"  subcontrol-origin: margin;\n"
"}\n"
"\n"
"QScrollBar::up-arrow:horizontal, QScrollBar::down-arrow:horizontal {\n"
"  background: none;\n"
"}\n"
"\n"
"QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {\n"
"  background: none;\n"
"}\n"
"\n"
"QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {\n"
"  background: none;\n"
"}\n"
"\n"
"QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {\n"
"  background: none;\n"
"}\n"
"\n"
"/* QTextEdit -------------------------"
                        "-------------------------------------\n"
"https://doc.qt.io/qt-5/stylesheet-examples.html#customizing-specific-widgets\n"
"--------------------------------------------------------------------------- */\n"
"\n"
"/* Cannot figure out how to reduce the line / paragraph spacing in textEdit_log :-( */\n"
"\n"
"QTextEdit {\n"
"  background-color: hsl(0, 0%, 40%);\n"
"  color: #eee;\n"
"  border: 1px solid #ccc;\n"
"  border-radius: px;\n"
"}\n"
"\n"
"QInputDialog QTextEdit {\n"
"  background-color: hsl(0, 0%, 40%);\n"
"  color: #eee;\n"
"  border: 1px solid #ccc;\n"
"  border-radius: px;\n"
"}\n"
"\n"
"/* QPlainTextEdit ---------------------------------------------------------\n"
"--------------------------------------------------------------------------- */\n"
"\n"
"QPlainTextEdit {\n"
"  background-color: #383838;\n"
"  color: #F0F0F0;\n"
"  border-radius: 4px;\n"
"  border: 1px solid #333;\n"
"}\n"
"\n"
"QPlainTextEdit:hover {\n"
"  border: 1px solid hsl(0, 0%, 60%);\n"
"  color: #F0F0F0;\n"
"}\n"
"\n"
"QPlainTex"
                        "tEdit:selected {\n"
"  background-color: hsl(0, 0%, 70%);\n"
"  color: #333;\n"
"}\n"
"\n"
"/* QSizeGrip --------------------------------------------------------------\n"
"https://doc.qt.io/qt-5/stylesheet-examples.html#customizing-qsizegrip\n"
"--------------------------------------------------------------------------- */\n"
"\n"
"QSizeGrip {\n"
"  background: transparent;\n"
"  width: 12px;\n"
"  height: 12px;\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/window_grip.png\");\n"
"}\n"
"\n"
"/* QStackedWidget ---------------------------------------------------------\n"
"--------------------------------------------------------------------------- */\n"
"\n"
"/* hmm */\n"
"QStackedWidget {\n"
"  padding: 2px;\n"
"  border: 1px solid #383838;\n"
"}\n"
"\n"
"/* QToolBar ---------------------------------------------------------------\n"
"https://doc.qt.io/qt-5/stylesheet-examples.html#customizing-qtoolbar\n"
"--------------------------------------------------------------------------- */\n"
"\n"
"QToolBar {\n"
""
                        "  background-color: #32414B;\n"
"  border-bottom: 1px solid #383838;\n"
"  padding: 2px;\n"
"  font-weight: bold;\n"
"}\n"
"\n"
"QToolBar QToolButton {\n"
"  background-color: #32414B;\n"
"  border: 1px solid #32414B;\n"
"}\n"
"\n"
"QToolBar QToolButton:hover {\n"
"  border: 1px solid hsl(0, 0%, 60%); \n"
"}\n"
"\n"
"QToolBar QToolButton:checked {\n"
"  border: 1px solid #383838;\n"
"  background-color: #383838;\n"
"}\n"
"\n"
"QToolBar QToolButton:checked:hover {\n"
"  border: 1px solid hsl(0, 0%, 60%);\n"
"}\n"
"\n"
"QToolBar::handle:horizontal {\n"
"  width: 16px;\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/toolbar_move_horizontal.png\");\n"
"}\n"
"\n"
"QToolBar::handle:vertical {\n"
"  height: 16px;\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/toolbar_move_horizontal.png\");\n"
"}\n"
"\n"
"QToolBar::separator:horizontal {\n"
"  width: 16px;\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/toolbar_separator_horizontal.png\");\n"
"}\n"
"\n"
"QToolBar::separator:vertical {\n"
"  height:"
                        " 16px;\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/toolbar_separator_vertical.png\");\n"
"}\n"
"\n"
"QToolButton#qt_toolbar_ext_button {\n"
"  background: #32414B;\n"
"  border: 0px;\n"
"  color: #F0F0F0;\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/arrow_right.png\");\n"
"}\n"
"\n"
"/* QAbstractSpinBox -------------------------------------------------------\n"
"--------------------------------------------------------------------------- */\n"
"\n"
"QAbstractSpinBox {\n"
"    padding-top: 2px;\n"
"    padding-bottom: 2px;\n"
"    margin-left: 6px;\n"
"    margin-right: 6px;\n"
"    border: none;\n"
"    background-color: hsl(0, 0%, 30%);\n"
"    color: #eee;\n"
"    /*min-width: 50px;*/\n"
"}\n"
"\n"
"/* MZ: we aren't actually using these */\n"
"QAbstractSpinBox:up-button {\n"
"  background-color: transparent;\n"
"  subcontrol-origin: border;\n"
"  subcontrol-position: center right;\n"
"}\n"
"\n"
"QAbstractSpinBox:down-button {\n"
"  background-color: transparent;\n"
"  subcontrol-origin: bor"
                        "der;\n"
"  subcontrol-position: center left;\n"
"}\n"
"\n"
"/* MZ: we use these */\n"
"QAbstractSpinBox::up-arrow, \n"
"QAbstractSpinBox::up-arrow:disabled, \n"
"QAbstractSpinBox::up-arrow:off {\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/up_arrow_disabled.png\");\n"
"  height: 12px;\n"
"  width: 12px;\n"
"}\n"
"\n"
"QAbstractSpinBox::up-arrow:hover {\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/up_arrow.png\");\n"
"}\n"
"\n"
"QAbstractSpinBox::down-arrow, \n"
"QAbstractSpinBox::down-arrow:disabled, \n"
"QAbstractSpinBox::down-arrow:off {\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/down_arrow_disabled.png\");\n"
"  height: 12px;\n"
"  width: 12px;\n"
"}\n"
"\n"
"QAbstractSpinBox::down-arrow:hover {\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/down_arrow.png\");\n"
"}\n"
"\n"
"QAbstractSpinBox:hover {\n"
"  border: 1px solid hsl(0, 0%, 60%);\n"
"  color: #F0F0F0;\n"
"}\n"
"\n"
"QAbstractSpinBox:selected {\n"
"  background-color: hsl(0, 0%, 70%);\n"
"  color: #333;\n"
"}\n"
""
                        "\n"
"/* ------------------------------------------------------------------------ */\n"
"/* DISPLAYS --------------------------------------------------------------- */\n"
"/* ------------------------------------------------------------------------ */\n"
"\n"
"/* ------------------------------------------------------------------------ */\n"
"/* QLabel -----------------------------------------------------------------\n"
"https://doc.qt.io/qt-5/stylesheet-examples.html#customizing-qframe\n"
"--------------------------------------------------------------------------- */\n"
"\n"
"QLabel {\n"
"  background-color: transparent;\n"
"  border: none;\n"
"  padding: 2px;\n"
"  margin: 0px;\n"
"  color: #eee;\n"
"}\n"
"\n"
"QLabel::disabled {\n"
"  background-color: transparent;\n"
"  border: none;\n"
"  color: #ccc;\n"
"}\n"
"\n"
"/* QTextBrowser -----------------------------------------------------------\n"
"https://doc.qt.io/qt-5/stylesheet-examples.html#customizing-qabstractscrollarea\n"
"-------------------------------"
                        "-------------------------------------------- */\n"
"\n"
"QTextBrowser {\n"
"  background-color: #383838;\n"
"  border: 1px solid #32414B;\n"
"  color: #F0F0F0;\n"
"  border-radius: 4px;\n"
"}\n"
"\n"
"QTextBrowser:disabled {\n"
"  background-color: #383838;\n"
"  border: 1px solid #32414B;\n"
"  color: #787878;\n"
"  border-radius: 4px;\n"
"}\n"
"\n"
"QTextBrowser:!hover, \n"
"QTextBrowser::selected, \n"
"QTextBrowser::pressed \n"
"{\n"
"  border: 1px solid #333;\n"
"}\n"
"\n"
"QTextBrowser:hover\n"
"{\n"
"  border: 1px solid hsl(0, 0%, 60%);\n"
"}\n"
"\n"
"/* QGraphicsView ----------------------------------------------------------\n"
"--------------------------------------------------------------------------- */\n"
"\n"
"QGraphicsView {\n"
"  background-color: #383838;\n"
"  border: 1px solid #32414B;\n"
"  color: #F0F0F0;\n"
"  border-radius: 4px;\n"
"}\n"
"\n"
"QGraphicsView:disabled {\n"
"  background-color: #383838;\n"
"  border: 1px solid #32414B;\n"
"  color: #787878;\n"
"  border-radius: 4px;\n"
"}\n"
""
                        "\n"
"QGraphicsView:hover, \n"
"QGraphicsView:!hover, \n"
"QGraphicsView::selected, \n"
"QGraphicsView::pressed \n"
"{\n"
"  border: 1px solid #333;\n"
"}\n"
"\n"
"/* QCalendarWidget --------------------------------------------------------\n"
"--------------------------------------------------------------------------- */\n"
"\n"
"QCalendarWidget {\n"
"  border: 1px solid #32414B;\n"
"  border-radius: 4px;\n"
"}\n"
"\n"
"QCalendarWidget:disabled {\n"
"  background-color: #383838;\n"
"  color: #787878;\n"
"}\n"
"\n"
"/* QLCDNumber -------------------------------------------------------------\n"
"--------------------------------------------------------------------------- */\n"
"\n"
"QLCDNumber {\n"
"  background-color: #383838;\n"
"  color: #F0F0F0;\n"
"}\n"
"\n"
"QLCDNumber:disabled {\n"
"  background-color: #383838;\n"
"  color: #787878;\n"
"}\n"
"\n"
"/* QProgressBar -----------------------------------------------------------\n"
"https://doc.qt.io/qt-5/stylesheet-examples.html#customizing-qprogressbar\n"
"-----"
                        "---------------------------------------------------------------------- */\n"
"\n"
"QProgressBar {\n"
"  background-color: #383838;\n"
"  border: 1px solid #333;\n"
"  color: #F0F0F0;\n"
"  border-radius: 4px;\n"
"  text-align: center;\n"
"}\n"
"\n"
"QProgressBar:disabled {\n"
"  background-color: #383838;\n"
"  border: 1px solid #333;\n"
"  color: #787878;\n"
"  border-radius: 4px;\n"
"  text-align: center;\n"
"}\n"
"\n"
"QProgressBar::chunk {\n"
"  background-color: hsl(0, 0%, 40%);\n"
"  color: #383838;\n"
"  border-radius: 4px;\n"
"}\n"
"\n"
"QProgressBar::chunk:disabled {\n"
"  background-color: #14506E;\n"
"  color: #787878;\n"
"  border-radius: 4px;\n"
"}\n"
"\n"
"/* ------------------------------------------------------------------------ */\n"
"/* BUTTONS ---------------------------------------------------------------- */\n"
"/* ------------------------------------------------------------------------ */\n"
"\n"
"/* ------------------------------------------------------------------------ */\n"
"/* QPushB"
                        "utton ------------------------------------------------------------\n"
"https://doc.qt.io/qt-5/stylesheet-examples.html#customizing-qpushbutton\n"
"--------------------------------------------------------------------------- */\n"
"\n"
"/* Most GUI buttons are wrapping images, so can be fairly tight */\n"
"QPushButton {\n"
"    border: 1px solid #333;\n"
"    background-color: qlineargradient(spread:pad, \n"
"        x1:0.5, y1:1, \n"
"        x2:0.5, y2:0, \n"
"        stop:0 hsl(0, 0%, 26%),\n"
"        stop:1 hsl(0, 0%, 37%));\n"
"    border-radius: 5px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    border: 1px solid hsl(0, 0%, 60%);\n"
"}\n"
"\n"
"/* This gets overridden down in the [wpBox] stuff at the bottom */\n"
"QPushButton:disabled \n"
"{\n"
"    color: #999;\n"
"    background-color: hsl(0, 0%, 66%);\n"
"    border: 1px solid #333;\n"
"}\n"
"\n"
"QPushButton:checked {\n"
"  background-color: #333;\n"
"  border: 1px solid #333;\n"
"  border-radius: 4px;\n"
"  padding: 3px;\n"
"}\n"
"\n"
"QPushButton:check"
                        "ed:selected {\n"
"  background-color: #333;\n"
"  color: #32414B;\n"
"}\n"
"\n"
"QPushButton:checked:hover {\n"
"  border: 1px solid hsl(0, 0%, 60%);\n"
"  color: #F0F0F0;\n"
"}\n"
"\n"
"QPushButton::menu-indicator {\n"
"  subcontrol-origin: padding;\n"
"  subcontrol-position: bottom right;\n"
"  bottom: 4px;\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"  background-color: #383838;\n"
"  border: 1px solid #383838;\n"
"}\n"
"\n"
"QPushButton:pressed:hover {\n"
"  border: 1px solid hsl(0, 0%, 60%);\n"
"}\n"
"\n"
"QPushButton:selected {\n"
"  background: #333;\n"
"  color: #eee;\n"
"}\n"
"\n"
"/* QInputDialog -----------------------------------------------------------\n"
"--------------------------------------------------------------------------- */\n"
"\n"
"QInputDialog {\n"
"    background-color: #383838;\n"
"}\n"
"\n"
"QDialog {\n"
"    background-color: #383838;\n"
"}\n"
"\n"
"/* Dialog Ok/Cancel buttons should be big and obvious */\n"
"QDialog QPushButton {\n"
"    padding-top: 10px;\n"
"    padding-bottom: 10px"
                        ";\n"
"    padding-left: 30px;\n"
"    padding-right: 30px;\n"
"}\n"
"\n"
"QMessageBox {\n"
"    background-color: #383838;\n"
"}\n"
"\n"
"/* QToolButton ------------------------------------------------------------\n"
"https://doc.qt.io/qt-5/stylesheet-examples.html#customizing-qtoolbutton\n"
"--------------------------------------------------------------------------- */\n"
"\n"
"QToolButton {\n"
"  background-color: transparent;\n"
"  border-radius: 4px;\n"
"  margin: 0px;\n"
"  padding: 2px;\n"
"  border: 2px solid red;\n"
"  /* The subcontrols below are used only in the MenuButtonPopup mode */\n"
"  /* The subcontrol below is used only in the InstantPopup or DelayedPopup mode */\n"
"}\n"
"\n"
"QToolButton:checked {\n"
"  background-color: transparent;\n"
"  border: 1px solid #1464A0;\n"
"}\n"
"\n"
"QToolButton:checked:disabled {\n"
"  border: 1px solid #14506E;\n"
"}\n"
"\n"
"QToolButton:pressed {\n"
"  margin: 1px;\n"
"  background-color: transparent;\n"
"  border: 1px solid #1464A0;\n"
"}\n"
"\n"
"QToolBut"
                        "ton:disabled {\n"
"  border: none;\n"
"}\n"
"\n"
"QToolButton:disabled:hover {\n"
"  border: 1px solid hsl(0, 0%, 60%);\n"
"}\n"
"\n"
"QToolButton:hover {\n"
"  border: 2px solid red; /* 1px solid hsl(0, 0%, 60%); */\n"
"}\n"
"\n"
"QToolButton[popupMode=\"1\"] {\n"
"  padding: 2px;\n"
"  padding-right: 12px;\n"
"  border: 1px solid blue; /* #32414B; */\n"
"  border-radius: 4px;\n"
"}\n"
"\n"
"/* This is the ENLIGHTEN StatusBar menu */\n"
"QToolButton[popupMode=\"2\"] {\n"
"  padding: 2px;\n"
"  padding-right: 12px;\n"
"  border: 1px solid #999; \n"
"  text-align: center;\n"
"}\n"
"\n"
"QToolButton[popupMode=\"2\"]:hover {\n"
"  padding: 2px;\n"
"  padding-right: 12px;\n"
"  border: 2px solid silver; /* #32414B; */\n"
"  text-align: center;\n"
"}\n"
"\n"
"QToolButton::menu-button {\n"
"  padding: 2px;\n"
"  border-radius: 4px;\n"
"  border: 1px solid yellow; /* #32414B; */\n"
"  border-top-right-radius: 4px;\n"
"  border-bottom-right-radius: 4px;\n"
"  /* 16px width + 4px for border = 20px allocated above */\n"
""
                        "  width: 16px;\n"
"}\n"
"\n"
"QToolButton::menu-button:hover {\n"
"  border: 1px solid hsl(0, 0%, 60%);\n"
"}\n"
"\n"
"QToolButton::menu-button:checked:hover {\n"
"  border: 1px solid hsl(0, 0%, 60%);\n"
"}\n"
"\n"
"QToolButton::menu-indicator {\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/arrow_down.png\");\n"
"  height: 12px;\n"
"  width: 12px;\n"
"  top: -8px;\n"
"  /* Shift it a bit */\n"
"  left: -4px;\n"
"  /* Shift it a bit */\n"
"}\n"
"\n"
"QToolButton::menu-arrow {\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/arrow_down.png\");\n"
"  height: 12px;\n"
"  width: 12px;\n"
"}\n"
"\n"
"QToolButton::menu-arrow:open {\n"
"  border: 1px solid #32414B;\n"
"}\n"
"\n"
"/* QCommandLinkButton -----------------------------------------------------\n"
"--------------------------------------------------------------------------- */\n"
"\n"
"QCommandLinkButton {\n"
"  background-color: transparent;\n"
"  border: 1px solid #32414B;\n"
"  color: #F0F0F0;\n"
"  border-radius: 4px;\n"
"  padding: 0px;\n"
""
                        "  margin: 0px;\n"
"}\n"
"\n"
"QCommandLinkButton:disabled {\n"
"  background-color: transparent;\n"
"  color: #787878;\n"
"}\n"
"\n"
"/* ------------------------------------------------------------------------ */\n"
"/* INPUTS - NO FIELDS ----------------------------------------------------- */\n"
"/* ------------------------------------------------------------------------ */\n"
"\n"
"/* QComboBox --------------------------------------------------------------\n"
"https://doc.qt.io/qt-5/stylesheet-examples.html#customizing-qcombobox\n"
"--------------------------------------------------------------------------- */\n"
"\n"
"/* YOU ARE HERE */\n"
"\n"
"/*\n"
"QComboBox\n"
"{\n"
"    selection-background-color: #3d8ec9;\n"
"    background-color: #201F1F;\n"
"    border-style: solid;\n"
"    border: 1px solid #3A3939;\n"
"    border-radius: 2px;\n"
"    min-width: 75px;\n"
"    color: white;\n"
"    padding: 1px 0px 1px 3px; \n"
"}\n"
"\n"
"QComboBox:on\n"
"{\n"
"    background-color: #626873;\n"
"    padding-top: "
                        "3px;\n"
"    padding-left: 4px;\n"
"    selection-background-color: #4a4a4a;\n"
"}\n"
"\n"
"QComboBox QAbstractItemView\n"
"{\n"
"    background-color: #201F1F;\n"
"    border-radius: 2px;\n"
"    border: 1px solid #444;\n"
"    selection-background-color: #3d8ec9;\n"
"    color: #eee;\n"
"}\n"
"*/\n"
"\n"
"QComboBox::drop-down\n"
"{\n"
"    subcontrol-origin: padding;\n"
"    subcontrol-position: top right;\n"
"    width: 15px;\n"
"\n"
"    border-left-width: 0px;\n"
"    border-left-color: darkgray;\n"
"    border-left-style: solid;\n"
"    border-top-right-radius: 3px;\n"
"    border-bottom-right-radius: 3px;\n"
"}\n"
"\n"
"QComboBox::down-arrow\n"
"{\n"
"    image: url(:/qss_icons/images/darkstyle_icons/down_arrow_disabled.png);\n"
"}\n"
"\n"
"QComboBox::down-arrow:on, \n"
"QComboBox::down-arrow:hover,\n"
"QComboBox::down-arrow:focus\n"
"{\n"
"    image: url(:/qss_icons/images/darkstyle_icons/down_arrow.png);\n"
"}\n"
"\n"
"/* QSlider ----------------------------------------------------------------\n"
"htt"
                        "ps://doc.qt.io/qt-5/stylesheet-examples.html#customizing-qslider\n"
"--------------------------------------------------------------------------- */\n"
"\n"
"QSlider:disabled {\n"
"  background: #383838;\n"
"}\n"
"\n"
"QSlider:focus {\n"
"  border: none;\n"
"}\n"
"\n"
"QSlider::groove:horizontal {\n"
"  background: #333;\n"
"  border: 1px solid #333;\n"
"  height: 4px;\n"
"  margin: 0px;\n"
"  border-radius: 4px;\n"
"}\n"
"\n"
"/*\n"
"QSlider::groove:vertical {\n"
"  background: #32414B;\n"
"  border: 1px solid #32414B;\n"
"  width: 4px;\n"
"  margin: 0px;\n"
"  border-radius: 4px;\n"
"}\n"
"\n"
"QSlider::add-page:vertical {\n"
"  background: #1464A0;\n"
"  border: 1px solid #32414B;\n"
"  width: 4px;\n"
"  margin: 0px;\n"
"  border-radius: 4px;\n"
"}\n"
"\n"
"QSlider::add-page:vertical :disabled {\n"
"  background: #14506E;\n"
"}\n"
"\n"
"QSlider::sub-page:horizontal {\n"
"  background: #1464A0;\n"
"  border: 1px solid #32414B;\n"
"  height: 4px;\n"
"  margin: 0px;\n"
"  border-radius: 4px;\n"
"}\n"
"\n"
"QSli"
                        "der::sub-page:horizontal:disabled {\n"
"  background: #14506E;\n"
"}\n"
"\n"
"QSlider::handle:horizontal {\n"
"  background: #787878;\n"
"  border: 1px solid #32414B;\n"
"  width: 8px;\n"
"  height: 8px;\n"
"  margin: -8px 0px;\n"
"  border-radius: 4px;\n"
"}\n"
"\n"
"QSlider::handle:horizontal:hover {\n"
"  background: #148CD2;\n"
"  border: 1px solid #148CD2;\n"
"}\n"
"\n"
"QSlider::handle:vertical {\n"
"  background: #787878;\n"
"  border: 1px solid #32414B;\n"
"  width: 8px;\n"
"  height: 8px;\n"
"  margin: 0 -8px;\n"
"  border-radius: 4px;\n"
"}\n"
"\n"
"QSlider::handle:vertical:hover {\n"
"  background: #148CD2;\n"
"  border: 1px solid #148CD2;\n"
"}\n"
"*/\n"
"\n"
"QSlider::groove:horizontal \n"
"{\n"
"    border: 1px solid #3A3939;\n"
"    height: 8px;\n"
"    background: #201F1F;\n"
"    margin: 2px 0;\n"
"    border-radius: 2px;\n"
"}\n"
"\n"
"QSlider::handle:horizontal \n"
"{\n"
"    background: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0.0 hsl(0, 0%, 60%), stop: 0.2 #a8a8a8, stop: 1 #72727"
                        "2);\n"
"    border: 1px solid #3A3939;\n"
"    width: 14px;\n"
"    height: 14px;\n"
"    margin: -4px 0;\n"
"    border-radius: 2px;\n"
"}\n"
"\n"
"QSlider::handle:horizontal:hover\n"
"{\n"
"    border: 1px solid hsl(0, 0%, 60%);\n"
"}\n"
"\n"
"QSlider::groove:vertical \n"
"{\n"
"    border: 1px solid #3A3939;\n"
"    width: 8px;\n"
"    background: #201F1F;\n"
"    margin: 0 0px;\n"
"    border-radius: 2px;\n"
"}\n"
"\n"
"QSlider::handle:vertical \n"
"{\n"
"    background: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0.0 hsl(0, 0%, 60%), stop: 0.2 #a8a8a8, stop: 1 #727272);\n"
"    border: 1px solid #3A3939;\n"
"    width: 14px;\n"
"    height: 14px;\n"
"    margin: 0 -4px;\n"
"    border-radius: 2px;\n"
"}\n"
"\n"
"QSlider::handle:vertical:hover\n"
"{\n"
"    border: 1px solid hsl(0, 0%, 60%);\n"
"}\n"
"\n"
"QSlider \n"
"{\n"
"    background: none;\n"
"}\n"
"\n"
"/* QLineEdit --------------------------------------------------------------\n"
"https://doc.qt.io/qt-5/stylesheet-examples.html#customizing-"
                        "qlineedit\n"
"--------------------------------------------------------------------------- */\n"
"\n"
"QLineEdit {\n"
"  background-color: hsl(0, 0%, 40%);\n"
"  color: #eee;\n"
"  padding-top: 2px;\n"
"  padding-bottom: 2px;\n"
"  padding-left: 4px;\n"
"  padding-right: 4px;\n"
"  border-style: solid;\n"
"  border: 1px solid #333;\n"
"  border-radius: 4px;\n"
"}\n"
"\n"
"QLineEdit:disabled {\n"
"  background-color: #383838;\n"
"  color: #787878;\n"
"}\n"
"\n"
"QLineEdit:hover {\n"
"  border: 1px solid hsl(0, 0%, 60%);\n"
"  color: #F0F0F0;\n"
"}\n"
"\n"
"QLineEdit:selected {\n"
"  background: #1464A0;\n"
"  color: #333;\n"
"}\n"
"\n"
"/* QTabWiget --------------------------------------------------------------\n"
"https://doc.qt.io/qt-5/stylesheet-examples.html#customizing-qtabwidget-and-qtabbar\n"
"--------------------------------------------------------------------------- */\n"
"\n"
"QTabWidget \n"
"{\n"
"    border: 1px solid green;\n"
"    border-radius: 6px;\n"
"}\n"
"\n"
"QTabWidget::pane \n"
"{\n"
"    b"
                        "order: 1px solid hsl(0, 0%, 37%);\n"
"    border-radius: 6px;\n"
"}\n"
"\n"
"/* QTabBar ----------------------------------------------------------------\n"
"https://doc.qt.io/qt-5/stylesheet-examples.html#customizing-qtabwidget-and-qtabbar\n"
"--------------------------------------------------------------------------- */\n"
"\n"
"QTabBar {\n"
"    border-radius: 6px;\n"
"    font-weight: bold;\n"
"}\n"
"\n"
"QTabBar::close-button {\n"
"  border: 0;\n"
"  margin: 2px;\n"
"  padding: 2px;\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/window_close.png\");\n"
"}\n"
"\n"
"QTabBar::close-button:hover {\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/window_close_focus.png\");\n"
"}\n"
"\n"
"QTabBar::close-button:pressed {\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/window_close_pressed.png\");\n"
"}\n"
"\n"
"/* QTabBar::tab - selected ------------------------------------------------\n"
"https://doc.qt.io/qt-5/stylesheet-examples.html#customizing-qtabwidget-and-qtabbar\n"
"--------------------"
                        "------------------------------------------------------- */\n"
"\n"
"/* This is the \"tab\" atop the QTabPane */\n"
"\n"
"QTabBar::tab {\n"
"}\n"
"\n"
"QTabBar::tab:top:selected:hover { border: 1px solid hsl(0, 0%, 60%); }\n"
"QTabBar::tab:top:!selected:hover { border: 1px solid hsl(0, 0%, 60%); }\n"
"\n"
"/* all the :top: styles can also be overridden for QTabWidgets with their QTabBar on the left, right or bottom of the widget */\n"
"\n"
"QTabBar::tab:top:selected \n"
"{\n"
"    background-color: qlineargradient(spread:pad, \n"
"        x1:0.5, y1:1, \n"
"        x2:0.5, y2:0, \n"
"        stop:0 rgba(137, 10, 10, 255), \n"
"        stop:1 rgba(186, 10, 10, 255));\n"
"}\n"
"\n"
"QTabBar::tab:top:!selected \n"
"{\n"
"    background-color: qlineargradient(spread:pad, \n"
"        x1:0.5, y1:1, \n"
"        x2:0.5, y2:0, \n"
"        stop:0 hsl(0, 0%, 26%),\n"
"        stop:1 hsl(0, 0%, 37%));\n"
"}\n"
"\n"
"QTabBar::tab:top \n"
"{\n"
"    color: #eee;\n"
"\n"
"    border: 1px solid #333;\n"
"    border-top-left"
                        "-radius: 5px;\n"
"    border-top-right-radius: 5px;\n"
"    border-bottom-right-radius: 0;\n"
"    border-bottom-left-radius: 0;\n"
"\n"
"    margin-top: 0;\n"
"    margin-bottom: 0;\n"
"    margin-right: 0;\n"
"    margin-left: 2px;\n"
"\n"
"    padding-left: 4ex;\n"
"    padding-right: 4ex;\n"
"    padding-top: 4px;\n"
"    padding-bottom: 4px;\n"
"}\n"
"\n"
"/* QDockWiget -------------------------------------------------------------\n"
"--------------------------------------------------------------------------- */\n"
"\n"
"QDockWidget {\n"
"  outline: 1px solid #32414B;\n"
"  background-color: #383838;\n"
"  border: 1px solid #32414B;\n"
"  border-radius: 4px;\n"
"  titlebar-close-icon: url(\":/qss_icons/images/darkstyle_icons/window_close.png\");\n"
"  titlebar-normal-icon: url(\":/qss_icons/images/darkstyle_icons/window_undock.png\");\n"
"}\n"
"\n"
"QDockWidget::title {\n"
"  padding: 6px;\n"
"  border: none;\n"
"  background-color: #32414B;\n"
"}\n"
"\n"
"QDockWidget::close-button {\n"
"  background-colo"
                        "r: #32414B;\n"
"  border-radius: 4px;\n"
"  border: none;\n"
"}\n"
"\n"
"QDockWidget::close-button:hover {\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/window_close_focus.png\");\n"
"}\n"
"\n"
"QDockWidget::close-button:pressed {\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/window_close_pressed.png\");\n"
"}\n"
"\n"
"QDockWidget::float-button {\n"
"  background-color: #32414B;\n"
"  border-radius: 4px;\n"
"  border: none;\n"
"}\n"
"\n"
"QDockWidget::float-button:hover {\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/window_undock_focus.png\");\n"
"}\n"
"\n"
"QDockWidget::float-button:pressed {\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/window_undock_pressed.png\");\n"
"}\n"
"\n"
"/* QTreeView QListView QTableView -----------------------------------------\n"
"https://doc.qt.io/qt-5/stylesheet-examples.html#customizing-qtreeview\n"
"https://doc.qt.io/qt-5/stylesheet-examples.html#customizing-qlistview\n"
"https://doc.qt.io/qt-5/stylesheet-examples.html#customizing-qtableview\n"
""
                        "--------------------------------------------------------------------------- */\n"
"\n"
"QTreeView:branch:selected, QTreeView:branch:hover {\n"
"  background: url(\":/qss_icons/images/darkstyle_icons/transparent.png\");\n"
"}\n"
"\n"
"QTreeView:branch:has-siblings:!adjoins-item {\n"
"  border-image: url(\":/qss_icons/images/darkstyle_icons/branch_line.png\") 0;\n"
"}\n"
"\n"
"QTreeView:branch:has-siblings:adjoins-item {\n"
"  border-image: url(\":/qss_icons/images/darkstyle_icons/branch_more.png\") 0;\n"
"}\n"
"\n"
"QTreeView:branch:!has-children:!has-siblings:adjoins-item {\n"
"  border-image: url(\":/qss_icons/images/darkstyle_icons/branch_end.png\") 0;\n"
"}\n"
"\n"
"QTreeView:branch:has-children:!has-siblings:closed, QTreeView:branch:closed:has-children:has-siblings {\n"
"  border-image: none;\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/branch_closed.png\");\n"
"}\n"
"\n"
"QTreeView:branch:open:has-children:!has-siblings, QTreeView:branch:open:has-children:has-siblings {\n"
"  border-image: none;\n"
""
                        "  image: url(\":/qss_icons/images/darkstyle_icons/branch_open.png\");\n"
"}\n"
"\n"
"QTreeView:branch:has-children:!has-siblings:closed:hover, QTreeView:branch:closed:has-children:has-siblings:hover {\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/branch_closed_focus.png\");\n"
"}\n"
"\n"
"QTreeView:branch:open:has-children:!has-siblings:hover, QTreeView:branch:open:has-children:has-siblings:hover {\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/branch_open_focus.png\");\n"
"}\n"
"\n"
"QTreeView::indicator:checked,\n"
"QListView::indicator:checked {\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/checkbox_checked.png\");\n"
"}\n"
"\n"
"QTreeView::indicator:checked:hover, QTreeView::indicator:checked:focus, QTreeView::indicator:checked:pressed,\n"
"QListView::indicator:checked:hover,\n"
"QListView::indicator:checked:focus,\n"
"QListView::indicator:checked:pressed {\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/checkbox_checked_focus.png\");\n"
"}\n"
"\n"
"QTreeView::indicator:uncheck"
                        "ed,\n"
"QListView::indicator:unchecked {\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/checkbox_unchecked.png\");\n"
"}\n"
"\n"
"QTreeView::indicator:unchecked:hover, QTreeView::indicator:unchecked:focus, QTreeView::indicator:unchecked:pressed,\n"
"QListView::indicator:unchecked:hover,\n"
"QListView::indicator:unchecked:focus,\n"
"QListView::indicator:unchecked:pressed {\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/checkbox_unchecked_focus.png\");\n"
"}\n"
"\n"
"QTreeView::indicator:indeterminate,\n"
"QListView::indicator:indeterminate {\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/checkbox_indeterminate.png\");\n"
"}\n"
"\n"
"QTreeView::indicator:indeterminate:hover, QTreeView::indicator:indeterminate:focus, QTreeView::indicator:indeterminate:pressed,\n"
"QListView::indicator:indeterminate:hover,\n"
"QListView::indicator:indeterminate:focus,\n"
"QListView::indicator:indeterminate:pressed {\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/checkbox_indeterminate_focus.png\");\n"
""
                        "}\n"
"\n"
"QTreeView,\n"
"QListView,\n"
"QTableView,\n"
"QColumnView {\n"
"  background-color: hsl(0, 0%, 13%);\n"
"  border: 1px solid #333;\n"
"  color: #F0F0F0;\n"
"  gridline-color: #ccc;\n"
"  border-radius: 4px;\n"
"  padding: 1px 0px 1px 3px; \n"
"}\n"
"\n"
"QTreeView:disabled,\n"
"QListView:disabled,\n"
"QTableView:disabled,\n"
"QColumnView:disabled {\n"
"  background-color: #383838;\n"
"  color: #787878;\n"
"}\n"
"\n"
"QTreeView:selected,\n"
"QListView:selected,\n"
"QTableView:selected,\n"
"QColumnView:selected {\n"
"  background: hsl(0, 0%, 36%);\n"
"  color: #ccc;\n"
"}\n"
"\n"
"QTreeView::hover,\n"
"QListView::hover,\n"
"QTableView::hover,\n"
"QColumnView::hover {\n"
"  background-color: #383838;\n"
"  border: 1px solid hsl(0, 0%, 60%);\n"
"}\n"
"\n"
"QTreeView::item:pressed,\n"
"QListView::item:pressed,\n"
"QTableView::item:pressed,\n"
"QColumnView::item:pressed {\n"
"  background-color: hsl(0, 0%, 70%);\n"
"}\n"
"\n"
"QTreeView::item:selected:hover,\n"
"QListView::item:selected:hover,\n"
"QTableV"
                        "iew::item:selected:hover,\n"
"QColumnView::item:selected:hover {\n"
"  background: hsl(0, 0%, 70%);\n"
"  color: #383838;\n"
"}\n"
"\n"
"QTreeView::item:selected:active,\n"
"QListView::item:selected:active,\n"
"QTableView::item:selected:active,\n"
"QColumnView::item:selected:active {\n"
"  background-color: hsl(0, 0%, 70%);\n"
"}\n"
"\n"
"QTreeView::item:!selected:hover,\n"
"QListView::item:!selected:hover,\n"
"QTableView::item:!selected:hover,\n"
"QColumnView::item:!selected:hover {\n"
"  color: #148CD2;\n"
"  background-color: #32414B;\n"
"}\n"
"\n"
"QTableCornerButton::section {\n"
"  background-color: #383838;\n"
"  border: 1px transparent #32414B;\n"
"  border-radius: 0px;\n"
"}\n"
"\n"
"/* QHeaderView ------------------------------------------------------------\n"
"https://doc.qt.io/qt-5/stylesheet-examples.html#customizing-qheaderview\n"
"--------------------------------------------------------------------------- */\n"
"\n"
"QHeaderView {\n"
"  background-color: hsl(0, 0%, 13%);\n"
"  border: 1px solid "
                        "#666;\n"
"  padding: 2px;\n"
"  margin: 0px;\n"
"  border-radius: 0px;\n"
"}\n"
"\n"
"QHeaderView:disabled {\n"
"  padding: 2px;\n"
"}\n"
"\n"
"QHeaderView::section {\n"
"  background-color: hsl(0, 0%, 15%);\n"
"  color: #F0F0F0;\n"
"  padding: 2px;\n"
"  border-radius: 0px;\n"
"  text-align: left;\n"
"}\n"
"\n"
"QHeaderView::section:checked {\n"
"  color: #F0F0F0;\n"
"  background-color: hsl(0, 0%, 70%);\n"
"}\n"
"\n"
"QHeaderView::section:checked:disabled {\n"
"  color: #787878;\n"
"  background-color: #14506E;\n"
"}\n"
"\n"
"QHeaderView::section::horizontal {\n"
"  border-left: 1px solid #383838;\n"
"}\n"
"\n"
"QHeaderView::section::horizontal::first, QHeaderView::section::horizontal::only-one {\n"
"  border: none;\n"
"}\n"
"\n"
"QHeaderView::section::horizontal:disabled {\n"
"  color: #787878;\n"
"}\n"
"\n"
"QHeaderView::section::vertical {\n"
"  border-top: 1px solid #383838;\n"
"}\n"
"\n"
"QHeaderView::section::vertical::first, QHeaderView::section::vertical::only-one {\n"
"  border: none;\n"
"}\n"
"\n"
""
                        "QHeaderView::section::vertical:disabled {\n"
"  color: #787878;\n"
"}\n"
"\n"
"QHeaderView::down-arrow {\n"
"  /* Those settings (border/width/height/background-color) solve bug */\n"
"  /* transparent arrow background and size */\n"
"  background-color: #32414B;\n"
"  height: 12px;\n"
"  width: 12px;\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/arrow_down.png\");\n"
"}\n"
"\n"
"QHeaderView::up-arrow {\n"
"  background-color: #32414B;\n"
"  height: 12px;\n"
"  width: 12px;\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/arrow_up.png\");\n"
"}\n"
"\n"
"/* QToolBox --------------------------------------------------------------\n"
"https://doc.qt.io/qt-5/stylesheet-examples.html#customizing-qtoolbox\n"
"--------------------------------------------------------------------------- */\n"
"\n"
"QToolBox {\n"
"  padding: 0px;\n"
"  border: 0px;\n"
"  border: 1px solid #32414B;\n"
"}\n"
"\n"
"QToolBox::selected {\n"
"  padding: 0px;\n"
"  border: 2px solid hsl(0, 0%, 70%);\n"
"}\n"
"\n"
"QToolBox::tab {\n"
""
                        "  background-color: #383838;\n"
"  border: 1px solid #32414B;\n"
"  color: #F0F0F0;\n"
"  border-top-left-radius: 4px;\n"
"  border-top-right-radius: 4px;\n"
"}\n"
"\n"
"QToolBox::tab:disabled {\n"
"  color: #787878;\n"
"}\n"
"\n"
"QToolBox::tab:selected {\n"
"  background-color: hsl(0, 0%, 60%);\n"
"  border-bottom: 2px solid hsl(0, 0%, 70%);\n"
"}\n"
"\n"
"QToolBox::tab:selected:disabled {\n"
"  background-color: #32414B;\n"
"  border-bottom: 2px solid #14506E;\n"
"}\n"
"\n"
"QToolBox::tab:!selected {\n"
"  background-color: #32414B;\n"
"  border-bottom: 2px solid #32414B;\n"
"}\n"
"\n"
"QToolBox::tab:!selected:disabled {\n"
"  background-color: #383838;\n"
"}\n"
"\n"
"QToolBox::tab:hover {\n"
"  border-color: hsl(0, 0%, 60%);\n"
"  border-bottom: 2px solid hsl(0, 0%, 60%);\n"
"}\n"
"\n"
"QToolBox QScrollArea QWidget QWidget {\n"
"  padding: 0px;\n"
"  border: 0px;\n"
"  background-color: #383838;\n"
"}\n"
"\n"
"/* QFrame -----------------------------------------------------------------\n"
"https://doc.qt.io"
                        "/qt-5/stylesheet-examples.html#customizing-qframe\n"
"--------------------------------------------------------------------------- */\n"
"\n"
"/*\n"
".QFrame {\n"
"    border: none;\n"
"    background-color: transparent;\n"
"}\n"
"\n"
".QFrame[height=\"3\"], .QFrame[width=\"3\"] {\n"
"  background-color: #383838;\n"
"}\n"
"*/\n"
"\n"
"/* QSplitter --------------------------------------------------------------\n"
"https://doc.qt.io/qt-5/stylesheet-examples.html#customizing-qsplitter\n"
"--------------------------------------------------------------------------- */\n"
"\n"
"QSplitter {\n"
"  background-color: #32414B;\n"
"  spacing: 0px;\n"
"  padding: 0px;\n"
"  margin: 0px;\n"
"}\n"
"\n"
"QSplitter::separator {\n"
"  background-color: #32414B;\n"
"  border: 0px solid #383838;\n"
"  spacing: 0px;\n"
"  padding: 1px;\n"
"  margin: 0px;\n"
"}\n"
"\n"
"QSplitter::separator:hover {\n"
"  background-color: #787878;\n"
"}\n"
"\n"
"QSplitter::separator:horizontal {\n"
"  width: 5px;\n"
"  image: url(\":/qss_icons/image"
                        "s/darkstyle_icons/line_vertical.png\");\n"
"}\n"
"\n"
"QSplitter::separator:vertical {\n"
"  height: 5px;\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/line_horizontal.png\");\n"
"}\n"
"\n"
"/* QDateEdit --------------------------------------------------------------\n"
"--------------------------------------------------------------------------- */\n"
"\n"
"QDateEdit {\n"
"  selection-background-color: hsl(0, 0%, 70%);\n"
"  border-style: solid;\n"
"  border: 1px solid #32414B;\n"
"  border-radius: 4px;\n"
"  padding-top: 2px;\n"
"  padding-bottom: 2px;\n"
"  padding-left: 4px;\n"
"  padding-right: 4px;\n"
"  min-width: 10px;\n"
"}\n"
"\n"
"QDateEdit:on {\n"
"  selection-background-color: hsl(0, 0%, 70%);\n"
"}\n"
"\n"
"QDateEdit::drop-down {\n"
"  subcontrol-origin: padding;\n"
"  subcontrol-position: top right;\n"
"  width: 20px;\n"
"  border-top-right-radius: 3px;\n"
"  border-bottom-right-radius: 3px;\n"
"}\n"
"\n"
"QDateEdit::down-arrow {\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/arrow_"
                        "down_disabled.png\");\n"
"  height: 12px;\n"
"  width: 12px;\n"
"}\n"
"\n"
"QDateEdit::down-arrow:on, QDateEdit::down-arrow:hover, QDateEdit::down-arrow:focus {\n"
"  image: url(\":/qss_icons/images/darkstyle_icons/arrow_down.png\");\n"
"}\n"
"\n"
"QDateEdit QAbstractItemView {\n"
"  background-color: #383838;\n"
"  border-radius: 4px;\n"
"  border: 1px solid #32414B;\n"
"  selection-background-color: hsl(0, 0%, 70%);\n"
"}\n"
"\n"
"/* what extends this? */\n"
"\n"
"QAbstractView:hover {\n"
"  border: 1px solid hsl(0, 0%, 60%);\n"
"  color: #F0F0F0;\n"
"}\n"
"\n"
"QAbstractView:selected {\n"
"  background: hsl(0, 0%, 70%);\n"
"  color: #32414B;\n"
"}\n"
"\n"
"PlotWidget {\n"
"  padding: 0;\n"
"}\n"
"\n"
"/* ---------------------------------------------------------------------- \n"
"   These are the Wasatch Photonics Qt \"Custom Properties\" which mimic\n"
"   the notion of standard CSS class selectors.  \n"
"   \n"
"   It would be nice to use [property=\"value\"] string selectors, but I \n"
"   couldn't get th"
                        "em to work.  These bool flags do seem to work (I don't\n"
"   even set values, just check for presence -- it defaults to 'false').\n"
"\n"
"   It would also be nice to use the following enums, but that path wasn't\n"
"   converging either; I forget why. (I think they worked in Qt Designer,\n"
"   but not in the ENLIGHTEN executable.)\n"
"\n"
"   https://doc.qt.io/qt-5/qframe.html#details\n"
"\n"
"   Shape\n"
"        NoFrame     0x00\n"
"        Box         0x01\n"
"        Panel       0x02\n"
"        WinPanel    0x03\n"
"        HLine       0x04\n"
"        VLine       0x05\n"
"        StyledPanel 0x06\n"
"\n"
"   Shadow\n"
"        Plain       0x10  \n"
"        Raised      0x20\n"
"        Sunken      0x30\n"
"\n"
"   enum StyleMask \n"
"        Shadow_Mask 0xf0  \n"
"        Shape_Mask  0x0f\n"
"\n"
"   [frameShape=\"0\"] { }\n"
"   [frameShape=\"1\"] { }\n"
"   [frameShape=\"2\"] { }\n"
"   [frameShape=\"3\"] { }\n"
"   [frameShape=\"4\"] { }\n"
"   [frameShape=\"5\"] { }\n"
"   [frameShape=\"6\"] { }\n"
""
                        "\n"
"   [frameShadow=\"16\"] { }\n"
"   [frameShadow=\"32\"] { }\n"
"   [frameShadow=\"48\"] { }\n"
"\n"
"   ---------------------------------------------------------------------- */\n"
"\n"
"[wpClear]\n"
"{\n"
"    border: none;\n"
"    background-color: transparent;\n"
"}\n"
"\n"
"[wpBox]\n"
"{\n"
"    color: #eee;\n"
"    border: 1px solid hsl(0, 0%, 37%);\n"
"    border-radius: 6px;\n"
"}\n"
"\n"
"[wpPanel]\n"
"{\n"
"    color: #eee;\n"
"    background: hsl(0, 0%, 21%);\n"
"    border: 2px solid #000000;\n"
"    border-radius: 6px;\n"
"}\n"
"\n"
"[wpGrad]\n"
"{\n"
"    color: #eee;\n"
"    background: hsl(0, 0%, 11%);\n"
"    border-style: solid;\n"
"    border: 2px solid #000000;\n"
"    border-radius: 6px;\n"
"    background-color: qlineargradient(spread:pad,\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0   hsl(0, 0%, 9%),\n"
"        stop:0.5 hsl(0, 0%, 20%),\n"
"        stop:1   hsl(0, 0%, 17%));\n"
"}\n"
"\n"
"[wpBenign]\n"
"{\n"
"    /* background: rgb(0, 165, 80); */\n"
"    colo"
                        "r: #fff;\n"
"    background-color: qlineargradient(spread:pad, \n"
"        x1:0.5, y1:1, \n"
"        x2:0.5, y2:0, \n"
"        stop:0 rgba(0, 170, 82, 255), \n"
"        stop:1 rgba(0, 140, 68, 255));\n"
"}\n"
"\n"
"[wpHazard]\n"
"{\n"
"    /* background: rgb(160, 10, 10); */\n"
"    color: #fff;\n"
"    background-color: qlineargradient(spread:pad, \n"
"        x1:0.5, y1:1, \n"
"        x2:0.5, y2:0, \n"
"        stop:0 rgba(137, 10, 10, 255), \n"
"        stop:1 rgba(186, 10, 10, 255));\n"
"}\n"
"\n"
"QComboBox\n"
"{\n"
"    color: #eee;\n"
"    background-color: qlineargradient(spread:pad, \n"
"        x1:0.5, y1:1, \n"
"        x2:0.5, y2:0, \n"
"        stop:0 hsl(0, 0%, 26%),\n"
"        stop:1 hsl(0, 0%, 37%));\n"
"    border: 1px solid hsl(0, 0%, 22%);\n"
"    border-radius: 12px;\n"
"    padding-left: 12px;\n"
"    padding-top: 6px;\n"
"    padding-bottom: 6px;\n"
"}\n"
"\n"
"QComboBox:hover\n"
"{\n"
"    border: 1px solid hsl(0, 0%, 60%);\n"
"}\n"
"\n"
"QComboBox QListView \n"
"{ \n"
"}\n"
"\n"
""
                        "[wpPanel] QPushButton:disabled,\n"
"[wpGrad]  QPushButton:disabled \n"
"{\n"
"    border: 1px solid #333;\n"
"    background-color: qlineargradient(spread:pad, \n"
"        x1:0.5, y1:1, \n"
"        x2:0.5, y2:0, \n"
"        stop:0 hsl(0, 0%, 60%),\n"
"        stop:1 hsl(0, 0%, 40%));\n"
"    border-radius: 5px;\n"
"}\n"
"\n"
"/* END: enlighten/assets/stylesheets/default/enlighten.css */\n"
"")
        MainWindow.setAnimated(True)
        MainWindow.setDockOptions(QMainWindow.DockOption.AnimatedDocks)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(5, 5, 5, -1)
        self.stackedWidget_high = QStackedWidget(self.centralwidget)
        self.stackedWidget_high.setObjectName(u"stackedWidget_high")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.stackedWidget_high.sizePolicy().hasHeightForWidth())
        self.stackedWidget_high.setSizePolicy(sizePolicy)
        self.stackedWidget_high.setMinimumSize(QSize(0, 64))
        self.stackedWidget_high.setMaximumSize(QSize(16777215, 64))
        self.page_navigation_buttons = QWidget()
        self.page_navigation_buttons.setObjectName(u"page_navigation_buttons")
        self.horizontalLayout = QHBoxLayout(self.page_navigation_buttons)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.frame_main_navigation = QFrame(self.page_navigation_buttons)
        self.frame_main_navigation.setObjectName(u"frame_main_navigation")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.frame_main_navigation.sizePolicy().hasHeightForWidth())
        self.frame_main_navigation.setSizePolicy(sizePolicy1)
        self.frame_main_navigation.setMaximumSize(QSize(16777215, 60))
        self.hboxLayout = QHBoxLayout(self.frame_main_navigation)
        self.hboxLayout.setSpacing(0)
        self.hboxLayout.setObjectName(u"hboxLayout")
        self.hboxLayout.setContentsMargins(0, 0, 0, 0)
        self.label_application_logo = QLabel(self.frame_main_navigation)
        self.label_application_logo.setObjectName(u"label_application_logo")
        sizePolicy1.setHeightForWidth(self.label_application_logo.sizePolicy().hasHeightForWidth())
        self.label_application_logo.setSizePolicy(sizePolicy1)
        self.label_application_logo.setMinimumSize(QSize(230, 60))
        self.label_application_logo.setMaximumSize(QSize(230, 60))
        self.label_application_logo.setStyleSheet(u"")
        self.label_application_logo.setPixmap(QPixmap(u":/application/images/enlightenLOGO.png"))
        self.label_application_logo.setScaledContents(True)

        self.hboxLayout.addWidget(self.label_application_logo)

        self.frame_nav_buttonbar = QFrame(self.frame_main_navigation)
        self.frame_nav_buttonbar.setObjectName(u"frame_nav_buttonbar")
        sizePolicy1.setHeightForWidth(self.frame_nav_buttonbar.sizePolicy().hasHeightForWidth())
        self.frame_nav_buttonbar.setSizePolicy(sizePolicy1)
        self.frame_nav_buttonbar.setStyleSheet(u"")
        self.hboxLayout1 = QHBoxLayout(self.frame_nav_buttonbar)
        self.hboxLayout1.setObjectName(u"hboxLayout1")
        self.comboBox_view = QComboBox(self.frame_nav_buttonbar)
        self.comboBox_view.addItem("")
        self.comboBox_view.addItem("")
        self.comboBox_view.addItem("")
        self.comboBox_view.addItem("")
        self.comboBox_view.setObjectName(u"comboBox_view")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(4)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.comboBox_view.sizePolicy().hasHeightForWidth())
        self.comboBox_view.setSizePolicy(sizePolicy2)
        self.comboBox_view.setMaximumSize(QSize(150, 16777215))
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.comboBox_view.setFont(font)
        self.comboBox_view.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        self.hboxLayout1.addWidget(self.comboBox_view)

        self.spacerItem = QSpacerItem(40, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.hboxLayout1.addItem(self.spacerItem)

        self.pushButton_raman = QPushButton(self.frame_nav_buttonbar)
        self.pushButton_raman.setObjectName(u"pushButton_raman")
        sizePolicy2.setHeightForWidth(self.pushButton_raman.sizePolicy().hasHeightForWidth())
        self.pushButton_raman.setSizePolicy(sizePolicy2)
        self.pushButton_raman.setMaximumSize(QSize(120, 30))
        self.pushButton_raman.setFont(font)
        self.pushButton_raman.setStyleSheet(u"")

        self.hboxLayout1.addWidget(self.pushButton_raman)

        self.pushButton_non_raman = QPushButton(self.frame_nav_buttonbar)
        self.pushButton_non_raman.setObjectName(u"pushButton_non_raman")
        sizePolicy2.setHeightForWidth(self.pushButton_non_raman.sizePolicy().hasHeightForWidth())
        self.pushButton_non_raman.setSizePolicy(sizePolicy2)
        self.pushButton_non_raman.setMaximumSize(QSize(120, 30))
        self.pushButton_non_raman.setFont(font)
        self.pushButton_non_raman.setStyleSheet(u"")

        self.hboxLayout1.addWidget(self.pushButton_non_raman)

        self.pushButton_expert = QPushButton(self.frame_nav_buttonbar)
        self.pushButton_expert.setObjectName(u"pushButton_expert")
        sizePolicy2.setHeightForWidth(self.pushButton_expert.sizePolicy().hasHeightForWidth())
        self.pushButton_expert.setSizePolicy(sizePolicy2)
        self.pushButton_expert.setMaximumSize(QSize(120, 30))
        self.pushButton_expert.setFont(font)
        self.pushButton_expert.setStyleSheet(u"")
        self.pushButton_expert.setCheckable(False)
        self.pushButton_expert.setChecked(False)

        self.hboxLayout1.addWidget(self.pushButton_expert)

        self.spacerItem1 = QSpacerItem(2, 20, QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Minimum)

        self.hboxLayout1.addItem(self.spacerItem1)

        self.pushButton_auto_raman_convenience = QPushButton(self.frame_nav_buttonbar)
        self.pushButton_auto_raman_convenience.setObjectName(u"pushButton_auto_raman_convenience")
        icon1 = QIcon()
        icon1.addFile(u":/greys/images/grey_icons/auto.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_auto_raman_convenience.setIcon(icon1)
        self.pushButton_auto_raman_convenience.setIconSize(QSize(20, 20))

        self.hboxLayout1.addWidget(self.pushButton_auto_raman_convenience)

        self.pushButton_laser_convenience = QPushButton(self.frame_nav_buttonbar)
        self.pushButton_laser_convenience.setObjectName(u"pushButton_laser_convenience")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy3.setHorizontalStretch(5)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.pushButton_laser_convenience.sizePolicy().hasHeightForWidth())
        self.pushButton_laser_convenience.setSizePolicy(sizePolicy3)
        self.pushButton_laser_convenience.setMinimumSize(QSize(16, 26))
        self.pushButton_laser_convenience.setMaximumSize(QSize(30, 26))
        icon2 = QIcon()
        icon2.addFile(u":/greys/images/grey_icons/laser.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_laser_convenience.setIcon(icon2)
        self.pushButton_laser_convenience.setIconSize(QSize(20, 20))

        self.hboxLayout1.addWidget(self.pushButton_laser_convenience)

        self.pushButton_dark_mode = QPushButton(self.frame_nav_buttonbar)
        self.pushButton_dark_mode.setObjectName(u"pushButton_dark_mode")
        sizePolicy1.setHeightForWidth(self.pushButton_dark_mode.sizePolicy().hasHeightForWidth())
        self.pushButton_dark_mode.setSizePolicy(sizePolicy1)
        self.pushButton_dark_mode.setMaximumSize(QSize(30, 26))
        icon3 = QIcon()
        icon3.addFile(u":/greys/images/grey_icons/dark-mode.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_dark_mode.setIcon(icon3)
        self.pushButton_dark_mode.setIconSize(QSize(16, 14))

        self.hboxLayout1.addWidget(self.pushButton_dark_mode)

        self.pushButton_whats_this = QPushButton(self.frame_nav_buttonbar)
        self.pushButton_whats_this.setObjectName(u"pushButton_whats_this")
        sizePolicy1.setHeightForWidth(self.pushButton_whats_this.sizePolicy().hasHeightForWidth())
        self.pushButton_whats_this.setSizePolicy(sizePolicy1)
        self.pushButton_whats_this.setMaximumSize(QSize(30, 26))
        icon4 = QIcon()
        icon4.addFile(u":/greys/images/grey_icons/arrow-info.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_whats_this.setIcon(icon4)
        self.pushButton_whats_this.setIconSize(QSize(16, 14))

        self.hboxLayout1.addWidget(self.pushButton_whats_this)

        self.pushButton_help = QPushButton(self.frame_nav_buttonbar)
        self.pushButton_help.setObjectName(u"pushButton_help")
        sizePolicy1.setHeightForWidth(self.pushButton_help.sizePolicy().hasHeightForWidth())
        self.pushButton_help.setSizePolicy(sizePolicy1)
        self.pushButton_help.setMaximumSize(QSize(30, 26))
        icon5 = QIcon()
        icon5.addFile(u":/greys/images/grey_icons/question-mark.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_help.setIcon(icon5)
        self.pushButton_help.setIconSize(QSize(16, 14))

        self.hboxLayout1.addWidget(self.pushButton_help)


        self.hboxLayout.addWidget(self.frame_nav_buttonbar)


        self.horizontalLayout.addWidget(self.frame_main_navigation)

        self.stackedWidget_high.addWidget(self.page_navigation_buttons)

        self.gridLayout.addWidget(self.stackedWidget_high, 0, 0, 1, 1)

        self.splitter_left_vs_controls = QSplitter(self.centralwidget)
        self.splitter_left_vs_controls.setObjectName(u"splitter_left_vs_controls")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(2)
        sizePolicy4.setHeightForWidth(self.splitter_left_vs_controls.sizePolicy().hasHeightForWidth())
        self.splitter_left_vs_controls.setSizePolicy(sizePolicy4)
        self.splitter_left_vs_controls.setOrientation(Qt.Orientation.Horizontal)
        self.splitter_left_vs_controls.setOpaqueResize(True)
        self.stackedWidget_low = QStackedWidget(self.splitter_left_vs_controls)
        self.stackedWidget_low.setObjectName(u"stackedWidget_low")
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy5.setHorizontalStretch(2)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.stackedWidget_low.sizePolicy().hasHeightForWidth())
        self.stackedWidget_low.setSizePolicy(sizePolicy5)
        self.scrollArea_hardware = QScrollArea()
        self.scrollArea_hardware.setObjectName(u"scrollArea_hardware")
        sizePolicy6 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy6.setHorizontalStretch(0)
        sizePolicy6.setVerticalStretch(0)
        sizePolicy6.setHeightForWidth(self.scrollArea_hardware.sizePolicy().hasHeightForWidth())
        self.scrollArea_hardware.setSizePolicy(sizePolicy6)
        self.scrollArea_hardware.setMinimumSize(QSize(0, 24))
        self.scrollArea_hardware.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scrollArea_hardware.setWidgetResizable(True)
        self.page_hardware_information = QWidget()
        self.page_hardware_information.setObjectName(u"page_hardware_information")
        self.page_hardware_information.setGeometry(QRect(0, 0, 740, 5778))
        sizePolicy7 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy7.setHorizontalStretch(0)
        sizePolicy7.setVerticalStretch(0)
        sizePolicy7.setHeightForWidth(self.page_hardware_information.sizePolicy().hasHeightForWidth())
        self.page_hardware_information.setSizePolicy(sizePolicy7)
        self.hboxLayout2 = QHBoxLayout(self.page_hardware_information)
        self.hboxLayout2.setSpacing(0)
        self.hboxLayout2.setObjectName(u"hboxLayout2")
        self.hboxLayout2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_serial_eeprom_etc = QVBoxLayout()
        self.verticalLayout_serial_eeprom_etc.setSpacing(5)
        self.verticalLayout_serial_eeprom_etc.setObjectName(u"verticalLayout_serial_eeprom_etc")
        self.horizontalLayout_serial_and_image = QHBoxLayout()
        self.horizontalLayout_serial_and_image.setObjectName(u"horizontalLayout_serial_and_image")
        self.label_serial = QLabel(self.page_hardware_information)
        self.label_serial.setObjectName(u"label_serial")
        self.label_serial.setEnabled(True)
        sizePolicy.setHeightForWidth(self.label_serial.sizePolicy().hasHeightForWidth())
        self.label_serial.setSizePolicy(sizePolicy)
        self.label_serial.setMinimumSize(QSize(200, 20))
        font1 = QFont()
        font1.setPointSize(20)
        font1.setBold(True)
        self.label_serial.setFont(font1)

        self.horizontalLayout_serial_and_image.addWidget(self.label_serial)

        self.label_product_image = QLabel(self.page_hardware_information)
        self.label_product_image.setObjectName(u"label_product_image")
        self.label_product_image.setPixmap(QPixmap(u":/spectrometers/images/devices/WP-785X-ILP.png"))
        self.label_product_image.setScaledContents(False)

        self.horizontalLayout_serial_and_image.addWidget(self.label_product_image)


        self.verticalLayout_serial_eeprom_etc.addLayout(self.horizontalLayout_serial_and_image)

        self.frame_eeprom_contents_white = QFrame(self.page_hardware_information)
        self.frame_eeprom_contents_white.setObjectName(u"frame_eeprom_contents_white")
        self.frame_eeprom_contents_white.setMaximumSize(QSize(450, 16777215))
        self.frame_eeprom_contents_white.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_eeprom_contents_white.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_eeprom_contents_white.setProperty(u"wpBox", False)
        self.vboxLayout = QVBoxLayout(self.frame_eeprom_contents_white)
        self.vboxLayout.setSpacing(0)
        self.vboxLayout.setObjectName(u"vboxLayout")
        self.vboxLayout.setContentsMargins(0, 0, 0, 0)
        self.searchFormLayout = QFormLayout()
        self.searchFormLayout.setObjectName(u"searchFormLayout")
        self.searchLabel = QLabel(self.frame_eeprom_contents_white)
        self.searchLabel.setObjectName(u"searchLabel")

        self.searchFormLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.searchLabel)

        self.searchLineEdit = QLineEdit(self.frame_eeprom_contents_white)
        self.searchLineEdit.setObjectName(u"searchLineEdit")

        self.searchFormLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.searchLineEdit)


        self.vboxLayout.addLayout(self.searchFormLayout)

        self.frame_eeprom_editor = QFrame(self.frame_eeprom_contents_white)
        self.frame_eeprom_editor.setObjectName(u"frame_eeprom_editor")
        self.frame_eeprom_editor.setProperty(u"wpPanel", False)
        self.vboxLayout1 = QVBoxLayout(self.frame_eeprom_editor)
        self.vboxLayout1.setObjectName(u"vboxLayout1")
        self.hboxLayout3 = QHBoxLayout()
        self.hboxLayout3.setObjectName(u"hboxLayout3")
        self.hboxLayout3.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self.hboxLayout3.setContentsMargins(-1, 0, -1, -1)
        self.label = QLabel(self.frame_eeprom_editor)
        self.label.setObjectName(u"label")
        self.label.setFont(font)

        self.hboxLayout3.addWidget(self.label)

        self.spacerItem2 = QSpacerItem(40, 20, QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Minimum)

        self.hboxLayout3.addItem(self.spacerItem2)

        self.pushButton_eeprom_clipboard = QPushButton(self.frame_eeprom_editor)
        self.pushButton_eeprom_clipboard.setObjectName(u"pushButton_eeprom_clipboard")
        self.pushButton_eeprom_clipboard.setMinimumSize(QSize(30, 26))
        icon6 = QIcon()
        icon6.addFile(u":/greys/images/grey_icons/clipboard.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_eeprom_clipboard.setIcon(icon6)
        self.pushButton_eeprom_clipboard.setIconSize(QSize(24, 24))

        self.hboxLayout3.addWidget(self.pushButton_eeprom_clipboard)


        self.vboxLayout1.addLayout(self.hboxLayout3)

        self.frame_eeprom_page_0_white = QFrame(self.frame_eeprom_editor)
        self.frame_eeprom_page_0_white.setObjectName(u"frame_eeprom_page_0_white")
        self.frame_eeprom_page_0_white.setProperty(u"wpBox", False)
        self.vboxLayout2 = QVBoxLayout(self.frame_eeprom_page_0_white)
        self.vboxLayout2.setSpacing(0)
        self.vboxLayout2.setObjectName(u"vboxLayout2")
        self.vboxLayout2.setContentsMargins(0, 0, 0, 0)
        self.frame_eeprom_page_0 = QFrame(self.frame_eeprom_page_0_white)
        self.frame_eeprom_page_0.setObjectName(u"frame_eeprom_page_0")
        self.frame_eeprom_page_0.setMinimumSize(QSize(0, 0))
        self.frame_eeprom_page_0.setProperty(u"wpPanel", False)
        self.vboxLayout3 = QVBoxLayout(self.frame_eeprom_page_0)
        self.vboxLayout3.setObjectName(u"vboxLayout3")
        self.label1 = QLabel(self.frame_eeprom_page_0)
        self.label1.setObjectName(u"label1")
        self.label1.setFont(font)

        self.vboxLayout3.addWidget(self.label1)

        self.formLayout_ee_page_0 = QFormLayout()
        self.formLayout_ee_page_0.setObjectName(u"formLayout_ee_page_0")
        self.formLayout_ee_page_0.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.formLayout_ee_page_0.setLabelAlignment(Qt.AlignmentFlag.AlignCenter)
        self.formLayout_ee_page_0.setFormAlignment(Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignTop)
        self.formLayout_ee_page_0.setVerticalSpacing(4)
        self.lineEdit_ee_serial_number = QLineEdit(self.frame_eeprom_page_0)
        self.lineEdit_ee_serial_number.setObjectName(u"lineEdit_ee_serial_number")

        self.formLayout_ee_page_0.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lineEdit_ee_serial_number)

        self.label2 = QLabel(self.frame_eeprom_page_0)
        self.label2.setObjectName(u"label2")

        self.formLayout_ee_page_0.setWidget(0, QFormLayout.ItemRole.FieldRole, self.label2)

        self.lineEdit_ee_model = QLineEdit(self.frame_eeprom_page_0)
        self.lineEdit_ee_model.setObjectName(u"lineEdit_ee_model")

        self.formLayout_ee_page_0.setWidget(1, QFormLayout.ItemRole.LabelRole, self.lineEdit_ee_model)

        self.label3 = QLabel(self.frame_eeprom_page_0)
        self.label3.setObjectName(u"label3")

        self.formLayout_ee_page_0.setWidget(1, QFormLayout.ItemRole.FieldRole, self.label3)

        self.checkBox_ee_has_cooling = QCheckBox(self.frame_eeprom_page_0)
        self.checkBox_ee_has_cooling.setObjectName(u"checkBox_ee_has_cooling")

        self.formLayout_ee_page_0.setWidget(3, QFormLayout.ItemRole.LabelRole, self.checkBox_ee_has_cooling)

        self.label4 = QLabel(self.frame_eeprom_page_0)
        self.label4.setObjectName(u"label4")

        self.formLayout_ee_page_0.setWidget(3, QFormLayout.ItemRole.FieldRole, self.label4)

        self.checkBox_ee_has_battery = QCheckBox(self.frame_eeprom_page_0)
        self.checkBox_ee_has_battery.setObjectName(u"checkBox_ee_has_battery")

        self.formLayout_ee_page_0.setWidget(4, QFormLayout.ItemRole.LabelRole, self.checkBox_ee_has_battery)

        self.label5 = QLabel(self.frame_eeprom_page_0)
        self.label5.setObjectName(u"label5")

        self.formLayout_ee_page_0.setWidget(4, QFormLayout.ItemRole.FieldRole, self.label5)

        self.checkBox_ee_has_laser = QCheckBox(self.frame_eeprom_page_0)
        self.checkBox_ee_has_laser.setObjectName(u"checkBox_ee_has_laser")

        self.formLayout_ee_page_0.setWidget(5, QFormLayout.ItemRole.LabelRole, self.checkBox_ee_has_laser)

        self.label6 = QLabel(self.frame_eeprom_page_0)
        self.label6.setObjectName(u"label6")

        self.formLayout_ee_page_0.setWidget(5, QFormLayout.ItemRole.FieldRole, self.label6)

        self.checkBox_ee_invert_x_axis = QCheckBox(self.frame_eeprom_page_0)
        self.checkBox_ee_invert_x_axis.setObjectName(u"checkBox_ee_invert_x_axis")

        self.formLayout_ee_page_0.setWidget(6, QFormLayout.ItemRole.LabelRole, self.checkBox_ee_invert_x_axis)

        self.label7 = QLabel(self.frame_eeprom_page_0)
        self.label7.setObjectName(u"label7")

        self.formLayout_ee_page_0.setWidget(6, QFormLayout.ItemRole.FieldRole, self.label7)

        self.checkBox_ee_horiz_binning_enabled = QCheckBox(self.frame_eeprom_page_0)
        self.checkBox_ee_horiz_binning_enabled.setObjectName(u"checkBox_ee_horiz_binning_enabled")

        self.formLayout_ee_page_0.setWidget(7, QFormLayout.ItemRole.LabelRole, self.checkBox_ee_horiz_binning_enabled)

        self.label8 = QLabel(self.frame_eeprom_page_0)
        self.label8.setObjectName(u"label8")

        self.formLayout_ee_page_0.setWidget(7, QFormLayout.ItemRole.FieldRole, self.label8)

        self.checkBox_ee_gen15 = QCheckBox(self.frame_eeprom_page_0)
        self.checkBox_ee_gen15.setObjectName(u"checkBox_ee_gen15")

        self.formLayout_ee_page_0.setWidget(8, QFormLayout.ItemRole.LabelRole, self.checkBox_ee_gen15)

        self.label9 = QLabel(self.frame_eeprom_page_0)
        self.label9.setObjectName(u"label9")

        self.formLayout_ee_page_0.setWidget(8, QFormLayout.ItemRole.FieldRole, self.label9)

        self.checkBox_ee_cutoff_filter_installed = QCheckBox(self.frame_eeprom_page_0)
        self.checkBox_ee_cutoff_filter_installed.setObjectName(u"checkBox_ee_cutoff_filter_installed")

        self.formLayout_ee_page_0.setWidget(9, QFormLayout.ItemRole.LabelRole, self.checkBox_ee_cutoff_filter_installed)

        self.label10 = QLabel(self.frame_eeprom_page_0)
        self.label10.setObjectName(u"label10")

        self.formLayout_ee_page_0.setWidget(9, QFormLayout.ItemRole.FieldRole, self.label10)

        self.checkBox_ee_hardware_even_odd = QCheckBox(self.frame_eeprom_page_0)
        self.checkBox_ee_hardware_even_odd.setObjectName(u"checkBox_ee_hardware_even_odd")

        self.formLayout_ee_page_0.setWidget(10, QFormLayout.ItemRole.LabelRole, self.checkBox_ee_hardware_even_odd)

        self.label11 = QLabel(self.frame_eeprom_page_0)
        self.label11.setObjectName(u"label11")

        self.formLayout_ee_page_0.setWidget(10, QFormLayout.ItemRole.FieldRole, self.label11)

        self.checkBox_ee_sig_laser_tec = QCheckBox(self.frame_eeprom_page_0)
        self.checkBox_ee_sig_laser_tec.setObjectName(u"checkBox_ee_sig_laser_tec")

        self.formLayout_ee_page_0.setWidget(11, QFormLayout.ItemRole.LabelRole, self.checkBox_ee_sig_laser_tec)

        self.label12 = QLabel(self.frame_eeprom_page_0)
        self.label12.setObjectName(u"label12")

        self.formLayout_ee_page_0.setWidget(11, QFormLayout.ItemRole.FieldRole, self.label12)

        self.checkBox_ee_has_interlock_feedback = QCheckBox(self.frame_eeprom_page_0)
        self.checkBox_ee_has_interlock_feedback.setObjectName(u"checkBox_ee_has_interlock_feedback")

        self.formLayout_ee_page_0.setWidget(12, QFormLayout.ItemRole.LabelRole, self.checkBox_ee_has_interlock_feedback)

        self.label13 = QLabel(self.frame_eeprom_page_0)
        self.label13.setObjectName(u"label13")

        self.formLayout_ee_page_0.setWidget(12, QFormLayout.ItemRole.FieldRole, self.label13)

        self.checkBox_ee_has_shutter = QCheckBox(self.frame_eeprom_page_0)
        self.checkBox_ee_has_shutter.setObjectName(u"checkBox_ee_has_shutter")

        self.formLayout_ee_page_0.setWidget(13, QFormLayout.ItemRole.LabelRole, self.checkBox_ee_has_shutter)

        self.label14 = QLabel(self.frame_eeprom_page_0)
        self.label14.setObjectName(u"label14")

        self.formLayout_ee_page_0.setWidget(13, QFormLayout.ItemRole.FieldRole, self.label14)

        self.checkBox_ee_disable_ble_power = QCheckBox(self.frame_eeprom_page_0)
        self.checkBox_ee_disable_ble_power.setObjectName(u"checkBox_ee_disable_ble_power")

        self.formLayout_ee_page_0.setWidget(14, QFormLayout.ItemRole.LabelRole, self.checkBox_ee_disable_ble_power)

        self.label15 = QLabel(self.frame_eeprom_page_0)
        self.label15.setObjectName(u"label15")

        self.formLayout_ee_page_0.setWidget(14, QFormLayout.ItemRole.FieldRole, self.label15)

        self.checkBox_ee_disable_laser_armed_indicator = QCheckBox(self.frame_eeprom_page_0)
        self.checkBox_ee_disable_laser_armed_indicator.setObjectName(u"checkBox_ee_disable_laser_armed_indicator")

        self.formLayout_ee_page_0.setWidget(15, QFormLayout.ItemRole.LabelRole, self.checkBox_ee_disable_laser_armed_indicator)

        self.label16 = QLabel(self.frame_eeprom_page_0)
        self.label16.setObjectName(u"label16")

        self.formLayout_ee_page_0.setWidget(15, QFormLayout.ItemRole.FieldRole, self.label16)

        self.doubleSpinBox_ee_excitation_nm_float = QDoubleSpinBox(self.frame_eeprom_page_0)
        self.doubleSpinBox_ee_excitation_nm_float.setObjectName(u"doubleSpinBox_ee_excitation_nm_float")
        self.doubleSpinBox_ee_excitation_nm_float.setMinimumSize(QSize(125, 0))
        self.doubleSpinBox_ee_excitation_nm_float.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.doubleSpinBox_ee_excitation_nm_float.setKeyboardTracking(False)
        self.doubleSpinBox_ee_excitation_nm_float.setDecimals(3)
        self.doubleSpinBox_ee_excitation_nm_float.setMinimum(0.000000000000000)
        self.doubleSpinBox_ee_excitation_nm_float.setMaximum(2500.000000000000000)
        self.doubleSpinBox_ee_excitation_nm_float.setSingleStep(0.010000000000000)
        self.doubleSpinBox_ee_excitation_nm_float.setValue(785.000000000000000)

        self.formLayout_ee_page_0.setWidget(17, QFormLayout.ItemRole.LabelRole, self.doubleSpinBox_ee_excitation_nm_float)

        self.label17 = QLabel(self.frame_eeprom_page_0)
        self.label17.setObjectName(u"label17")

        self.formLayout_ee_page_0.setWidget(17, QFormLayout.ItemRole.FieldRole, self.label17)

        self.spinBox_ee_slit_size_um = QSpinBox(self.frame_eeprom_page_0)
        self.spinBox_ee_slit_size_um.setObjectName(u"spinBox_ee_slit_size_um")
        self.spinBox_ee_slit_size_um.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_slit_size_um.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_slit_size_um.setKeyboardTracking(False)
        self.spinBox_ee_slit_size_um.setMinimum(5)
        self.spinBox_ee_slit_size_um.setMaximum(1000)
        self.spinBox_ee_slit_size_um.setSingleStep(5)
        self.spinBox_ee_slit_size_um.setValue(50)

        self.formLayout_ee_page_0.setWidget(18, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_slit_size_um)

        self.label18 = QLabel(self.frame_eeprom_page_0)
        self.label18.setObjectName(u"label18")

        self.formLayout_ee_page_0.setWidget(18, QFormLayout.ItemRole.FieldRole, self.label18)

        self.spinBox_ee_startup_integration_time_ms = QSpinBox(self.frame_eeprom_page_0)
        self.spinBox_ee_startup_integration_time_ms.setObjectName(u"spinBox_ee_startup_integration_time_ms")
        self.spinBox_ee_startup_integration_time_ms.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_startup_integration_time_ms.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_startup_integration_time_ms.setKeyboardTracking(False)
        self.spinBox_ee_startup_integration_time_ms.setMinimum(1)
        self.spinBox_ee_startup_integration_time_ms.setMaximum(60000)
        self.spinBox_ee_startup_integration_time_ms.setValue(10)

        self.formLayout_ee_page_0.setWidget(19, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_startup_integration_time_ms)

        self.label19 = QLabel(self.frame_eeprom_page_0)
        self.label19.setObjectName(u"label19")

        self.formLayout_ee_page_0.setWidget(19, QFormLayout.ItemRole.FieldRole, self.label19)

        self.spinBox_ee_startup_temp_degC = QSpinBox(self.frame_eeprom_page_0)
        self.spinBox_ee_startup_temp_degC.setObjectName(u"spinBox_ee_startup_temp_degC")
        self.spinBox_ee_startup_temp_degC.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_startup_temp_degC.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_startup_temp_degC.setKeyboardTracking(False)
        self.spinBox_ee_startup_temp_degC.setMinimum(-120)
        self.spinBox_ee_startup_temp_degC.setMaximum(4095)
        self.spinBox_ee_startup_temp_degC.setValue(10)

        self.formLayout_ee_page_0.setWidget(20, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_startup_temp_degC)

        self.label20 = QLabel(self.frame_eeprom_page_0)
        self.label20.setObjectName(u"label20")

        self.formLayout_ee_page_0.setWidget(20, QFormLayout.ItemRole.FieldRole, self.label20)

        self.spinBox_ee_startup_triggering_scheme = QSpinBox(self.frame_eeprom_page_0)
        self.spinBox_ee_startup_triggering_scheme.setObjectName(u"spinBox_ee_startup_triggering_scheme")
        self.spinBox_ee_startup_triggering_scheme.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_startup_triggering_scheme.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_startup_triggering_scheme.setKeyboardTracking(False)
        self.spinBox_ee_startup_triggering_scheme.setMaximum(255)

        self.formLayout_ee_page_0.setWidget(21, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_startup_triggering_scheme)

        self.label21 = QLabel(self.frame_eeprom_page_0)
        self.label21.setObjectName(u"label21")

        self.formLayout_ee_page_0.setWidget(21, QFormLayout.ItemRole.FieldRole, self.label21)

        self.doubleSpinBox_ee_detector_gain = QDoubleSpinBox(self.frame_eeprom_page_0)
        self.doubleSpinBox_ee_detector_gain.setObjectName(u"doubleSpinBox_ee_detector_gain")
        self.doubleSpinBox_ee_detector_gain.setMinimumSize(QSize(125, 0))
        self.doubleSpinBox_ee_detector_gain.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.doubleSpinBox_ee_detector_gain.setKeyboardTracking(False)
        self.doubleSpinBox_ee_detector_gain.setDecimals(5)
        self.doubleSpinBox_ee_detector_gain.setMinimum(0.000000000000000)
        self.doubleSpinBox_ee_detector_gain.setMaximum(255.000000000000000)
        self.doubleSpinBox_ee_detector_gain.setValue(1.900000000000000)

        self.formLayout_ee_page_0.setWidget(22, QFormLayout.ItemRole.LabelRole, self.doubleSpinBox_ee_detector_gain)

        self.label22 = QLabel(self.frame_eeprom_page_0)
        self.label22.setObjectName(u"label22")

        self.formLayout_ee_page_0.setWidget(22, QFormLayout.ItemRole.FieldRole, self.label22)

        self.spinBox_ee_detector_offset = QSpinBox(self.frame_eeprom_page_0)
        self.spinBox_ee_detector_offset.setObjectName(u"spinBox_ee_detector_offset")
        self.spinBox_ee_detector_offset.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_detector_offset.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_detector_offset.setKeyboardTracking(False)
        self.spinBox_ee_detector_offset.setMinimum(-32000)
        self.spinBox_ee_detector_offset.setMaximum(32000)

        self.formLayout_ee_page_0.setWidget(23, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_detector_offset)

        self.label23 = QLabel(self.frame_eeprom_page_0)
        self.label23.setObjectName(u"label23")

        self.formLayout_ee_page_0.setWidget(23, QFormLayout.ItemRole.FieldRole, self.label23)

        self.doubleSpinBox_ee_detector_gain_odd = QDoubleSpinBox(self.frame_eeprom_page_0)
        self.doubleSpinBox_ee_detector_gain_odd.setObjectName(u"doubleSpinBox_ee_detector_gain_odd")
        self.doubleSpinBox_ee_detector_gain_odd.setMinimumSize(QSize(125, 0))
        self.doubleSpinBox_ee_detector_gain_odd.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.doubleSpinBox_ee_detector_gain_odd.setKeyboardTracking(False)
        self.doubleSpinBox_ee_detector_gain_odd.setDecimals(5)
        self.doubleSpinBox_ee_detector_gain_odd.setMinimum(0.000000000000000)
        self.doubleSpinBox_ee_detector_gain_odd.setMaximum(255.000000000000000)

        self.formLayout_ee_page_0.setWidget(24, QFormLayout.ItemRole.LabelRole, self.doubleSpinBox_ee_detector_gain_odd)

        self.label24 = QLabel(self.frame_eeprom_page_0)
        self.label24.setObjectName(u"label24")

        self.formLayout_ee_page_0.setWidget(24, QFormLayout.ItemRole.FieldRole, self.label24)

        self.spinBox_ee_detector_offset_odd = QSpinBox(self.frame_eeprom_page_0)
        self.spinBox_ee_detector_offset_odd.setObjectName(u"spinBox_ee_detector_offset_odd")
        self.spinBox_ee_detector_offset_odd.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_detector_offset_odd.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_detector_offset_odd.setKeyboardTracking(False)
        self.spinBox_ee_detector_offset_odd.setMinimum(-32000)
        self.spinBox_ee_detector_offset_odd.setMaximum(32000)

        self.formLayout_ee_page_0.setWidget(25, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_detector_offset_odd)

        self.label25 = QLabel(self.frame_eeprom_page_0)
        self.label25.setObjectName(u"label25")

        self.formLayout_ee_page_0.setWidget(25, QFormLayout.ItemRole.FieldRole, self.label25)

        self.spinBox_ee_startup_laser_tec_setpoint = QSpinBox(self.frame_eeprom_page_0)
        self.spinBox_ee_startup_laser_tec_setpoint.setObjectName(u"spinBox_ee_startup_laser_tec_setpoint")
        self.spinBox_ee_startup_laser_tec_setpoint.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_startup_laser_tec_setpoint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_startup_laser_tec_setpoint.setKeyboardTracking(False)
        self.spinBox_ee_startup_laser_tec_setpoint.setMinimum(0)
        self.spinBox_ee_startup_laser_tec_setpoint.setMaximum(4095)

        self.formLayout_ee_page_0.setWidget(26, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_startup_laser_tec_setpoint)

        self.label26 = QLabel(self.frame_eeprom_page_0)
        self.label26.setObjectName(u"label26")

        self.formLayout_ee_page_0.setWidget(26, QFormLayout.ItemRole.FieldRole, self.label26)

        self.label_ee_format = QLabel(self.frame_eeprom_page_0)
        self.label_ee_format.setObjectName(u"label_ee_format")

        self.formLayout_ee_page_0.setWidget(27, QFormLayout.ItemRole.LabelRole, self.label_ee_format)

        self.label27 = QLabel(self.frame_eeprom_page_0)
        self.label27.setObjectName(u"label27")

        self.formLayout_ee_page_0.setWidget(27, QFormLayout.ItemRole.FieldRole, self.label27)


        self.vboxLayout3.addLayout(self.formLayout_ee_page_0)


        self.vboxLayout2.addWidget(self.frame_eeprom_page_0)


        self.vboxLayout1.addWidget(self.frame_eeprom_page_0_white)

        self.frame_eeprom_page_1_white = QFrame(self.frame_eeprom_editor)
        self.frame_eeprom_page_1_white.setObjectName(u"frame_eeprom_page_1_white")
        self.frame_eeprom_page_1_white.setProperty(u"wpBox", False)
        self.vboxLayout4 = QVBoxLayout(self.frame_eeprom_page_1_white)
        self.vboxLayout4.setSpacing(0)
        self.vboxLayout4.setObjectName(u"vboxLayout4")
        self.vboxLayout4.setContentsMargins(0, 0, 0, 0)
        self.frame_eeprom_page_1 = QFrame(self.frame_eeprom_page_1_white)
        self.frame_eeprom_page_1.setObjectName(u"frame_eeprom_page_1")
        self.frame_eeprom_page_1.setProperty(u"wpPanel", False)
        self.vboxLayout5 = QVBoxLayout(self.frame_eeprom_page_1)
        self.vboxLayout5.setObjectName(u"vboxLayout5")
        self.label28 = QLabel(self.frame_eeprom_page_1)
        self.label28.setObjectName(u"label28")
        self.label28.setFont(font)

        self.vboxLayout5.addWidget(self.label28)

        self.formLayout_ee_page_1 = QFormLayout()
        self.formLayout_ee_page_1.setObjectName(u"formLayout_ee_page_1")
        self.formLayout_ee_page_1.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.formLayout_ee_page_1.setLabelAlignment(Qt.AlignmentFlag.AlignCenter)
        self.formLayout_ee_page_1.setFormAlignment(Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignTop)
        self.formLayout_ee_page_1.setVerticalSpacing(4)
        self.lineEdit_ee_wavelength_coeff_0 = QLineEdit(self.frame_eeprom_page_1)
        self.lineEdit_ee_wavelength_coeff_0.setObjectName(u"lineEdit_ee_wavelength_coeff_0")

        self.formLayout_ee_page_1.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lineEdit_ee_wavelength_coeff_0)

        self.label29 = QLabel(self.frame_eeprom_page_1)
        self.label29.setObjectName(u"label29")

        self.formLayout_ee_page_1.setWidget(0, QFormLayout.ItemRole.FieldRole, self.label29)

        self.label30 = QLabel(self.frame_eeprom_page_1)
        self.label30.setObjectName(u"label30")

        self.formLayout_ee_page_1.setWidget(1, QFormLayout.ItemRole.FieldRole, self.label30)

        self.label31 = QLabel(self.frame_eeprom_page_1)
        self.label31.setObjectName(u"label31")

        self.formLayout_ee_page_1.setWidget(2, QFormLayout.ItemRole.FieldRole, self.label31)

        self.label32 = QLabel(self.frame_eeprom_page_1)
        self.label32.setObjectName(u"label32")

        self.formLayout_ee_page_1.setWidget(3, QFormLayout.ItemRole.FieldRole, self.label32)

        self.label33 = QLabel(self.frame_eeprom_page_1)
        self.label33.setObjectName(u"label33")

        self.formLayout_ee_page_1.setWidget(5, QFormLayout.ItemRole.FieldRole, self.label33)

        self.label34 = QLabel(self.frame_eeprom_page_1)
        self.label34.setObjectName(u"label34")

        self.formLayout_ee_page_1.setWidget(6, QFormLayout.ItemRole.FieldRole, self.label34)

        self.label35 = QLabel(self.frame_eeprom_page_1)
        self.label35.setObjectName(u"label35")

        self.formLayout_ee_page_1.setWidget(7, QFormLayout.ItemRole.FieldRole, self.label35)

        self.label36 = QLabel(self.frame_eeprom_page_1)
        self.label36.setObjectName(u"label36")

        self.formLayout_ee_page_1.setWidget(8, QFormLayout.ItemRole.FieldRole, self.label36)

        self.label37 = QLabel(self.frame_eeprom_page_1)
        self.label37.setObjectName(u"label37")

        self.formLayout_ee_page_1.setWidget(9, QFormLayout.ItemRole.FieldRole, self.label37)

        self.label38 = QLabel(self.frame_eeprom_page_1)
        self.label38.setObjectName(u"label38")

        self.formLayout_ee_page_1.setWidget(10, QFormLayout.ItemRole.FieldRole, self.label38)

        self.label39 = QLabel(self.frame_eeprom_page_1)
        self.label39.setObjectName(u"label39")

        self.formLayout_ee_page_1.setWidget(11, QFormLayout.ItemRole.FieldRole, self.label39)

        self.label40 = QLabel(self.frame_eeprom_page_1)
        self.label40.setObjectName(u"label40")

        self.formLayout_ee_page_1.setWidget(12, QFormLayout.ItemRole.FieldRole, self.label40)

        self.label41 = QLabel(self.frame_eeprom_page_1)
        self.label41.setObjectName(u"label41")

        self.formLayout_ee_page_1.setWidget(13, QFormLayout.ItemRole.FieldRole, self.label41)

        self.label42 = QLabel(self.frame_eeprom_page_1)
        self.label42.setObjectName(u"label42")

        self.formLayout_ee_page_1.setWidget(14, QFormLayout.ItemRole.FieldRole, self.label42)

        self.label43 = QLabel(self.frame_eeprom_page_1)
        self.label43.setObjectName(u"label43")

        self.formLayout_ee_page_1.setWidget(15, QFormLayout.ItemRole.FieldRole, self.label43)

        self.label44 = QLabel(self.frame_eeprom_page_1)
        self.label44.setObjectName(u"label44")

        self.formLayout_ee_page_1.setWidget(16, QFormLayout.ItemRole.FieldRole, self.label44)

        self.lineEdit_ee_wavelength_coeff_1 = QLineEdit(self.frame_eeprom_page_1)
        self.lineEdit_ee_wavelength_coeff_1.setObjectName(u"lineEdit_ee_wavelength_coeff_1")

        self.formLayout_ee_page_1.setWidget(1, QFormLayout.ItemRole.LabelRole, self.lineEdit_ee_wavelength_coeff_1)

        self.lineEdit_ee_wavelength_coeff_2 = QLineEdit(self.frame_eeprom_page_1)
        self.lineEdit_ee_wavelength_coeff_2.setObjectName(u"lineEdit_ee_wavelength_coeff_2")

        self.formLayout_ee_page_1.setWidget(2, QFormLayout.ItemRole.LabelRole, self.lineEdit_ee_wavelength_coeff_2)

        self.lineEdit_ee_wavelength_coeff_3 = QLineEdit(self.frame_eeprom_page_1)
        self.lineEdit_ee_wavelength_coeff_3.setObjectName(u"lineEdit_ee_wavelength_coeff_3")

        self.formLayout_ee_page_1.setWidget(3, QFormLayout.ItemRole.LabelRole, self.lineEdit_ee_wavelength_coeff_3)

        self.lineEdit_ee_degC_to_dac_coeff_0 = QLineEdit(self.frame_eeprom_page_1)
        self.lineEdit_ee_degC_to_dac_coeff_0.setObjectName(u"lineEdit_ee_degC_to_dac_coeff_0")

        self.formLayout_ee_page_1.setWidget(5, QFormLayout.ItemRole.LabelRole, self.lineEdit_ee_degC_to_dac_coeff_0)

        self.lineEdit_ee_degC_to_dac_coeff_1 = QLineEdit(self.frame_eeprom_page_1)
        self.lineEdit_ee_degC_to_dac_coeff_1.setObjectName(u"lineEdit_ee_degC_to_dac_coeff_1")

        self.formLayout_ee_page_1.setWidget(6, QFormLayout.ItemRole.LabelRole, self.lineEdit_ee_degC_to_dac_coeff_1)

        self.lineEdit_ee_degC_to_dac_coeff_2 = QLineEdit(self.frame_eeprom_page_1)
        self.lineEdit_ee_degC_to_dac_coeff_2.setObjectName(u"lineEdit_ee_degC_to_dac_coeff_2")

        self.formLayout_ee_page_1.setWidget(7, QFormLayout.ItemRole.LabelRole, self.lineEdit_ee_degC_to_dac_coeff_2)

        self.spinBox_ee_max_temp_degC = QSpinBox(self.frame_eeprom_page_1)
        self.spinBox_ee_max_temp_degC.setObjectName(u"spinBox_ee_max_temp_degC")
        self.spinBox_ee_max_temp_degC.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_max_temp_degC.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_max_temp_degC.setKeyboardTracking(False)
        self.spinBox_ee_max_temp_degC.setMinimum(-30)
        self.spinBox_ee_max_temp_degC.setMaximum(50)
        self.spinBox_ee_max_temp_degC.setValue(20)

        self.formLayout_ee_page_1.setWidget(8, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_max_temp_degC)

        self.spinBox_ee_min_temp_degC = QSpinBox(self.frame_eeprom_page_1)
        self.spinBox_ee_min_temp_degC.setObjectName(u"spinBox_ee_min_temp_degC")
        self.spinBox_ee_min_temp_degC.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_min_temp_degC.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_min_temp_degC.setKeyboardTracking(False)
        self.spinBox_ee_min_temp_degC.setMinimum(-300)
        self.spinBox_ee_min_temp_degC.setMaximum(50)
        self.spinBox_ee_min_temp_degC.setValue(0)

        self.formLayout_ee_page_1.setWidget(9, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_min_temp_degC)

        self.lineEdit_ee_adc_to_degC_coeff_0 = QLineEdit(self.frame_eeprom_page_1)
        self.lineEdit_ee_adc_to_degC_coeff_0.setObjectName(u"lineEdit_ee_adc_to_degC_coeff_0")

        self.formLayout_ee_page_1.setWidget(10, QFormLayout.ItemRole.LabelRole, self.lineEdit_ee_adc_to_degC_coeff_0)

        self.lineEdit_ee_adc_to_degC_coeff_1 = QLineEdit(self.frame_eeprom_page_1)
        self.lineEdit_ee_adc_to_degC_coeff_1.setObjectName(u"lineEdit_ee_adc_to_degC_coeff_1")

        self.formLayout_ee_page_1.setWidget(11, QFormLayout.ItemRole.LabelRole, self.lineEdit_ee_adc_to_degC_coeff_1)

        self.lineEdit_ee_adc_to_degC_coeff_2 = QLineEdit(self.frame_eeprom_page_1)
        self.lineEdit_ee_adc_to_degC_coeff_2.setObjectName(u"lineEdit_ee_adc_to_degC_coeff_2")

        self.formLayout_ee_page_1.setWidget(12, QFormLayout.ItemRole.LabelRole, self.lineEdit_ee_adc_to_degC_coeff_2)

        self.spinBox_ee_tec_r298 = QSpinBox(self.frame_eeprom_page_1)
        self.spinBox_ee_tec_r298.setObjectName(u"spinBox_ee_tec_r298")
        self.spinBox_ee_tec_r298.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_tec_r298.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_tec_r298.setKeyboardTracking(False)
        self.spinBox_ee_tec_r298.setMinimum(-32768)
        self.spinBox_ee_tec_r298.setMaximum(32767)

        self.formLayout_ee_page_1.setWidget(13, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_tec_r298)

        self.spinBox_ee_tec_beta = QSpinBox(self.frame_eeprom_page_1)
        self.spinBox_ee_tec_beta.setObjectName(u"spinBox_ee_tec_beta")
        self.spinBox_ee_tec_beta.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_tec_beta.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_tec_beta.setKeyboardTracking(False)
        self.spinBox_ee_tec_beta.setMinimum(-32768)
        self.spinBox_ee_tec_beta.setMaximum(32767)

        self.formLayout_ee_page_1.setWidget(14, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_tec_beta)

        self.lineEdit_ee_calibration_date = QLineEdit(self.frame_eeprom_page_1)
        self.lineEdit_ee_calibration_date.setObjectName(u"lineEdit_ee_calibration_date")

        self.formLayout_ee_page_1.setWidget(15, QFormLayout.ItemRole.LabelRole, self.lineEdit_ee_calibration_date)

        self.lineEdit_ee_calibrated_by = QLineEdit(self.frame_eeprom_page_1)
        self.lineEdit_ee_calibrated_by.setObjectName(u"lineEdit_ee_calibrated_by")

        self.formLayout_ee_page_1.setWidget(16, QFormLayout.ItemRole.LabelRole, self.lineEdit_ee_calibrated_by)

        self.lineEdit_ee_wavelength_coeff_4 = QLineEdit(self.frame_eeprom_page_1)
        self.lineEdit_ee_wavelength_coeff_4.setObjectName(u"lineEdit_ee_wavelength_coeff_4")

        self.formLayout_ee_page_1.setWidget(4, QFormLayout.ItemRole.LabelRole, self.lineEdit_ee_wavelength_coeff_4)

        self.label45 = QLabel(self.frame_eeprom_page_1)
        self.label45.setObjectName(u"label45")

        self.formLayout_ee_page_1.setWidget(4, QFormLayout.ItemRole.FieldRole, self.label45)


        self.vboxLayout5.addLayout(self.formLayout_ee_page_1)


        self.vboxLayout4.addWidget(self.frame_eeprom_page_1)


        self.vboxLayout1.addWidget(self.frame_eeprom_page_1_white)

        self.frame_eeprom_page_2_white = QFrame(self.frame_eeprom_editor)
        self.frame_eeprom_page_2_white.setObjectName(u"frame_eeprom_page_2_white")
        self.frame_eeprom_page_2_white.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_eeprom_page_2_white.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_eeprom_page_2_white.setProperty(u"wpBox", False)
        self.vboxLayout6 = QVBoxLayout(self.frame_eeprom_page_2_white)
        self.vboxLayout6.setSpacing(0)
        self.vboxLayout6.setObjectName(u"vboxLayout6")
        self.vboxLayout6.setContentsMargins(0, 0, 0, 0)
        self.frame_eeprom_page_2 = QFrame(self.frame_eeprom_page_2_white)
        self.frame_eeprom_page_2.setObjectName(u"frame_eeprom_page_2")
        self.frame_eeprom_page_2.setMinimumSize(QSize(0, 0))
        self.frame_eeprom_page_2.setProperty(u"wpPanel", False)
        self.vboxLayout7 = QVBoxLayout(self.frame_eeprom_page_2)
        self.vboxLayout7.setObjectName(u"vboxLayout7")
        self.label46 = QLabel(self.frame_eeprom_page_2)
        self.label46.setObjectName(u"label46")
        self.label46.setFont(font)

        self.vboxLayout7.addWidget(self.label46)

        self.formLayout_ee_page_2 = QFormLayout()
        self.formLayout_ee_page_2.setObjectName(u"formLayout_ee_page_2")
        self.formLayout_ee_page_2.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.formLayout_ee_page_2.setLabelAlignment(Qt.AlignmentFlag.AlignCenter)
        self.formLayout_ee_page_2.setVerticalSpacing(4)
        self.lineEdit_ee_detector = QLineEdit(self.frame_eeprom_page_2)
        self.lineEdit_ee_detector.setObjectName(u"lineEdit_ee_detector")

        self.formLayout_ee_page_2.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lineEdit_ee_detector)

        self.label47 = QLabel(self.frame_eeprom_page_2)
        self.label47.setObjectName(u"label47")

        self.formLayout_ee_page_2.setWidget(0, QFormLayout.ItemRole.FieldRole, self.label47)

        self.label48 = QLabel(self.frame_eeprom_page_2)
        self.label48.setObjectName(u"label48")

        self.formLayout_ee_page_2.setWidget(1, QFormLayout.ItemRole.FieldRole, self.label48)

        self.label49 = QLabel(self.frame_eeprom_page_2)
        self.label49.setObjectName(u"label49")

        self.formLayout_ee_page_2.setWidget(2, QFormLayout.ItemRole.FieldRole, self.label49)

        self.label50 = QLabel(self.frame_eeprom_page_2)
        self.label50.setObjectName(u"label50")

        self.formLayout_ee_page_2.setWidget(5, QFormLayout.ItemRole.FieldRole, self.label50)

        self.label51 = QLabel(self.frame_eeprom_page_2)
        self.label51.setObjectName(u"label51")

        self.formLayout_ee_page_2.setWidget(6, QFormLayout.ItemRole.FieldRole, self.label51)

        self.label52 = QLabel(self.frame_eeprom_page_2)
        self.label52.setObjectName(u"label52")

        self.formLayout_ee_page_2.setWidget(7, QFormLayout.ItemRole.FieldRole, self.label52)

        self.label53 = QLabel(self.frame_eeprom_page_2)
        self.label53.setObjectName(u"label53")

        self.formLayout_ee_page_2.setWidget(8, QFormLayout.ItemRole.FieldRole, self.label53)

        self.label54 = QLabel(self.frame_eeprom_page_2)
        self.label54.setObjectName(u"label54")

        self.formLayout_ee_page_2.setWidget(9, QFormLayout.ItemRole.FieldRole, self.label54)

        self.label55 = QLabel(self.frame_eeprom_page_2)
        self.label55.setObjectName(u"label55")

        self.formLayout_ee_page_2.setWidget(10, QFormLayout.ItemRole.FieldRole, self.label55)

        self.label56 = QLabel(self.frame_eeprom_page_2)
        self.label56.setObjectName(u"label56")

        self.formLayout_ee_page_2.setWidget(11, QFormLayout.ItemRole.FieldRole, self.label56)

        self.label57 = QLabel(self.frame_eeprom_page_2)
        self.label57.setObjectName(u"label57")

        self.formLayout_ee_page_2.setWidget(12, QFormLayout.ItemRole.FieldRole, self.label57)

        self.label58 = QLabel(self.frame_eeprom_page_2)
        self.label58.setObjectName(u"label58")

        self.formLayout_ee_page_2.setWidget(13, QFormLayout.ItemRole.FieldRole, self.label58)

        self.spinBox_ee_active_pixels_horizontal = QSpinBox(self.frame_eeprom_page_2)
        self.spinBox_ee_active_pixels_horizontal.setObjectName(u"spinBox_ee_active_pixels_horizontal")
        self.spinBox_ee_active_pixels_horizontal.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_active_pixels_horizontal.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_active_pixels_horizontal.setKeyboardTracking(False)
        self.spinBox_ee_active_pixels_horizontal.setMinimum(0)
        self.spinBox_ee_active_pixels_horizontal.setMaximum(9999)
        self.spinBox_ee_active_pixels_horizontal.setValue(0)

        self.formLayout_ee_page_2.setWidget(1, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_active_pixels_horizontal)

        self.spinBox_ee_active_pixels_vertical = QSpinBox(self.frame_eeprom_page_2)
        self.spinBox_ee_active_pixels_vertical.setObjectName(u"spinBox_ee_active_pixels_vertical")
        self.spinBox_ee_active_pixels_vertical.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_active_pixels_vertical.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_active_pixels_vertical.setKeyboardTracking(False)
        self.spinBox_ee_active_pixels_vertical.setMinimum(-1)
        self.spinBox_ee_active_pixels_vertical.setMaximum(4096)
        self.spinBox_ee_active_pixels_vertical.setValue(0)

        self.formLayout_ee_page_2.setWidget(2, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_active_pixels_vertical)

        self.spinBox_ee_actual_pixels_horizontal = QSpinBox(self.frame_eeprom_page_2)
        self.spinBox_ee_actual_pixels_horizontal.setObjectName(u"spinBox_ee_actual_pixels_horizontal")
        self.spinBox_ee_actual_pixels_horizontal.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_actual_pixels_horizontal.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_actual_pixels_horizontal.setKeyboardTracking(False)
        self.spinBox_ee_actual_pixels_horizontal.setMinimum(-1)
        self.spinBox_ee_actual_pixels_horizontal.setMaximum(9999)
        self.spinBox_ee_actual_pixels_horizontal.setValue(0)

        self.formLayout_ee_page_2.setWidget(5, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_actual_pixels_horizontal)

        self.spinBox_ee_roi_horizontal_start = QSpinBox(self.frame_eeprom_page_2)
        self.spinBox_ee_roi_horizontal_start.setObjectName(u"spinBox_ee_roi_horizontal_start")
        self.spinBox_ee_roi_horizontal_start.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_roi_horizontal_start.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_roi_horizontal_start.setKeyboardTracking(False)
        self.spinBox_ee_roi_horizontal_start.setMinimum(-1)
        self.spinBox_ee_roi_horizontal_start.setMaximum(9999)
        self.spinBox_ee_roi_horizontal_start.setValue(0)

        self.formLayout_ee_page_2.setWidget(6, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_roi_horizontal_start)

        self.spinBox_ee_roi_horizontal_end = QSpinBox(self.frame_eeprom_page_2)
        self.spinBox_ee_roi_horizontal_end.setObjectName(u"spinBox_ee_roi_horizontal_end")
        self.spinBox_ee_roi_horizontal_end.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_roi_horizontal_end.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_roi_horizontal_end.setKeyboardTracking(False)
        self.spinBox_ee_roi_horizontal_end.setMinimum(-1)
        self.spinBox_ee_roi_horizontal_end.setMaximum(9999)
        self.spinBox_ee_roi_horizontal_end.setValue(0)

        self.formLayout_ee_page_2.setWidget(7, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_roi_horizontal_end)

        self.spinBox_ee_roi_vertical_region_1_start = QSpinBox(self.frame_eeprom_page_2)
        self.spinBox_ee_roi_vertical_region_1_start.setObjectName(u"spinBox_ee_roi_vertical_region_1_start")
        self.spinBox_ee_roi_vertical_region_1_start.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_roi_vertical_region_1_start.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_roi_vertical_region_1_start.setKeyboardTracking(False)
        self.spinBox_ee_roi_vertical_region_1_start.setMinimum(-1)
        self.spinBox_ee_roi_vertical_region_1_start.setMaximum(2048)
        self.spinBox_ee_roi_vertical_region_1_start.setValue(0)

        self.formLayout_ee_page_2.setWidget(8, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_roi_vertical_region_1_start)

        self.spinBox_ee_roi_vertical_region_1_end = QSpinBox(self.frame_eeprom_page_2)
        self.spinBox_ee_roi_vertical_region_1_end.setObjectName(u"spinBox_ee_roi_vertical_region_1_end")
        self.spinBox_ee_roi_vertical_region_1_end.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_roi_vertical_region_1_end.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_roi_vertical_region_1_end.setKeyboardTracking(False)
        self.spinBox_ee_roi_vertical_region_1_end.setMinimum(-1)
        self.spinBox_ee_roi_vertical_region_1_end.setMaximum(2048)
        self.spinBox_ee_roi_vertical_region_1_end.setValue(0)

        self.formLayout_ee_page_2.setWidget(9, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_roi_vertical_region_1_end)

        self.spinBox_ee_roi_vertical_region_2_start = QSpinBox(self.frame_eeprom_page_2)
        self.spinBox_ee_roi_vertical_region_2_start.setObjectName(u"spinBox_ee_roi_vertical_region_2_start")
        self.spinBox_ee_roi_vertical_region_2_start.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_roi_vertical_region_2_start.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_roi_vertical_region_2_start.setKeyboardTracking(False)
        self.spinBox_ee_roi_vertical_region_2_start.setMinimum(-1)
        self.spinBox_ee_roi_vertical_region_2_start.setMaximum(2048)
        self.spinBox_ee_roi_vertical_region_2_start.setValue(0)

        self.formLayout_ee_page_2.setWidget(10, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_roi_vertical_region_2_start)

        self.spinBox_ee_roi_vertical_region_2_end = QSpinBox(self.frame_eeprom_page_2)
        self.spinBox_ee_roi_vertical_region_2_end.setObjectName(u"spinBox_ee_roi_vertical_region_2_end")
        self.spinBox_ee_roi_vertical_region_2_end.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_roi_vertical_region_2_end.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_roi_vertical_region_2_end.setKeyboardTracking(False)
        self.spinBox_ee_roi_vertical_region_2_end.setMinimum(-1)
        self.spinBox_ee_roi_vertical_region_2_end.setMaximum(2048)
        self.spinBox_ee_roi_vertical_region_2_end.setValue(0)

        self.formLayout_ee_page_2.setWidget(11, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_roi_vertical_region_2_end)

        self.spinBox_ee_roi_vertical_region_3_start = QSpinBox(self.frame_eeprom_page_2)
        self.spinBox_ee_roi_vertical_region_3_start.setObjectName(u"spinBox_ee_roi_vertical_region_3_start")
        self.spinBox_ee_roi_vertical_region_3_start.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_roi_vertical_region_3_start.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_roi_vertical_region_3_start.setKeyboardTracking(False)
        self.spinBox_ee_roi_vertical_region_3_start.setMinimum(-1)
        self.spinBox_ee_roi_vertical_region_3_start.setMaximum(2048)
        self.spinBox_ee_roi_vertical_region_3_start.setValue(0)

        self.formLayout_ee_page_2.setWidget(12, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_roi_vertical_region_3_start)

        self.spinBox_ee_roi_vertical_region_3_end = QSpinBox(self.frame_eeprom_page_2)
        self.spinBox_ee_roi_vertical_region_3_end.setObjectName(u"spinBox_ee_roi_vertical_region_3_end")
        self.spinBox_ee_roi_vertical_region_3_end.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_roi_vertical_region_3_end.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_roi_vertical_region_3_end.setKeyboardTracking(False)
        self.spinBox_ee_roi_vertical_region_3_end.setMinimum(-1)
        self.spinBox_ee_roi_vertical_region_3_end.setMaximum(2048)
        self.spinBox_ee_roi_vertical_region_3_end.setValue(0)

        self.formLayout_ee_page_2.setWidget(13, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_roi_vertical_region_3_end)

        self.spinBox_ee_laser_warmup_sec = QSpinBox(self.frame_eeprom_page_2)
        self.spinBox_ee_laser_warmup_sec.setObjectName(u"spinBox_ee_laser_warmup_sec")
        self.spinBox_ee_laser_warmup_sec.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_laser_warmup_sec.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_laser_warmup_sec.setMaximum(255)

        self.formLayout_ee_page_2.setWidget(3, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_laser_warmup_sec)

        self.label59 = QLabel(self.frame_eeprom_page_2)
        self.label59.setObjectName(u"label59")

        self.formLayout_ee_page_2.setWidget(3, QFormLayout.ItemRole.FieldRole, self.label59)


        self.vboxLayout7.addLayout(self.formLayout_ee_page_2)


        self.vboxLayout6.addWidget(self.frame_eeprom_page_2)


        self.vboxLayout1.addWidget(self.frame_eeprom_page_2_white)

        self.frame_eeprom_page_3_white = QFrame(self.frame_eeprom_editor)
        self.frame_eeprom_page_3_white.setObjectName(u"frame_eeprom_page_3_white")
        self.frame_eeprom_page_3_white.setProperty(u"wpBox", False)
        self.vboxLayout8 = QVBoxLayout(self.frame_eeprom_page_3_white)
        self.vboxLayout8.setSpacing(0)
        self.vboxLayout8.setObjectName(u"vboxLayout8")
        self.vboxLayout8.setContentsMargins(0, 0, 0, 0)
        self.frame_eeprom_page_3 = QFrame(self.frame_eeprom_page_3_white)
        self.frame_eeprom_page_3.setObjectName(u"frame_eeprom_page_3")
        self.frame_eeprom_page_3.setMinimumSize(QSize(0, 0))
        self.frame_eeprom_page_3.setProperty(u"wpPanel", False)
        self.formLayout = QFormLayout(self.frame_eeprom_page_3)
        self.formLayout.setObjectName(u"formLayout")
        self.label60 = QLabel(self.frame_eeprom_page_3)
        self.label60.setObjectName(u"label60")
        self.label60.setFont(font)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label60)

        self.formLayout_ee_page_3 = QFormLayout()
        self.formLayout_ee_page_3.setObjectName(u"formLayout_ee_page_3")
        self.formLayout_ee_page_3.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.formLayout_ee_page_3.setLabelAlignment(Qt.AlignmentFlag.AlignCenter)
        self.formLayout_ee_page_3.setFormAlignment(Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignTop)
        self.formLayout_ee_page_3.setVerticalSpacing(4)
        self.spinBox_ee_max_laser_temp_deg_c = QSpinBox(self.frame_eeprom_page_3)
        self.spinBox_ee_max_laser_temp_deg_c.setObjectName(u"spinBox_ee_max_laser_temp_deg_c")
        self.spinBox_ee_max_laser_temp_deg_c.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_max_laser_temp_deg_c.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_max_laser_temp_deg_c.setKeyboardTracking(False)
        self.spinBox_ee_max_laser_temp_deg_c.setMinimum(-128)
        self.spinBox_ee_max_laser_temp_deg_c.setMaximum(127)
        self.spinBox_ee_max_laser_temp_deg_c.setValue(40)

        self.formLayout_ee_page_3.setWidget(2, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_max_laser_temp_deg_c)

        self.label61 = QLabel(self.frame_eeprom_page_3)
        self.label61.setObjectName(u"label61")

        self.formLayout_ee_page_3.setWidget(2, QFormLayout.ItemRole.FieldRole, self.label61)

        self.lineEdit_ee_laser_power_coeff_0 = QLineEdit(self.frame_eeprom_page_3)
        self.lineEdit_ee_laser_power_coeff_0.setObjectName(u"lineEdit_ee_laser_power_coeff_0")

        self.formLayout_ee_page_3.setWidget(4, QFormLayout.ItemRole.LabelRole, self.lineEdit_ee_laser_power_coeff_0)

        self.label62 = QLabel(self.frame_eeprom_page_3)
        self.label62.setObjectName(u"label62")

        self.formLayout_ee_page_3.setWidget(4, QFormLayout.ItemRole.FieldRole, self.label62)

        self.lineEdit_ee_laser_power_coeff_1 = QLineEdit(self.frame_eeprom_page_3)
        self.lineEdit_ee_laser_power_coeff_1.setObjectName(u"lineEdit_ee_laser_power_coeff_1")

        self.formLayout_ee_page_3.setWidget(5, QFormLayout.ItemRole.LabelRole, self.lineEdit_ee_laser_power_coeff_1)

        self.label63 = QLabel(self.frame_eeprom_page_3)
        self.label63.setObjectName(u"label63")

        self.formLayout_ee_page_3.setWidget(5, QFormLayout.ItemRole.FieldRole, self.label63)

        self.lineEdit_ee_laser_power_coeff_2 = QLineEdit(self.frame_eeprom_page_3)
        self.lineEdit_ee_laser_power_coeff_2.setObjectName(u"lineEdit_ee_laser_power_coeff_2")

        self.formLayout_ee_page_3.setWidget(6, QFormLayout.ItemRole.LabelRole, self.lineEdit_ee_laser_power_coeff_2)

        self.label64 = QLabel(self.frame_eeprom_page_3)
        self.label64.setObjectName(u"label64")

        self.formLayout_ee_page_3.setWidget(6, QFormLayout.ItemRole.FieldRole, self.label64)

        self.lineEdit_ee_laser_power_coeff_3 = QLineEdit(self.frame_eeprom_page_3)
        self.lineEdit_ee_laser_power_coeff_3.setObjectName(u"lineEdit_ee_laser_power_coeff_3")

        self.formLayout_ee_page_3.setWidget(7, QFormLayout.ItemRole.LabelRole, self.lineEdit_ee_laser_power_coeff_3)

        self.label65 = QLabel(self.frame_eeprom_page_3)
        self.label65.setObjectName(u"label65")

        self.formLayout_ee_page_3.setWidget(7, QFormLayout.ItemRole.FieldRole, self.label65)

        self.doubleSpinBox_ee_max_laser_power_mW = QDoubleSpinBox(self.frame_eeprom_page_3)
        self.doubleSpinBox_ee_max_laser_power_mW.setObjectName(u"doubleSpinBox_ee_max_laser_power_mW")
        self.doubleSpinBox_ee_max_laser_power_mW.setMinimumSize(QSize(125, 0))
        self.doubleSpinBox_ee_max_laser_power_mW.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.doubleSpinBox_ee_max_laser_power_mW.setKeyboardTracking(False)
        self.doubleSpinBox_ee_max_laser_power_mW.setDecimals(1)
        self.doubleSpinBox_ee_max_laser_power_mW.setMaximum(30000.000000000000000)
        self.doubleSpinBox_ee_max_laser_power_mW.setValue(100.000000000000000)

        self.formLayout_ee_page_3.setWidget(8, QFormLayout.ItemRole.LabelRole, self.doubleSpinBox_ee_max_laser_power_mW)

        self.label66 = QLabel(self.frame_eeprom_page_3)
        self.label66.setObjectName(u"label66")

        self.formLayout_ee_page_3.setWidget(8, QFormLayout.ItemRole.FieldRole, self.label66)

        self.doubleSpinBox_ee_min_laser_power_mW = QDoubleSpinBox(self.frame_eeprom_page_3)
        self.doubleSpinBox_ee_min_laser_power_mW.setObjectName(u"doubleSpinBox_ee_min_laser_power_mW")
        self.doubleSpinBox_ee_min_laser_power_mW.setMinimumSize(QSize(125, 0))
        self.doubleSpinBox_ee_min_laser_power_mW.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.doubleSpinBox_ee_min_laser_power_mW.setKeyboardTracking(False)
        self.doubleSpinBox_ee_min_laser_power_mW.setDecimals(1)
        self.doubleSpinBox_ee_min_laser_power_mW.setMaximum(500.000000000000000)
        self.doubleSpinBox_ee_min_laser_power_mW.setValue(0.000000000000000)

        self.formLayout_ee_page_3.setWidget(9, QFormLayout.ItemRole.LabelRole, self.doubleSpinBox_ee_min_laser_power_mW)

        self.label67 = QLabel(self.frame_eeprom_page_3)
        self.label67.setObjectName(u"label67")

        self.formLayout_ee_page_3.setWidget(9, QFormLayout.ItemRole.FieldRole, self.label67)

        self.spinBox_ee_max_integration_time_ms = QSpinBox(self.frame_eeprom_page_3)
        self.spinBox_ee_max_integration_time_ms.setObjectName(u"spinBox_ee_max_integration_time_ms")
        self.spinBox_ee_max_integration_time_ms.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_max_integration_time_ms.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_max_integration_time_ms.setKeyboardTracking(False)
        self.spinBox_ee_max_integration_time_ms.setMinimum(-1)
        self.spinBox_ee_max_integration_time_ms.setMaximum(65535)
        self.spinBox_ee_max_integration_time_ms.setValue(0)

        self.formLayout_ee_page_3.setWidget(10, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_max_integration_time_ms)

        self.label68 = QLabel(self.frame_eeprom_page_3)
        self.label68.setObjectName(u"label68")

        self.formLayout_ee_page_3.setWidget(10, QFormLayout.ItemRole.FieldRole, self.label68)

        self.spinBox_ee_min_integration_time_ms = QSpinBox(self.frame_eeprom_page_3)
        self.spinBox_ee_min_integration_time_ms.setObjectName(u"spinBox_ee_min_integration_time_ms")
        self.spinBox_ee_min_integration_time_ms.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_min_integration_time_ms.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_min_integration_time_ms.setKeyboardTracking(False)
        self.spinBox_ee_min_integration_time_ms.setMinimum(-1)
        self.spinBox_ee_min_integration_time_ms.setMaximum(65535)
        self.spinBox_ee_min_integration_time_ms.setValue(0)

        self.formLayout_ee_page_3.setWidget(11, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_min_integration_time_ms)

        self.label69 = QLabel(self.frame_eeprom_page_3)
        self.label69.setObjectName(u"label69")

        self.formLayout_ee_page_3.setWidget(11, QFormLayout.ItemRole.FieldRole, self.label69)

        self.doubleSpinBox_ee_avg_resolution = QDoubleSpinBox(self.frame_eeprom_page_3)
        self.doubleSpinBox_ee_avg_resolution.setObjectName(u"doubleSpinBox_ee_avg_resolution")
        self.doubleSpinBox_ee_avg_resolution.setMinimumSize(QSize(125, 0))
        self.doubleSpinBox_ee_avg_resolution.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.formLayout_ee_page_3.setWidget(12, QFormLayout.ItemRole.LabelRole, self.doubleSpinBox_ee_avg_resolution)

        self.label70 = QLabel(self.frame_eeprom_page_3)
        self.label70.setObjectName(u"label70")

        self.formLayout_ee_page_3.setWidget(12, QFormLayout.ItemRole.FieldRole, self.label70)

        self.spinBox_ee_laser_watchdog_sec = QSpinBox(self.frame_eeprom_page_3)
        self.spinBox_ee_laser_watchdog_sec.setObjectName(u"spinBox_ee_laser_watchdog_sec")
        self.spinBox_ee_laser_watchdog_sec.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_laser_watchdog_sec.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_laser_watchdog_sec.setKeyboardTracking(False)
        self.spinBox_ee_laser_watchdog_sec.setMaximum(1200)
        self.spinBox_ee_laser_watchdog_sec.setValue(10)

        self.formLayout_ee_page_3.setWidget(13, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_laser_watchdog_sec)

        self.label71 = QLabel(self.frame_eeprom_page_3)
        self.label71.setObjectName(u"label71")

        self.formLayout_ee_page_3.setWidget(13, QFormLayout.ItemRole.FieldRole, self.label71)

        self.spinBox_ee_light_source_type = QSpinBox(self.frame_eeprom_page_3)
        self.spinBox_ee_light_source_type.setObjectName(u"spinBox_ee_light_source_type")
        self.spinBox_ee_light_source_type.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_light_source_type.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_light_source_type.setKeyboardTracking(False)
        self.spinBox_ee_light_source_type.setMaximum(255)

        self.formLayout_ee_page_3.setWidget(14, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_light_source_type)

        self.label72 = QLabel(self.frame_eeprom_page_3)
        self.label72.setObjectName(u"label72")

        self.formLayout_ee_page_3.setWidget(14, QFormLayout.ItemRole.FieldRole, self.label72)

        self.spinBox_ee_power_timeout_sec = QSpinBox(self.frame_eeprom_page_3)
        self.spinBox_ee_power_timeout_sec.setObjectName(u"spinBox_ee_power_timeout_sec")
        self.spinBox_ee_power_timeout_sec.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_power_timeout_sec.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_power_timeout_sec.setKeyboardTracking(False)
        self.spinBox_ee_power_timeout_sec.setMaximum(65535)

        self.formLayout_ee_page_3.setWidget(15, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_power_timeout_sec)

        self.label73 = QLabel(self.frame_eeprom_page_3)
        self.label73.setObjectName(u"label73")

        self.formLayout_ee_page_3.setWidget(15, QFormLayout.ItemRole.FieldRole, self.label73)

        self.spinBox_ee_detector_timeout_sec = QSpinBox(self.frame_eeprom_page_3)
        self.spinBox_ee_detector_timeout_sec.setObjectName(u"spinBox_ee_detector_timeout_sec")
        self.spinBox_ee_detector_timeout_sec.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_detector_timeout_sec.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_detector_timeout_sec.setKeyboardTracking(False)
        self.spinBox_ee_detector_timeout_sec.setMaximum(255)

        self.formLayout_ee_page_3.setWidget(16, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_detector_timeout_sec)

        self.label74 = QLabel(self.frame_eeprom_page_3)
        self.label74.setObjectName(u"label74")

        self.formLayout_ee_page_3.setWidget(16, QFormLayout.ItemRole.FieldRole, self.label74)

        self.spinBox_ee_horiz_binning_mode = QSpinBox(self.frame_eeprom_page_3)
        self.spinBox_ee_horiz_binning_mode.setObjectName(u"spinBox_ee_horiz_binning_mode")
        self.spinBox_ee_horiz_binning_mode.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_horiz_binning_mode.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_horiz_binning_mode.setKeyboardTracking(False)
        self.spinBox_ee_horiz_binning_mode.setMaximum(255)

        self.formLayout_ee_page_3.setWidget(17, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_horiz_binning_mode)

        self.label75 = QLabel(self.frame_eeprom_page_3)
        self.label75.setObjectName(u"label75")

        self.formLayout_ee_page_3.setWidget(17, QFormLayout.ItemRole.FieldRole, self.label75)

        self.spinBox_ee_startup_scans_to_average = QSpinBox(self.frame_eeprom_page_3)
        self.spinBox_ee_startup_scans_to_average.setObjectName(u"spinBox_ee_startup_scans_to_average")
        self.spinBox_ee_startup_scans_to_average.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_startup_scans_to_average.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_startup_scans_to_average.setKeyboardTracking(False)
        self.spinBox_ee_startup_scans_to_average.setMaximum(100)
        self.spinBox_ee_startup_scans_to_average.setMinimum(1)

        self.formLayout_ee_page_3.setWidget(18, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_startup_scans_to_average)

        self.label76 = QLabel(self.frame_eeprom_page_3)
        self.label76.setObjectName(u"label76")

        self.formLayout_ee_page_3.setWidget(18, QFormLayout.ItemRole.FieldRole, self.label76)

        self.spinBox_ee_laser_attenuator = QSpinBox(self.frame_eeprom_page_3)
        self.spinBox_ee_laser_attenuator.setObjectName(u"spinBox_ee_laser_attenuator")
        self.spinBox_ee_laser_attenuator.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_laser_attenuator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_laser_attenuator.setKeyboardTracking(False)
        self.spinBox_ee_laser_attenuator.setMaximum(255)
        self.spinBox_ee_laser_attenuator.setMinimum(0)

        self.formLayout_ee_page_3.setWidget(19, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_laser_attenuator)

        self.label77 = QLabel(self.frame_eeprom_page_3)
        self.label77.setObjectName(u"label77")

        self.formLayout_ee_page_3.setWidget(19, QFormLayout.ItemRole.FieldRole, self.label77)


        self.formLayout.setLayout(1, QFormLayout.ItemRole.LabelRole, self.formLayout_ee_page_3)


        self.vboxLayout8.addWidget(self.frame_eeprom_page_3)


        self.vboxLayout1.addWidget(self.frame_eeprom_page_3_white)

        self.frame_eeprom_page_4_white = QFrame(self.frame_eeprom_editor)
        self.frame_eeprom_page_4_white.setObjectName(u"frame_eeprom_page_4_white")
        self.frame_eeprom_page_4_white.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_eeprom_page_4_white.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_eeprom_page_4_white.setProperty(u"wpBox", False)
        self.vboxLayout9 = QVBoxLayout(self.frame_eeprom_page_4_white)
        self.vboxLayout9.setSpacing(0)
        self.vboxLayout9.setObjectName(u"vboxLayout9")
        self.vboxLayout9.setContentsMargins(0, 0, 0, 0)
        self.frame_eeprom_page_4 = QFrame(self.frame_eeprom_page_4_white)
        self.frame_eeprom_page_4.setObjectName(u"frame_eeprom_page_4")
        self.frame_eeprom_page_4.setMinimumSize(QSize(0, 0))
        self.frame_eeprom_page_4.setProperty(u"wpPanel", False)
        self.vboxLayout10 = QVBoxLayout(self.frame_eeprom_page_4)
        self.vboxLayout10.setObjectName(u"vboxLayout10")
        self.label78 = QLabel(self.frame_eeprom_page_4)
        self.label78.setObjectName(u"label78")
        self.label78.setFont(font)

        self.vboxLayout10.addWidget(self.label78)

        self.formLayout_ee_page_4 = QFormLayout()
        self.formLayout_ee_page_4.setObjectName(u"formLayout_ee_page_4")
        self.formLayout_ee_page_4.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.label79 = QLabel(self.frame_eeprom_page_4)
        self.label79.setObjectName(u"label79")

        self.formLayout_ee_page_4.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label79)

        self.lineEdit_ee_user_text = QLineEdit(self.frame_eeprom_page_4)
        self.lineEdit_ee_user_text.setObjectName(u"lineEdit_ee_user_text")

        self.formLayout_ee_page_4.setWidget(0, QFormLayout.ItemRole.FieldRole, self.lineEdit_ee_user_text)


        self.vboxLayout10.addLayout(self.formLayout_ee_page_4)


        self.vboxLayout9.addWidget(self.frame_eeprom_page_4)


        self.vboxLayout1.addWidget(self.frame_eeprom_page_4_white)

        self.frame_eeprom_page_5_white = QFrame(self.frame_eeprom_editor)
        self.frame_eeprom_page_5_white.setObjectName(u"frame_eeprom_page_5_white")
        self.frame_eeprom_page_5_white.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_eeprom_page_5_white.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_eeprom_page_5_white.setProperty(u"wpBox", False)
        self.vboxLayout11 = QVBoxLayout(self.frame_eeprom_page_5_white)
        self.vboxLayout11.setSpacing(0)
        self.vboxLayout11.setObjectName(u"vboxLayout11")
        self.vboxLayout11.setContentsMargins(0, 0, 0, 0)
        self.frame_eeprom_page_5 = QFrame(self.frame_eeprom_page_5_white)
        self.frame_eeprom_page_5.setObjectName(u"frame_eeprom_page_5")
        self.frame_eeprom_page_5.setMinimumSize(QSize(0, 0))
        self.frame_eeprom_page_5.setProperty(u"wpPanel", False)
        self.vboxLayout12 = QVBoxLayout(self.frame_eeprom_page_5)
        self.vboxLayout12.setObjectName(u"vboxLayout12")
        self.label80 = QLabel(self.frame_eeprom_page_5)
        self.label80.setObjectName(u"label80")
        self.label80.setFont(font)

        self.vboxLayout12.addWidget(self.label80)

        self.formLayout_ee_page_5 = QFormLayout()
        self.formLayout_ee_page_5.setObjectName(u"formLayout_ee_page_5")
        self.formLayout_ee_page_5.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.formLayout_ee_page_5.setVerticalSpacing(4)
        self.spinBox_ee_bad_pixel_0 = QSpinBox(self.frame_eeprom_page_5)
        self.spinBox_ee_bad_pixel_0.setObjectName(u"spinBox_ee_bad_pixel_0")
        self.spinBox_ee_bad_pixel_0.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_bad_pixel_0.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_bad_pixel_0.setKeyboardTracking(False)
        self.spinBox_ee_bad_pixel_0.setMinimum(-1)
        self.spinBox_ee_bad_pixel_0.setMaximum(9999)
        self.spinBox_ee_bad_pixel_0.setValue(-1)

        self.formLayout_ee_page_5.setWidget(0, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_bad_pixel_0)

        self.label81 = QLabel(self.frame_eeprom_page_5)
        self.label81.setObjectName(u"label81")

        self.formLayout_ee_page_5.setWidget(0, QFormLayout.ItemRole.FieldRole, self.label81)

        self.spinBox_ee_bad_pixel_1 = QSpinBox(self.frame_eeprom_page_5)
        self.spinBox_ee_bad_pixel_1.setObjectName(u"spinBox_ee_bad_pixel_1")
        self.spinBox_ee_bad_pixel_1.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_bad_pixel_1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_bad_pixel_1.setKeyboardTracking(False)
        self.spinBox_ee_bad_pixel_1.setMinimum(-1)
        self.spinBox_ee_bad_pixel_1.setMaximum(9999)
        self.spinBox_ee_bad_pixel_1.setValue(-1)

        self.formLayout_ee_page_5.setWidget(1, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_bad_pixel_1)

        self.label82 = QLabel(self.frame_eeprom_page_5)
        self.label82.setObjectName(u"label82")

        self.formLayout_ee_page_5.setWidget(1, QFormLayout.ItemRole.FieldRole, self.label82)

        self.spinBox_ee_bad_pixel_2 = QSpinBox(self.frame_eeprom_page_5)
        self.spinBox_ee_bad_pixel_2.setObjectName(u"spinBox_ee_bad_pixel_2")
        self.spinBox_ee_bad_pixel_2.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_bad_pixel_2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_bad_pixel_2.setKeyboardTracking(False)
        self.spinBox_ee_bad_pixel_2.setMinimum(-1)
        self.spinBox_ee_bad_pixel_2.setMaximum(9999)
        self.spinBox_ee_bad_pixel_2.setValue(-1)

        self.formLayout_ee_page_5.setWidget(2, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_bad_pixel_2)

        self.label83 = QLabel(self.frame_eeprom_page_5)
        self.label83.setObjectName(u"label83")

        self.formLayout_ee_page_5.setWidget(2, QFormLayout.ItemRole.FieldRole, self.label83)

        self.spinBox_ee_bad_pixel_3 = QSpinBox(self.frame_eeprom_page_5)
        self.spinBox_ee_bad_pixel_3.setObjectName(u"spinBox_ee_bad_pixel_3")
        self.spinBox_ee_bad_pixel_3.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_bad_pixel_3.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_bad_pixel_3.setKeyboardTracking(False)
        self.spinBox_ee_bad_pixel_3.setMinimum(-1)
        self.spinBox_ee_bad_pixel_3.setMaximum(9999)
        self.spinBox_ee_bad_pixel_3.setValue(-1)

        self.formLayout_ee_page_5.setWidget(3, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_bad_pixel_3)

        self.label84 = QLabel(self.frame_eeprom_page_5)
        self.label84.setObjectName(u"label84")

        self.formLayout_ee_page_5.setWidget(3, QFormLayout.ItemRole.FieldRole, self.label84)

        self.spinBox_ee_bad_pixel_4 = QSpinBox(self.frame_eeprom_page_5)
        self.spinBox_ee_bad_pixel_4.setObjectName(u"spinBox_ee_bad_pixel_4")
        self.spinBox_ee_bad_pixel_4.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_bad_pixel_4.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_bad_pixel_4.setKeyboardTracking(False)
        self.spinBox_ee_bad_pixel_4.setMinimum(-1)
        self.spinBox_ee_bad_pixel_4.setMaximum(9999)
        self.spinBox_ee_bad_pixel_4.setValue(-1)

        self.formLayout_ee_page_5.setWidget(4, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_bad_pixel_4)

        self.label85 = QLabel(self.frame_eeprom_page_5)
        self.label85.setObjectName(u"label85")

        self.formLayout_ee_page_5.setWidget(4, QFormLayout.ItemRole.FieldRole, self.label85)

        self.spinBox_ee_bad_pixel_5 = QSpinBox(self.frame_eeprom_page_5)
        self.spinBox_ee_bad_pixel_5.setObjectName(u"spinBox_ee_bad_pixel_5")
        self.spinBox_ee_bad_pixel_5.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_bad_pixel_5.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_bad_pixel_5.setKeyboardTracking(False)
        self.spinBox_ee_bad_pixel_5.setMinimum(-1)
        self.spinBox_ee_bad_pixel_5.setMaximum(9999)
        self.spinBox_ee_bad_pixel_5.setValue(-1)

        self.formLayout_ee_page_5.setWidget(5, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_bad_pixel_5)

        self.label86 = QLabel(self.frame_eeprom_page_5)
        self.label86.setObjectName(u"label86")

        self.formLayout_ee_page_5.setWidget(5, QFormLayout.ItemRole.FieldRole, self.label86)

        self.spinBox_ee_bad_pixel_6 = QSpinBox(self.frame_eeprom_page_5)
        self.spinBox_ee_bad_pixel_6.setObjectName(u"spinBox_ee_bad_pixel_6")
        self.spinBox_ee_bad_pixel_6.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_bad_pixel_6.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_bad_pixel_6.setKeyboardTracking(False)
        self.spinBox_ee_bad_pixel_6.setMinimum(-1)
        self.spinBox_ee_bad_pixel_6.setMaximum(9999)
        self.spinBox_ee_bad_pixel_6.setValue(-1)

        self.formLayout_ee_page_5.setWidget(6, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_bad_pixel_6)

        self.label87 = QLabel(self.frame_eeprom_page_5)
        self.label87.setObjectName(u"label87")

        self.formLayout_ee_page_5.setWidget(6, QFormLayout.ItemRole.FieldRole, self.label87)

        self.spinBox_ee_bad_pixel_7 = QSpinBox(self.frame_eeprom_page_5)
        self.spinBox_ee_bad_pixel_7.setObjectName(u"spinBox_ee_bad_pixel_7")
        self.spinBox_ee_bad_pixel_7.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_bad_pixel_7.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_bad_pixel_7.setKeyboardTracking(False)
        self.spinBox_ee_bad_pixel_7.setMinimum(-1)
        self.spinBox_ee_bad_pixel_7.setMaximum(9999)
        self.spinBox_ee_bad_pixel_7.setValue(-1)

        self.formLayout_ee_page_5.setWidget(7, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_bad_pixel_7)

        self.label88 = QLabel(self.frame_eeprom_page_5)
        self.label88.setObjectName(u"label88")

        self.formLayout_ee_page_5.setWidget(7, QFormLayout.ItemRole.FieldRole, self.label88)

        self.spinBox_ee_bad_pixel_8 = QSpinBox(self.frame_eeprom_page_5)
        self.spinBox_ee_bad_pixel_8.setObjectName(u"spinBox_ee_bad_pixel_8")
        self.spinBox_ee_bad_pixel_8.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_bad_pixel_8.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_bad_pixel_8.setKeyboardTracking(False)
        self.spinBox_ee_bad_pixel_8.setMinimum(-1)
        self.spinBox_ee_bad_pixel_8.setMaximum(9999)
        self.spinBox_ee_bad_pixel_8.setValue(-1)

        self.formLayout_ee_page_5.setWidget(8, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_bad_pixel_8)

        self.label89 = QLabel(self.frame_eeprom_page_5)
        self.label89.setObjectName(u"label89")

        self.formLayout_ee_page_5.setWidget(8, QFormLayout.ItemRole.FieldRole, self.label89)

        self.spinBox_ee_bad_pixel_9 = QSpinBox(self.frame_eeprom_page_5)
        self.spinBox_ee_bad_pixel_9.setObjectName(u"spinBox_ee_bad_pixel_9")
        self.spinBox_ee_bad_pixel_9.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_bad_pixel_9.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_bad_pixel_9.setKeyboardTracking(False)
        self.spinBox_ee_bad_pixel_9.setMinimum(-1)
        self.spinBox_ee_bad_pixel_9.setMaximum(9999)
        self.spinBox_ee_bad_pixel_9.setValue(-1)

        self.formLayout_ee_page_5.setWidget(9, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_bad_pixel_9)

        self.label90 = QLabel(self.frame_eeprom_page_5)
        self.label90.setObjectName(u"label90")

        self.formLayout_ee_page_5.setWidget(9, QFormLayout.ItemRole.FieldRole, self.label90)

        self.spinBox_ee_bad_pixel_10 = QSpinBox(self.frame_eeprom_page_5)
        self.spinBox_ee_bad_pixel_10.setObjectName(u"spinBox_ee_bad_pixel_10")
        self.spinBox_ee_bad_pixel_10.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_bad_pixel_10.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_bad_pixel_10.setKeyboardTracking(False)
        self.spinBox_ee_bad_pixel_10.setMinimum(-1)
        self.spinBox_ee_bad_pixel_10.setMaximum(9999)
        self.spinBox_ee_bad_pixel_10.setValue(-1)

        self.formLayout_ee_page_5.setWidget(10, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_bad_pixel_10)

        self.label91 = QLabel(self.frame_eeprom_page_5)
        self.label91.setObjectName(u"label91")

        self.formLayout_ee_page_5.setWidget(10, QFormLayout.ItemRole.FieldRole, self.label91)

        self.spinBox_ee_bad_pixel_11 = QSpinBox(self.frame_eeprom_page_5)
        self.spinBox_ee_bad_pixel_11.setObjectName(u"spinBox_ee_bad_pixel_11")
        self.spinBox_ee_bad_pixel_11.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_bad_pixel_11.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_bad_pixel_11.setKeyboardTracking(False)
        self.spinBox_ee_bad_pixel_11.setMinimum(-1)
        self.spinBox_ee_bad_pixel_11.setMaximum(9999)
        self.spinBox_ee_bad_pixel_11.setValue(-1)

        self.formLayout_ee_page_5.setWidget(11, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_bad_pixel_11)

        self.label92 = QLabel(self.frame_eeprom_page_5)
        self.label92.setObjectName(u"label92")

        self.formLayout_ee_page_5.setWidget(11, QFormLayout.ItemRole.FieldRole, self.label92)

        self.spinBox_ee_bad_pixel_12 = QSpinBox(self.frame_eeprom_page_5)
        self.spinBox_ee_bad_pixel_12.setObjectName(u"spinBox_ee_bad_pixel_12")
        self.spinBox_ee_bad_pixel_12.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_bad_pixel_12.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_bad_pixel_12.setKeyboardTracking(False)
        self.spinBox_ee_bad_pixel_12.setMinimum(-1)
        self.spinBox_ee_bad_pixel_12.setMaximum(9999)
        self.spinBox_ee_bad_pixel_12.setValue(-1)

        self.formLayout_ee_page_5.setWidget(12, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_bad_pixel_12)

        self.label93 = QLabel(self.frame_eeprom_page_5)
        self.label93.setObjectName(u"label93")

        self.formLayout_ee_page_5.setWidget(12, QFormLayout.ItemRole.FieldRole, self.label93)

        self.spinBox_ee_bad_pixel_13 = QSpinBox(self.frame_eeprom_page_5)
        self.spinBox_ee_bad_pixel_13.setObjectName(u"spinBox_ee_bad_pixel_13")
        self.spinBox_ee_bad_pixel_13.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_bad_pixel_13.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_bad_pixel_13.setKeyboardTracking(False)
        self.spinBox_ee_bad_pixel_13.setMinimum(-1)
        self.spinBox_ee_bad_pixel_13.setMaximum(9999)
        self.spinBox_ee_bad_pixel_13.setValue(-1)

        self.formLayout_ee_page_5.setWidget(13, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_bad_pixel_13)

        self.label94 = QLabel(self.frame_eeprom_page_5)
        self.label94.setObjectName(u"label94")

        self.formLayout_ee_page_5.setWidget(13, QFormLayout.ItemRole.FieldRole, self.label94)

        self.spinBox_ee_bad_pixel_14 = QSpinBox(self.frame_eeprom_page_5)
        self.spinBox_ee_bad_pixel_14.setObjectName(u"spinBox_ee_bad_pixel_14")
        self.spinBox_ee_bad_pixel_14.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_bad_pixel_14.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_bad_pixel_14.setKeyboardTracking(False)
        self.spinBox_ee_bad_pixel_14.setMinimum(-1)
        self.spinBox_ee_bad_pixel_14.setMaximum(9999)
        self.spinBox_ee_bad_pixel_14.setValue(-1)

        self.formLayout_ee_page_5.setWidget(14, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_bad_pixel_14)

        self.label95 = QLabel(self.frame_eeprom_page_5)
        self.label95.setObjectName(u"label95")

        self.formLayout_ee_page_5.setWidget(14, QFormLayout.ItemRole.FieldRole, self.label95)

        self.lineEdit_ee_assembly_revision_packed = QLineEdit(self.frame_eeprom_page_5)
        self.lineEdit_ee_assembly_revision_packed.setObjectName(u"lineEdit_ee_assembly_revision_packed")
        self.lineEdit_ee_assembly_revision_packed.setMinimumSize(QSize(125, 0))

        self.formLayout_ee_page_5.setWidget(16, QFormLayout.ItemRole.LabelRole, self.lineEdit_ee_assembly_revision_packed)

        self.label96 = QLabel(self.frame_eeprom_page_5)
        self.label96.setObjectName(u"label96")

        self.formLayout_ee_page_5.setWidget(16, QFormLayout.ItemRole.FieldRole, self.label96)

        self.spinBox_ee_subformat = QSpinBox(self.frame_eeprom_page_5)
        self.spinBox_ee_subformat.setObjectName(u"spinBox_ee_subformat")
        self.spinBox_ee_subformat.setMinimumSize(QSize(125, 0))

        self.formLayout_ee_page_5.setWidget(17, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_subformat)

        self.label97 = QLabel(self.frame_eeprom_page_5)
        self.label97.setObjectName(u"label97")

        self.formLayout_ee_page_5.setWidget(17, QFormLayout.ItemRole.FieldRole, self.label97)


        self.vboxLayout12.addLayout(self.formLayout_ee_page_5)


        self.vboxLayout11.addWidget(self.frame_eeprom_page_5)


        self.vboxLayout1.addWidget(self.frame_eeprom_page_5_white)

        self.frame_eeprom_sub_1 = QFrame(self.frame_eeprom_editor)
        self.frame_eeprom_sub_1.setObjectName(u"frame_eeprom_sub_1")
        self.frame_eeprom_sub_1.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_eeprom_sub_1.setFrameShadow(QFrame.Shadow.Raised)
        self.vboxLayout13 = QVBoxLayout(self.frame_eeprom_sub_1)
        self.vboxLayout13.setSpacing(0)
        self.vboxLayout13.setObjectName(u"vboxLayout13")
        self.vboxLayout13.setContentsMargins(0, 0, 0, 0)
        self.frame_eeprom_sub_1_page_6_white = QFrame(self.frame_eeprom_sub_1)
        self.frame_eeprom_sub_1_page_6_white.setObjectName(u"frame_eeprom_sub_1_page_6_white")
        self.frame_eeprom_sub_1_page_6_white.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_eeprom_sub_1_page_6_white.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_eeprom_sub_1_page_6_white.setProperty(u"wpBox", False)
        self.vboxLayout14 = QVBoxLayout(self.frame_eeprom_sub_1_page_6_white)
        self.vboxLayout14.setSpacing(0)
        self.vboxLayout14.setObjectName(u"vboxLayout14")
        self.vboxLayout14.setContentsMargins(0, 0, 0, 0)
        self.frame_eeprom_sub_1_page_6_black = QFrame(self.frame_eeprom_sub_1_page_6_white)
        self.frame_eeprom_sub_1_page_6_black.setObjectName(u"frame_eeprom_sub_1_page_6_black")
        self.frame_eeprom_sub_1_page_6_black.setProperty(u"wpPanel", False)
        self.vboxLayout15 = QVBoxLayout(self.frame_eeprom_sub_1_page_6_black)
        self.vboxLayout15.setObjectName(u"vboxLayout15")
        self.label98 = QLabel(self.frame_eeprom_sub_1_page_6_black)
        self.label98.setObjectName(u"label98")
        self.label98.setFont(font)

        self.vboxLayout15.addWidget(self.label98)

        self.formLayout_ee_sub1_page_6 = QFormLayout()
        self.formLayout_ee_sub1_page_6.setObjectName(u"formLayout_ee_sub1_page_6")
        self.formLayout_ee_sub1_page_6.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.lineEdit_ee_raman_intensity_coeff_0 = QLineEdit(self.frame_eeprom_sub_1_page_6_black)
        self.lineEdit_ee_raman_intensity_coeff_0.setObjectName(u"lineEdit_ee_raman_intensity_coeff_0")
        self.lineEdit_ee_raman_intensity_coeff_0.setMaxLength(30)

        self.formLayout_ee_sub1_page_6.setWidget(1, QFormLayout.ItemRole.LabelRole, self.lineEdit_ee_raman_intensity_coeff_0)

        self.lineEdit_ee_raman_intensity_coeff_1 = QLineEdit(self.frame_eeprom_sub_1_page_6_black)
        self.lineEdit_ee_raman_intensity_coeff_1.setObjectName(u"lineEdit_ee_raman_intensity_coeff_1")
        self.lineEdit_ee_raman_intensity_coeff_1.setMaxLength(30)

        self.formLayout_ee_sub1_page_6.setWidget(2, QFormLayout.ItemRole.LabelRole, self.lineEdit_ee_raman_intensity_coeff_1)

        self.lineEdit_ee_raman_intensity_coeff_2 = QLineEdit(self.frame_eeprom_sub_1_page_6_black)
        self.lineEdit_ee_raman_intensity_coeff_2.setObjectName(u"lineEdit_ee_raman_intensity_coeff_2")
        self.lineEdit_ee_raman_intensity_coeff_2.setMaxLength(30)

        self.formLayout_ee_sub1_page_6.setWidget(3, QFormLayout.ItemRole.LabelRole, self.lineEdit_ee_raman_intensity_coeff_2)

        self.lineEdit_ee_raman_intensity_coeff_3 = QLineEdit(self.frame_eeprom_sub_1_page_6_black)
        self.lineEdit_ee_raman_intensity_coeff_3.setObjectName(u"lineEdit_ee_raman_intensity_coeff_3")
        self.lineEdit_ee_raman_intensity_coeff_3.setMaxLength(30)

        self.formLayout_ee_sub1_page_6.setWidget(4, QFormLayout.ItemRole.LabelRole, self.lineEdit_ee_raman_intensity_coeff_3)

        self.lineEdit_ee_raman_intensity_coeff_4 = QLineEdit(self.frame_eeprom_sub_1_page_6_black)
        self.lineEdit_ee_raman_intensity_coeff_4.setObjectName(u"lineEdit_ee_raman_intensity_coeff_4")
        self.lineEdit_ee_raman_intensity_coeff_4.setMaxLength(30)

        self.formLayout_ee_sub1_page_6.setWidget(5, QFormLayout.ItemRole.LabelRole, self.lineEdit_ee_raman_intensity_coeff_4)

        self.lineEdit_ee_raman_intensity_coeff_5 = QLineEdit(self.frame_eeprom_sub_1_page_6_black)
        self.lineEdit_ee_raman_intensity_coeff_5.setObjectName(u"lineEdit_ee_raman_intensity_coeff_5")
        self.lineEdit_ee_raman_intensity_coeff_5.setMaxLength(30)

        self.formLayout_ee_sub1_page_6.setWidget(6, QFormLayout.ItemRole.LabelRole, self.lineEdit_ee_raman_intensity_coeff_5)

        self.lineEdit_ee_raman_intensity_coeff_6 = QLineEdit(self.frame_eeprom_sub_1_page_6_black)
        self.lineEdit_ee_raman_intensity_coeff_6.setObjectName(u"lineEdit_ee_raman_intensity_coeff_6")
        self.lineEdit_ee_raman_intensity_coeff_6.setMaxLength(30)

        self.formLayout_ee_sub1_page_6.setWidget(7, QFormLayout.ItemRole.LabelRole, self.lineEdit_ee_raman_intensity_coeff_6)

        self.label99 = QLabel(self.frame_eeprom_sub_1_page_6_black)
        self.label99.setObjectName(u"label99")

        self.formLayout_ee_sub1_page_6.setWidget(1, QFormLayout.ItemRole.FieldRole, self.label99)

        self.label100 = QLabel(self.frame_eeprom_sub_1_page_6_black)
        self.label100.setObjectName(u"label100")

        self.formLayout_ee_sub1_page_6.setWidget(2, QFormLayout.ItemRole.FieldRole, self.label100)

        self.label101 = QLabel(self.frame_eeprom_sub_1_page_6_black)
        self.label101.setObjectName(u"label101")

        self.formLayout_ee_sub1_page_6.setWidget(3, QFormLayout.ItemRole.FieldRole, self.label101)

        self.label102 = QLabel(self.frame_eeprom_sub_1_page_6_black)
        self.label102.setObjectName(u"label102")

        self.formLayout_ee_sub1_page_6.setWidget(4, QFormLayout.ItemRole.FieldRole, self.label102)

        self.label103 = QLabel(self.frame_eeprom_sub_1_page_6_black)
        self.label103.setObjectName(u"label103")

        self.formLayout_ee_sub1_page_6.setWidget(5, QFormLayout.ItemRole.FieldRole, self.label103)

        self.label104 = QLabel(self.frame_eeprom_sub_1_page_6_black)
        self.label104.setObjectName(u"label104")

        self.formLayout_ee_sub1_page_6.setWidget(6, QFormLayout.ItemRole.FieldRole, self.label104)

        self.label105 = QLabel(self.frame_eeprom_sub_1_page_6_black)
        self.label105.setObjectName(u"label105")

        self.formLayout_ee_sub1_page_6.setWidget(7, QFormLayout.ItemRole.FieldRole, self.label105)


        self.vboxLayout15.addLayout(self.formLayout_ee_sub1_page_6)


        self.vboxLayout14.addWidget(self.frame_eeprom_sub_1_page_6_black)


        self.vboxLayout13.addWidget(self.frame_eeprom_sub_1_page_6_white)


        self.vboxLayout1.addWidget(self.frame_eeprom_sub_1)

        self.frame_eeprom_sub_3 = QFrame(self.frame_eeprom_editor)
        self.frame_eeprom_sub_3.setObjectName(u"frame_eeprom_sub_3")
        self.frame_eeprom_sub_3.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_eeprom_sub_3.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_eeprom_sub_3.setProperty(u"wpBox", False)
        self.vboxLayout16 = QVBoxLayout(self.frame_eeprom_sub_3)
        self.vboxLayout16.setObjectName(u"vboxLayout16")
        self.vboxLayout16.setContentsMargins(1, 1, 1, 1)
        self.frame_eeprom_sub_3_black = QFrame(self.frame_eeprom_sub_3)
        self.frame_eeprom_sub_3_black.setObjectName(u"frame_eeprom_sub_3_black")
        self.frame_eeprom_sub_3_black.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_eeprom_sub_3_black.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_eeprom_sub_3_black.setProperty(u"wpPanel", False)
        self.vboxLayout17 = QVBoxLayout(self.frame_eeprom_sub_3_black)
        self.vboxLayout17.setObjectName(u"vboxLayout17")
        self.vboxLayout17.setContentsMargins(1, 1, 1, 1)
        self.label106 = QLabel(self.frame_eeprom_sub_3_black)
        self.label106.setObjectName(u"label106")
        self.label106.setFont(font)

        self.vboxLayout17.addWidget(self.label106)

        self.formLayout_ee_sub3_page_7 = QFormLayout()
        self.formLayout_ee_sub3_page_7.setObjectName(u"formLayout_ee_sub3_page_7")
        self.label107 = QLabel(self.frame_eeprom_sub_3_black)
        self.label107.setObjectName(u"label107")

        self.formLayout_ee_sub3_page_7.setWidget(1, QFormLayout.ItemRole.FieldRole, self.label107)

        self.spinBox_ee_untethered_library_type = QSpinBox(self.frame_eeprom_sub_3_black)
        self.spinBox_ee_untethered_library_type.setObjectName(u"spinBox_ee_untethered_library_type")
        self.spinBox_ee_untethered_library_type.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_untethered_library_type.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.formLayout_ee_sub3_page_7.setWidget(1, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_untethered_library_type)

        self.spinBox_ee_untethered_library_id = QSpinBox(self.frame_eeprom_sub_3_black)
        self.spinBox_ee_untethered_library_id.setObjectName(u"spinBox_ee_untethered_library_id")
        self.spinBox_ee_untethered_library_id.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_untethered_library_id.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.formLayout_ee_sub3_page_7.setWidget(2, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_untethered_library_id)

        self.spinBox_ee_untethered_scans_to_average = QSpinBox(self.frame_eeprom_sub_3_black)
        self.spinBox_ee_untethered_scans_to_average.setObjectName(u"spinBox_ee_untethered_scans_to_average")
        self.spinBox_ee_untethered_scans_to_average.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_untethered_scans_to_average.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_untethered_scans_to_average.setMinimum(1)
        self.spinBox_ee_untethered_scans_to_average.setValue(5)

        self.formLayout_ee_sub3_page_7.setWidget(3, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_untethered_scans_to_average)

        self.spinBox_ee_untethered_min_ramp_pixels = QSpinBox(self.frame_eeprom_sub_3_black)
        self.spinBox_ee_untethered_min_ramp_pixels.setObjectName(u"spinBox_ee_untethered_min_ramp_pixels")
        self.spinBox_ee_untethered_min_ramp_pixels.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_untethered_min_ramp_pixels.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_untethered_min_ramp_pixels.setValue(4)

        self.formLayout_ee_sub3_page_7.setWidget(4, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_untethered_min_ramp_pixels)

        self.spinBox_ee_untethered_min_peak_height = QSpinBox(self.frame_eeprom_sub_3_black)
        self.spinBox_ee_untethered_min_peak_height.setObjectName(u"spinBox_ee_untethered_min_peak_height")
        self.spinBox_ee_untethered_min_peak_height.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_untethered_min_peak_height.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_untethered_min_peak_height.setMaximum(30000)
        self.spinBox_ee_untethered_min_peak_height.setValue(200)

        self.formLayout_ee_sub3_page_7.setWidget(5, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_untethered_min_peak_height)

        self.spinBox_ee_untethered_match_threshold = QSpinBox(self.frame_eeprom_sub_3_black)
        self.spinBox_ee_untethered_match_threshold.setObjectName(u"spinBox_ee_untethered_match_threshold")
        self.spinBox_ee_untethered_match_threshold.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_untethered_match_threshold.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_untethered_match_threshold.setMaximum(100)

        self.formLayout_ee_sub3_page_7.setWidget(6, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_untethered_match_threshold)

        self.label108 = QLabel(self.frame_eeprom_sub_3_black)
        self.label108.setObjectName(u"label108")

        self.formLayout_ee_sub3_page_7.setWidget(2, QFormLayout.ItemRole.FieldRole, self.label108)

        self.label109 = QLabel(self.frame_eeprom_sub_3_black)
        self.label109.setObjectName(u"label109")

        self.formLayout_ee_sub3_page_7.setWidget(3, QFormLayout.ItemRole.FieldRole, self.label109)

        self.label110 = QLabel(self.frame_eeprom_sub_3_black)
        self.label110.setObjectName(u"label110")

        self.formLayout_ee_sub3_page_7.setWidget(4, QFormLayout.ItemRole.FieldRole, self.label110)

        self.label111 = QLabel(self.frame_eeprom_sub_3_black)
        self.label111.setObjectName(u"label111")

        self.formLayout_ee_sub3_page_7.setWidget(5, QFormLayout.ItemRole.FieldRole, self.label111)

        self.label112 = QLabel(self.frame_eeprom_sub_3_black)
        self.label112.setObjectName(u"label112")

        self.formLayout_ee_sub3_page_7.setWidget(6, QFormLayout.ItemRole.FieldRole, self.label112)

        self.spinBox_ee_untethered_library_count = QSpinBox(self.frame_eeprom_sub_3_black)
        self.spinBox_ee_untethered_library_count.setObjectName(u"spinBox_ee_untethered_library_count")
        self.spinBox_ee_untethered_library_count.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_untethered_library_count.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_untethered_library_count.setMaximum(8)

        self.formLayout_ee_sub3_page_7.setWidget(7, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_untethered_library_count)

        self.label113 = QLabel(self.frame_eeprom_sub_3_black)
        self.label113.setObjectName(u"label113")

        self.formLayout_ee_sub3_page_7.setWidget(7, QFormLayout.ItemRole.FieldRole, self.label113)


        self.vboxLayout17.addLayout(self.formLayout_ee_sub3_page_7)


        self.vboxLayout16.addWidget(self.frame_eeprom_sub_3_black)


        self.vboxLayout1.addWidget(self.frame_eeprom_sub_3)

        self.frame_eeprom_sub_2 = QFrame(self.frame_eeprom_editor)
        self.frame_eeprom_sub_2.setObjectName(u"frame_eeprom_sub_2")
        self.frame_eeprom_sub_2.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_eeprom_sub_2.setFrameShadow(QFrame.Shadow.Raised)
        self.vboxLayout18 = QVBoxLayout(self.frame_eeprom_sub_2)
        self.vboxLayout18.setSpacing(0)
        self.vboxLayout18.setObjectName(u"vboxLayout18")
        self.vboxLayout18.setContentsMargins(0, 0, 0, 0)
        self.frame_eeprom_sub_2_page_6_white = QFrame(self.frame_eeprom_sub_2)
        self.frame_eeprom_sub_2_page_6_white.setObjectName(u"frame_eeprom_sub_2_page_6_white")
        self.frame_eeprom_sub_2_page_6_white.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_eeprom_sub_2_page_6_white.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_eeprom_sub_2_page_6_white.setProperty(u"wpBox", False)
        self.vboxLayout19 = QVBoxLayout(self.frame_eeprom_sub_2_page_6_white)
        self.vboxLayout19.setSpacing(0)
        self.vboxLayout19.setObjectName(u"vboxLayout19")
        self.vboxLayout19.setContentsMargins(0, 0, 0, 0)
        self.frame_eeprom_sub_2_page_6_black = QFrame(self.frame_eeprom_sub_2_page_6_white)
        self.frame_eeprom_sub_2_page_6_black.setObjectName(u"frame_eeprom_sub_2_page_6_black")
        self.frame_eeprom_sub_2_page_6_black.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_eeprom_sub_2_page_6_black.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_eeprom_sub_2_page_6_black.setProperty(u"wpPanel", False)
        self.vboxLayout20 = QVBoxLayout(self.frame_eeprom_sub_2_page_6_black)
        self.vboxLayout20.setObjectName(u"vboxLayout20")
        self.label114 = QLabel(self.frame_eeprom_sub_2_page_6_black)
        self.label114.setObjectName(u"label114")
        self.label114.setFont(font)

        self.vboxLayout20.addWidget(self.label114)

        self.formLayout_ee_sub2_page_6 = QFormLayout()
        self.formLayout_ee_sub2_page_6.setObjectName(u"formLayout_ee_sub2_page_6")
        self.spinBox_ee_spline_points = QSpinBox(self.frame_eeprom_sub_2_page_6_black)
        self.spinBox_ee_spline_points.setObjectName(u"spinBox_ee_spline_points")
        self.spinBox_ee_spline_points.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_spline_points.setMaximum(14)

        self.formLayout_ee_sub2_page_6.setWidget(0, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_spline_points)

        self.label115 = QLabel(self.frame_eeprom_sub_2_page_6_black)
        self.label115.setObjectName(u"label115")

        self.formLayout_ee_sub2_page_6.setWidget(0, QFormLayout.ItemRole.FieldRole, self.label115)

        self.doubleSpinBox_ee_spline_min = QDoubleSpinBox(self.frame_eeprom_sub_2_page_6_black)
        self.doubleSpinBox_ee_spline_min.setObjectName(u"doubleSpinBox_ee_spline_min")
        self.doubleSpinBox_ee_spline_min.setMinimumSize(QSize(125, 0))

        self.formLayout_ee_sub2_page_6.setWidget(1, QFormLayout.ItemRole.LabelRole, self.doubleSpinBox_ee_spline_min)

        self.label116 = QLabel(self.frame_eeprom_sub_2_page_6_black)
        self.label116.setObjectName(u"label116")

        self.formLayout_ee_sub2_page_6.setWidget(1, QFormLayout.ItemRole.FieldRole, self.label116)

        self.doubleSpinBox_ee_spline_max = QDoubleSpinBox(self.frame_eeprom_sub_2_page_6_black)
        self.doubleSpinBox_ee_spline_max.setObjectName(u"doubleSpinBox_ee_spline_max")
        self.doubleSpinBox_ee_spline_max.setMinimumSize(QSize(125, 0))

        self.formLayout_ee_sub2_page_6.setWidget(2, QFormLayout.ItemRole.LabelRole, self.doubleSpinBox_ee_spline_max)

        self.label117 = QLabel(self.frame_eeprom_sub_2_page_6_black)
        self.label117.setObjectName(u"label117")

        self.formLayout_ee_sub2_page_6.setWidget(2, QFormLayout.ItemRole.FieldRole, self.label117)


        self.vboxLayout20.addLayout(self.formLayout_ee_sub2_page_6)

        self.frame = QFrame(self.frame_eeprom_sub_2_page_6_black)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout1 = QGridLayout(self.frame)
        self.gridLayout1.setObjectName(u"gridLayout1")
        self.lineEdit_ee_spline_wl_12 = QLineEdit(self.frame)
        self.lineEdit_ee_spline_wl_12.setObjectName(u"lineEdit_ee_spline_wl_12")

        self.gridLayout1.addWidget(self.lineEdit_ee_spline_wl_12, 13, 0, 1, 1)

        self.lineEdit_ee_spline_y2_5 = QLineEdit(self.frame)
        self.lineEdit_ee_spline_y2_5.setObjectName(u"lineEdit_ee_spline_y2_5")

        self.gridLayout1.addWidget(self.lineEdit_ee_spline_y2_5, 6, 2, 1, 1)

        self.lineEdit_ee_spline_y_5 = QLineEdit(self.frame)
        self.lineEdit_ee_spline_y_5.setObjectName(u"lineEdit_ee_spline_y_5")

        self.gridLayout1.addWidget(self.lineEdit_ee_spline_y_5, 6, 1, 1, 1)

        self.lineEdit_ee_spline_wl_0 = QLineEdit(self.frame)
        self.lineEdit_ee_spline_wl_0.setObjectName(u"lineEdit_ee_spline_wl_0")

        self.gridLayout1.addWidget(self.lineEdit_ee_spline_wl_0, 1, 0, 1, 1)

        self.lineEdit_ee_spline_y_7 = QLineEdit(self.frame)
        self.lineEdit_ee_spline_y_7.setObjectName(u"lineEdit_ee_spline_y_7")

        self.gridLayout1.addWidget(self.lineEdit_ee_spline_y_7, 8, 1, 1, 1)

        self.lineEdit_ee_spline_y_8 = QLineEdit(self.frame)
        self.lineEdit_ee_spline_y_8.setObjectName(u"lineEdit_ee_spline_y_8")

        self.gridLayout1.addWidget(self.lineEdit_ee_spline_y_8, 9, 1, 1, 1)

        self.lineEdit_ee_spline_wl_3 = QLineEdit(self.frame)
        self.lineEdit_ee_spline_wl_3.setObjectName(u"lineEdit_ee_spline_wl_3")

        self.gridLayout1.addWidget(self.lineEdit_ee_spline_wl_3, 4, 0, 1, 1)

        self.lineEdit_ee_spline_y2_7 = QLineEdit(self.frame)
        self.lineEdit_ee_spline_y2_7.setObjectName(u"lineEdit_ee_spline_y2_7")

        self.gridLayout1.addWidget(self.lineEdit_ee_spline_y2_7, 8, 2, 1, 1)

        self.label118 = QLabel(self.frame)
        self.label118.setObjectName(u"label118")

        self.gridLayout1.addWidget(self.label118, 0, 2, 1, 1)

        self.lineEdit_ee_spline_y_3 = QLineEdit(self.frame)
        self.lineEdit_ee_spline_y_3.setObjectName(u"lineEdit_ee_spline_y_3")

        self.gridLayout1.addWidget(self.lineEdit_ee_spline_y_3, 4, 1, 1, 1)

        self.lineEdit_ee_spline_y_0 = QLineEdit(self.frame)
        self.lineEdit_ee_spline_y_0.setObjectName(u"lineEdit_ee_spline_y_0")

        self.gridLayout1.addWidget(self.lineEdit_ee_spline_y_0, 1, 1, 1, 1)

        self.lineEdit_ee_spline_y2_3 = QLineEdit(self.frame)
        self.lineEdit_ee_spline_y2_3.setObjectName(u"lineEdit_ee_spline_y2_3")

        self.gridLayout1.addWidget(self.lineEdit_ee_spline_y2_3, 4, 2, 1, 1)

        self.lineEdit_ee_spline_wl_6 = QLineEdit(self.frame)
        self.lineEdit_ee_spline_wl_6.setObjectName(u"lineEdit_ee_spline_wl_6")

        self.gridLayout1.addWidget(self.lineEdit_ee_spline_wl_6, 7, 0, 1, 1)

        self.lineEdit_ee_spline_y2_2 = QLineEdit(self.frame)
        self.lineEdit_ee_spline_y2_2.setObjectName(u"lineEdit_ee_spline_y2_2")

        self.gridLayout1.addWidget(self.lineEdit_ee_spline_y2_2, 3, 2, 1, 1)

        self.label119 = QLabel(self.frame)
        self.label119.setObjectName(u"label119")

        self.gridLayout1.addWidget(self.label119, 0, 0, 1, 1)

        self.lineEdit_ee_spline_wl_5 = QLineEdit(self.frame)
        self.lineEdit_ee_spline_wl_5.setObjectName(u"lineEdit_ee_spline_wl_5")

        self.gridLayout1.addWidget(self.lineEdit_ee_spline_wl_5, 6, 0, 1, 1)

        self.lineEdit_ee_spline_wl_10 = QLineEdit(self.frame)
        self.lineEdit_ee_spline_wl_10.setObjectName(u"lineEdit_ee_spline_wl_10")

        self.gridLayout1.addWidget(self.lineEdit_ee_spline_wl_10, 11, 0, 1, 1)

        self.lineEdit_ee_spline_wl_7 = QLineEdit(self.frame)
        self.lineEdit_ee_spline_wl_7.setObjectName(u"lineEdit_ee_spline_wl_7")

        self.gridLayout1.addWidget(self.lineEdit_ee_spline_wl_7, 8, 0, 1, 1)

        self.lineEdit_ee_spline_wl_8 = QLineEdit(self.frame)
        self.lineEdit_ee_spline_wl_8.setObjectName(u"lineEdit_ee_spline_wl_8")

        self.gridLayout1.addWidget(self.lineEdit_ee_spline_wl_8, 9, 0, 1, 1)

        self.lineEdit_ee_spline_y2_6 = QLineEdit(self.frame)
        self.lineEdit_ee_spline_y2_6.setObjectName(u"lineEdit_ee_spline_y2_6")

        self.gridLayout1.addWidget(self.lineEdit_ee_spline_y2_6, 7, 2, 1, 1)

        self.lineEdit_ee_spline_y2_0 = QLineEdit(self.frame)
        self.lineEdit_ee_spline_y2_0.setObjectName(u"lineEdit_ee_spline_y2_0")

        self.gridLayout1.addWidget(self.lineEdit_ee_spline_y2_0, 1, 2, 1, 1)

        self.label120 = QLabel(self.frame)
        self.label120.setObjectName(u"label120")

        self.gridLayout1.addWidget(self.label120, 0, 1, 1, 1)

        self.lineEdit_ee_spline_y2_1 = QLineEdit(self.frame)
        self.lineEdit_ee_spline_y2_1.setObjectName(u"lineEdit_ee_spline_y2_1")

        self.gridLayout1.addWidget(self.lineEdit_ee_spline_y2_1, 2, 2, 1, 1)

        self.lineEdit_ee_spline_y_1 = QLineEdit(self.frame)
        self.lineEdit_ee_spline_y_1.setObjectName(u"lineEdit_ee_spline_y_1")

        self.gridLayout1.addWidget(self.lineEdit_ee_spline_y_1, 2, 1, 1, 1)

        self.lineEdit_ee_spline_wl_4 = QLineEdit(self.frame)
        self.lineEdit_ee_spline_wl_4.setObjectName(u"lineEdit_ee_spline_wl_4")

        self.gridLayout1.addWidget(self.lineEdit_ee_spline_wl_4, 5, 0, 1, 1)

        self.lineEdit_ee_spline_y_4 = QLineEdit(self.frame)
        self.lineEdit_ee_spline_y_4.setObjectName(u"lineEdit_ee_spline_y_4")

        self.gridLayout1.addWidget(self.lineEdit_ee_spline_y_4, 5, 1, 1, 1)

        self.lineEdit_ee_spline_wl_11 = QLineEdit(self.frame)
        self.lineEdit_ee_spline_wl_11.setObjectName(u"lineEdit_ee_spline_wl_11")

        self.gridLayout1.addWidget(self.lineEdit_ee_spline_wl_11, 12, 0, 1, 1)

        self.lineEdit_ee_spline_y2_4 = QLineEdit(self.frame)
        self.lineEdit_ee_spline_y2_4.setObjectName(u"lineEdit_ee_spline_y2_4")

        self.gridLayout1.addWidget(self.lineEdit_ee_spline_y2_4, 5, 2, 1, 1)

        self.lineEdit_ee_spline_y2_9 = QLineEdit(self.frame)
        self.lineEdit_ee_spline_y2_9.setObjectName(u"lineEdit_ee_spline_y2_9")

        self.gridLayout1.addWidget(self.lineEdit_ee_spline_y2_9, 10, 2, 1, 1)

        self.lineEdit_ee_spline_wl_2 = QLineEdit(self.frame)
        self.lineEdit_ee_spline_wl_2.setObjectName(u"lineEdit_ee_spline_wl_2")

        self.gridLayout1.addWidget(self.lineEdit_ee_spline_wl_2, 3, 0, 1, 1)

        self.lineEdit_ee_spline_wl_1 = QLineEdit(self.frame)
        self.lineEdit_ee_spline_wl_1.setObjectName(u"lineEdit_ee_spline_wl_1")

        self.gridLayout1.addWidget(self.lineEdit_ee_spline_wl_1, 2, 0, 1, 1)

        self.lineEdit_ee_spline_y_6 = QLineEdit(self.frame)
        self.lineEdit_ee_spline_y_6.setObjectName(u"lineEdit_ee_spline_y_6")

        self.gridLayout1.addWidget(self.lineEdit_ee_spline_y_6, 7, 1, 1, 1)

        self.lineEdit_ee_spline_y_9 = QLineEdit(self.frame)
        self.lineEdit_ee_spline_y_9.setObjectName(u"lineEdit_ee_spline_y_9")

        self.gridLayout1.addWidget(self.lineEdit_ee_spline_y_9, 10, 1, 1, 1)

        self.lineEdit_ee_spline_y2_8 = QLineEdit(self.frame)
        self.lineEdit_ee_spline_y2_8.setObjectName(u"lineEdit_ee_spline_y2_8")

        self.gridLayout1.addWidget(self.lineEdit_ee_spline_y2_8, 9, 2, 1, 1)

        self.lineEdit_ee_spline_y_2 = QLineEdit(self.frame)
        self.lineEdit_ee_spline_y_2.setObjectName(u"lineEdit_ee_spline_y_2")

        self.gridLayout1.addWidget(self.lineEdit_ee_spline_y_2, 3, 1, 1, 1)

        self.lineEdit_ee_spline_wl_9 = QLineEdit(self.frame)
        self.lineEdit_ee_spline_wl_9.setObjectName(u"lineEdit_ee_spline_wl_9")

        self.gridLayout1.addWidget(self.lineEdit_ee_spline_wl_9, 10, 0, 1, 1)

        self.lineEdit_ee_spline_wl_13 = QLineEdit(self.frame)
        self.lineEdit_ee_spline_wl_13.setObjectName(u"lineEdit_ee_spline_wl_13")

        self.gridLayout1.addWidget(self.lineEdit_ee_spline_wl_13, 14, 0, 1, 1)

        self.lineEdit_ee_spline_y_10 = QLineEdit(self.frame)
        self.lineEdit_ee_spline_y_10.setObjectName(u"lineEdit_ee_spline_y_10")

        self.gridLayout1.addWidget(self.lineEdit_ee_spline_y_10, 11, 1, 1, 1)

        self.lineEdit_ee_spline_y_11 = QLineEdit(self.frame)
        self.lineEdit_ee_spline_y_11.setObjectName(u"lineEdit_ee_spline_y_11")

        self.gridLayout1.addWidget(self.lineEdit_ee_spline_y_11, 12, 1, 1, 1)

        self.lineEdit_ee_spline_y_12 = QLineEdit(self.frame)
        self.lineEdit_ee_spline_y_12.setObjectName(u"lineEdit_ee_spline_y_12")

        self.gridLayout1.addWidget(self.lineEdit_ee_spline_y_12, 13, 1, 1, 1)

        self.lineEdit_ee_spline_y_13 = QLineEdit(self.frame)
        self.lineEdit_ee_spline_y_13.setObjectName(u"lineEdit_ee_spline_y_13")

        self.gridLayout1.addWidget(self.lineEdit_ee_spline_y_13, 14, 1, 1, 1)

        self.lineEdit_ee_spline_y2_10 = QLineEdit(self.frame)
        self.lineEdit_ee_spline_y2_10.setObjectName(u"lineEdit_ee_spline_y2_10")

        self.gridLayout1.addWidget(self.lineEdit_ee_spline_y2_10, 11, 2, 1, 1)

        self.lineEdit_ee_spline_y2_11 = QLineEdit(self.frame)
        self.lineEdit_ee_spline_y2_11.setObjectName(u"lineEdit_ee_spline_y2_11")

        self.gridLayout1.addWidget(self.lineEdit_ee_spline_y2_11, 12, 2, 1, 1)

        self.lineEdit_ee_spline_y2_12 = QLineEdit(self.frame)
        self.lineEdit_ee_spline_y2_12.setObjectName(u"lineEdit_ee_spline_y2_12")

        self.gridLayout1.addWidget(self.lineEdit_ee_spline_y2_12, 13, 2, 1, 1)

        self.lineEdit_ee_spline_y2_13 = QLineEdit(self.frame)
        self.lineEdit_ee_spline_y2_13.setObjectName(u"lineEdit_ee_spline_y2_13")

        self.gridLayout1.addWidget(self.lineEdit_ee_spline_y2_13, 14, 2, 1, 1)


        self.vboxLayout20.addWidget(self.frame)


        self.vboxLayout19.addWidget(self.frame_eeprom_sub_2_page_6_black)


        self.vboxLayout18.addWidget(self.frame_eeprom_sub_2_page_6_white)


        self.vboxLayout1.addWidget(self.frame_eeprom_sub_2)

        self.frame_eeprom_sub_4 = QFrame(self.frame_eeprom_editor)
        self.frame_eeprom_sub_4.setObjectName(u"frame_eeprom_sub_4")
        self.frame_eeprom_sub_4.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_eeprom_sub_4.setFrameShadow(QFrame.Shadow.Raised)
        self.vboxLayout21 = QVBoxLayout(self.frame_eeprom_sub_4)
        self.vboxLayout21.setObjectName(u"vboxLayout21")
        self.vboxLayout21.setContentsMargins(0, 0, 0, 0)

        self.vboxLayout1.addWidget(self.frame_eeprom_sub_4)

        self.frame_eeprom_sub_5 = QFrame(self.frame_eeprom_editor)
        self.frame_eeprom_sub_5.setObjectName(u"frame_eeprom_sub_5")
        self.frame_eeprom_sub_5.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_eeprom_sub_5.setFrameShadow(QFrame.Shadow.Raised)
        self.vboxLayout22 = QVBoxLayout(self.frame_eeprom_sub_5)
        self.vboxLayout22.setObjectName(u"vboxLayout22")
        self.vboxLayout22.setContentsMargins(0, 0, 0, 0)
        self.frame_eeprom_sub_multi_wavelength_white = QFrame(self.frame_eeprom_sub_5)
        self.frame_eeprom_sub_multi_wavelength_white.setObjectName(u"frame_eeprom_sub_multi_wavelength_white")
        self.frame_eeprom_sub_multi_wavelength_white.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_eeprom_sub_multi_wavelength_white.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_eeprom_sub_multi_wavelength_white.setProperty(u"wpBox", False)
        self.vboxLayout23 = QVBoxLayout(self.frame_eeprom_sub_multi_wavelength_white)
        self.vboxLayout23.setObjectName(u"vboxLayout23")
        self.vboxLayout23.setContentsMargins(0, 0, 0, 0)
        self.frame_eeprom_sub_multi_wavelengths_black = QFrame(self.frame_eeprom_sub_multi_wavelength_white)
        self.frame_eeprom_sub_multi_wavelengths_black.setObjectName(u"frame_eeprom_sub_multi_wavelengths_black")
        self.frame_eeprom_sub_multi_wavelengths_black.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_eeprom_sub_multi_wavelengths_black.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_eeprom_sub_multi_wavelengths_black.setProperty(u"wpPanel", False)
        self.vboxLayout24 = QVBoxLayout(self.frame_eeprom_sub_multi_wavelengths_black)
        self.vboxLayout24.setObjectName(u"vboxLayout24")
        self.label121 = QLabel(self.frame_eeprom_sub_multi_wavelengths_black)
        self.label121.setObjectName(u"label121")
        self.label121.setFont(font)

        self.vboxLayout24.addWidget(self.label121)

        self.formLayout_ee_sub5_page_7 = QFormLayout()
        self.formLayout_ee_sub5_page_7.setObjectName(u"formLayout_ee_sub5_page_7")
        self.label122 = QLabel(self.frame_eeprom_sub_multi_wavelengths_black)
        self.label122.setObjectName(u"label122")

        self.formLayout_ee_sub5_page_7.setWidget(0, QFormLayout.ItemRole.FieldRole, self.label122)

        self.doubleSpinBox_ee_sub5_excitation_nm_float = QDoubleSpinBox(self.frame_eeprom_sub_multi_wavelengths_black)
        self.doubleSpinBox_ee_sub5_excitation_nm_float.setObjectName(u"doubleSpinBox_ee_sub5_excitation_nm_float")
        sizePolicy8 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy8.setHorizontalStretch(0)
        sizePolicy8.setVerticalStretch(0)
        sizePolicy8.setHeightForWidth(self.doubleSpinBox_ee_sub5_excitation_nm_float.sizePolicy().hasHeightForWidth())
        self.doubleSpinBox_ee_sub5_excitation_nm_float.setSizePolicy(sizePolicy8)
        self.doubleSpinBox_ee_sub5_excitation_nm_float.setMinimumSize(QSize(125, 0))
        self.doubleSpinBox_ee_sub5_excitation_nm_float.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.doubleSpinBox_ee_sub5_excitation_nm_float.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.doubleSpinBox_ee_sub5_excitation_nm_float.setMinimum(200.000000000000000)
        self.doubleSpinBox_ee_sub5_excitation_nm_float.setMaximum(2500.000000000000000)
        self.doubleSpinBox_ee_sub5_excitation_nm_float.setValue(784.000000000000000)

        self.formLayout_ee_sub5_page_7.setWidget(0, QFormLayout.ItemRole.LabelRole, self.doubleSpinBox_ee_sub5_excitation_nm_float)

        self.label123 = QLabel(self.frame_eeprom_sub_multi_wavelengths_black)
        self.label123.setObjectName(u"label123")

        self.formLayout_ee_sub5_page_7.setWidget(1, QFormLayout.ItemRole.FieldRole, self.label123)

        self.lineEdit_ee_sub5_wavelength_coeff_0 = QLineEdit(self.frame_eeprom_sub_multi_wavelengths_black)
        self.lineEdit_ee_sub5_wavelength_coeff_0.setObjectName(u"lineEdit_ee_sub5_wavelength_coeff_0")

        self.formLayout_ee_sub5_page_7.setWidget(1, QFormLayout.ItemRole.LabelRole, self.lineEdit_ee_sub5_wavelength_coeff_0)

        self.label124 = QLabel(self.frame_eeprom_sub_multi_wavelengths_black)
        self.label124.setObjectName(u"label124")

        self.formLayout_ee_sub5_page_7.setWidget(2, QFormLayout.ItemRole.FieldRole, self.label124)

        self.lineEdit_ee_sub5_wavelength_coeff_1 = QLineEdit(self.frame_eeprom_sub_multi_wavelengths_black)
        self.lineEdit_ee_sub5_wavelength_coeff_1.setObjectName(u"lineEdit_ee_sub5_wavelength_coeff_1")

        self.formLayout_ee_sub5_page_7.setWidget(2, QFormLayout.ItemRole.LabelRole, self.lineEdit_ee_sub5_wavelength_coeff_1)

        self.label125 = QLabel(self.frame_eeprom_sub_multi_wavelengths_black)
        self.label125.setObjectName(u"label125")

        self.formLayout_ee_sub5_page_7.setWidget(3, QFormLayout.ItemRole.FieldRole, self.label125)

        self.lineEdit_ee_sub5_wavelength_coeff_2 = QLineEdit(self.frame_eeprom_sub_multi_wavelengths_black)
        self.lineEdit_ee_sub5_wavelength_coeff_2.setObjectName(u"lineEdit_ee_sub5_wavelength_coeff_2")

        self.formLayout_ee_sub5_page_7.setWidget(3, QFormLayout.ItemRole.LabelRole, self.lineEdit_ee_sub5_wavelength_coeff_2)

        self.label126 = QLabel(self.frame_eeprom_sub_multi_wavelengths_black)
        self.label126.setObjectName(u"label126")

        self.formLayout_ee_sub5_page_7.setWidget(4, QFormLayout.ItemRole.FieldRole, self.label126)

        self.lineEdit_ee_sub5_wavelength_coeff_3 = QLineEdit(self.frame_eeprom_sub_multi_wavelengths_black)
        self.lineEdit_ee_sub5_wavelength_coeff_3.setObjectName(u"lineEdit_ee_sub5_wavelength_coeff_3")

        self.formLayout_ee_sub5_page_7.setWidget(4, QFormLayout.ItemRole.LabelRole, self.lineEdit_ee_sub5_wavelength_coeff_3)

        self.label127 = QLabel(self.frame_eeprom_sub_multi_wavelengths_black)
        self.label127.setObjectName(u"label127")

        self.formLayout_ee_sub5_page_7.setWidget(5, QFormLayout.ItemRole.FieldRole, self.label127)

        self.lineEdit_ee_sub5_wavelength_coeff_4 = QLineEdit(self.frame_eeprom_sub_multi_wavelengths_black)
        self.lineEdit_ee_sub5_wavelength_coeff_4.setObjectName(u"lineEdit_ee_sub5_wavelength_coeff_4")

        self.formLayout_ee_sub5_page_7.setWidget(5, QFormLayout.ItemRole.LabelRole, self.lineEdit_ee_sub5_wavelength_coeff_4)

        self.label128 = QLabel(self.frame_eeprom_sub_multi_wavelengths_black)
        self.label128.setObjectName(u"label128")

        self.formLayout_ee_sub5_page_7.setWidget(6, QFormLayout.ItemRole.FieldRole, self.label128)

        self.spinBox_ee_sub5_roi_horizontal_start = QSpinBox(self.frame_eeprom_sub_multi_wavelengths_black)
        self.spinBox_ee_sub5_roi_horizontal_start.setObjectName(u"spinBox_ee_sub5_roi_horizontal_start")
        sizePolicy9 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        sizePolicy9.setHorizontalStretch(0)
        sizePolicy9.setVerticalStretch(0)
        sizePolicy9.setHeightForWidth(self.spinBox_ee_sub5_roi_horizontal_start.sizePolicy().hasHeightForWidth())
        self.spinBox_ee_sub5_roi_horizontal_start.setSizePolicy(sizePolicy9)
        self.spinBox_ee_sub5_roi_horizontal_start.setMinimumSize(QSize(100, 0))
        self.spinBox_ee_sub5_roi_horizontal_start.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_sub5_roi_horizontal_start.setValue(-1)

        self.formLayout_ee_sub5_page_7.setWidget(6, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_sub5_roi_horizontal_start)

        self.label129 = QLabel(self.frame_eeprom_sub_multi_wavelengths_black)
        self.label129.setObjectName(u"label129")

        self.formLayout_ee_sub5_page_7.setWidget(7, QFormLayout.ItemRole.FieldRole, self.label129)

        self.spinBox_ee_sub5_roi_horizontal_end = QSpinBox(self.frame_eeprom_sub_multi_wavelengths_black)
        self.spinBox_ee_sub5_roi_horizontal_end.setObjectName(u"spinBox_ee_sub5_roi_horizontal_end")
        sizePolicy9.setHeightForWidth(self.spinBox_ee_sub5_roi_horizontal_end.sizePolicy().hasHeightForWidth())
        self.spinBox_ee_sub5_roi_horizontal_end.setSizePolicy(sizePolicy9)
        self.spinBox_ee_sub5_roi_horizontal_end.setMinimumSize(QSize(100, 0))
        self.spinBox_ee_sub5_roi_horizontal_end.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_sub5_roi_horizontal_end.setValue(-1)

        self.formLayout_ee_sub5_page_7.setWidget(7, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_sub5_roi_horizontal_end)

        self.label130 = QLabel(self.frame_eeprom_sub_multi_wavelengths_black)
        self.label130.setObjectName(u"label130")

        self.formLayout_ee_sub5_page_7.setWidget(8, QFormLayout.ItemRole.FieldRole, self.label130)

        self.doubleSpinBox_ee_sub5_avg_resolution = QDoubleSpinBox(self.frame_eeprom_sub_multi_wavelengths_black)
        self.doubleSpinBox_ee_sub5_avg_resolution.setObjectName(u"doubleSpinBox_ee_sub5_avg_resolution")
        sizePolicy8.setHeightForWidth(self.doubleSpinBox_ee_sub5_avg_resolution.sizePolicy().hasHeightForWidth())
        self.doubleSpinBox_ee_sub5_avg_resolution.setSizePolicy(sizePolicy8)
        self.doubleSpinBox_ee_sub5_avg_resolution.setMinimumSize(QSize(125, 0))
        self.doubleSpinBox_ee_sub5_avg_resolution.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.doubleSpinBox_ee_sub5_avg_resolution.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.formLayout_ee_sub5_page_7.setWidget(8, QFormLayout.ItemRole.LabelRole, self.doubleSpinBox_ee_sub5_avg_resolution)

        self.label131 = QLabel(self.frame_eeprom_sub_multi_wavelengths_black)
        self.label131.setObjectName(u"label131")

        self.formLayout_ee_sub5_page_7.setWidget(9, QFormLayout.ItemRole.FieldRole, self.label131)

        self.lineEdit_ee_sub5_raman_intensity_coeff_0 = QLineEdit(self.frame_eeprom_sub_multi_wavelengths_black)
        self.lineEdit_ee_sub5_raman_intensity_coeff_0.setObjectName(u"lineEdit_ee_sub5_raman_intensity_coeff_0")

        self.formLayout_ee_sub5_page_7.setWidget(9, QFormLayout.ItemRole.LabelRole, self.lineEdit_ee_sub5_raman_intensity_coeff_0)

        self.label132 = QLabel(self.frame_eeprom_sub_multi_wavelengths_black)
        self.label132.setObjectName(u"label132")

        self.formLayout_ee_sub5_page_7.setWidget(10, QFormLayout.ItemRole.FieldRole, self.label132)

        self.lineEdit_ee_sub5_raman_intensity_coeff_1 = QLineEdit(self.frame_eeprom_sub_multi_wavelengths_black)
        self.lineEdit_ee_sub5_raman_intensity_coeff_1.setObjectName(u"lineEdit_ee_sub5_raman_intensity_coeff_1")

        self.formLayout_ee_sub5_page_7.setWidget(10, QFormLayout.ItemRole.LabelRole, self.lineEdit_ee_sub5_raman_intensity_coeff_1)

        self.label133 = QLabel(self.frame_eeprom_sub_multi_wavelengths_black)
        self.label133.setObjectName(u"label133")

        self.formLayout_ee_sub5_page_7.setWidget(11, QFormLayout.ItemRole.FieldRole, self.label133)

        self.lineEdit_ee_sub5_raman_intensity_coeff_2 = QLineEdit(self.frame_eeprom_sub_multi_wavelengths_black)
        self.lineEdit_ee_sub5_raman_intensity_coeff_2.setObjectName(u"lineEdit_ee_sub5_raman_intensity_coeff_2")

        self.formLayout_ee_sub5_page_7.setWidget(11, QFormLayout.ItemRole.LabelRole, self.lineEdit_ee_sub5_raman_intensity_coeff_2)

        self.label134 = QLabel(self.frame_eeprom_sub_multi_wavelengths_black)
        self.label134.setObjectName(u"label134")

        self.formLayout_ee_sub5_page_7.setWidget(12, QFormLayout.ItemRole.FieldRole, self.label134)

        self.lineEdit_ee_sub5_raman_intensity_coeff_3 = QLineEdit(self.frame_eeprom_sub_multi_wavelengths_black)
        self.lineEdit_ee_sub5_raman_intensity_coeff_3.setObjectName(u"lineEdit_ee_sub5_raman_intensity_coeff_3")

        self.formLayout_ee_sub5_page_7.setWidget(12, QFormLayout.ItemRole.LabelRole, self.lineEdit_ee_sub5_raman_intensity_coeff_3)

        self.label135 = QLabel(self.frame_eeprom_sub_multi_wavelengths_black)
        self.label135.setObjectName(u"label135")

        self.formLayout_ee_sub5_page_7.setWidget(13, QFormLayout.ItemRole.FieldRole, self.label135)

        self.lineEdit_ee_sub5_raman_intensity_coeff_4 = QLineEdit(self.frame_eeprom_sub_multi_wavelengths_black)
        self.lineEdit_ee_sub5_raman_intensity_coeff_4.setObjectName(u"lineEdit_ee_sub5_raman_intensity_coeff_4")

        self.formLayout_ee_sub5_page_7.setWidget(13, QFormLayout.ItemRole.LabelRole, self.lineEdit_ee_sub5_raman_intensity_coeff_4)

        self.label136 = QLabel(self.frame_eeprom_sub_multi_wavelengths_black)
        self.label136.setObjectName(u"label136")

        self.formLayout_ee_sub5_page_7.setWidget(14, QFormLayout.ItemRole.FieldRole, self.label136)

        self.lineEdit_ee_sub5_raman_intensity_coeff_5 = QLineEdit(self.frame_eeprom_sub_multi_wavelengths_black)
        self.lineEdit_ee_sub5_raman_intensity_coeff_5.setObjectName(u"lineEdit_ee_sub5_raman_intensity_coeff_5")

        self.formLayout_ee_sub5_page_7.setWidget(14, QFormLayout.ItemRole.LabelRole, self.lineEdit_ee_sub5_raman_intensity_coeff_5)

        self.label137 = QLabel(self.frame_eeprom_sub_multi_wavelengths_black)
        self.label137.setObjectName(u"label137")

        self.formLayout_ee_sub5_page_7.setWidget(15, QFormLayout.ItemRole.FieldRole, self.label137)

        self.lineEdit_ee_sub5_raman_intensity_coeff_6 = QLineEdit(self.frame_eeprom_sub_multi_wavelengths_black)
        self.lineEdit_ee_sub5_raman_intensity_coeff_6.setObjectName(u"lineEdit_ee_sub5_raman_intensity_coeff_6")

        self.formLayout_ee_sub5_page_7.setWidget(15, QFormLayout.ItemRole.LabelRole, self.lineEdit_ee_sub5_raman_intensity_coeff_6)

        self.label138 = QLabel(self.frame_eeprom_sub_multi_wavelengths_black)
        self.label138.setObjectName(u"label138")

        self.formLayout_ee_sub5_page_7.setWidget(16, QFormLayout.ItemRole.FieldRole, self.label138)

        self.spinBox_ee_sub5_horiz_binning_mode = QSpinBox(self.frame_eeprom_sub_multi_wavelengths_black)
        self.spinBox_ee_sub5_horiz_binning_mode.setObjectName(u"spinBox_ee_sub5_horiz_binning_mode")
        sizePolicy9.setHeightForWidth(self.spinBox_ee_sub5_horiz_binning_mode.sizePolicy().hasHeightForWidth())
        self.spinBox_ee_sub5_horiz_binning_mode.setSizePolicy(sizePolicy9)
        self.spinBox_ee_sub5_horiz_binning_mode.setMinimumSize(QSize(100, 0))
        self.spinBox_ee_sub5_horiz_binning_mode.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.formLayout_ee_sub5_page_7.setWidget(16, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_sub5_horiz_binning_mode)


        self.vboxLayout24.addLayout(self.formLayout_ee_sub5_page_7)


        self.vboxLayout23.addWidget(self.frame_eeprom_sub_multi_wavelengths_black)


        self.vboxLayout22.addWidget(self.frame_eeprom_sub_multi_wavelength_white)


        self.vboxLayout1.addWidget(self.frame_eeprom_sub_5)

        self.frame_eeprom_page_8_white = QFrame(self.frame_eeprom_editor)
        self.frame_eeprom_page_8_white.setObjectName(u"frame_eeprom_page_8_white")
        self.frame_eeprom_page_8_white.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_eeprom_page_8_white.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_eeprom_page_8_white.setProperty(u"wpBox", False)
        self.vboxLayout25 = QVBoxLayout(self.frame_eeprom_page_8_white)
        self.vboxLayout25.setSpacing(0)
        self.vboxLayout25.setObjectName(u"vboxLayout25")
        self.vboxLayout25.setContentsMargins(0, 0, 0, 0)
        self.frame_eeprom_page_8 = QFrame(self.frame_eeprom_page_8_white)
        self.frame_eeprom_page_8.setObjectName(u"frame_eeprom_page_8")
        self.frame_eeprom_page_8.setMinimumSize(QSize(0, 0))
        self.frame_eeprom_page_8.setProperty(u"wpPanel", False)
        self.vboxLayout26 = QVBoxLayout(self.frame_eeprom_page_8)
        self.vboxLayout26.setObjectName(u"vboxLayout26")
        self.label139 = QLabel(self.frame_eeprom_page_8)
        self.label139.setObjectName(u"label139")
        self.label139.setFont(font)

        self.vboxLayout26.addWidget(self.label139)

        self.formLayout_ee_page_8 = QFormLayout()
        self.formLayout_ee_page_8.setObjectName(u"formLayout_ee_page_8")
        self.formLayout_ee_page_8.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.formLayout_ee_page_8.setLabelAlignment(Qt.AlignmentFlag.AlignCenter)
        self.formLayout_ee_page_8.setFormAlignment(Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignTop)
        self.formLayout_ee_page_8.setVerticalSpacing(4)
        self.lineEdit_ee_laser_password = QLineEdit(self.frame_eeprom_page_8)
        self.lineEdit_ee_laser_password.setObjectName(u"lineEdit_ee_laser_password")
        self.lineEdit_ee_laser_password.setEchoMode(QLineEdit.PasswordEchoOnEdit)

        self.formLayout_ee_page_8.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lineEdit_ee_laser_password)

        self.label140 = QLabel(self.frame_eeprom_page_8)
        self.label140.setObjectName(u"label140")

        self.formLayout_ee_page_8.setWidget(0, QFormLayout.ItemRole.FieldRole, self.label140)

        self.checkBox_ee_ble_door_sensor = QCheckBox(self.frame_eeprom_page_8)
        self.checkBox_ee_ble_door_sensor.setObjectName(u"checkBox_ee_ble_door_sensor")

        self.formLayout_ee_page_8.setWidget(1, QFormLayout.ItemRole.LabelRole, self.checkBox_ee_ble_door_sensor)

        self.label141 = QLabel(self.frame_eeprom_page_8)
        self.label141.setObjectName(u"label141")

        self.formLayout_ee_page_8.setWidget(1, QFormLayout.ItemRole.FieldRole, self.label141)

        self.checkBox_ee_ext_laser_control = QCheckBox(self.frame_eeprom_page_8)
        self.checkBox_ee_ext_laser_control.setObjectName(u"checkBox_ee_ext_laser_control")

        self.formLayout_ee_page_8.setWidget(2, QFormLayout.ItemRole.LabelRole, self.checkBox_ee_ext_laser_control)

        self.label142 = QLabel(self.frame_eeprom_page_8)
        self.label142.setObjectName(u"label142")

        self.formLayout_ee_page_8.setWidget(2, QFormLayout.ItemRole.FieldRole, self.label142)

        self.checkBox_ee_aux_button_laser_enable = QCheckBox(self.frame_eeprom_page_8)
        self.checkBox_ee_aux_button_laser_enable.setObjectName(u"checkBox_ee_aux_button_laser_enable")

        self.formLayout_ee_page_8.setWidget(3, QFormLayout.ItemRole.LabelRole, self.checkBox_ee_aux_button_laser_enable)

        self.label143 = QLabel(self.frame_eeprom_page_8)
        self.label143.setObjectName(u"label143")

        self.formLayout_ee_page_8.setWidget(3, QFormLayout.ItemRole.FieldRole, self.label143)

        self.checkBox_ee_disable_laser_sub_sys = QCheckBox(self.frame_eeprom_page_8)
        self.checkBox_ee_disable_laser_sub_sys.setObjectName(u"checkBox_ee_disable_laser_sub_sys")

        self.formLayout_ee_page_8.setWidget(4, QFormLayout.ItemRole.LabelRole, self.checkBox_ee_disable_laser_sub_sys)

        self.label144 = QLabel(self.frame_eeprom_page_8)
        self.label144.setObjectName(u"label144")

        self.formLayout_ee_page_8.setWidget(4, QFormLayout.ItemRole.FieldRole, self.label144)

        self.checkBox_ee_leave_acc_5v_out_powered = QCheckBox(self.frame_eeprom_page_8)
        self.checkBox_ee_leave_acc_5v_out_powered.setObjectName(u"checkBox_ee_leave_acc_5v_out_powered")

        self.formLayout_ee_page_8.setWidget(5, QFormLayout.ItemRole.LabelRole, self.checkBox_ee_leave_acc_5v_out_powered)

        self.label145 = QLabel(self.frame_eeprom_page_8)
        self.label145.setObjectName(u"label145")

        self.formLayout_ee_page_8.setWidget(5, QFormLayout.ItemRole.FieldRole, self.label145)

        self.checkBox_ee_disable_detector = QCheckBox(self.frame_eeprom_page_8)
        self.checkBox_ee_disable_detector.setObjectName(u"checkBox_ee_disable_detector")

        self.formLayout_ee_page_8.setWidget(6, QFormLayout.ItemRole.LabelRole, self.checkBox_ee_disable_detector)

        self.label146 = QLabel(self.frame_eeprom_page_8)
        self.label146.setObjectName(u"label146")

        self.formLayout_ee_page_8.setWidget(6, QFormLayout.ItemRole.FieldRole, self.label146)

        self.lineEdit_ee_acc_state = QLineEdit(self.frame_eeprom_page_8)
        self.lineEdit_ee_acc_state.setObjectName(u"lineEdit_ee_acc_state")

        self.formLayout_ee_page_8.setWidget(7, QFormLayout.ItemRole.LabelRole, self.lineEdit_ee_acc_state)

        self.label147 = QLabel(self.frame_eeprom_page_8)
        self.label147.setObjectName(u"label147")

        self.formLayout_ee_page_8.setWidget(7, QFormLayout.ItemRole.FieldRole, self.label147)

        self.lineEdit_ee_acc_state_gpio1 = QLineEdit(self.frame_eeprom_page_8)
        self.lineEdit_ee_acc_state_gpio1.setObjectName(u"lineEdit_ee_acc_state_gpio1")

        self.formLayout_ee_page_8.setWidget(8, QFormLayout.ItemRole.LabelRole, self.lineEdit_ee_acc_state_gpio1)

        self.label148 = QLabel(self.frame_eeprom_page_8)
        self.label148.setObjectName(u"label148")

        self.formLayout_ee_page_8.setWidget(8, QFormLayout.ItemRole.FieldRole, self.label148)

        self.lineEdit_ee_acc_state_gpio2 = QLineEdit(self.frame_eeprom_page_8)
        self.lineEdit_ee_acc_state_gpio2.setObjectName(u"lineEdit_ee_acc_state_gpio2")

        self.formLayout_ee_page_8.setWidget(9, QFormLayout.ItemRole.LabelRole, self.lineEdit_ee_acc_state_gpio2)

        self.label149 = QLabel(self.frame_eeprom_page_8)
        self.label149.setObjectName(u"label149")

        self.formLayout_ee_page_8.setWidget(9, QFormLayout.ItemRole.FieldRole, self.label149)

        self.spinBox_ee_acc_cont_strobe_period_us = QSpinBox(self.frame_eeprom_page_8)
        self.spinBox_ee_acc_cont_strobe_period_us.setObjectName(u"spinBox_ee_acc_cont_strobe_period_us")
        self.spinBox_ee_acc_cont_strobe_period_us.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_acc_cont_strobe_period_us.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_acc_cont_strobe_period_us.setKeyboardTracking(False)
        self.spinBox_ee_acc_cont_strobe_period_us.setMinimum(0)
        self.spinBox_ee_acc_cont_strobe_period_us.setMaximum(999999)
        self.spinBox_ee_acc_cont_strobe_period_us.setSingleStep(1)
        self.spinBox_ee_acc_cont_strobe_period_us.setValue(0)

        self.formLayout_ee_page_8.setWidget(10, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_acc_cont_strobe_period_us)

        self.label150 = QLabel(self.frame_eeprom_page_8)
        self.label150.setObjectName(u"label150")

        self.formLayout_ee_page_8.setWidget(10, QFormLayout.ItemRole.FieldRole, self.label150)

        self.spinBox_ee_acc_cont_strobe_width_us = QSpinBox(self.frame_eeprom_page_8)
        self.spinBox_ee_acc_cont_strobe_width_us.setObjectName(u"spinBox_ee_acc_cont_strobe_width_us")
        self.spinBox_ee_acc_cont_strobe_width_us.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_acc_cont_strobe_width_us.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_acc_cont_strobe_width_us.setKeyboardTracking(False)
        self.spinBox_ee_acc_cont_strobe_width_us.setMinimum(0)
        self.spinBox_ee_acc_cont_strobe_width_us.setMaximum(999999)
        self.spinBox_ee_acc_cont_strobe_width_us.setSingleStep(1)
        self.spinBox_ee_acc_cont_strobe_width_us.setValue(0)

        self.formLayout_ee_page_8.setWidget(11, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_acc_cont_strobe_width_us)

        self.label151 = QLabel(self.frame_eeprom_page_8)
        self.label151.setObjectName(u"label151")

        self.formLayout_ee_page_8.setWidget(11, QFormLayout.ItemRole.FieldRole, self.label151)

        self.spinBox_ee_acc_cont_strobe_delay_us = QSpinBox(self.frame_eeprom_page_8)
        self.spinBox_ee_acc_cont_strobe_delay_us.setObjectName(u"spinBox_ee_acc_cont_strobe_delay_us")
        self.spinBox_ee_acc_cont_strobe_delay_us.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_acc_cont_strobe_delay_us.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_acc_cont_strobe_delay_us.setKeyboardTracking(False)
        self.spinBox_ee_acc_cont_strobe_delay_us.setMinimum(0)
        self.spinBox_ee_acc_cont_strobe_delay_us.setMaximum(999999)
        self.spinBox_ee_acc_cont_strobe_delay_us.setSingleStep(1)
        self.spinBox_ee_acc_cont_strobe_delay_us.setValue(0)

        self.formLayout_ee_page_8.setWidget(12, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_acc_cont_strobe_delay_us)

        self.label152 = QLabel(self.frame_eeprom_page_8)
        self.label152.setObjectName(u"label152")

        self.formLayout_ee_page_8.setWidget(12, QFormLayout.ItemRole.FieldRole, self.label152)

        self.spinBox_ee_acc_cont_strobe_count = QSpinBox(self.frame_eeprom_page_8)
        self.spinBox_ee_acc_cont_strobe_count.setObjectName(u"spinBox_ee_acc_cont_strobe_count")
        self.spinBox_ee_acc_cont_strobe_count.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_acc_cont_strobe_count.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_acc_cont_strobe_count.setKeyboardTracking(False)
        self.spinBox_ee_acc_cont_strobe_count.setMinimum(0)
        self.spinBox_ee_acc_cont_strobe_count.setMaximum(999999)
        self.spinBox_ee_acc_cont_strobe_count.setSingleStep(1)
        self.spinBox_ee_acc_cont_strobe_count.setValue(0)

        self.formLayout_ee_page_8.setWidget(13, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_acc_cont_strobe_count)

        self.label153 = QLabel(self.frame_eeprom_page_8)
        self.label153.setObjectName(u"label153")

        self.formLayout_ee_page_8.setWidget(13, QFormLayout.ItemRole.FieldRole, self.label153)

        self.spinBox_ee_max_battery_temp_deg_c = QSpinBox(self.frame_eeprom_page_8)
        self.spinBox_ee_max_battery_temp_deg_c.setObjectName(u"spinBox_ee_max_battery_temp_deg_c")
        self.spinBox_ee_max_battery_temp_deg_c.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_max_battery_temp_deg_c.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_max_battery_temp_deg_c.setKeyboardTracking(False)
        self.spinBox_ee_max_battery_temp_deg_c.setMinimum(0)
        self.spinBox_ee_max_battery_temp_deg_c.setMaximum(100)
        self.spinBox_ee_max_battery_temp_deg_c.setSingleStep(1)
        self.spinBox_ee_max_battery_temp_deg_c.setValue(0)

        self.formLayout_ee_page_8.setWidget(14, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_max_battery_temp_deg_c)

        self.label154 = QLabel(self.frame_eeprom_page_8)
        self.label154.setObjectName(u"label154")

        self.formLayout_ee_page_8.setWidget(14, QFormLayout.ItemRole.FieldRole, self.label154)

        self.spinBox_ee_pixel_correction_type = QSpinBox(self.frame_eeprom_page_8)
        self.spinBox_ee_pixel_correction_type.setObjectName(u"spinBox_ee_pixel_correction_type")
        self.spinBox_ee_pixel_correction_type.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_pixel_correction_type.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_pixel_correction_type.setKeyboardTracking(False)
        self.spinBox_ee_pixel_correction_type.setMinimum(0)
        self.spinBox_ee_pixel_correction_type.setMaximum(255)
        self.spinBox_ee_pixel_correction_type.setSingleStep(1)
        self.spinBox_ee_pixel_correction_type.setValue(0)

        self.formLayout_ee_page_8.setWidget(15, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_pixel_correction_type)

        self.label155 = QLabel(self.frame_eeprom_page_8)
        self.label155.setObjectName(u"label155")

        self.formLayout_ee_page_8.setWidget(15, QFormLayout.ItemRole.FieldRole, self.label155)

        self.lineEdit_ee_usb_manufacturer_name = QLineEdit(self.frame_eeprom_page_8)
        self.lineEdit_ee_usb_manufacturer_name.setObjectName(u"lineEdit_ee_usb_manufacturer_name")

        self.formLayout_ee_page_8.setWidget(16, QFormLayout.ItemRole.LabelRole, self.lineEdit_ee_usb_manufacturer_name)

        self.label156 = QLabel(self.frame_eeprom_page_8)
        self.label156.setObjectName(u"label156")

        self.formLayout_ee_page_8.setWidget(16, QFormLayout.ItemRole.FieldRole, self.label156)

        self.spinBox_ee_aux_button_function = QSpinBox(self.frame_eeprom_page_8)
        self.spinBox_ee_aux_button_function.setObjectName(u"spinBox_ee_aux_button_function")
        self.spinBox_ee_aux_button_function.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_aux_button_function.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_aux_button_function.setKeyboardTracking(False)
        self.spinBox_ee_aux_button_function.setMinimum(0)
        self.spinBox_ee_aux_button_function.setMaximum(255)
        self.spinBox_ee_aux_button_function.setSingleStep(1)
        self.spinBox_ee_aux_button_function.setValue(0)

        self.formLayout_ee_page_8.setWidget(17, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_aux_button_function)

        self.label157 = QLabel(self.frame_eeprom_page_8)
        self.label157.setObjectName(u"label157")

        self.formLayout_ee_page_8.setWidget(17, QFormLayout.ItemRole.FieldRole, self.label157)

        self.spinBox_ee_aux_button_param = QSpinBox(self.frame_eeprom_page_8)
        self.spinBox_ee_aux_button_param.setObjectName(u"spinBox_ee_aux_button_param")
        self.spinBox_ee_aux_button_param.setMinimumSize(QSize(125, 0))
        self.spinBox_ee_aux_button_param.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_ee_aux_button_param.setKeyboardTracking(False)
        self.spinBox_ee_aux_button_param.setMinimum(0)
        self.spinBox_ee_aux_button_param.setMaximum(255)
        self.spinBox_ee_aux_button_param.setSingleStep(1)
        self.spinBox_ee_aux_button_param.setValue(0)

        self.formLayout_ee_page_8.setWidget(18, QFormLayout.ItemRole.LabelRole, self.spinBox_ee_aux_button_param)

        self.label158 = QLabel(self.frame_eeprom_page_8)
        self.label158.setObjectName(u"label158")

        self.formLayout_ee_page_8.setWidget(18, QFormLayout.ItemRole.FieldRole, self.label158)

        self.lineEdit_ee_latched_hardware_failures = QLineEdit(self.frame_eeprom_page_8)
        self.lineEdit_ee_latched_hardware_failures.setObjectName(u"lineEdit_ee_latched_hardware_failures")

        self.formLayout_ee_page_8.setWidget(19, QFormLayout.ItemRole.LabelRole, self.lineEdit_ee_latched_hardware_failures)

        self.label159 = QLabel(self.frame_eeprom_page_8)
        self.label159.setObjectName(u"label159")

        self.formLayout_ee_page_8.setWidget(19, QFormLayout.ItemRole.FieldRole, self.label159)


        self.vboxLayout26.addLayout(self.formLayout_ee_page_8)


        self.vboxLayout25.addWidget(self.frame_eeprom_page_8)


        self.vboxLayout1.addWidget(self.frame_eeprom_page_8_white)


        self.vboxLayout.addWidget(self.frame_eeprom_editor)


        self.verticalLayout_serial_eeprom_etc.addWidget(self.frame_eeprom_contents_white)

        self.frame_fpga_compilation_options = QFrame(self.page_hardware_information)
        self.frame_fpga_compilation_options.setObjectName(u"frame_fpga_compilation_options")
        self.frame_fpga_compilation_options.setMinimumSize(QSize(0, 0))
        self.vboxLayout27 = QVBoxLayout(self.frame_fpga_compilation_options)
        self.vboxLayout27.setObjectName(u"vboxLayout27")
        self.label160 = QLabel(self.frame_fpga_compilation_options)
        self.label160.setObjectName(u"label160")
        self.label160.setFont(font)

        self.vboxLayout27.addWidget(self.label160)

        self.formLayout1 = QFormLayout()
        self.formLayout1.setObjectName(u"formLayout1")
        self.label_fpga_integration_time_resolution = QLabel(self.frame_fpga_compilation_options)
        self.label_fpga_integration_time_resolution.setObjectName(u"label_fpga_integration_time_resolution")

        self.formLayout1.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_fpga_integration_time_resolution)

        self.label161 = QLabel(self.frame_fpga_compilation_options)
        self.label161.setObjectName(u"label161")

        self.formLayout1.setWidget(0, QFormLayout.ItemRole.FieldRole, self.label161)

        self.label_fpga_data_header = QLabel(self.frame_fpga_compilation_options)
        self.label_fpga_data_header.setObjectName(u"label_fpga_data_header")

        self.formLayout1.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_fpga_data_header)

        self.label162 = QLabel(self.frame_fpga_compilation_options)
        self.label162.setObjectName(u"label162")

        self.formLayout1.setWidget(1, QFormLayout.ItemRole.FieldRole, self.label162)

        self.label_fpga_has_cf_select = QLabel(self.frame_fpga_compilation_options)
        self.label_fpga_has_cf_select.setObjectName(u"label_fpga_has_cf_select")

        self.formLayout1.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_fpga_has_cf_select)

        self.label163 = QLabel(self.frame_fpga_compilation_options)
        self.label163.setObjectName(u"label163")

        self.formLayout1.setWidget(2, QFormLayout.ItemRole.FieldRole, self.label163)

        self.label_fpga_laser_type = QLabel(self.frame_fpga_compilation_options)
        self.label_fpga_laser_type.setObjectName(u"label_fpga_laser_type")

        self.formLayout1.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label_fpga_laser_type)

        self.label164 = QLabel(self.frame_fpga_compilation_options)
        self.label164.setObjectName(u"label164")

        self.formLayout1.setWidget(3, QFormLayout.ItemRole.FieldRole, self.label164)

        self.label_fpga_laser_control = QLabel(self.frame_fpga_compilation_options)
        self.label_fpga_laser_control.setObjectName(u"label_fpga_laser_control")

        self.formLayout1.setWidget(4, QFormLayout.ItemRole.LabelRole, self.label_fpga_laser_control)

        self.label165 = QLabel(self.frame_fpga_compilation_options)
        self.label165.setObjectName(u"label165")

        self.formLayout1.setWidget(4, QFormLayout.ItemRole.FieldRole, self.label165)

        self.label_has_area_scan = QLabel(self.frame_fpga_compilation_options)
        self.label_has_area_scan.setObjectName(u"label_has_area_scan")

        self.formLayout1.setWidget(5, QFormLayout.ItemRole.LabelRole, self.label_has_area_scan)

        self.label166 = QLabel(self.frame_fpga_compilation_options)
        self.label166.setObjectName(u"label166")

        self.formLayout1.setWidget(5, QFormLayout.ItemRole.FieldRole, self.label166)

        self.label_has_actual_integration_time = QLabel(self.frame_fpga_compilation_options)
        self.label_has_actual_integration_time.setObjectName(u"label_has_actual_integration_time")

        self.formLayout1.setWidget(6, QFormLayout.ItemRole.LabelRole, self.label_has_actual_integration_time)

        self.label167 = QLabel(self.frame_fpga_compilation_options)
        self.label167.setObjectName(u"label167")

        self.formLayout1.setWidget(6, QFormLayout.ItemRole.FieldRole, self.label167)

        self.label_has_horizontal_binning = QLabel(self.frame_fpga_compilation_options)
        self.label_has_horizontal_binning.setObjectName(u"label_has_horizontal_binning")

        self.formLayout1.setWidget(7, QFormLayout.ItemRole.LabelRole, self.label_has_horizontal_binning)

        self.label168 = QLabel(self.frame_fpga_compilation_options)
        self.label168.setObjectName(u"label168")

        self.formLayout1.setWidget(7, QFormLayout.ItemRole.FieldRole, self.label168)


        self.vboxLayout27.addLayout(self.formLayout1)


        self.verticalLayout_serial_eeprom_etc.addWidget(self.frame_fpga_compilation_options)

        self.frame_miscellaneous_settings = QFrame(self.page_hardware_information)
        self.frame_miscellaneous_settings.setObjectName(u"frame_miscellaneous_settings")
        self.frame_miscellaneous_settings.setMinimumSize(QSize(0, 0))
        self.vboxLayout28 = QVBoxLayout(self.frame_miscellaneous_settings)
        self.vboxLayout28.setObjectName(u"vboxLayout28")
        self.label169 = QLabel(self.frame_miscellaneous_settings)
        self.label169.setObjectName(u"label169")
        self.label169.setFont(font)

        self.vboxLayout28.addWidget(self.label169)

        self.formLayout2 = QFormLayout()
        self.formLayout2.setObjectName(u"formLayout2")
        self.formLayout2.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.label_microcontroller_firmware_version = QLabel(self.frame_miscellaneous_settings)
        self.label_microcontroller_firmware_version.setObjectName(u"label_microcontroller_firmware_version")

        self.formLayout2.setWidget(0, QFormLayout.ItemRole.FieldRole, self.label_microcontroller_firmware_version)

        self.label170 = QLabel(self.frame_miscellaneous_settings)
        self.label170.setObjectName(u"label170")

        self.formLayout2.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label170)

        self.label_fpga_firmware_version = QLabel(self.frame_miscellaneous_settings)
        self.label_fpga_firmware_version.setObjectName(u"label_fpga_firmware_version")

        self.formLayout2.setWidget(1, QFormLayout.ItemRole.FieldRole, self.label_fpga_firmware_version)

        self.label171 = QLabel(self.frame_miscellaneous_settings)
        self.label171.setObjectName(u"label171")

        self.formLayout2.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label171)

        self.label_ble_firmware_version = QLabel(self.frame_miscellaneous_settings)
        self.label_ble_firmware_version.setObjectName(u"label_ble_firmware_version")

        self.formLayout2.setWidget(2, QFormLayout.ItemRole.FieldRole, self.label_ble_firmware_version)

        self.label172 = QLabel(self.frame_miscellaneous_settings)
        self.label172.setObjectName(u"label172")

        self.formLayout2.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label172)

        self.label_microcontroller_serial_number = QLabel(self.frame_miscellaneous_settings)
        self.label_microcontroller_serial_number.setObjectName(u"label_microcontroller_serial_number")

        self.formLayout2.setWidget(3, QFormLayout.ItemRole.FieldRole, self.label_microcontroller_serial_number)

        self.label173 = QLabel(self.frame_miscellaneous_settings)
        self.label173.setObjectName(u"label173")

        self.formLayout2.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label173)

        self.label_detector_serial_number = QLabel(self.frame_miscellaneous_settings)
        self.label_detector_serial_number.setObjectName(u"label_detector_serial_number")

        self.formLayout2.setWidget(4, QFormLayout.ItemRole.FieldRole, self.label_detector_serial_number)

        self.label174 = QLabel(self.frame_miscellaneous_settings)
        self.label174.setObjectName(u"label174")

        self.formLayout2.setWidget(4, QFormLayout.ItemRole.LabelRole, self.label174)

        self.label_hw_view_battery_parsed = QLabel(self.frame_miscellaneous_settings)
        self.label_hw_view_battery_parsed.setObjectName(u"label_hw_view_battery_parsed")

        self.formLayout2.setWidget(7, QFormLayout.ItemRole.FieldRole, self.label_hw_view_battery_parsed)

        self.label_battery_static = QLabel(self.frame_miscellaneous_settings)
        self.label_battery_static.setObjectName(u"label_battery_static")

        self.formLayout2.setWidget(7, QFormLayout.ItemRole.LabelRole, self.label_battery_static)

        self.label_hw_view_power_connection_state = QLabel(self.frame_miscellaneous_settings)
        self.label_hw_view_power_connection_state.setObjectName(u"label_hw_view_power_connection_state")
        self.label_hw_view_power_connection_state.setWordWrap(False)

        self.formLayout2.setWidget(9, QFormLayout.ItemRole.FieldRole, self.label_hw_view_power_connection_state)

        self.label175 = QLabel(self.frame_miscellaneous_settings)
        self.label175.setObjectName(u"label175")

        self.formLayout2.setWidget(9, QFormLayout.ItemRole.LabelRole, self.label175)

        self.label_assembly_revision = QLabel(self.frame_miscellaneous_settings)
        self.label_assembly_revision.setObjectName(u"label_assembly_revision")
        self.label_assembly_revision.setWordWrap(False)

        self.formLayout2.setWidget(10, QFormLayout.ItemRole.FieldRole, self.label_assembly_revision)

        self.label176 = QLabel(self.frame_miscellaneous_settings)
        self.label176.setObjectName(u"label176")

        self.formLayout2.setWidget(10, QFormLayout.ItemRole.LabelRole, self.label176)


        self.vboxLayout28.addLayout(self.formLayout2)


        self.verticalLayout_serial_eeprom_etc.addWidget(self.frame_miscellaneous_settings)

        self.frame_python_settings = QFrame(self.page_hardware_information)
        self.frame_python_settings.setObjectName(u"frame_python_settings")
        self.vboxLayout29 = QVBoxLayout(self.frame_python_settings)
        self.vboxLayout29.setObjectName(u"vboxLayout29")
        self.label177 = QLabel(self.frame_python_settings)
        self.label177.setObjectName(u"label177")
        self.label177.setFont(font)

        self.vboxLayout29.addWidget(self.label177)

        self.formLayout3 = QFormLayout()
        self.formLayout3.setObjectName(u"formLayout3")
        self.formLayout3.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.label_python_version = QLabel(self.frame_python_settings)
        self.label_python_version.setObjectName(u"label_python_version")

        self.formLayout3.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_python_version)

        self.label178 = QLabel(self.frame_python_settings)
        self.label178.setObjectName(u"label178")

        self.formLayout3.setWidget(0, QFormLayout.ItemRole.FieldRole, self.label178)

        self.label_process_size_mb = QLabel(self.frame_python_settings)
        self.label_process_size_mb.setObjectName(u"label_process_size_mb")

        self.formLayout3.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_process_size_mb)

        self.label179 = QLabel(self.frame_python_settings)
        self.label179.setObjectName(u"label179")

        self.formLayout3.setWidget(1, QFormLayout.ItemRole.FieldRole, self.label179)

        self.label_process_growth_mb = QLabel(self.frame_python_settings)
        self.label_process_growth_mb.setObjectName(u"label_process_growth_mb")

        self.formLayout3.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_process_growth_mb)

        self.label180 = QLabel(self.frame_python_settings)
        self.label180.setObjectName(u"label180")

        self.formLayout3.setWidget(2, QFormLayout.ItemRole.FieldRole, self.label180)


        self.vboxLayout29.addLayout(self.formLayout3)


        self.verticalLayout_serial_eeprom_etc.addWidget(self.frame_python_settings)

        self.frame_hardware_setup_buttons = QFrame(self.page_hardware_information)
        self.frame_hardware_setup_buttons.setObjectName(u"frame_hardware_setup_buttons")
        self.frame_hardware_setup_buttons.setMinimumSize(QSize(0, 0))
        self.vboxLayout30 = QVBoxLayout(self.frame_hardware_setup_buttons)
        self.vboxLayout30.setObjectName(u"vboxLayout30")
        self.formLayout4 = QFormLayout()
        self.formLayout4.setObjectName(u"formLayout4")
        self.pushButton_save_ini = QPushButton(self.frame_hardware_setup_buttons)
        self.pushButton_save_ini.setObjectName(u"pushButton_save_ini")
        self.pushButton_save_ini.setMinimumSize(QSize(130, 30))

        self.formLayout4.setWidget(0, QFormLayout.ItemRole.LabelRole, self.pushButton_save_ini)

        self.label_save_ini_result = QLabel(self.frame_hardware_setup_buttons)
        self.label_save_ini_result.setObjectName(u"label_save_ini_result")

        self.formLayout4.setWidget(0, QFormLayout.ItemRole.FieldRole, self.label_save_ini_result)

        self.pushButton_admin_login = QPushButton(self.frame_hardware_setup_buttons)
        self.pushButton_admin_login.setObjectName(u"pushButton_admin_login")
        self.pushButton_admin_login.setMinimumSize(QSize(130, 30))
        self.pushButton_admin_login.setMaximumSize(QSize(130, 30))
        icon7 = QIcon()
        icon7.addFile(u":/greys/images/grey_icons/lock-active.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_admin_login.setIcon(icon7)

        self.formLayout4.setWidget(2, QFormLayout.ItemRole.LabelRole, self.pushButton_admin_login)

        self.pushButton_write_eeprom = QPushButton(self.frame_hardware_setup_buttons)
        self.pushButton_write_eeprom.setObjectName(u"pushButton_write_eeprom")
        self.pushButton_write_eeprom.setMinimumSize(QSize(130, 30))
        self.pushButton_write_eeprom.setProperty(u"initiallyVisible", False)

        self.formLayout4.setWidget(5, QFormLayout.ItemRole.LabelRole, self.pushButton_write_eeprom)

        self.pushButton_importEEPROM = QPushButton(self.frame_hardware_setup_buttons)
        self.pushButton_importEEPROM.setObjectName(u"pushButton_importEEPROM")
        sizePolicy8.setHeightForWidth(self.pushButton_importEEPROM.sizePolicy().hasHeightForWidth())
        self.pushButton_importEEPROM.setSizePolicy(sizePolicy8)
        self.pushButton_importEEPROM.setMinimumSize(QSize(130, 30))
        self.pushButton_importEEPROM.setProperty(u"initiallyVisible", False)

        self.formLayout4.setWidget(6, QFormLayout.ItemRole.LabelRole, self.pushButton_importEEPROM)

        self.pushButton_exportEEPROM = QPushButton(self.frame_hardware_setup_buttons)
        self.pushButton_exportEEPROM.setObjectName(u"pushButton_exportEEPROM")
        self.pushButton_exportEEPROM.setMinimumSize(QSize(130, 30))
        self.pushButton_exportEEPROM.setProperty(u"initiallyVisible", False)

        self.formLayout4.setWidget(8, QFormLayout.ItemRole.LabelRole, self.pushButton_exportEEPROM)

        self.pushButton_restore_eeprom = QPushButton(self.frame_hardware_setup_buttons)
        self.pushButton_restore_eeprom.setObjectName(u"pushButton_restore_eeprom")
        self.pushButton_restore_eeprom.setMinimumSize(QSize(130, 30))
        self.pushButton_restore_eeprom.setProperty(u"initiallyVisible", False)

        self.formLayout4.setWidget(4, QFormLayout.ItemRole.LabelRole, self.pushButton_restore_eeprom)

        self.pushButton_reset_fpga = QPushButton(self.frame_hardware_setup_buttons)
        self.pushButton_reset_fpga.setObjectName(u"pushButton_reset_fpga")
        self.pushButton_reset_fpga.setMinimumSize(QSize(130, 30))
        self.pushButton_reset_fpga.setProperty(u"initiallyVisible", False)

        self.formLayout4.setWidget(9, QFormLayout.ItemRole.LabelRole, self.pushButton_reset_fpga)


        self.vboxLayout30.addLayout(self.formLayout4)


        self.verticalLayout_serial_eeprom_etc.addWidget(self.frame_hardware_setup_buttons)


        self.hboxLayout2.addLayout(self.verticalLayout_serial_eeprom_etc)

        self.spacerItem3 = QSpacerItem(20, 550, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.hboxLayout2.addItem(self.spacerItem3)

        self.tabWidget_advanced_features = QTabWidget(self.page_hardware_information)
        self.tabWidget_advanced_features.setObjectName(u"tabWidget_advanced_features")
        self.tabWidget_advanced_features.setProperty(u"initiallyVisible", False)
        self.tab_manufacturing = QWidget()
        self.tab_manufacturing.setObjectName(u"tab_manufacturing")
        self.vboxLayout31 = QVBoxLayout(self.tab_manufacturing)
        self.vboxLayout31.setObjectName(u"vboxLayout31")
        self.label181 = QLabel(self.tab_manufacturing)
        self.label181.setObjectName(u"label181")

        self.vboxLayout31.addWidget(self.label181)

        self.frame1 = QFrame(self.tab_manufacturing)
        self.frame1.setObjectName(u"frame1")
        self.frame1.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame1.setFrameShadow(QFrame.Shadow.Raised)
        self.frame1.setProperty(u"wpBox", False)
        self.vboxLayout32 = QVBoxLayout(self.frame1)
        self.vboxLayout32.setSpacing(0)
        self.vboxLayout32.setObjectName(u"vboxLayout32")
        self.vboxLayout32.setContentsMargins(0, 0, 0, 0)
        self.frame2 = QFrame(self.frame1)
        self.frame2.setObjectName(u"frame2")
        self.frame2.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame2.setFrameShadow(QFrame.Shadow.Raised)
        self.frame2.setProperty(u"wpGrad", False)
        self.hboxLayout4 = QHBoxLayout(self.frame2)
        self.hboxLayout4.setObjectName(u"hboxLayout4")
        self.pushButton_mfg_dfu = QPushButton(self.frame2)
        self.pushButton_mfg_dfu.setObjectName(u"pushButton_mfg_dfu")
        self.pushButton_mfg_dfu.setMinimumSize(QSize(130, 30))

        self.hboxLayout4.addWidget(self.pushButton_mfg_dfu)

        self.checkBox_diagnostic_mode = QCheckBox(self.frame2)
        self.checkBox_diagnostic_mode.setObjectName(u"checkBox_diagnostic_mode")

        self.hboxLayout4.addWidget(self.checkBox_diagnostic_mode)

        self.spacerItem4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.hboxLayout4.addItem(self.spacerItem4)


        self.vboxLayout32.addWidget(self.frame2)


        self.vboxLayout31.addWidget(self.frame1)

        self.spacerItem5 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.vboxLayout31.addItem(self.spacerItem5)

        self.tabWidget_advanced_features.addTab(self.tab_manufacturing, "")
        self.tab_oem = QWidget()
        self.tab_oem.setObjectName(u"tab_oem")
        self.vboxLayout33 = QVBoxLayout(self.tab_oem)
        self.vboxLayout33.setObjectName(u"vboxLayout33")
        self.label182 = QLabel(self.tab_oem)
        self.label182.setObjectName(u"label182")

        self.vboxLayout33.addWidget(self.label182)

        self.frame_oem_post_processing_white = QFrame(self.tab_oem)
        self.frame_oem_post_processing_white.setObjectName(u"frame_oem_post_processing_white")
        self.frame_oem_post_processing_white.setProperty(u"wpBox", False)
        self.vboxLayout34 = QVBoxLayout(self.frame_oem_post_processing_white)
        self.vboxLayout34.setSpacing(0)
        self.vboxLayout34.setObjectName(u"vboxLayout34")
        self.vboxLayout34.setContentsMargins(0, 0, 0, 0)
        self.frame_oem_post_processing_black = QFrame(self.frame_oem_post_processing_white)
        self.frame_oem_post_processing_black.setObjectName(u"frame_oem_post_processing_black")
        self.frame_oem_post_processing_black.setProperty(u"wpGrad", False)
        self.vboxLayout35 = QVBoxLayout(self.frame_oem_post_processing_black)
        self.vboxLayout35.setObjectName(u"vboxLayout35")
        self.checkBox_graph_alternating_pixels = QCheckBox(self.frame_oem_post_processing_black)
        self.checkBox_graph_alternating_pixels.setObjectName(u"checkBox_graph_alternating_pixels")

        self.vboxLayout35.addWidget(self.checkBox_graph_alternating_pixels)

        self.checkBox_swap_alternating_pixels = QCheckBox(self.frame_oem_post_processing_black)
        self.checkBox_swap_alternating_pixels.setObjectName(u"checkBox_swap_alternating_pixels")

        self.vboxLayout35.addWidget(self.checkBox_swap_alternating_pixels)


        self.vboxLayout34.addWidget(self.frame_oem_post_processing_black)


        self.vboxLayout33.addWidget(self.frame_oem_post_processing_white)

        self.spacerItem6 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.vboxLayout33.addItem(self.spacerItem6)

        self.tabWidget_advanced_features.addTab(self.tab_oem, "")

        self.hboxLayout2.addWidget(self.tabWidget_advanced_features)

        self.spacerItem7 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.hboxLayout2.addItem(self.spacerItem7)

        self.scrollArea_hardware.setWidget(self.page_hardware_information)
        self.stackedWidget_low.addWidget(self.scrollArea_hardware)
        self.page_factory = QWidget()
        self.page_factory.setObjectName(u"page_factory")
        sizePolicy6.setHeightForWidth(self.page_factory.sizePolicy().hasHeightForWidth())
        self.page_factory.setSizePolicy(sizePolicy6)
        self.hboxLayout5 = QHBoxLayout(self.page_factory)
        self.hboxLayout5.setSpacing(0)
        self.hboxLayout5.setObjectName(u"hboxLayout5")
        self.hboxLayout5.setContentsMargins(0, 0, 0, 0)
        self.frame_hardware_capture_middle = QFrame(self.page_factory)
        self.frame_hardware_capture_middle.setObjectName(u"frame_hardware_capture_middle")
        self.frame_hardware_capture_middle.setMinimumSize(QSize(400, 0))
        self.frame_hardware_capture_middle.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_hardware_capture_middle.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_hardware_capture_middle.setLineWidth(1)
        self.gridLayout2 = QGridLayout(self.frame_hardware_capture_middle)
        self.gridLayout2.setSpacing(0)
        self.gridLayout2.setObjectName(u"gridLayout2")
        self.gridLayout2.setContentsMargins(0, 0, 0, 0)
        self.frame_hardware_capture_middle_nest = QFrame(self.frame_hardware_capture_middle)
        self.frame_hardware_capture_middle_nest.setObjectName(u"frame_hardware_capture_middle_nest")
        self.frame_hardware_capture_middle_nest.setMinimumSize(QSize(400, 0))
        self.frame_hardware_capture_middle_nest.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_hardware_capture_middle_nest.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_hardware_capture_middle_nest.setLineWidth(1)
        self.vboxLayout36 = QVBoxLayout(self.frame_hardware_capture_middle_nest)
        self.vboxLayout36.setObjectName(u"vboxLayout36")
        self.scrollArea = QScrollArea(self.frame_hardware_capture_middle_nest)
        self.scrollArea.setObjectName(u"scrollArea")
        sizePolicy10 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        sizePolicy10.setHorizontalStretch(0)
        sizePolicy10.setVerticalStretch(0)
        sizePolicy10.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())
        self.scrollArea.setSizePolicy(sizePolicy10)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scrollArea.setWidgetResizable(True)
        self.widget = QWidget()
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(QRect(0, 0, 421, 1502))
        self.verticalLayout = QVBoxLayout(self.widget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.stackedWidget_hardware_capture_details_spectrum = QStackedWidget(self.widget)
        self.stackedWidget_hardware_capture_details_spectrum.setObjectName(u"stackedWidget_hardware_capture_details_spectrum")
        sizePolicy10.setHeightForWidth(self.stackedWidget_hardware_capture_details_spectrum.sizePolicy().hasHeightForWidth())
        self.stackedWidget_hardware_capture_details_spectrum.setSizePolicy(sizePolicy10)
        self.stackedWidget_hardware_capture_details_spectrum.setStyleSheet(u"")
        self.page_hardware_capture_details_spectrum = QWidget()
        self.page_hardware_capture_details_spectrum.setObjectName(u"page_hardware_capture_details_spectrum")
        self.vboxLayout37 = QVBoxLayout(self.page_hardware_capture_details_spectrum)
        self.vboxLayout37.setObjectName(u"vboxLayout37")
        self.frame_area_scan_image = QFrame(self.page_hardware_capture_details_spectrum)
        self.frame_area_scan_image.setObjectName(u"frame_area_scan_image")
        sizePolicy11 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy11.setHorizontalStretch(0)
        sizePolicy11.setVerticalStretch(0)
        sizePolicy11.setHeightForWidth(self.frame_area_scan_image.sizePolicy().hasHeightForWidth())
        self.frame_area_scan_image.setSizePolicy(sizePolicy11)
        self.frame_area_scan_image.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_area_scan_image.setFrameShadow(QFrame.Shadow.Raised)
        self.hboxLayout6 = QHBoxLayout(self.frame_area_scan_image)
        self.hboxLayout6.setObjectName(u"hboxLayout6")
        self.layout_area_scan_image = QHBoxLayout()
        self.layout_area_scan_image.setSpacing(0)
        self.layout_area_scan_image.setObjectName(u"layout_area_scan_image")
        self.graphicsView_area_scan = QGraphicsView(self.frame_area_scan_image)
        self.graphicsView_area_scan.setObjectName(u"graphicsView_area_scan")
        sizePolicy12 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy12.setHorizontalStretch(1)
        sizePolicy12.setVerticalStretch(5)
        sizePolicy12.setHeightForWidth(self.graphicsView_area_scan.sizePolicy().hasHeightForWidth())
        self.graphicsView_area_scan.setSizePolicy(sizePolicy12)
        self.graphicsView_area_scan.setInteractive(True)
        self.graphicsView_area_scan.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        self.layout_area_scan_image.addWidget(self.graphicsView_area_scan)


        self.hboxLayout6.addLayout(self.layout_area_scan_image)


        self.vboxLayout37.addWidget(self.frame_area_scan_image)

        self.frame_area_scan_live = QFrame(self.page_hardware_capture_details_spectrum)
        self.frame_area_scan_live.setObjectName(u"frame_area_scan_live")
        sizePolicy11.setHeightForWidth(self.frame_area_scan_live.sizePolicy().hasHeightForWidth())
        self.frame_area_scan_live.setSizePolicy(sizePolicy11)
        self.frame_area_scan_live.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_area_scan_live.setFrameShadow(QFrame.Shadow.Raised)
        self.hboxLayout7 = QHBoxLayout(self.frame_area_scan_live)
        self.hboxLayout7.setObjectName(u"hboxLayout7")
        self.layout_area_scan_live = QHBoxLayout()
        self.layout_area_scan_live.setObjectName(u"layout_area_scan_live")

        self.hboxLayout7.addLayout(self.layout_area_scan_live)


        self.vboxLayout37.addWidget(self.frame_area_scan_live)

        self.progressBar_area_scan = QProgressBar(self.page_hardware_capture_details_spectrum)
        self.progressBar_area_scan.setObjectName(u"progressBar_area_scan")
        sizePolicy11.setHeightForWidth(self.progressBar_area_scan.sizePolicy().hasHeightForWidth())
        self.progressBar_area_scan.setSizePolicy(sizePolicy11)
        self.progressBar_area_scan.setMinimumSize(QSize(0, 14))
        self.progressBar_area_scan.setMaximumSize(QSize(16777215, 14))
        self.progressBar_area_scan.setValue(24)

        self.vboxLayout37.addWidget(self.progressBar_area_scan)

        self.layout_strip_charts = QVBoxLayout()
        self.layout_strip_charts.setObjectName(u"layout_strip_charts")

        self.vboxLayout37.addLayout(self.layout_strip_charts)

        self.stackedWidget_hardware_capture_details_spectrum.addWidget(self.page_hardware_capture_details_spectrum)

        self.verticalLayout.addWidget(self.stackedWidget_hardware_capture_details_spectrum)

        self.scrollArea.setWidget(self.widget)

        self.vboxLayout36.addWidget(self.scrollArea)

        self.frame_hardware_capture_details_nest = QFrame(self.frame_hardware_capture_middle_nest)
        self.frame_hardware_capture_details_nest.setObjectName(u"frame_hardware_capture_details_nest")
        self.frame_hardware_capture_details_nest.setMinimumSize(QSize(0, 0))
        self.frame_hardware_capture_details_nest.setMaximumSize(QSize(16777215, 16777215))
        self.frame_hardware_capture_details_nest.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_hardware_capture_details_nest.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_hardware_capture_details_nest.setLineWidth(1)
        self.vboxLayout38 = QVBoxLayout(self.frame_hardware_capture_details_nest)
        self.vboxLayout38.setSpacing(0)
        self.vboxLayout38.setObjectName(u"vboxLayout38")
        self.vboxLayout38.setContentsMargins(0, 0, 0, 0)
        self.frame_hardware_capture_details_nest_over = QFrame(self.frame_hardware_capture_details_nest)
        self.frame_hardware_capture_details_nest_over.setObjectName(u"frame_hardware_capture_details_nest_over")
        self.frame_hardware_capture_details_nest_over.setStyleSheet(u"")
        self.frame_hardware_capture_details_nest_over.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_hardware_capture_details_nest_over.setFrameShadow(QFrame.Shadow.Raised)
        self.hboxLayout8 = QHBoxLayout(self.frame_hardware_capture_details_nest_over)
        self.hboxLayout8.setSpacing(0)
        self.hboxLayout8.setObjectName(u"hboxLayout8")
        self.hboxLayout8.setContentsMargins(0, 0, 0, 0)

        self.vboxLayout38.addWidget(self.frame_hardware_capture_details_nest_over)


        self.vboxLayout36.addWidget(self.frame_hardware_capture_details_nest)


        self.gridLayout2.addWidget(self.frame_hardware_capture_middle_nest, 0, 1, 1, 1)


        self.hboxLayout5.addWidget(self.frame_hardware_capture_middle)

        self.stackedWidget_low.addWidget(self.page_factory)
        self.page_settings = QWidget()
        self.page_settings.setObjectName(u"page_settings")
        sizePolicy6.setHeightForWidth(self.page_settings.sizePolicy().hasHeightForWidth())
        self.page_settings.setSizePolicy(sizePolicy6)
        self.hboxLayout9 = QHBoxLayout(self.page_settings)
        self.hboxLayout9.setSpacing(0)
        self.hboxLayout9.setObjectName(u"hboxLayout9")
        self.hboxLayout9.setContentsMargins(0, 0, 0, 0)
        self.scrollArea_scope_setup_options = QScrollArea(self.page_settings)
        self.scrollArea_scope_setup_options.setObjectName(u"scrollArea_scope_setup_options")
        sizePolicy13 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy13.setHorizontalStretch(0)
        sizePolicy13.setVerticalStretch(0)
        sizePolicy13.setHeightForWidth(self.scrollArea_scope_setup_options.sizePolicy().hasHeightForWidth())
        self.scrollArea_scope_setup_options.setSizePolicy(sizePolicy13)
        self.scrollArea_scope_setup_options.setWidgetResizable(True)
        self.scrollAreaWidgetContents_scope_setup_options = QWidget()
        self.scrollAreaWidgetContents_scope_setup_options.setObjectName(u"scrollAreaWidgetContents_scope_setup_options")
        self.scrollAreaWidgetContents_scope_setup_options.setGeometry(QRect(0, 0, 580, 1444))
        sizePolicy7.setHeightForWidth(self.scrollAreaWidgetContents_scope_setup_options.sizePolicy().hasHeightForWidth())
        self.scrollAreaWidgetContents_scope_setup_options.setSizePolicy(sizePolicy7)
        self.vboxLayout39 = QVBoxLayout(self.scrollAreaWidgetContents_scope_setup_options)
        self.vboxLayout39.setSpacing(0)
        self.vboxLayout39.setObjectName(u"vboxLayout39")
        self.vboxLayout39.setContentsMargins(0, 0, 0, 0)
        self.frame_scope_setup_options = QFrame(self.scrollAreaWidgetContents_scope_setup_options)
        self.frame_scope_setup_options.setObjectName(u"frame_scope_setup_options")
        self.frame_scope_setup_options.setMaximumSize(QSize(16777215, 16777215))
        self.hboxLayout10 = QHBoxLayout(self.frame_scope_setup_options)
        self.hboxLayout10.setSpacing(0)
        self.hboxLayout10.setObjectName(u"hboxLayout10")
        self.hboxLayout10.setContentsMargins(0, 0, 0, 0)
        self.frame_scopeSetup_left = QFrame(self.frame_scope_setup_options)
        self.frame_scopeSetup_left.setObjectName(u"frame_scopeSetup_left")
        sizePolicy13.setHeightForWidth(self.frame_scopeSetup_left.sizePolicy().hasHeightForWidth())
        self.frame_scopeSetup_left.setSizePolicy(sizePolicy13)
        self.frame_scopeSetup_left.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_scopeSetup_left.setFrameShadow(QFrame.Shadow.Raised)
        self.vboxLayout40 = QVBoxLayout(self.frame_scopeSetup_left)
        self.vboxLayout40.setObjectName(u"vboxLayout40")
        self.frame_scopeSetup_saveLocation_white = QFrame(self.frame_scopeSetup_left)
        self.frame_scopeSetup_saveLocation_white.setObjectName(u"frame_scopeSetup_saveLocation_white")
        self.frame_scopeSetup_saveLocation_white.setProperty(u"wpBox", False)
        self.vboxLayout41 = QVBoxLayout(self.frame_scopeSetup_saveLocation_white)
        self.vboxLayout41.setSpacing(0)
        self.vboxLayout41.setObjectName(u"vboxLayout41")
        self.vboxLayout41.setContentsMargins(0, 0, 0, 0)
        self.frame_saveOptions_location_black = QFrame(self.frame_scopeSetup_saveLocation_white)
        self.frame_saveOptions_location_black.setObjectName(u"frame_saveOptions_location_black")
        self.frame_saveOptions_location_black.setProperty(u"wpPanel", False)
        self.vboxLayout42 = QVBoxLayout(self.frame_saveOptions_location_black)
        self.vboxLayout42.setObjectName(u"vboxLayout42")
        self.label_rssd_timestamp_69 = QLabel(self.frame_saveOptions_location_black)
        self.label_rssd_timestamp_69.setObjectName(u"label_rssd_timestamp_69")
        sizePolicy.setHeightForWidth(self.label_rssd_timestamp_69.sizePolicy().hasHeightForWidth())
        self.label_rssd_timestamp_69.setSizePolicy(sizePolicy)
        self.label_rssd_timestamp_69.setFont(font)

        self.vboxLayout42.addWidget(self.label_rssd_timestamp_69)

        self.hboxLayout11 = QHBoxLayout()
        self.hboxLayout11.setObjectName(u"hboxLayout11")
        self.hboxLayout11.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self.spacerItem8 = QSpacerItem(20, 28, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.hboxLayout11.addItem(self.spacerItem8)

        self.vboxLayout43 = QVBoxLayout()
        self.vboxLayout43.setSpacing(3)
        self.vboxLayout43.setObjectName(u"vboxLayout43")
        self.formLayout5 = QFormLayout()
        self.formLayout5.setObjectName(u"formLayout5")
        self.formLayout5.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self.formLayout5.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.formLayout5.setHorizontalSpacing(0)
        self.formLayout5.setVerticalSpacing(0)
        self.label183 = QLabel(self.frame_saveOptions_location_black)
        self.label183.setObjectName(u"label183")

        self.formLayout5.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label183)

        self.hboxLayout12 = QHBoxLayout()
        self.hboxLayout12.setObjectName(u"hboxLayout12")
        self.label_scope_setup_save_location = QLabel(self.frame_saveOptions_location_black)
        self.label_scope_setup_save_location.setObjectName(u"label_scope_setup_save_location")

        self.hboxLayout12.addWidget(self.label_scope_setup_save_location)

        self.pushButton_scope_setup_change_save_location = QPushButton(self.frame_saveOptions_location_black)
        self.pushButton_scope_setup_change_save_location.setObjectName(u"pushButton_scope_setup_change_save_location")
        sizePolicy14 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy14.setHorizontalStretch(0)
        sizePolicy14.setVerticalStretch(0)
        sizePolicy14.setHeightForWidth(self.pushButton_scope_setup_change_save_location.sizePolicy().hasHeightForWidth())
        self.pushButton_scope_setup_change_save_location.setSizePolicy(sizePolicy14)
        self.pushButton_scope_setup_change_save_location.setMinimumSize(QSize(20, 20))
        self.pushButton_scope_setup_change_save_location.setMaximumSize(QSize(100, 100))
        self.pushButton_scope_setup_change_save_location.setFont(font)
        self.pushButton_scope_setup_change_save_location.setIconSize(QSize(40, 40))

        self.hboxLayout12.addWidget(self.pushButton_scope_setup_change_save_location)


        self.formLayout5.setLayout(0, QFormLayout.ItemRole.FieldRole, self.hboxLayout12)

        self.lineEdit_save_filename_template = QLineEdit(self.frame_saveOptions_location_black)
        self.lineEdit_save_filename_template.setObjectName(u"lineEdit_save_filename_template")
        self.lineEdit_save_filename_template.setMaximumSize(QSize(300, 16777215))

        self.formLayout5.setWidget(1, QFormLayout.ItemRole.FieldRole, self.lineEdit_save_filename_template)

        self.lineEdit_save_label_template = QLineEdit(self.frame_saveOptions_location_black)
        self.lineEdit_save_label_template.setObjectName(u"lineEdit_save_label_template")
        self.lineEdit_save_label_template.setMaximumSize(QSize(300, 16777215))

        self.formLayout5.setWidget(2, QFormLayout.ItemRole.FieldRole, self.lineEdit_save_label_template)

        self.label_foo_baz = QLabel(self.frame_saveOptions_location_black)
        self.label_foo_baz.setObjectName(u"label_foo_baz")

        self.formLayout5.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_foo_baz)

        self.label_foo_baz2 = QLabel(self.frame_saveOptions_location_black)
        self.label_foo_baz2.setObjectName(u"label_foo_baz2")

        self.formLayout5.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_foo_baz2)


        self.vboxLayout43.addLayout(self.formLayout5)

        self.checkBox_save_filename_as_label = QCheckBox(self.frame_saveOptions_location_black)
        self.checkBox_save_filename_as_label.setObjectName(u"checkBox_save_filename_as_label")

        self.vboxLayout43.addWidget(self.checkBox_save_filename_as_label)

        self.checkBox_load_raw = QCheckBox(self.frame_saveOptions_location_black)
        self.checkBox_load_raw.setObjectName(u"checkBox_load_raw")

        self.vboxLayout43.addWidget(self.checkBox_load_raw)


        self.hboxLayout11.addLayout(self.vboxLayout43)


        self.vboxLayout42.addLayout(self.hboxLayout11)


        self.vboxLayout41.addWidget(self.frame_saveOptions_location_black)


        self.vboxLayout40.addWidget(self.frame_scopeSetup_saveLocation_white)

        self.frame_scopeSetup_saveOptions_white = QFrame(self.frame_scopeSetup_left)
        self.frame_scopeSetup_saveOptions_white.setObjectName(u"frame_scopeSetup_saveOptions_white")
        self.frame_scopeSetup_saveOptions_white.setMinimumSize(QSize(475, 0))
        self.frame_scopeSetup_saveOptions_white.setProperty(u"wpBox", False)
        self.vboxLayout44 = QVBoxLayout(self.frame_scopeSetup_saveOptions_white)
        self.vboxLayout44.setSpacing(0)
        self.vboxLayout44.setObjectName(u"vboxLayout44")
        self.vboxLayout44.setContentsMargins(0, 0, 0, 0)
        self.frame_scopeSetup_saveOptions_black = QFrame(self.frame_scopeSetup_saveOptions_white)
        self.frame_scopeSetup_saveOptions_black.setObjectName(u"frame_scopeSetup_saveOptions_black")
        self.frame_scopeSetup_saveOptions_black.setProperty(u"wpPanel", False)
        self.vboxLayout45 = QVBoxLayout(self.frame_scopeSetup_saveOptions_black)
        self.vboxLayout45.setObjectName(u"vboxLayout45")
        self.label_Saved_Data_Options = QLabel(self.frame_scopeSetup_saveOptions_black)
        self.label_Saved_Data_Options.setObjectName(u"label_Saved_Data_Options")
        sizePolicy.setHeightForWidth(self.label_Saved_Data_Options.sizePolicy().hasHeightForWidth())
        self.label_Saved_Data_Options.setSizePolicy(sizePolicy)
        self.label_Saved_Data_Options.setFont(font)

        self.vboxLayout45.addWidget(self.label_Saved_Data_Options)

        self.horizontalLayout_scopeSetup_saveOptions_indent = QHBoxLayout()
        self.horizontalLayout_scopeSetup_saveOptions_indent.setSpacing(0)
        self.horizontalLayout_scopeSetup_saveOptions_indent.setObjectName(u"horizontalLayout_scopeSetup_saveOptions_indent")
        self.horizontalLayout_scopeSetup_saveOptions_indent.setContentsMargins(0, 0, 0, 0)
        self.spacerItem9 = QSpacerItem(20, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_scopeSetup_saveOptions_indent.addItem(self.spacerItem9)

        self.verticalLayout_scopeSetup_saveOptions_stack = QVBoxLayout()
        self.verticalLayout_scopeSetup_saveOptions_stack.setSpacing(0)
        self.verticalLayout_scopeSetup_saveOptions_stack.setObjectName(u"verticalLayout_scopeSetup_saveOptions_stack")
        self.gridLayout_saveOptions_fileFormats = QGridLayout()
        self.gridLayout_saveOptions_fileFormats.setSpacing(0)
        self.gridLayout_saveOptions_fileFormats.setObjectName(u"gridLayout_saveOptions_fileFormats")
        self.gridLayout_saveOptions_fileFormats.setContentsMargins(0, 0, 0, 0)
        self.label184 = QLabel(self.frame_scopeSetup_saveOptions_black)
        self.label184.setObjectName(u"label184")

        self.gridLayout_saveOptions_fileFormats.addWidget(self.label184, 0, 0, 1, 1)

        self.label185 = QLabel(self.frame_scopeSetup_saveOptions_black)
        self.label185.setObjectName(u"label185")

        self.gridLayout_saveOptions_fileFormats.addWidget(self.label185, 0, 2, 1, 1)

        self.checkBox_save_csv = QCheckBox(self.frame_scopeSetup_saveOptions_black)
        self.checkBox_save_csv.setObjectName(u"checkBox_save_csv")
        self.checkBox_save_csv.setChecked(True)

        self.gridLayout_saveOptions_fileFormats.addWidget(self.checkBox_save_csv, 1, 0, 1, 1)

        self.groupBox_csv_direction = QGroupBox(self.frame_scopeSetup_saveOptions_black)
        self.groupBox_csv_direction.setObjectName(u"groupBox_csv_direction")
        self.groupBox_csv_direction.setStyleSheet(u"margin: 0;")
        self.hboxLayout13 = QHBoxLayout(self.groupBox_csv_direction)
        self.hboxLayout13.setSpacing(0)
        self.hboxLayout13.setObjectName(u"hboxLayout13")
        self.hboxLayout13.setContentsMargins(0, 0, 0, 0)
        self.radioButton_save_by_row = QRadioButton(self.groupBox_csv_direction)
        self.radioButton_save_by_row.setObjectName(u"radioButton_save_by_row")
        self.radioButton_save_by_row.setChecked(False)

        self.hboxLayout13.addWidget(self.radioButton_save_by_row)

        self.radioButton_save_by_column = QRadioButton(self.groupBox_csv_direction)
        self.radioButton_save_by_column.setObjectName(u"radioButton_save_by_column")
        self.radioButton_save_by_column.setChecked(True)

        self.hboxLayout13.addWidget(self.radioButton_save_by_column)


        self.gridLayout_saveOptions_fileFormats.addWidget(self.groupBox_csv_direction, 1, 1, 1, 1)

        self.checkBox_save_pixel = QCheckBox(self.frame_scopeSetup_saveOptions_black)
        self.checkBox_save_pixel.setObjectName(u"checkBox_save_pixel")
        self.checkBox_save_pixel.setChecked(False)

        self.gridLayout_saveOptions_fileFormats.addWidget(self.checkBox_save_pixel, 1, 2, 1, 1)

        self.checkBox_save_raw = QCheckBox(self.frame_scopeSetup_saveOptions_black)
        self.checkBox_save_raw.setObjectName(u"checkBox_save_raw")
        self.checkBox_save_raw.setChecked(False)

        self.gridLayout_saveOptions_fileFormats.addWidget(self.checkBox_save_raw, 1, 3, 1, 1)

        self.checkBox_save_excel = QCheckBox(self.frame_scopeSetup_saveOptions_black)
        self.checkBox_save_excel.setObjectName(u"checkBox_save_excel")
        self.checkBox_save_excel.setStyleSheet(u"")
        self.checkBox_save_excel.setChecked(False)

        self.gridLayout_saveOptions_fileFormats.addWidget(self.checkBox_save_excel, 2, 0, 1, 1)

        self.checkBox_save_data_append = QCheckBox(self.frame_scopeSetup_saveOptions_black)
        self.checkBox_save_data_append.setObjectName(u"checkBox_save_data_append")

        self.gridLayout_saveOptions_fileFormats.addWidget(self.checkBox_save_data_append, 2, 1, 1, 1)

        self.checkBox_save_wavelength = QCheckBox(self.frame_scopeSetup_saveOptions_black)
        self.checkBox_save_wavelength.setObjectName(u"checkBox_save_wavelength")
        self.checkBox_save_wavelength.setChecked(True)

        self.gridLayout_saveOptions_fileFormats.addWidget(self.checkBox_save_wavelength, 2, 2, 1, 1)

        self.checkBox_save_dark = QCheckBox(self.frame_scopeSetup_saveOptions_black)
        self.checkBox_save_dark.setObjectName(u"checkBox_save_dark")
        self.checkBox_save_dark.setChecked(False)

        self.gridLayout_saveOptions_fileFormats.addWidget(self.checkBox_save_dark, 2, 3, 1, 1)

        self.checkBox_save_text = QCheckBox(self.frame_scopeSetup_saveOptions_black)
        self.checkBox_save_text.setObjectName(u"checkBox_save_text")

        self.gridLayout_saveOptions_fileFormats.addWidget(self.checkBox_save_text, 3, 0, 1, 1)

        self.checkBox_save_wavenumber = QCheckBox(self.frame_scopeSetup_saveOptions_black)
        self.checkBox_save_wavenumber.setObjectName(u"checkBox_save_wavenumber")
        self.checkBox_save_wavenumber.setChecked(False)

        self.gridLayout_saveOptions_fileFormats.addWidget(self.checkBox_save_wavenumber, 3, 2, 1, 1)

        self.checkBox_save_reference = QCheckBox(self.frame_scopeSetup_saveOptions_black)
        self.checkBox_save_reference.setObjectName(u"checkBox_save_reference")
        self.checkBox_save_reference.setChecked(False)

        self.gridLayout_saveOptions_fileFormats.addWidget(self.checkBox_save_reference, 3, 3, 1, 1)

        self.checkBox_save_spc = QCheckBox(self.frame_scopeSetup_saveOptions_black)
        self.checkBox_save_spc.setObjectName(u"checkBox_save_spc")

        self.gridLayout_saveOptions_fileFormats.addWidget(self.checkBox_save_spc, 4, 0, 1, 1)

        self.checkBox_save_json = QCheckBox(self.frame_scopeSetup_saveOptions_black)
        self.checkBox_save_json.setObjectName(u"checkBox_save_json")

        self.gridLayout_saveOptions_fileFormats.addWidget(self.checkBox_save_json, 5, 0, 1, 1)

        self.checkBox_save_cloud = QCheckBox(self.frame_scopeSetup_saveOptions_black)
        self.checkBox_save_cloud.setObjectName(u"checkBox_save_cloud")
        self.checkBox_save_cloud.setEnabled(False)

        self.gridLayout_saveOptions_fileFormats.addWidget(self.checkBox_save_cloud, 5, 1, 1, 1)

        self.checkBox_save_dx = QCheckBox(self.frame_scopeSetup_saveOptions_black)
        self.checkBox_save_dx.setObjectName(u"checkBox_save_dx")

        self.gridLayout_saveOptions_fileFormats.addWidget(self.checkBox_save_dx, 6, 0, 1, 1)

        self.checkBox_save_all = QCheckBox(self.frame_scopeSetup_saveOptions_black)
        self.checkBox_save_all.setObjectName(u"checkBox_save_all")

        self.gridLayout_saveOptions_fileFormats.addWidget(self.checkBox_save_all, 7, 0, 1, 1)

        self.checkBox_allow_rename_files = QCheckBox(self.frame_scopeSetup_saveOptions_black)
        self.checkBox_allow_rename_files.setObjectName(u"checkBox_allow_rename_files")
        self.checkBox_allow_rename_files.setChecked(True)

        self.gridLayout_saveOptions_fileFormats.addWidget(self.checkBox_allow_rename_files, 7, 1, 1, 1)

        self.checkBox_save_collated = QCheckBox(self.frame_scopeSetup_saveOptions_black)
        self.checkBox_save_collated.setObjectName(u"checkBox_save_collated")
        self.checkBox_save_collated.setChecked(True)

        self.gridLayout_saveOptions_fileFormats.addWidget(self.checkBox_save_collated, 8, 0, 1, 1)


        self.verticalLayout_scopeSetup_saveOptions_stack.addLayout(self.gridLayout_saveOptions_fileFormats)


        self.horizontalLayout_scopeSetup_saveOptions_indent.addLayout(self.verticalLayout_scopeSetup_saveOptions_stack)

        self.spacerItem10 = QSpacerItem(5, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_scopeSetup_saveOptions_indent.addItem(self.spacerItem10)


        self.vboxLayout45.addLayout(self.horizontalLayout_scopeSetup_saveOptions_indent)


        self.vboxLayout44.addWidget(self.frame_scopeSetup_saveOptions_black)


        self.vboxLayout40.addWidget(self.frame_scopeSetup_saveOptions_white)

        self.frame_interpolation_white = QFrame(self.frame_scopeSetup_left)
        self.frame_interpolation_white.setObjectName(u"frame_interpolation_white")
        sizePolicy15 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        sizePolicy15.setHorizontalStretch(0)
        sizePolicy15.setVerticalStretch(0)
        sizePolicy15.setHeightForWidth(self.frame_interpolation_white.sizePolicy().hasHeightForWidth())
        self.frame_interpolation_white.setSizePolicy(sizePolicy15)
        self.frame_interpolation_white.setProperty(u"wpBox", False)
        self.vboxLayout46 = QVBoxLayout(self.frame_interpolation_white)
        self.vboxLayout46.setSpacing(0)
        self.vboxLayout46.setObjectName(u"vboxLayout46")
        self.vboxLayout46.setContentsMargins(0, 0, 0, 0)
        self.frame_interpolation_black = QFrame(self.frame_interpolation_white)
        self.frame_interpolation_black.setObjectName(u"frame_interpolation_black")
        sizePolicy15.setHeightForWidth(self.frame_interpolation_black.sizePolicy().hasHeightForWidth())
        self.frame_interpolation_black.setSizePolicy(sizePolicy15)
        self.frame_interpolation_black.setProperty(u"wpPanel", False)
        self.vboxLayout47 = QVBoxLayout(self.frame_interpolation_black)
        self.vboxLayout47.setObjectName(u"vboxLayout47")
        self.label_interpolation_title = QLabel(self.frame_interpolation_black)
        self.label_interpolation_title.setObjectName(u"label_interpolation_title")
        sizePolicy.setHeightForWidth(self.label_interpolation_title.sizePolicy().hasHeightForWidth())
        self.label_interpolation_title.setSizePolicy(sizePolicy)
        self.label_interpolation_title.setFont(font)

        self.vboxLayout47.addWidget(self.label_interpolation_title)

        self.hboxLayout14 = QHBoxLayout()
        self.hboxLayout14.setObjectName(u"hboxLayout14")
        self.spacerItem11 = QSpacerItem(20, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.hboxLayout14.addItem(self.spacerItem11)

        self.gridLayout3 = QGridLayout()
        self.gridLayout3.setSpacing(0)
        self.gridLayout3.setObjectName(u"gridLayout3")
        self.gridLayout3.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self.checkBox_save_interpolation_enabled = QCheckBox(self.frame_interpolation_black)
        self.checkBox_save_interpolation_enabled.setObjectName(u"checkBox_save_interpolation_enabled")

        self.gridLayout3.addWidget(self.checkBox_save_interpolation_enabled, 0, 0, 1, 1)

        self.label186 = QLabel(self.frame_interpolation_black)
        self.label186.setObjectName(u"label186")

        self.gridLayout3.addWidget(self.label186, 0, 1, 1, 1)

        self.doubleSpinBox_save_interpolation_start = QDoubleSpinBox(self.frame_interpolation_black)
        self.doubleSpinBox_save_interpolation_start.setObjectName(u"doubleSpinBox_save_interpolation_start")
        sizePolicy8.setHeightForWidth(self.doubleSpinBox_save_interpolation_start.sizePolicy().hasHeightForWidth())
        self.doubleSpinBox_save_interpolation_start.setSizePolicy(sizePolicy8)
        self.doubleSpinBox_save_interpolation_start.setMinimumSize(QSize(125, 0))
        self.doubleSpinBox_save_interpolation_start.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.doubleSpinBox_save_interpolation_start.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.doubleSpinBox_save_interpolation_start.setMinimum(-9999.000000000000000)
        self.doubleSpinBox_save_interpolation_start.setMaximum(9999.000000000000000)
        self.doubleSpinBox_save_interpolation_start.setValue(400.000000000000000)

        self.gridLayout3.addWidget(self.doubleSpinBox_save_interpolation_start, 0, 2, 1, 1)

        self.radioButton_save_interpolation_wavelength = QRadioButton(self.frame_interpolation_black)
        self.radioButton_save_interpolation_wavelength.setObjectName(u"radioButton_save_interpolation_wavelength")
        self.radioButton_save_interpolation_wavelength.setChecked(False)

        self.gridLayout3.addWidget(self.radioButton_save_interpolation_wavelength, 1, 0, 1, 1)

        self.label187 = QLabel(self.frame_interpolation_black)
        self.label187.setObjectName(u"label187")

        self.gridLayout3.addWidget(self.label187, 1, 1, 1, 1)

        self.doubleSpinBox_save_interpolation_end = QDoubleSpinBox(self.frame_interpolation_black)
        self.doubleSpinBox_save_interpolation_end.setObjectName(u"doubleSpinBox_save_interpolation_end")
        sizePolicy8.setHeightForWidth(self.doubleSpinBox_save_interpolation_end.sizePolicy().hasHeightForWidth())
        self.doubleSpinBox_save_interpolation_end.setSizePolicy(sizePolicy8)
        self.doubleSpinBox_save_interpolation_end.setMinimumSize(QSize(125, 0))
        self.doubleSpinBox_save_interpolation_end.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.doubleSpinBox_save_interpolation_end.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.doubleSpinBox_save_interpolation_end.setAccelerated(True)
        self.doubleSpinBox_save_interpolation_end.setKeyboardTracking(False)
        self.doubleSpinBox_save_interpolation_end.setMinimum(-9999.000000000000000)
        self.doubleSpinBox_save_interpolation_end.setMaximum(9999.000000000000000)
        self.doubleSpinBox_save_interpolation_end.setValue(2400.000000000000000)

        self.gridLayout3.addWidget(self.doubleSpinBox_save_interpolation_end, 1, 2, 1, 1)

        self.radioButton_save_interpolation_wavenumber = QRadioButton(self.frame_interpolation_black)
        self.radioButton_save_interpolation_wavenumber.setObjectName(u"radioButton_save_interpolation_wavenumber")
        self.radioButton_save_interpolation_wavenumber.setChecked(True)

        self.gridLayout3.addWidget(self.radioButton_save_interpolation_wavenumber, 2, 0, 1, 1)

        self.label188 = QLabel(self.frame_interpolation_black)
        self.label188.setObjectName(u"label188")

        self.gridLayout3.addWidget(self.label188, 2, 1, 1, 1)

        self.doubleSpinBox_save_interpolation_incr = QDoubleSpinBox(self.frame_interpolation_black)
        self.doubleSpinBox_save_interpolation_incr.setObjectName(u"doubleSpinBox_save_interpolation_incr")
        sizePolicy8.setHeightForWidth(self.doubleSpinBox_save_interpolation_incr.sizePolicy().hasHeightForWidth())
        self.doubleSpinBox_save_interpolation_incr.setSizePolicy(sizePolicy8)
        self.doubleSpinBox_save_interpolation_incr.setMinimumSize(QSize(125, 0))
        self.doubleSpinBox_save_interpolation_incr.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.doubleSpinBox_save_interpolation_incr.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.doubleSpinBox_save_interpolation_incr.setMinimum(0.100000000000000)
        self.doubleSpinBox_save_interpolation_incr.setMaximum(100.000000000000000)
        self.doubleSpinBox_save_interpolation_incr.setValue(1.000000000000000)

        self.gridLayout3.addWidget(self.doubleSpinBox_save_interpolation_incr, 2, 2, 1, 1)

        self.gridLayout3.setColumnMinimumWidth(0, 100)
        self.gridLayout3.setColumnMinimumWidth(1, 100)
        self.gridLayout3.setColumnMinimumWidth(2, 100)

        self.hboxLayout14.addLayout(self.gridLayout3)

        self.spacerItem12 = QSpacerItem(5, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.hboxLayout14.addItem(self.spacerItem12)


        self.vboxLayout47.addLayout(self.hboxLayout14)


        self.vboxLayout46.addWidget(self.frame_interpolation_black)


        self.vboxLayout40.addWidget(self.frame_interpolation_white)

        self.frame_ramanCorrection_white = QFrame(self.frame_scopeSetup_left)
        self.frame_ramanCorrection_white.setObjectName(u"frame_ramanCorrection_white")
        self.frame_ramanCorrection_white.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_ramanCorrection_white.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_ramanCorrection_white.setProperty(u"wpBox", False)
        self.hboxLayout15 = QHBoxLayout(self.frame_ramanCorrection_white)
        self.hboxLayout15.setSpacing(6)
        self.hboxLayout15.setObjectName(u"hboxLayout15")
        self.hboxLayout15.setContentsMargins(1, 1, 1, 1)
        self.frame_ramanCorrection_dark = QFrame(self.frame_ramanCorrection_white)
        self.frame_ramanCorrection_dark.setObjectName(u"frame_ramanCorrection_dark")
        self.frame_ramanCorrection_dark.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_ramanCorrection_dark.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_ramanCorrection_dark.setProperty(u"wpPanel", False)
        self.vboxLayout48 = QVBoxLayout(self.frame_ramanCorrection_dark)
        self.vboxLayout48.setObjectName(u"vboxLayout48")
        self.label189 = QLabel(self.frame_ramanCorrection_dark)
        self.label189.setObjectName(u"label189")
        sizePolicy.setHeightForWidth(self.label189.sizePolicy().hasHeightForWidth())
        self.label189.setSizePolicy(sizePolicy)
        self.label189.setFont(font)

        self.vboxLayout48.addWidget(self.label189)

        self.hboxLayout16 = QHBoxLayout()
        self.hboxLayout16.setObjectName(u"hboxLayout16")
        self.spacerItem13 = QSpacerItem(20, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.hboxLayout16.addItem(self.spacerItem13)

        self.gridLayout4 = QGridLayout()
        self.gridLayout4.setObjectName(u"gridLayout4")
        self.label190 = QLabel(self.frame_ramanCorrection_dark)
        self.label190.setObjectName(u"label190")

        self.gridLayout4.addWidget(self.label190, 0, 0, 1, 1)

        self.spacerItem14 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout4.addItem(self.spacerItem14, 0, 2, 1, 1)

        self.comboBox_ramanCorrection_compoundName = QComboBox(self.frame_ramanCorrection_dark)
        self.comboBox_ramanCorrection_compoundName.setObjectName(u"comboBox_ramanCorrection_compoundName")
        self.comboBox_ramanCorrection_compoundName.setMinimumSize(QSize(200, 0))
        self.comboBox_ramanCorrection_compoundName.setFont(font)
        self.comboBox_ramanCorrection_compoundName.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.gridLayout4.addWidget(self.comboBox_ramanCorrection_compoundName, 0, 1, 1, 1)

        self.checkBox_ramanCorrection_visible = QCheckBox(self.frame_ramanCorrection_dark)
        self.checkBox_ramanCorrection_visible.setObjectName(u"checkBox_ramanCorrection_visible")

        self.gridLayout4.addWidget(self.checkBox_ramanCorrection_visible, 1, 0, 1, 1)


        self.hboxLayout16.addLayout(self.gridLayout4)


        self.vboxLayout48.addLayout(self.hboxLayout16)


        self.hboxLayout15.addWidget(self.frame_ramanCorrection_dark)


        self.vboxLayout40.addWidget(self.frame_ramanCorrection_white)

        self.frame_BatchCollection_white = QFrame(self.frame_scopeSetup_left)
        self.frame_BatchCollection_white.setObjectName(u"frame_BatchCollection_white")
        self.frame_BatchCollection_white.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_BatchCollection_white.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_BatchCollection_white.setProperty(u"wpBox", False)
        self.vboxLayout49 = QVBoxLayout(self.frame_BatchCollection_white)
        self.vboxLayout49.setSpacing(0)
        self.vboxLayout49.setObjectName(u"vboxLayout49")
        self.vboxLayout49.setContentsMargins(0, 0, 0, 0)
        self.frame_BatchCollection_black = QFrame(self.frame_BatchCollection_white)
        self.frame_BatchCollection_black.setObjectName(u"frame_BatchCollection_black")
        self.frame_BatchCollection_black.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_BatchCollection_black.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_BatchCollection_black.setProperty(u"wpPanel", False)
        self.vboxLayout50 = QVBoxLayout(self.frame_BatchCollection_black)
        self.vboxLayout50.setObjectName(u"vboxLayout50")
        self.label_BatchCollection_title = QLabel(self.frame_BatchCollection_black)
        self.label_BatchCollection_title.setObjectName(u"label_BatchCollection_title")
        sizePolicy.setHeightForWidth(self.label_BatchCollection_title.sizePolicy().hasHeightForWidth())
        self.label_BatchCollection_title.setSizePolicy(sizePolicy)
        self.label_BatchCollection_title.setFont(font)

        self.vboxLayout50.addWidget(self.label_BatchCollection_title)

        self.hboxLayout17 = QHBoxLayout()
        self.hboxLayout17.setObjectName(u"hboxLayout17")
        self.spacerItem15 = QSpacerItem(20, 10, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.hboxLayout17.addItem(self.spacerItem15)

        self.hboxLayout18 = QHBoxLayout()
        self.hboxLayout18.setObjectName(u"hboxLayout18")
        self.vboxLayout51 = QVBoxLayout()
        self.vboxLayout51.setSpacing(3)
        self.vboxLayout51.setObjectName(u"vboxLayout51")
        self.hboxLayout19 = QHBoxLayout()
        self.hboxLayout19.setObjectName(u"hboxLayout19")
        self.checkBox_BatchCollection_enabled = QCheckBox(self.frame_BatchCollection_black)
        self.checkBox_BatchCollection_enabled.setObjectName(u"checkBox_BatchCollection_enabled")
        sizePolicy9.setHeightForWidth(self.checkBox_BatchCollection_enabled.sizePolicy().hasHeightForWidth())
        self.checkBox_BatchCollection_enabled.setSizePolicy(sizePolicy9)
        self.checkBox_BatchCollection_enabled.setMinimumSize(QSize(30, 0))
        self.checkBox_BatchCollection_enabled.setMaximumSize(QSize(1677215, 16777215))
        self.checkBox_BatchCollection_enabled.setChecked(False)

        self.hboxLayout19.addWidget(self.checkBox_BatchCollection_enabled)

        self.label_BatchCollection_explain = QLabel(self.frame_BatchCollection_black)
        self.label_BatchCollection_explain.setObjectName(u"label_BatchCollection_explain")
        self.label_BatchCollection_explain.setStyleSheet(u"color: #999;")
        self.label_BatchCollection_explain.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.hboxLayout19.addWidget(self.label_BatchCollection_explain)


        self.vboxLayout51.addLayout(self.hboxLayout19)

        self.formLayout6 = QFormLayout()
        self.formLayout6.setObjectName(u"formLayout6")
        self.formLayout6.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.formLayout6.setVerticalSpacing(0)
        self.label191 = QLabel(self.frame_BatchCollection_black)
        self.label191.setObjectName(u"label191")

        self.formLayout6.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label191)

        self.spinBox_BatchCollection_measurement_count = QSpinBox(self.frame_BatchCollection_black)
        self.spinBox_BatchCollection_measurement_count.setObjectName(u"spinBox_BatchCollection_measurement_count")
        self.spinBox_BatchCollection_measurement_count.setMinimumSize(QSize(125, 0))
        self.spinBox_BatchCollection_measurement_count.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.spinBox_BatchCollection_measurement_count.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_BatchCollection_measurement_count.setAccelerated(True)
        self.spinBox_BatchCollection_measurement_count.setKeyboardTracking(False)
        self.spinBox_BatchCollection_measurement_count.setMinimum(1)
        self.spinBox_BatchCollection_measurement_count.setMaximum(99999)
        self.spinBox_BatchCollection_measurement_count.setValue(5)

        self.formLayout6.setWidget(0, QFormLayout.ItemRole.FieldRole, self.spinBox_BatchCollection_measurement_count)

        self.label192 = QLabel(self.frame_BatchCollection_black)
        self.label192.setObjectName(u"label192")

        self.formLayout6.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label192)

        self.spinBox_BatchCollection_measurement_period_ms = QSpinBox(self.frame_BatchCollection_black)
        self.spinBox_BatchCollection_measurement_period_ms.setObjectName(u"spinBox_BatchCollection_measurement_period_ms")
        self.spinBox_BatchCollection_measurement_period_ms.setMinimumSize(QSize(125, 0))
        self.spinBox_BatchCollection_measurement_period_ms.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.spinBox_BatchCollection_measurement_period_ms.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_BatchCollection_measurement_period_ms.setAccelerated(True)
        self.spinBox_BatchCollection_measurement_period_ms.setKeyboardTracking(False)
        self.spinBox_BatchCollection_measurement_period_ms.setMinimum(0)
        self.spinBox_BatchCollection_measurement_period_ms.setMaximum(3600000)
        self.spinBox_BatchCollection_measurement_period_ms.setSingleStep(100)
        self.spinBox_BatchCollection_measurement_period_ms.setValue(1000)

        self.formLayout6.setWidget(1, QFormLayout.ItemRole.FieldRole, self.spinBox_BatchCollection_measurement_period_ms)

        self.spacerItem16 = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.formLayout6.setItem(2, QFormLayout.ItemRole.LabelRole, self.spacerItem16)

        self.label193 = QLabel(self.frame_BatchCollection_black)
        self.label193.setObjectName(u"label193")

        self.formLayout6.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label193)

        self.spinBox_BatchCollection_batch_count = QSpinBox(self.frame_BatchCollection_black)
        self.spinBox_BatchCollection_batch_count.setObjectName(u"spinBox_BatchCollection_batch_count")
        self.spinBox_BatchCollection_batch_count.setMinimumSize(QSize(125, 0))
        self.spinBox_BatchCollection_batch_count.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.spinBox_BatchCollection_batch_count.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_BatchCollection_batch_count.setMaximum(9999)
        self.spinBox_BatchCollection_batch_count.setValue(1)

        self.formLayout6.setWidget(3, QFormLayout.ItemRole.FieldRole, self.spinBox_BatchCollection_batch_count)

        self.label194 = QLabel(self.frame_BatchCollection_black)
        self.label194.setObjectName(u"label194")

        self.formLayout6.setWidget(4, QFormLayout.ItemRole.LabelRole, self.label194)

        self.spinBox_BatchCollection_batch_period_sec = QSpinBox(self.frame_BatchCollection_black)
        self.spinBox_BatchCollection_batch_period_sec.setObjectName(u"spinBox_BatchCollection_batch_period_sec")
        self.spinBox_BatchCollection_batch_period_sec.setMinimumSize(QSize(125, 0))
        self.spinBox_BatchCollection_batch_period_sec.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.spinBox_BatchCollection_batch_period_sec.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_BatchCollection_batch_period_sec.setAccelerated(True)
        self.spinBox_BatchCollection_batch_period_sec.setKeyboardTracking(False)
        self.spinBox_BatchCollection_batch_period_sec.setMaximum(3600)
        self.spinBox_BatchCollection_batch_period_sec.setSingleStep(1)
        self.spinBox_BatchCollection_batch_period_sec.setValue(0)

        self.formLayout6.setWidget(4, QFormLayout.ItemRole.FieldRole, self.spinBox_BatchCollection_batch_period_sec)

        self.spacerItem17 = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.formLayout6.setItem(5, QFormLayout.ItemRole.LabelRole, self.spacerItem17)

        self.label195 = QLabel(self.frame_BatchCollection_black)
        self.label195.setObjectName(u"label195")

        self.formLayout6.setWidget(6, QFormLayout.ItemRole.LabelRole, self.label195)

        self.spinBox_BatchCollection_collection_timeout = QSpinBox(self.frame_BatchCollection_black)
        self.spinBox_BatchCollection_collection_timeout.setObjectName(u"spinBox_BatchCollection_collection_timeout")
        self.spinBox_BatchCollection_collection_timeout.setMinimumSize(QSize(125, 0))
        self.spinBox_BatchCollection_collection_timeout.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.spinBox_BatchCollection_collection_timeout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_BatchCollection_collection_timeout.setAccelerated(True)
        self.spinBox_BatchCollection_collection_timeout.setKeyboardTracking(False)
        self.spinBox_BatchCollection_collection_timeout.setMaximum(3600)
        self.spinBox_BatchCollection_collection_timeout.setSingleStep(1)
        self.spinBox_BatchCollection_collection_timeout.setValue(0)

        self.formLayout6.setWidget(6, QFormLayout.ItemRole.FieldRole, self.spinBox_BatchCollection_collection_timeout)


        self.vboxLayout51.addLayout(self.formLayout6)

        self.checkBox_BatchCollection_clear_before_batch = QCheckBox(self.frame_BatchCollection_black)
        self.checkBox_BatchCollection_clear_before_batch.setObjectName(u"checkBox_BatchCollection_clear_before_batch")
        self.checkBox_BatchCollection_clear_before_batch.setChecked(True)

        self.vboxLayout51.addWidget(self.checkBox_BatchCollection_clear_before_batch)

        self.checkBox_BatchCollection_export_after_batch = QCheckBox(self.frame_BatchCollection_black)
        self.checkBox_BatchCollection_export_after_batch.setObjectName(u"checkBox_BatchCollection_export_after_batch")
        self.checkBox_BatchCollection_export_after_batch.setChecked(True)

        self.vboxLayout51.addWidget(self.checkBox_BatchCollection_export_after_batch)

        self.checkBox_BatchCollection_dark_before_batch = QCheckBox(self.frame_BatchCollection_black)
        self.checkBox_BatchCollection_dark_before_batch.setObjectName(u"checkBox_BatchCollection_dark_before_batch")
        self.checkBox_BatchCollection_dark_before_batch.setChecked(True)

        self.vboxLayout51.addWidget(self.checkBox_BatchCollection_dark_before_batch)

        self.checkBox_BatchCollection_save_area_scan = QCheckBox(self.frame_BatchCollection_black)
        self.checkBox_BatchCollection_save_area_scan.setObjectName(u"checkBox_BatchCollection_save_area_scan")
        self.checkBox_BatchCollection_save_area_scan.setChecked(False)

        self.vboxLayout51.addWidget(self.checkBox_BatchCollection_save_area_scan)


        self.hboxLayout18.addLayout(self.vboxLayout51)

        self.spacerItem18 = QSpacerItem(40, 10, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.hboxLayout18.addItem(self.spacerItem18)

        self.vboxLayout52 = QVBoxLayout()
        self.vboxLayout52.setSpacing(0)
        self.vboxLayout52.setObjectName(u"vboxLayout52")
        self.groupBox_BatchCollection_laser_mode = QGroupBox(self.frame_BatchCollection_black)
        self.groupBox_BatchCollection_laser_mode.setObjectName(u"groupBox_BatchCollection_laser_mode")
        self.groupBox_BatchCollection_laser_mode.setStyleSheet(u"")
        self.groupBox_BatchCollection_laser_mode.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)
        self.groupBox_BatchCollection_laser_mode.setFlat(False)
        self.groupBox_BatchCollection_laser_mode.setCheckable(False)
        self.vboxLayout53 = QVBoxLayout(self.groupBox_BatchCollection_laser_mode)
        self.vboxLayout53.setSpacing(0)
        self.vboxLayout53.setObjectName(u"vboxLayout53")
        self.vboxLayout53.setContentsMargins(0, 5, 0, 0)
        self.radioButton_BatchCollection_laser_manual = QRadioButton(self.groupBox_BatchCollection_laser_mode)
        self.radioButton_BatchCollection_laser_manual.setObjectName(u"radioButton_BatchCollection_laser_manual")
        self.radioButton_BatchCollection_laser_manual.setChecked(True)

        self.vboxLayout53.addWidget(self.radioButton_BatchCollection_laser_manual)

        self.radioButton_BatchCollection_laser_spectrum = QRadioButton(self.groupBox_BatchCollection_laser_mode)
        self.radioButton_BatchCollection_laser_spectrum.setObjectName(u"radioButton_BatchCollection_laser_spectrum")

        self.vboxLayout53.addWidget(self.radioButton_BatchCollection_laser_spectrum)

        self.radioButton_BatchCollection_laser_batch = QRadioButton(self.groupBox_BatchCollection_laser_mode)
        self.radioButton_BatchCollection_laser_batch.setObjectName(u"radioButton_BatchCollection_laser_batch")

        self.vboxLayout53.addWidget(self.radioButton_BatchCollection_laser_batch)

        self.radioButton_BatchCollection_laser_auto_raman = QRadioButton(self.groupBox_BatchCollection_laser_mode)
        self.radioButton_BatchCollection_laser_auto_raman.setObjectName(u"radioButton_BatchCollection_laser_auto_raman")

        self.vboxLayout53.addWidget(self.radioButton_BatchCollection_laser_auto_raman)


        self.vboxLayout52.addWidget(self.groupBox_BatchCollection_laser_mode)

        self.formLayout7 = QFormLayout()
        self.formLayout7.setObjectName(u"formLayout7")
        self.formLayout7.setVerticalSpacing(0)
        self.label196 = QLabel(self.frame_BatchCollection_black)
        self.label196.setObjectName(u"label196")

        self.formLayout7.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label196)

        self.spinBox_BatchCollection_laser_warmup_ms = QSpinBox(self.frame_BatchCollection_black)
        self.spinBox_BatchCollection_laser_warmup_ms.setObjectName(u"spinBox_BatchCollection_laser_warmup_ms")
        self.spinBox_BatchCollection_laser_warmup_ms.setMinimumSize(QSize(125, 0))
        self.spinBox_BatchCollection_laser_warmup_ms.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.spinBox_BatchCollection_laser_warmup_ms.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_BatchCollection_laser_warmup_ms.setMaximum(300000)
        self.spinBox_BatchCollection_laser_warmup_ms.setSingleStep(100)
        self.spinBox_BatchCollection_laser_warmup_ms.setValue(5000)

        self.formLayout7.setWidget(0, QFormLayout.ItemRole.FieldRole, self.spinBox_BatchCollection_laser_warmup_ms)


        self.vboxLayout52.addLayout(self.formLayout7)


        self.hboxLayout18.addLayout(self.vboxLayout52)


        self.hboxLayout17.addLayout(self.hboxLayout18)

        self.spacerItem19 = QSpacerItem(40, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.hboxLayout17.addItem(self.spacerItem19)


        self.vboxLayout50.addLayout(self.hboxLayout17)


        self.vboxLayout49.addWidget(self.frame_BatchCollection_black)


        self.vboxLayout40.addWidget(self.frame_BatchCollection_white)

        self.frame_CloudOptions_white = QFrame(self.frame_scopeSetup_left)
        self.frame_CloudOptions_white.setObjectName(u"frame_CloudOptions_white")
        self.frame_CloudOptions_white.setMinimumSize(QSize(0, 100))
        self.frame_CloudOptions_white.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_CloudOptions_white.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_CloudOptions_white.setProperty(u"wpBox", False)
        self.vboxLayout54 = QVBoxLayout(self.frame_CloudOptions_white)
        self.vboxLayout54.setSpacing(0)
        self.vboxLayout54.setObjectName(u"vboxLayout54")
        self.vboxLayout54.setContentsMargins(0, 0, 0, 0)
        self.frame_CloudOptions_black = QFrame(self.frame_CloudOptions_white)
        self.frame_CloudOptions_black.setObjectName(u"frame_CloudOptions_black")
        self.frame_CloudOptions_black.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_CloudOptions_black.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_CloudOptions_black.setProperty(u"wpPanel", False)
        self.vboxLayout55 = QVBoxLayout(self.frame_CloudOptions_black)
        self.vboxLayout55.setObjectName(u"vboxLayout55")
        self.label_BatchCollection_title_2 = QLabel(self.frame_CloudOptions_black)
        self.label_BatchCollection_title_2.setObjectName(u"label_BatchCollection_title_2")
        sizePolicy.setHeightForWidth(self.label_BatchCollection_title_2.sizePolicy().hasHeightForWidth())
        self.label_BatchCollection_title_2.setSizePolicy(sizePolicy)
        self.label_BatchCollection_title_2.setFont(font)

        self.vboxLayout55.addWidget(self.label_BatchCollection_title_2)

        self.hboxLayout20 = QHBoxLayout()
        self.hboxLayout20.setObjectName(u"hboxLayout20")
        self.spacerItem20 = QSpacerItem(20, 10, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.hboxLayout20.addItem(self.spacerItem20)

        self.gridLayout5 = QGridLayout()
        self.gridLayout5.setObjectName(u"gridLayout5")
        self.checkBox_cloud_config_download_enabled = QCheckBox(self.frame_CloudOptions_black)
        self.checkBox_cloud_config_download_enabled.setObjectName(u"checkBox_cloud_config_download_enabled")

        self.gridLayout5.addWidget(self.checkBox_cloud_config_download_enabled, 0, 0, 1, 1)


        self.hboxLayout20.addLayout(self.gridLayout5)


        self.vboxLayout55.addLayout(self.hboxLayout20)


        self.vboxLayout54.addWidget(self.frame_CloudOptions_black)


        self.vboxLayout40.addWidget(self.frame_CloudOptions_white)

        self.frame_Theme = QFrame(self.frame_scopeSetup_left)
        self.frame_Theme.setObjectName(u"frame_Theme")
        self.frame_Theme.setProperty(u"wpPanel", False)
        self.vboxLayout56 = QVBoxLayout(self.frame_Theme)
        self.vboxLayout56.setObjectName(u"vboxLayout56")
        self.label_Theme = QLabel(self.frame_Theme)
        self.label_Theme.setObjectName(u"label_Theme")
        sizePolicy.setHeightForWidth(self.label_Theme.sizePolicy().hasHeightForWidth())
        self.label_Theme.setSizePolicy(sizePolicy)
        self.label_Theme.setFont(font)

        self.vboxLayout56.addWidget(self.label_Theme)

        self.hboxLayout21 = QHBoxLayout()
        self.hboxLayout21.setObjectName(u"hboxLayout21")
        self.comboBox_Theme = QComboBox(self.frame_Theme)
        self.comboBox_Theme.setObjectName(u"comboBox_Theme")
        self.comboBox_Theme.setMinimumSize(QSize(150, 0))

        self.hboxLayout21.addWidget(self.comboBox_Theme)

        self.label197 = QLabel(self.frame_Theme)
        self.label197.setObjectName(u"label197")

        self.hboxLayout21.addWidget(self.label197)

        self.horizontalSpacer = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.hboxLayout21.addItem(self.horizontalSpacer)


        self.vboxLayout56.addLayout(self.hboxLayout21)

        self.checkBox_sound_enable = QCheckBox(self.frame_Theme)
        self.checkBox_sound_enable.setObjectName(u"checkBox_sound_enable")

        self.vboxLayout56.addWidget(self.checkBox_sound_enable)


        self.vboxLayout40.addWidget(self.frame_Theme)

        self.verticalSpacer = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.MinimumExpanding)

        self.vboxLayout40.addItem(self.verticalSpacer)


        self.hboxLayout10.addWidget(self.frame_scopeSetup_left)


        self.vboxLayout39.addWidget(self.frame_scope_setup_options)

        self.scrollArea_scope_setup_options.setWidget(self.scrollAreaWidgetContents_scope_setup_options)

        self.hboxLayout9.addWidget(self.scrollArea_scope_setup_options)

        self.frame_scopeSetup_spectra = QFrame(self.page_settings)
        self.frame_scopeSetup_spectra.setObjectName(u"frame_scopeSetup_spectra")
        sizePolicy13.setHeightForWidth(self.frame_scopeSetup_spectra.sizePolicy().hasHeightForWidth())
        self.frame_scopeSetup_spectra.setSizePolicy(sizePolicy13)
        self.frame_scopeSetup_spectra.setMaximumSize(QSize(500, 16777215))
        self.vboxLayout57 = QVBoxLayout(self.frame_scopeSetup_spectra)
        self.vboxLayout57.setSpacing(9)
        self.vboxLayout57.setObjectName(u"vboxLayout57")
        self.vboxLayout57.setContentsMargins(5, 0, 5, 0)
        self.frame_scopeSetup_spectra_live_white = QFrame(self.frame_scopeSetup_spectra)
        self.frame_scopeSetup_spectra_live_white.setObjectName(u"frame_scopeSetup_spectra_live_white")
        self.frame_scopeSetup_spectra_live_white.setMaximumSize(QSize(16777215, 500))
        self.frame_scopeSetup_spectra_live_white.setProperty(u"wpBox", False)
        self.hboxLayout22 = QHBoxLayout(self.frame_scopeSetup_spectra_live_white)
        self.hboxLayout22.setSpacing(0)
        self.hboxLayout22.setObjectName(u"hboxLayout22")
        self.hboxLayout22.setContentsMargins(0, 0, 0, 0)
        self.frame_scopeSetup_spectra_live_black = QFrame(self.frame_scopeSetup_spectra_live_white)
        self.frame_scopeSetup_spectra_live_black.setObjectName(u"frame_scopeSetup_spectra_live_black")
        self.frame_scopeSetup_spectra_live_black.setProperty(u"wpPanel", False)
        self.vboxLayout58 = QVBoxLayout(self.frame_scopeSetup_spectra_live_black)
        self.vboxLayout58.setObjectName(u"vboxLayout58")
        self.label_Live_Preview_Unprocessed = QLabel(self.frame_scopeSetup_spectra_live_black)
        self.label_Live_Preview_Unprocessed.setObjectName(u"label_Live_Preview_Unprocessed")
        self.label_Live_Preview_Unprocessed.setFont(font)

        self.vboxLayout58.addWidget(self.label_Live_Preview_Unprocessed)

        self.stackedWidget_scope_setup_live_spectrum = QStackedWidget(self.frame_scopeSetup_spectra_live_black)
        self.stackedWidget_scope_setup_live_spectrum.setObjectName(u"stackedWidget_scope_setup_live_spectrum")
        self.page_scope_setup_live = QWidget()
        self.page_scope_setup_live.setObjectName(u"page_scope_setup_live")
        self.stackedWidget_scope_setup_live_spectrum.addWidget(self.page_scope_setup_live)

        self.vboxLayout58.addWidget(self.stackedWidget_scope_setup_live_spectrum)

        self.hboxLayout23 = QHBoxLayout()
        self.hboxLayout23.setObjectName(u"hboxLayout23")
        self.pushButton_dark_store = QPushButton(self.frame_scopeSetup_spectra_live_black)
        self.pushButton_dark_store.setObjectName(u"pushButton_dark_store")
        sizePolicy9.setHeightForWidth(self.pushButton_dark_store.sizePolicy().hasHeightForWidth())
        self.pushButton_dark_store.setSizePolicy(sizePolicy9)
        self.pushButton_dark_store.setMinimumSize(QSize(140, 30))
        self.pushButton_dark_store.setMaximumSize(QSize(140, 30))
        self.pushButton_dark_store.setFont(font)
        icon8 = QIcon()
        icon8.addFile(u":/greys/images/grey_icons/bulb-dark.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_dark_store.setIcon(icon8)

        self.hboxLayout23.addWidget(self.pushButton_dark_store)

        self.pushButton_reference_store = QPushButton(self.frame_scopeSetup_spectra_live_black)
        self.pushButton_reference_store.setObjectName(u"pushButton_reference_store")
        sizePolicy9.setHeightForWidth(self.pushButton_reference_store.sizePolicy().hasHeightForWidth())
        self.pushButton_reference_store.setSizePolicy(sizePolicy9)
        self.pushButton_reference_store.setMinimumSize(QSize(160, 30))
        self.pushButton_reference_store.setMaximumSize(QSize(140, 30))
        self.pushButton_reference_store.setFont(font)
        icon9 = QIcon()
        icon9.addFile(u":/greys/images/grey_icons/bulb-light.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_reference_store.setIcon(icon9)

        self.hboxLayout23.addWidget(self.pushButton_reference_store)

        self.spacerItem21 = QSpacerItem(20, 5, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.hboxLayout23.addItem(self.spacerItem21)


        self.vboxLayout58.addLayout(self.hboxLayout23)


        self.hboxLayout22.addWidget(self.frame_scopeSetup_spectra_live_black)


        self.vboxLayout57.addWidget(self.frame_scopeSetup_spectra_live_white)

        self.frame_scopeSetup_spectra_dark_white = QFrame(self.frame_scopeSetup_spectra)
        self.frame_scopeSetup_spectra_dark_white.setObjectName(u"frame_scopeSetup_spectra_dark_white")
        self.frame_scopeSetup_spectra_dark_white.setMaximumSize(QSize(16777215, 500))
        self.frame_scopeSetup_spectra_dark_white.setProperty(u"wpBox", False)
        self.hboxLayout24 = QHBoxLayout(self.frame_scopeSetup_spectra_dark_white)
        self.hboxLayout24.setSpacing(0)
        self.hboxLayout24.setObjectName(u"hboxLayout24")
        self.hboxLayout24.setContentsMargins(0, 0, 0, 0)
        self.frame_scopeSetup_spectra_dark_black = QFrame(self.frame_scopeSetup_spectra_dark_white)
        self.frame_scopeSetup_spectra_dark_black.setObjectName(u"frame_scopeSetup_spectra_dark_black")
        self.frame_scopeSetup_spectra_dark_black.setProperty(u"wpPanel", False)
        self.vboxLayout59 = QVBoxLayout(self.frame_scopeSetup_spectra_dark_black)
        self.vboxLayout59.setObjectName(u"vboxLayout59")
        self.label_rsrd_label_header_3 = QLabel(self.frame_scopeSetup_spectra_dark_black)
        self.label_rsrd_label_header_3.setObjectName(u"label_rsrd_label_header_3")
        sizePolicy.setHeightForWidth(self.label_rsrd_label_header_3.sizePolicy().hasHeightForWidth())
        self.label_rsrd_label_header_3.setSizePolicy(sizePolicy)
        self.label_rsrd_label_header_3.setFont(font)

        self.vboxLayout59.addWidget(self.label_rsrd_label_header_3)

        self.stackedWidget_scope_setup_dark_spectrum = QStackedWidget(self.frame_scopeSetup_spectra_dark_black)
        self.stackedWidget_scope_setup_dark_spectrum.setObjectName(u"stackedWidget_scope_setup_dark_spectrum")
        sizePolicy13.setHeightForWidth(self.stackedWidget_scope_setup_dark_spectrum.sizePolicy().hasHeightForWidth())
        self.stackedWidget_scope_setup_dark_spectrum.setSizePolicy(sizePolicy13)
        self.page_scope_setup_recorded_dark = QWidget()
        self.page_scope_setup_recorded_dark.setObjectName(u"page_scope_setup_recorded_dark")
        self.stackedWidget_scope_setup_dark_spectrum.addWidget(self.page_scope_setup_recorded_dark)

        self.vboxLayout59.addWidget(self.stackedWidget_scope_setup_dark_spectrum)

        self.hboxLayout25 = QHBoxLayout()
        self.hboxLayout25.setObjectName(u"hboxLayout25")
        self.pushButton_dark_clear = QPushButton(self.frame_scopeSetup_spectra_dark_black)
        self.pushButton_dark_clear.setObjectName(u"pushButton_dark_clear")
        self.pushButton_dark_clear.setMinimumSize(QSize(80, 30))
        self.pushButton_dark_clear.setMaximumSize(QSize(80, 30))
        self.pushButton_dark_clear.setFont(font)
        self.pushButton_dark_clear.setIconSize(QSize(28, 28))

        self.hboxLayout25.addWidget(self.pushButton_dark_clear)

        self.pushButton_dark_load = QPushButton(self.frame_scopeSetup_spectra_dark_black)
        self.pushButton_dark_load.setObjectName(u"pushButton_dark_load")
        self.pushButton_dark_load.setMinimumSize(QSize(80, 30))
        self.pushButton_dark_load.setMaximumSize(QSize(80, 30))
        self.pushButton_dark_load.setFont(font)
        self.pushButton_dark_load.setIconSize(QSize(28, 28))

        self.hboxLayout25.addWidget(self.pushButton_dark_load)

        self.label_dark_timestamp = QLabel(self.frame_scopeSetup_spectra_dark_black)
        self.label_dark_timestamp.setObjectName(u"label_dark_timestamp")
        sizePolicy.setHeightForWidth(self.label_dark_timestamp.sizePolicy().hasHeightForWidth())
        self.label_dark_timestamp.setSizePolicy(sizePolicy)

        self.hboxLayout25.addWidget(self.label_dark_timestamp)


        self.vboxLayout59.addLayout(self.hboxLayout25)


        self.hboxLayout24.addWidget(self.frame_scopeSetup_spectra_dark_black)


        self.vboxLayout57.addWidget(self.frame_scopeSetup_spectra_dark_white)

        self.frame_scopeSetup_spectra_reference_white = QFrame(self.frame_scopeSetup_spectra)
        self.frame_scopeSetup_spectra_reference_white.setObjectName(u"frame_scopeSetup_spectra_reference_white")
        self.frame_scopeSetup_spectra_reference_white.setMaximumSize(QSize(16777215, 500))
        self.frame_scopeSetup_spectra_reference_white.setProperty(u"wpBox", False)
        self.hboxLayout26 = QHBoxLayout(self.frame_scopeSetup_spectra_reference_white)
        self.hboxLayout26.setSpacing(0)
        self.hboxLayout26.setObjectName(u"hboxLayout26")
        self.hboxLayout26.setContentsMargins(0, 0, 0, 0)
        self.frame_scopeSetup_spectra_reference_black = QFrame(self.frame_scopeSetup_spectra_reference_white)
        self.frame_scopeSetup_spectra_reference_black.setObjectName(u"frame_scopeSetup_spectra_reference_black")
        self.frame_scopeSetup_spectra_reference_black.setProperty(u"wpPanel", False)
        self.vboxLayout60 = QVBoxLayout(self.frame_scopeSetup_spectra_reference_black)
        self.vboxLayout60.setObjectName(u"vboxLayout60")
        self.label_tsrl_label_header_3 = QLabel(self.frame_scopeSetup_spectra_reference_black)
        self.label_tsrl_label_header_3.setObjectName(u"label_tsrl_label_header_3")
        self.label_tsrl_label_header_3.setFont(font)

        self.vboxLayout60.addWidget(self.label_tsrl_label_header_3)

        self.stackedWidget_scope_setup_reference_spectrum = QStackedWidget(self.frame_scopeSetup_spectra_reference_black)
        self.stackedWidget_scope_setup_reference_spectrum.setObjectName(u"stackedWidget_scope_setup_reference_spectrum")
        self.page_rsrd_design_3 = QWidget()
        self.page_rsrd_design_3.setObjectName(u"page_rsrd_design_3")
        self.stackedWidget_scope_setup_reference_spectrum.addWidget(self.page_rsrd_design_3)

        self.vboxLayout60.addWidget(self.stackedWidget_scope_setup_reference_spectrum)

        self.hboxLayout27 = QHBoxLayout()
        self.hboxLayout27.setObjectName(u"hboxLayout27")
        self.pushButton_reference_clear = QPushButton(self.frame_scopeSetup_spectra_reference_black)
        self.pushButton_reference_clear.setObjectName(u"pushButton_reference_clear")
        sizePolicy8.setHeightForWidth(self.pushButton_reference_clear.sizePolicy().hasHeightForWidth())
        self.pushButton_reference_clear.setSizePolicy(sizePolicy8)
        self.pushButton_reference_clear.setMinimumSize(QSize(80, 30))
        self.pushButton_reference_clear.setMaximumSize(QSize(80, 30))
        self.pushButton_reference_clear.setFont(font)
        self.pushButton_reference_clear.setIconSize(QSize(28, 28))

        self.hboxLayout27.addWidget(self.pushButton_reference_clear)

        self.pushButton_reference_load = QPushButton(self.frame_scopeSetup_spectra_reference_black)
        self.pushButton_reference_load.setObjectName(u"pushButton_reference_load")
        self.pushButton_reference_load.setMinimumSize(QSize(80, 30))
        self.pushButton_reference_load.setMaximumSize(QSize(80, 30))
        self.pushButton_reference_load.setFont(font)
        self.pushButton_reference_load.setIconSize(QSize(28, 28))

        self.hboxLayout27.addWidget(self.pushButton_reference_load)

        self.label_reference_timestamp = QLabel(self.frame_scopeSetup_spectra_reference_black)
        self.label_reference_timestamp.setObjectName(u"label_reference_timestamp")

        self.hboxLayout27.addWidget(self.label_reference_timestamp)


        self.vboxLayout60.addLayout(self.hboxLayout27)


        self.hboxLayout26.addWidget(self.frame_scopeSetup_spectra_reference_black)


        self.vboxLayout57.addWidget(self.frame_scopeSetup_spectra_reference_white)

        self.verticalSpacer_moveLower = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.vboxLayout57.addItem(self.verticalSpacer_moveLower)


        self.hboxLayout9.addWidget(self.frame_scopeSetup_spectra)

        self.stackedWidget_low.addWidget(self.page_settings)
        self.page_scope = QWidget()
        self.page_scope.setObjectName(u"page_scope")
        sizePolicy6.setHeightForWidth(self.page_scope.sizePolicy().hasHeightForWidth())
        self.page_scope.setSizePolicy(sizePolicy6)
        self.verticalLayout_new_splitter = QVBoxLayout(self.page_scope)
        self.verticalLayout_new_splitter.setSpacing(0)
        self.verticalLayout_new_splitter.setObjectName(u"verticalLayout_new_splitter")
        self.verticalLayout_new_splitter.setContentsMargins(0, 0, 0, 0)
        self.splitter_saves_vs_graph = QSplitter(self.page_scope)
        self.splitter_saves_vs_graph.setObjectName(u"splitter_saves_vs_graph")
        sizePolicy16 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy16.setHorizontalStretch(0)
        sizePolicy16.setVerticalStretch(0)
        sizePolicy16.setHeightForWidth(self.splitter_saves_vs_graph.sizePolicy().hasHeightForWidth())
        self.splitter_saves_vs_graph.setSizePolicy(sizePolicy16)
        self.splitter_saves_vs_graph.setOrientation(Qt.Orientation.Horizontal)
        self.splitter_saves_vs_graph.setHandleWidth(5)
        self.frame_new_save_col_holder = QFrame(self.splitter_saves_vs_graph)
        self.frame_new_save_col_holder.setObjectName(u"frame_new_save_col_holder")
        sizePolicy17 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy17.setHorizontalStretch(5)
        sizePolicy17.setVerticalStretch(0)
        sizePolicy17.setHeightForWidth(self.frame_new_save_col_holder.sizePolicy().hasHeightForWidth())
        self.frame_new_save_col_holder.setSizePolicy(sizePolicy17)
        self.frame_new_save_col_holder.setMaximumSize(QSize(260, 16777215))
        self.verticalLayout_save_column = QVBoxLayout(self.frame_new_save_col_holder)
        self.verticalLayout_save_column.setSpacing(0)
        self.verticalLayout_save_column.setObjectName(u"verticalLayout_save_column")
        self.verticalLayout_save_column.setContentsMargins(0, 0, 0, 0)
        self.scrollArea_save_column = QScrollArea(self.frame_new_save_col_holder)
        self.scrollArea_save_column.setObjectName(u"scrollArea_save_column")
        sizePolicy6.setHeightForWidth(self.scrollArea_save_column.sizePolicy().hasHeightForWidth())
        self.scrollArea_save_column.setSizePolicy(sizePolicy6)
        self.scrollArea_save_column.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scrollArea_save_column.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.scrollArea_save_column.setWidgetResizable(True)
        self.scrollArea_save_column.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 197, 774))
        sizePolicy16.setHeightForWidth(self.scrollAreaWidgetContents.sizePolicy().hasHeightForWidth())
        self.scrollAreaWidgetContents.setSizePolicy(sizePolicy16)
        self.vboxLayout61 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.vboxLayout61.setSpacing(6)
        self.vboxLayout61.setObjectName(u"vboxLayout61")
        self.vboxLayout61.setContentsMargins(0, 0, 0, 0)
        self.frame_clipboard = QFrame(self.scrollAreaWidgetContents)
        self.frame_clipboard.setObjectName(u"frame_clipboard")
        sizePolicy16.setHeightForWidth(self.frame_clipboard.sizePolicy().hasHeightForWidth())
        self.frame_clipboard.setSizePolicy(sizePolicy16)
        self.frame_clipboard.setMaximumSize(QSize(16777215, 16777215))
        self.frame_clipboard.setProperty(u"wpBox", False)
        self.vboxLayout62 = QVBoxLayout(self.frame_clipboard)
        self.vboxLayout62.setSpacing(0)
        self.vboxLayout62.setObjectName(u"vboxLayout62")
        self.vboxLayout62.setContentsMargins(0, 0, 0, 0)
        self.frame_scope_capture_nest = QFrame(self.frame_clipboard)
        self.frame_scope_capture_nest.setObjectName(u"frame_scope_capture_nest")
        sizePolicy16.setHeightForWidth(self.frame_scope_capture_nest.sizePolicy().hasHeightForWidth())
        self.frame_scope_capture_nest.setSizePolicy(sizePolicy16)
        self.frame_scope_capture_nest.setProperty(u"wpPanel", False)
        self.verticalLayout_scope_setup_left_nest_3 = QVBoxLayout(self.frame_scope_capture_nest)
        self.verticalLayout_scope_setup_left_nest_3.setSpacing(0)
        self.verticalLayout_scope_setup_left_nest_3.setObjectName(u"verticalLayout_scope_setup_left_nest_3")
        self.verticalLayout_scope_setup_left_nest_3.setContentsMargins(0, -1, 2, 5)
        self.hboxLayout28 = QHBoxLayout()
        self.hboxLayout28.setSpacing(3)
        self.hboxLayout28.setObjectName(u"hboxLayout28")
        self.label_scope_capture_save_title = QLabel(self.frame_scope_capture_nest)
        self.label_scope_capture_save_title.setObjectName(u"label_scope_capture_save_title")
        sizePolicy16.setHeightForWidth(self.label_scope_capture_save_title.sizePolicy().hasHeightForWidth())
        self.label_scope_capture_save_title.setSizePolicy(sizePolicy16)
        self.label_scope_capture_save_title.setMaximumSize(QSize(16777215, 20))
        font2 = QFont()
        font2.setBold(True)
        self.label_scope_capture_save_title.setFont(font2)
        self.label_scope_capture_save_title.setScaledContents(True)
        self.label_scope_capture_save_title.setWordWrap(False)

        self.hboxLayout28.addWidget(self.label_scope_capture_save_title)

        self.spacerItem22 = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.hboxLayout28.addItem(self.spacerItem22)

        self.pushButton_erase_captures = QPushButton(self.frame_scope_capture_nest)
        self.pushButton_erase_captures.setObjectName(u"pushButton_erase_captures")
        sizePolicy1.setHeightForWidth(self.pushButton_erase_captures.sizePolicy().hasHeightForWidth())
        self.pushButton_erase_captures.setSizePolicy(sizePolicy1)
        self.pushButton_erase_captures.setMinimumSize(QSize(16, 0))
        self.pushButton_erase_captures.setMaximumSize(QSize(26, 26))
        icon10 = QIcon()
        icon10.addFile(u":/greys/images/grey_icons/eraser.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_erase_captures.setIcon(icon10)
        self.pushButton_erase_captures.setIconSize(QSize(22, 22))

        self.hboxLayout28.addWidget(self.pushButton_erase_captures)

        self.pushButton_resize_captures = QPushButton(self.frame_scope_capture_nest)
        self.pushButton_resize_captures.setObjectName(u"pushButton_resize_captures")
        sizePolicy1.setHeightForWidth(self.pushButton_resize_captures.sizePolicy().hasHeightForWidth())
        self.pushButton_resize_captures.setSizePolicy(sizePolicy1)
        self.pushButton_resize_captures.setMinimumSize(QSize(16, 0))
        self.pushButton_resize_captures.setMaximumSize(QSize(26, 26))
        icon11 = QIcon()
        icon11.addFile(u":/greys/images/grey_icons/eye.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_resize_captures.setIcon(icon11)
        self.pushButton_resize_captures.setIconSize(QSize(22, 22))

        self.hboxLayout28.addWidget(self.pushButton_resize_captures)

        self.pushButton_resort_captures = QPushButton(self.frame_scope_capture_nest)
        self.pushButton_resort_captures.setObjectName(u"pushButton_resort_captures")
        sizePolicy1.setHeightForWidth(self.pushButton_resort_captures.sizePolicy().hasHeightForWidth())
        self.pushButton_resort_captures.setSizePolicy(sizePolicy1)
        self.pushButton_resort_captures.setMinimumSize(QSize(16, 0))
        self.pushButton_resort_captures.setMaximumSize(QSize(26, 26))
        icon12 = QIcon()
        icon12.addFile(u":/greys/images/grey_icons/cross_arrows.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_resort_captures.setIcon(icon12)
        self.pushButton_resort_captures.setIconSize(QSize(22, 22))

        self.hboxLayout28.addWidget(self.pushButton_resort_captures)


        self.verticalLayout_scope_setup_left_nest_3.addLayout(self.hboxLayout28)

        self.frame_scope_capture_left_nest_over = QFrame(self.frame_scope_capture_nest)
        self.frame_scope_capture_left_nest_over.setObjectName(u"frame_scope_capture_left_nest_over")
        sizePolicy16.setHeightForWidth(self.frame_scope_capture_left_nest_over.sizePolicy().hasHeightForWidth())
        self.frame_scope_capture_left_nest_over.setSizePolicy(sizePolicy16)
        self.verticalLayout_setup_left_nest_over_9 = QVBoxLayout(self.frame_scope_capture_left_nest_over)
        self.verticalLayout_setup_left_nest_over_9.setSpacing(0)
        self.verticalLayout_setup_left_nest_over_9.setObjectName(u"verticalLayout_setup_left_nest_over_9")
        self.verticalLayout_setup_left_nest_over_9.setContentsMargins(0, 0, 0, 0)
        self.stackedWidget_scope_capture_save = QStackedWidget(self.frame_scope_capture_left_nest_over)
        self.stackedWidget_scope_capture_save.setObjectName(u"stackedWidget_scope_capture_save")
        sizePolicy16.setHeightForWidth(self.stackedWidget_scope_capture_save.sizePolicy().hasHeightForWidth())
        self.stackedWidget_scope_capture_save.setSizePolicy(sizePolicy16)
        self.page_scope_capture_save_design = QWidget()
        self.page_scope_capture_save_design.setObjectName(u"page_scope_capture_save_design")
        sizePolicy16.setHeightForWidth(self.page_scope_capture_save_design.sizePolicy().hasHeightForWidth())
        self.page_scope_capture_save_design.setSizePolicy(sizePolicy16)
        self.vboxLayout63 = QVBoxLayout(self.page_scope_capture_save_design)
        self.vboxLayout63.setSpacing(0)
        self.vboxLayout63.setObjectName(u"vboxLayout63")
        self.vboxLayout63.setContentsMargins(0, 0, 0, 0)
        self.scrollArea_scope_capture_save_design = QScrollArea(self.page_scope_capture_save_design)
        self.scrollArea_scope_capture_save_design.setObjectName(u"scrollArea_scope_capture_save_design")
        self.scrollArea_scope_capture_save_design.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scrollArea_scope_capture_save_design.setWidgetResizable(True)
        self.scrollAreaWidgetContents_scope_capture_save_design = QWidget()
        self.scrollAreaWidgetContents_scope_capture_save_design.setObjectName(u"scrollAreaWidgetContents_scope_capture_save_design")
        self.scrollAreaWidgetContents_scope_capture_save_design.setGeometry(QRect(0, 0, 190, 333))
        sizePolicy16.setHeightForWidth(self.scrollAreaWidgetContents_scope_capture_save_design.sizePolicy().hasHeightForWidth())
        self.scrollAreaWidgetContents_scope_capture_save_design.setSizePolicy(sizePolicy16)
        self.verticalLayout_scope_capture_save_design = QVBoxLayout(self.scrollAreaWidgetContents_scope_capture_save_design)
        self.verticalLayout_scope_capture_save_design.setSpacing(6)
        self.verticalLayout_scope_capture_save_design.setObjectName(u"verticalLayout_scope_capture_save_design")
        self.verticalLayout_scope_capture_save_design.setContentsMargins(0, 0, 0, 0)
        self.frame_rcsd_white_5 = QFrame(self.scrollAreaWidgetContents_scope_capture_save_design)
        self.frame_rcsd_white_5.setObjectName(u"frame_rcsd_white_5")
        sizePolicy16.setHeightForWidth(self.frame_rcsd_white_5.sizePolicy().hasHeightForWidth())
        self.frame_rcsd_white_5.setSizePolicy(sizePolicy16)
        self.frame_rcsd_white_5.setMinimumSize(QSize(190, 200))
        self.frame_rcsd_white_5.setMaximumSize(QSize(190, 200))
        self.frame_rcsd_white_5.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_rcsd_white_5.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_rcsd_nest_5 = QFrame(self.frame_rcsd_white_5)
        self.frame_rcsd_nest_5.setObjectName(u"frame_rcsd_nest_5")
        self.frame_rcsd_nest_5.setGeometry(QRect(1, 1, 188, 198))
        sizePolicy16.setHeightForWidth(self.frame_rcsd_nest_5.sizePolicy().hasHeightForWidth())
        self.frame_rcsd_nest_5.setSizePolicy(sizePolicy16)
        self.frame_rcsd_nest_5.setMinimumSize(QSize(100, 198))
        self.frame_rcsd_nest_5.setMaximumSize(QSize(190, 198))
        self.frame_rcsd_nest_5.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_rcsd_nest_5.setFrameShadow(QFrame.Shadow.Raised)
        self.label_rcsd_timestamp_9 = QLabel(self.frame_rcsd_nest_5)
        self.label_rcsd_timestamp_9.setObjectName(u"label_rcsd_timestamp_9")
        self.label_rcsd_timestamp_9.setGeometry(QRect(10, 7, 141, 21))
        sizePolicy16.setHeightForWidth(self.label_rcsd_timestamp_9.sizePolicy().hasHeightForWidth())
        self.label_rcsd_timestamp_9.setSizePolicy(sizePolicy16)

        self.verticalLayout_scope_capture_save_design.addWidget(self.frame_rcsd_white_5)

        self.verticalSpacer_rcsd_3 = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_scope_capture_save_design.addItem(self.verticalSpacer_rcsd_3)

        self.scrollArea_scope_capture_save_design.setWidget(self.scrollAreaWidgetContents_scope_capture_save_design)

        self.vboxLayout63.addWidget(self.scrollArea_scope_capture_save_design)

        self.stackedWidget_scope_capture_save.addWidget(self.page_scope_capture_save_design)
        self.page_scope_capture_save = QWidget()
        self.page_scope_capture_save.setObjectName(u"page_scope_capture_save")
        sizePolicy16.setHeightForWidth(self.page_scope_capture_save.sizePolicy().hasHeightForWidth())
        self.page_scope_capture_save.setSizePolicy(sizePolicy16)
        self.vboxLayout64 = QVBoxLayout(self.page_scope_capture_save)
        self.vboxLayout64.setSpacing(0)
        self.vboxLayout64.setObjectName(u"vboxLayout64")
        self.vboxLayout64.setContentsMargins(0, 0, 0, 0)
        self.scrollArea_scope_capture_save = QScrollArea(self.page_scope_capture_save)
        self.scrollArea_scope_capture_save.setObjectName(u"scrollArea_scope_capture_save")
        self.scrollArea_scope_capture_save.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scrollArea_scope_capture_save.setWidgetResizable(True)
        self.scrollAreaWidgetContents_scope_capture_save = QWidget()
        self.scrollAreaWidgetContents_scope_capture_save.setObjectName(u"scrollAreaWidgetContents_scope_capture_save")
        self.scrollAreaWidgetContents_scope_capture_save.setGeometry(QRect(0, 0, 80, 26))
        sizePolicy16.setHeightForWidth(self.scrollAreaWidgetContents_scope_capture_save.sizePolicy().hasHeightForWidth())
        self.scrollAreaWidgetContents_scope_capture_save.setSizePolicy(sizePolicy16)
        self.verticalLayout_scope_capture_save = QVBoxLayout(self.scrollAreaWidgetContents_scope_capture_save)
        self.verticalLayout_scope_capture_save.setSpacing(6)
        self.verticalLayout_scope_capture_save.setObjectName(u"verticalLayout_scope_capture_save")
        self.verticalLayout_scope_capture_save.setContentsMargins(0, 0, 0, 0)
        self.verticalSpacer_scope_capture_save = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_scope_capture_save.addItem(self.verticalSpacer_scope_capture_save)

        self.scrollArea_scope_capture_save.setWidget(self.scrollAreaWidgetContents_scope_capture_save)

        self.vboxLayout64.addWidget(self.scrollArea_scope_capture_save)

        self.stackedWidget_scope_capture_save.addWidget(self.page_scope_capture_save)

        self.verticalLayout_setup_left_nest_over_9.addWidget(self.stackedWidget_scope_capture_save)


        self.verticalLayout_scope_setup_left_nest_3.addWidget(self.frame_scope_capture_left_nest_over)

        self.frame_scope_capture_bottom = QFrame(self.frame_scope_capture_nest)
        self.frame_scope_capture_bottom.setObjectName(u"frame_scope_capture_bottom")
        sizePolicy16.setHeightForWidth(self.frame_scope_capture_bottom.sizePolicy().hasHeightForWidth())
        self.frame_scope_capture_bottom.setSizePolicy(sizePolicy16)
        self.frame_scope_capture_bottom.setFrameShape(QFrame.Shape.NoFrame)
        self.frame_scope_capture_bottom.setFrameShadow(QFrame.Shadow.Plain)
        self.frame_scope_capture_bottom.setLineWidth(0)
        self.vboxLayout65 = QVBoxLayout(self.frame_scope_capture_bottom)
        self.vboxLayout65.setObjectName(u"vboxLayout65")
        self.vboxLayout65.setContentsMargins(0, -1, 0, -1)
        self.label_session_count = QLabel(self.frame_scope_capture_bottom)
        self.label_session_count.setObjectName(u"label_session_count")
        sizePolicy16.setHeightForWidth(self.label_session_count.sizePolicy().hasHeightForWidth())
        self.label_session_count.setSizePolicy(sizePolicy16)
        self.label_session_count.setMaximumSize(QSize(16777215, 20))
        self.label_session_count.setWordWrap(True)

        self.vboxLayout65.addWidget(self.label_session_count)

        self.hboxLayout29 = QHBoxLayout()
        self.hboxLayout29.setObjectName(u"hboxLayout29")
        self.pushButton_scope_capture_load = QPushButton(self.frame_scope_capture_bottom)
        self.pushButton_scope_capture_load.setObjectName(u"pushButton_scope_capture_load")
        sizePolicy16.setHeightForWidth(self.pushButton_scope_capture_load.sizePolicy().hasHeightForWidth())
        self.pushButton_scope_capture_load.setSizePolicy(sizePolicy16)

        self.hboxLayout29.addWidget(self.pushButton_scope_capture_load)

        self.pushButton_export_session = QPushButton(self.frame_scope_capture_bottom)
        self.pushButton_export_session.setObjectName(u"pushButton_export_session")
        sizePolicy16.setHeightForWidth(self.pushButton_export_session.sizePolicy().hasHeightForWidth())
        self.pushButton_export_session.setSizePolicy(sizePolicy16)
        self.pushButton_export_session.setMinimumSize(QSize(0, 25))
        icon13 = QIcon()
        icon13.addFile(u":/greys/images/grey_icons/triangle_down_underline.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_export_session.setIcon(icon13)

        self.hboxLayout29.addWidget(self.pushButton_export_session)


        self.vboxLayout65.addLayout(self.hboxLayout29)

        self.horizontalLayout_correction_status_title = QHBoxLayout()
        self.horizontalLayout_correction_status_title.setObjectName(u"horizontalLayout_correction_status_title")
        self.label_correction_status_title = QLabel(self.frame_scope_capture_bottom)
        self.label_correction_status_title.setObjectName(u"label_correction_status_title")
        sizePolicy16.setHeightForWidth(self.label_correction_status_title.sizePolicy().hasHeightForWidth())
        self.label_correction_status_title.setSizePolicy(sizePolicy16)
        self.label_correction_status_title.setMaximumSize(QSize(16777215, 20))
        self.label_correction_status_title.setFont(font2)
        self.label_correction_status_title.setScaledContents(True)
        self.label_correction_status_title.setWordWrap(False)

        self.horizontalLayout_correction_status_title.addWidget(self.label_correction_status_title)

        self.spacerItem23 = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_correction_status_title.addItem(self.spacerItem23)

        self.pushButton_correction_status_minimize = QPushButton(self.frame_scope_capture_bottom)
        self.pushButton_correction_status_minimize.setObjectName(u"pushButton_correction_status_minimize")
        sizePolicy1.setHeightForWidth(self.pushButton_correction_status_minimize.sizePolicy().hasHeightForWidth())
        self.pushButton_correction_status_minimize.setSizePolicy(sizePolicy1)
        self.pushButton_correction_status_minimize.setMinimumSize(QSize(12, 0))
        self.pushButton_correction_status_minimize.setMaximumSize(QSize(12, 12))
        icon14 = QIcon()
        icon14.addFile(u":/greys/images/grey_icons/down_triangle.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_correction_status_minimize.setIcon(icon14)
        self.pushButton_correction_status_minimize.setIconSize(QSize(12, 12))

        self.horizontalLayout_correction_status_title.addWidget(self.pushButton_correction_status_minimize)


        self.vboxLayout65.addLayout(self.horizontalLayout_correction_status_title)

        self.frame_correction_status_1 = QFrame(self.frame_scope_capture_bottom)
        self.frame_correction_status_1.setObjectName(u"frame_correction_status_1")
        self.frame_correction_status_1.setMinimumSize(QSize(0, 0))
        self.form_correction_status_1 = QFormLayout(self.frame_correction_status_1)
        self.form_correction_status_1.setObjectName(u"form_correction_status_1")
        self.form_correction_status_1.setVerticalSpacing(1)
        self.label_correction_status_raman_shift_label = QLabel(self.frame_correction_status_1)
        self.label_correction_status_raman_shift_label.setObjectName(u"label_correction_status_raman_shift_label")
        sizePolicy16.setHeightForWidth(self.label_correction_status_raman_shift_label.sizePolicy().hasHeightForWidth())
        self.label_correction_status_raman_shift_label.setSizePolicy(sizePolicy16)

        self.form_correction_status_1.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_correction_status_raman_shift_label)

        self.label_correction_status_raman_shift = QLabel(self.frame_correction_status_1)
        self.label_correction_status_raman_shift.setObjectName(u"label_correction_status_raman_shift")
        sizePolicy16.setHeightForWidth(self.label_correction_status_raman_shift.sizePolicy().hasHeightForWidth())
        self.label_correction_status_raman_shift.setSizePolicy(sizePolicy16)

        self.form_correction_status_1.setWidget(0, QFormLayout.ItemRole.FieldRole, self.label_correction_status_raman_shift)

        self.label_correction_status_edc_label = QLabel(self.frame_correction_status_1)
        self.label_correction_status_edc_label.setObjectName(u"label_correction_status_edc_label")
        sizePolicy16.setHeightForWidth(self.label_correction_status_edc_label.sizePolicy().hasHeightForWidth())
        self.label_correction_status_edc_label.setSizePolicy(sizePolicy16)

        self.form_correction_status_1.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_correction_status_edc_label)

        self.label_correction_status_edc = QLabel(self.frame_correction_status_1)
        self.label_correction_status_edc.setObjectName(u"label_correction_status_edc")
        sizePolicy16.setHeightForWidth(self.label_correction_status_edc.sizePolicy().hasHeightForWidth())
        self.label_correction_status_edc.setSizePolicy(sizePolicy16)

        self.form_correction_status_1.setWidget(1, QFormLayout.ItemRole.FieldRole, self.label_correction_status_edc)

        self.label_correction_status_ingaas_label = QLabel(self.frame_correction_status_1)
        self.label_correction_status_ingaas_label.setObjectName(u"label_correction_status_ingaas_label")
        sizePolicy16.setHeightForWidth(self.label_correction_status_ingaas_label.sizePolicy().hasHeightForWidth())
        self.label_correction_status_ingaas_label.setSizePolicy(sizePolicy16)

        self.form_correction_status_1.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_correction_status_ingaas_label)

        self.label_correction_status_ingaas = QLabel(self.frame_correction_status_1)
        self.label_correction_status_ingaas.setObjectName(u"label_correction_status_ingaas")
        sizePolicy16.setHeightForWidth(self.label_correction_status_ingaas.sizePolicy().hasHeightForWidth())
        self.label_correction_status_ingaas.setSizePolicy(sizePolicy16)

        self.form_correction_status_1.setWidget(2, QFormLayout.ItemRole.FieldRole, self.label_correction_status_ingaas)

        self.label_correction_status_etalon_label = QLabel(self.frame_correction_status_1)
        self.label_correction_status_etalon_label.setObjectName(u"label_correction_status_etalon_label")
        sizePolicy16.setHeightForWidth(self.label_correction_status_etalon_label.sizePolicy().hasHeightForWidth())
        self.label_correction_status_etalon_label.setSizePolicy(sizePolicy16)

        self.form_correction_status_1.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label_correction_status_etalon_label)

        self.label_correction_status_etalon = QLabel(self.frame_correction_status_1)
        self.label_correction_status_etalon.setObjectName(u"label_correction_status_etalon")
        sizePolicy16.setHeightForWidth(self.label_correction_status_etalon.sizePolicy().hasHeightForWidth())
        self.label_correction_status_etalon.setSizePolicy(sizePolicy16)

        self.form_correction_status_1.setWidget(3, QFormLayout.ItemRole.FieldRole, self.label_correction_status_etalon)

        self.label_correction_status_srm_label = QLabel(self.frame_correction_status_1)
        self.label_correction_status_srm_label.setObjectName(u"label_correction_status_srm_label")
        sizePolicy16.setHeightForWidth(self.label_correction_status_srm_label.sizePolicy().hasHeightForWidth())
        self.label_correction_status_srm_label.setSizePolicy(sizePolicy16)

        self.form_correction_status_1.setWidget(4, QFormLayout.ItemRole.LabelRole, self.label_correction_status_srm_label)

        self.label_correction_status_srm = QLabel(self.frame_correction_status_1)
        self.label_correction_status_srm.setObjectName(u"label_correction_status_srm")
        sizePolicy16.setHeightForWidth(self.label_correction_status_srm.sizePolicy().hasHeightForWidth())
        self.label_correction_status_srm.setSizePolicy(sizePolicy16)

        self.form_correction_status_1.setWidget(4, QFormLayout.ItemRole.FieldRole, self.label_correction_status_srm)

        self.label_correction_status_XD_label = QLabel(self.frame_correction_status_1)
        self.label_correction_status_XD_label.setObjectName(u"label_correction_status_XD_label")
        sizePolicy16.setHeightForWidth(self.label_correction_status_XD_label.sizePolicy().hasHeightForWidth())
        self.label_correction_status_XD_label.setSizePolicy(sizePolicy16)

        self.form_correction_status_1.setWidget(5, QFormLayout.ItemRole.LabelRole, self.label_correction_status_XD_label)

        self.label_correction_status_XD = QLabel(self.frame_correction_status_1)
        self.label_correction_status_XD.setObjectName(u"label_correction_status_XD")
        sizePolicy16.setHeightForWidth(self.label_correction_status_XD.sizePolicy().hasHeightForWidth())
        self.label_correction_status_XD.setSizePolicy(sizePolicy16)

        self.form_correction_status_1.setWidget(5, QFormLayout.ItemRole.FieldRole, self.label_correction_status_XD)

        self.label_correction_status_baseline_label = QLabel(self.frame_correction_status_1)
        self.label_correction_status_baseline_label.setObjectName(u"label_correction_status_baseline_label")
        sizePolicy16.setHeightForWidth(self.label_correction_status_baseline_label.sizePolicy().hasHeightForWidth())
        self.label_correction_status_baseline_label.setSizePolicy(sizePolicy16)

        self.form_correction_status_1.setWidget(6, QFormLayout.ItemRole.LabelRole, self.label_correction_status_baseline_label)

        self.label_correction_status_baseline = QLabel(self.frame_correction_status_1)
        self.label_correction_status_baseline.setObjectName(u"label_correction_status_baseline")
        sizePolicy16.setHeightForWidth(self.label_correction_status_baseline.sizePolicy().hasHeightForWidth())
        self.label_correction_status_baseline.setSizePolicy(sizePolicy16)

        self.form_correction_status_1.setWidget(6, QFormLayout.ItemRole.FieldRole, self.label_correction_status_baseline)


        self.vboxLayout65.addWidget(self.frame_correction_status_1)

        self.formLayout8 = QFormLayout()
        self.formLayout8.setObjectName(u"formLayout8")
        self.label198 = QLabel(self.frame_scope_capture_bottom)
        self.label198.setObjectName(u"label198")
        sizePolicy16.setHeightForWidth(self.label198.sizePolicy().hasHeightForWidth())
        self.label198.setSizePolicy(sizePolicy16)

        self.formLayout8.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label198)

        self.lineEdit_scope_capture_save_prefix = QLineEdit(self.frame_scope_capture_bottom)
        self.lineEdit_scope_capture_save_prefix.setObjectName(u"lineEdit_scope_capture_save_prefix")

        self.formLayout8.setWidget(0, QFormLayout.ItemRole.FieldRole, self.lineEdit_scope_capture_save_prefix)

        self.label199 = QLabel(self.frame_scope_capture_bottom)
        self.label199.setObjectName(u"label199")
        sizePolicy16.setHeightForWidth(self.label199.sizePolicy().hasHeightForWidth())
        self.label199.setSizePolicy(sizePolicy16)

        self.formLayout8.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label199)

        self.lineEdit_scope_capture_save_note = QLineEdit(self.frame_scope_capture_bottom)
        self.lineEdit_scope_capture_save_note.setObjectName(u"lineEdit_scope_capture_save_note")

        self.formLayout8.setWidget(2, QFormLayout.ItemRole.FieldRole, self.lineEdit_scope_capture_save_note)

        self.label200 = QLabel(self.frame_scope_capture_bottom)
        self.label200.setObjectName(u"label200")
        sizePolicy16.setHeightForWidth(self.label200.sizePolicy().hasHeightForWidth())
        self.label200.setSizePolicy(sizePolicy16)

        self.formLayout8.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label200)

        self.lineEdit_scope_capture_save_suffix = QLineEdit(self.frame_scope_capture_bottom)
        self.lineEdit_scope_capture_save_suffix.setObjectName(u"lineEdit_scope_capture_save_suffix")

        self.formLayout8.setWidget(1, QFormLayout.ItemRole.FieldRole, self.lineEdit_scope_capture_save_suffix)


        self.vboxLayout65.addLayout(self.formLayout8)


        self.verticalLayout_scope_setup_left_nest_3.addWidget(self.frame_scope_capture_bottom)


        self.vboxLayout62.addWidget(self.frame_scope_capture_nest)


        self.vboxLayout61.addWidget(self.frame_clipboard)

        self.scrollArea_save_column.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_save_column.addWidget(self.scrollArea_save_column)

        self.splitter_saves_vs_graph.addWidget(self.frame_new_save_col_holder)
        self.frame_new_scope_capture_holder = QFrame(self.splitter_saves_vs_graph)
        self.frame_new_scope_capture_holder.setObjectName(u"frame_new_scope_capture_holder")
        sizePolicy18 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy18.setHorizontalStretch(2)
        sizePolicy18.setVerticalStretch(0)
        sizePolicy18.setHeightForWidth(self.frame_new_scope_capture_holder.sizePolicy().hasHeightForWidth())
        self.frame_new_scope_capture_holder.setSizePolicy(sizePolicy18)
        self.vboxLayout66 = QVBoxLayout(self.frame_new_scope_capture_holder)
        self.vboxLayout66.setObjectName(u"vboxLayout66")
        self.vboxLayout66.setContentsMargins(0, 0, 0, 0)
        self.frame_scope_capture_middle = QFrame(self.frame_new_scope_capture_holder)
        self.frame_scope_capture_middle.setObjectName(u"frame_scope_capture_middle")
        self.frame_scope_capture_middle.setProperty(u"wpBox", False)
        self.gridLayout6 = QGridLayout(self.frame_scope_capture_middle)
        self.gridLayout6.setSpacing(0)
        self.gridLayout6.setObjectName(u"gridLayout6")
        self.gridLayout6.setContentsMargins(0, 0, 0, 0)
        self.frame_scope_capture_middle_nest = QFrame(self.frame_scope_capture_middle)
        self.frame_scope_capture_middle_nest.setObjectName(u"frame_scope_capture_middle_nest")
        sizePolicy19 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        sizePolicy19.setHorizontalStretch(0)
        sizePolicy19.setVerticalStretch(0)
        sizePolicy19.setHeightForWidth(self.frame_scope_capture_middle_nest.sizePolicy().hasHeightForWidth())
        self.frame_scope_capture_middle_nest.setSizePolicy(sizePolicy19)
        self.frame_scope_capture_middle_nest.setLineWidth(1)
        self.frame_scope_capture_middle_nest.setProperty(u"wpPanel", False)
        self.vboxLayout67 = QVBoxLayout(self.frame_scope_capture_middle_nest)
        self.vboxLayout67.setObjectName(u"vboxLayout67")
        self.frame_scope_capture_buttons = QFrame(self.frame_scope_capture_middle_nest)
        self.frame_scope_capture_buttons.setObjectName(u"frame_scope_capture_buttons")
        sizePolicy6.setHeightForWidth(self.frame_scope_capture_buttons.sizePolicy().hasHeightForWidth())
        self.frame_scope_capture_buttons.setSizePolicy(sizePolicy6)
        self.frame_scope_capture_buttons.setMaximumSize(QSize(16777215, 50))
        self.frame_scope_capture_buttons.setFrameShadow(QFrame.Shadow.Plain)
        self.frame_scope_capture_buttons.setLineWidth(1)
        self.frame_scope_capture_buttons.setProperty(u"wpBox", False)
        self.gridLayout7 = QGridLayout(self.frame_scope_capture_buttons)
        self.gridLayout7.setSpacing(0)
        self.gridLayout7.setObjectName(u"gridLayout7")
        self.gridLayout7.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.gridLayout7.setContentsMargins(0, 0, 0, 0)
        self.frame_scope_capture_button_bar = QFrame(self.frame_scope_capture_buttons)
        self.frame_scope_capture_button_bar.setObjectName(u"frame_scope_capture_button_bar")
        sizePolicy16.setHeightForWidth(self.frame_scope_capture_button_bar.sizePolicy().hasHeightForWidth())
        self.frame_scope_capture_button_bar.setSizePolicy(sizePolicy16)
        self.frame_scope_capture_button_bar.setMinimumSize(QSize(0, 0))
        self.frame_scope_capture_button_bar.setMaximumSize(QSize(16777215, 16777215))
        self.frame_scope_capture_button_bar.setProperty(u"wpGrad", False)
        self.hboxLayout30 = QHBoxLayout(self.frame_scope_capture_button_bar)
        self.hboxLayout30.setSpacing(0)
        self.hboxLayout30.setObjectName(u"hboxLayout30")
        self.hboxLayout30.setSizeConstraint(QLayout.SizeConstraint.SetMaximumSize)
        self.hboxLayout30.setContentsMargins(9, 9, 9, 9)
        self.horizontalLayout_graph_controls = QHBoxLayout()
        self.horizontalLayout_graph_controls.setSpacing(2)
        self.horizontalLayout_graph_controls.setObjectName(u"horizontalLayout_graph_controls")
        self.horizontalLayout_graph_controls.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.pushButton_lock_axes = QPushButton(self.frame_scope_capture_button_bar)
        self.pushButton_lock_axes.setObjectName(u"pushButton_lock_axes")
        sizePolicy3.setHeightForWidth(self.pushButton_lock_axes.sizePolicy().hasHeightForWidth())
        self.pushButton_lock_axes.setSizePolicy(sizePolicy3)
        self.pushButton_lock_axes.setMinimumSize(QSize(14, 26))
        self.pushButton_lock_axes.setMaximumSize(QSize(30, 26))
        icon15 = QIcon()
        icon15.addFile(u":/greys/images/grey_icons/lock-spectra.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_lock_axes.setIcon(icon15)

        self.horizontalLayout_graph_controls.addWidget(self.pushButton_lock_axes)

        self.pushButton_zoom_graph = QPushButton(self.frame_scope_capture_button_bar)
        self.pushButton_zoom_graph.setObjectName(u"pushButton_zoom_graph")
        sizePolicy3.setHeightForWidth(self.pushButton_zoom_graph.sizePolicy().hasHeightForWidth())
        self.pushButton_zoom_graph.setSizePolicy(sizePolicy3)
        self.pushButton_zoom_graph.setMinimumSize(QSize(14, 26))
        self.pushButton_zoom_graph.setMaximumSize(QSize(30, 26))
        icon16 = QIcon()
        icon16.addFile(u":/greys/images/grey_icons/zoom.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_zoom_graph.setIcon(icon16)

        self.horizontalLayout_graph_controls.addWidget(self.pushButton_zoom_graph)

        self.pushButton_graphGrid = QPushButton(self.frame_scope_capture_button_bar)
        self.pushButton_graphGrid.setObjectName(u"pushButton_graphGrid")
        sizePolicy3.setHeightForWidth(self.pushButton_graphGrid.sizePolicy().hasHeightForWidth())
        self.pushButton_graphGrid.setSizePolicy(sizePolicy3)
        self.pushButton_graphGrid.setMinimumSize(QSize(14, 26))
        self.pushButton_graphGrid.setMaximumSize(QSize(30, 26))
        icon17 = QIcon()
        icon17.addFile(u":/greys/images/grey_icons/GridIcon.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_graphGrid.setIcon(icon17)

        self.horizontalLayout_graph_controls.addWidget(self.pushButton_graphGrid)

        self.pushButton_invert_x_axis = QPushButton(self.frame_scope_capture_button_bar)
        self.pushButton_invert_x_axis.setObjectName(u"pushButton_invert_x_axis")
        sizePolicy3.setHeightForWidth(self.pushButton_invert_x_axis.sizePolicy().hasHeightForWidth())
        self.pushButton_invert_x_axis.setSizePolicy(sizePolicy3)
        self.pushButton_invert_x_axis.setMinimumSize(QSize(14, 26))
        self.pushButton_invert_x_axis.setMaximumSize(QSize(30, 26))
        icon18 = QIcon()
        icon18.addFile(u":/greys/images/grey_icons/flip-horiz.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_invert_x_axis.setIcon(icon18)

        self.horizontalLayout_graph_controls.addWidget(self.pushButton_invert_x_axis)

        self.pushButton_roi_toggle = QPushButton(self.frame_scope_capture_button_bar)
        self.pushButton_roi_toggle.setObjectName(u"pushButton_roi_toggle")
        sizePolicy3.setHeightForWidth(self.pushButton_roi_toggle.sizePolicy().hasHeightForWidth())
        self.pushButton_roi_toggle.setSizePolicy(sizePolicy3)
        self.pushButton_roi_toggle.setMinimumSize(QSize(14, 26))
        self.pushButton_roi_toggle.setMaximumSize(QSize(30, 26))

        self.horizontalLayout_graph_controls.addWidget(self.pushButton_roi_toggle)

        self.pushButton_interp_toggle = QPushButton(self.frame_scope_capture_button_bar)
        self.pushButton_interp_toggle.setObjectName(u"pushButton_interp_toggle")
        sizePolicy3.setHeightForWidth(self.pushButton_interp_toggle.sizePolicy().hasHeightForWidth())
        self.pushButton_interp_toggle.setSizePolicy(sizePolicy3)
        self.pushButton_interp_toggle.setMinimumSize(QSize(14, 26))
        self.pushButton_interp_toggle.setMaximumSize(QSize(30, 26))
        icon19 = QIcon()
        icon19.addFile(u":/greys/images/grey_icons/ruler.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_interp_toggle.setIcon(icon19)

        self.horizontalLayout_graph_controls.addWidget(self.pushButton_interp_toggle)

        self.horizontalSpacer_gap_left = QSpacerItem(0, 6, QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_graph_controls.addItem(self.horizontalSpacer_gap_left)

        self.pushButton_scope_toggle_dark = QPushButton(self.frame_scope_capture_button_bar)
        self.pushButton_scope_toggle_dark.setObjectName(u"pushButton_scope_toggle_dark")
        sizePolicy3.setHeightForWidth(self.pushButton_scope_toggle_dark.sizePolicy().hasHeightForWidth())
        self.pushButton_scope_toggle_dark.setSizePolicy(sizePolicy3)
        self.pushButton_scope_toggle_dark.setMinimumSize(QSize(16, 26))
        self.pushButton_scope_toggle_dark.setMaximumSize(QSize(30, 26))
        self.pushButton_scope_toggle_dark.setIcon(icon8)

        self.horizontalLayout_graph_controls.addWidget(self.pushButton_scope_toggle_dark)

        self.pushButton_scope_toggle_reference = QPushButton(self.frame_scope_capture_button_bar)
        self.pushButton_scope_toggle_reference.setObjectName(u"pushButton_scope_toggle_reference")
        sizePolicy3.setHeightForWidth(self.pushButton_scope_toggle_reference.sizePolicy().hasHeightForWidth())
        self.pushButton_scope_toggle_reference.setSizePolicy(sizePolicy3)
        self.pushButton_scope_toggle_reference.setMinimumSize(QSize(16, 26))
        self.pushButton_scope_toggle_reference.setMaximumSize(QSize(30, 26))
        self.pushButton_scope_toggle_reference.setIcon(icon9)

        self.horizontalLayout_graph_controls.addWidget(self.pushButton_scope_toggle_reference)

        self.pushButton_ramanCorrection = QPushButton(self.frame_scope_capture_button_bar)
        self.pushButton_ramanCorrection.setObjectName(u"pushButton_ramanCorrection")
        sizePolicy3.setHeightForWidth(self.pushButton_ramanCorrection.sizePolicy().hasHeightForWidth())
        self.pushButton_ramanCorrection.setSizePolicy(sizePolicy3)
        self.pushButton_ramanCorrection.setMinimumSize(QSize(16, 26))
        self.pushButton_ramanCorrection.setMaximumSize(QSize(30, 26))
        icon20 = QIcon()
        icon20.addFile(u":/greys/images/grey_icons/raman_correction.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_ramanCorrection.setIcon(icon20)
        self.pushButton_ramanCorrection.setIconSize(QSize(20, 20))

        self.horizontalLayout_graph_controls.addWidget(self.pushButton_ramanCorrection)

        self.pushButton_ingaas_correction = QPushButton(self.frame_scope_capture_button_bar)
        self.pushButton_ingaas_correction.setObjectName(u"pushButton_ingaas_correction")
        sizePolicy3.setHeightForWidth(self.pushButton_ingaas_correction.sizePolicy().hasHeightForWidth())
        self.pushButton_ingaas_correction.setSizePolicy(sizePolicy3)
        self.pushButton_ingaas_correction.setMinimumSize(QSize(16, 26))
        self.pushButton_ingaas_correction.setMaximumSize(QSize(30, 26))
        icon21 = QIcon()
        icon21.addFile(u":/greys/images/grey_icons/ingaas.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_ingaas_correction.setIcon(icon21)

        self.horizontalLayout_graph_controls.addWidget(self.pushButton_ingaas_correction)

        self.pushButton_etalon_correction = QPushButton(self.frame_scope_capture_button_bar)
        self.pushButton_etalon_correction.setObjectName(u"pushButton_etalon_correction")
        sizePolicy3.setHeightForWidth(self.pushButton_etalon_correction.sizePolicy().hasHeightForWidth())
        self.pushButton_etalon_correction.setSizePolicy(sizePolicy3)
        self.pushButton_etalon_correction.setMinimumSize(QSize(16, 26))
        self.pushButton_etalon_correction.setMaximumSize(QSize(30, 26))
        icon22 = QIcon()
        icon22.addFile(u":/greys/images/grey_icons/etalon.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_etalon_correction.setIcon(icon22)

        self.horizontalLayout_graph_controls.addWidget(self.pushButton_etalon_correction)

        self.pushButton_raman_intensity_correction_tristate = QPushButton(self.frame_scope_capture_button_bar)
        self.pushButton_raman_intensity_correction_tristate.setObjectName(u"pushButton_raman_intensity_correction_tristate")
        sizePolicy3.setHeightForWidth(self.pushButton_raman_intensity_correction_tristate.sizePolicy().hasHeightForWidth())
        self.pushButton_raman_intensity_correction_tristate.setSizePolicy(sizePolicy3)
        self.pushButton_raman_intensity_correction_tristate.setMinimumSize(QSize(14, 26))
        self.pushButton_raman_intensity_correction_tristate.setMaximumSize(QSize(30, 26))
        icon23 = QIcon()
        icon23.addFile(u":/greys/images/grey_icons/srm.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_raman_intensity_correction_tristate.setIcon(icon23)

        self.horizontalLayout_graph_controls.addWidget(self.pushButton_raman_intensity_correction_tristate)

        self.pushButton_XD_toggle = QPushButton(self.frame_scope_capture_button_bar)
        self.pushButton_XD_toggle.setObjectName(u"pushButton_XD_toggle")
        sizePolicy3.setHeightForWidth(self.pushButton_XD_toggle.sizePolicy().hasHeightForWidth())
        self.pushButton_XD_toggle.setSizePolicy(sizePolicy3)
        self.pushButton_XD_toggle.setMinimumSize(QSize(16, 26))
        self.pushButton_XD_toggle.setMaximumSize(QSize(30, 26))
        icon24 = QIcon()
        icon24.addFile(u":/greys/images/grey_icons/XD.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_XD_toggle.setIcon(icon24)

        self.horizontalLayout_graph_controls.addWidget(self.pushButton_XD_toggle)

        self.pushButton_library_matching_toggle = QPushButton(self.frame_scope_capture_button_bar)
        self.pushButton_library_matching_toggle.setObjectName(u"pushButton_library_matching_toggle")
        sizePolicy3.setHeightForWidth(self.pushButton_library_matching_toggle.sizePolicy().hasHeightForWidth())
        self.pushButton_library_matching_toggle.setSizePolicy(sizePolicy3)
        self.pushButton_library_matching_toggle.setMinimumSize(QSize(16, 26))
        self.pushButton_library_matching_toggle.setMaximumSize(QSize(30, 26))
        icon25 = QIcon()
        icon25.addFile(u":/greys/images/grey_icons/fingerprint.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_library_matching_toggle.setIcon(icon25)

        self.horizontalLayout_graph_controls.addWidget(self.pushButton_library_matching_toggle)

        self.horizontalSpacer_gap_right = QSpacerItem(0, 5, QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_graph_controls.addItem(self.horizontalSpacer_gap_right)

        self.pushButton_show_ble_selector = QPushButton(self.frame_scope_capture_button_bar)
        self.pushButton_show_ble_selector.setObjectName(u"pushButton_show_ble_selector")
        sizePolicy3.setHeightForWidth(self.pushButton_show_ble_selector.sizePolicy().hasHeightForWidth())
        self.pushButton_show_ble_selector.setSizePolicy(sizePolicy3)
        self.pushButton_show_ble_selector.setMinimumSize(QSize(16, 26))
        self.pushButton_show_ble_selector.setMaximumSize(QSize(30, 26))
        icon26 = QIcon()
        icon26.addFile(u":/greys/images/grey_icons/bluetooth.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_show_ble_selector.setIcon(icon26)
        self.pushButton_show_ble_selector.setIconSize(QSize(16, 16))

        self.horizontalLayout_graph_controls.addWidget(self.pushButton_show_ble_selector)

        self.pushButton_guide = QPushButton(self.frame_scope_capture_button_bar)
        self.pushButton_guide.setObjectName(u"pushButton_guide")
        sizePolicy3.setHeightForWidth(self.pushButton_guide.sizePolicy().hasHeightForWidth())
        self.pushButton_guide.setSizePolicy(sizePolicy3)
        self.pushButton_guide.setMinimumSize(QSize(16, 26))
        self.pushButton_guide.setMaximumSize(QSize(30, 26))
        self.pushButton_guide.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        icon27 = QIcon()
        icon27.addFile(u":/greys/images/grey_icons/wizard.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_guide.setIcon(icon27)
        self.pushButton_guide.setIconSize(QSize(16, 16))

        self.horizontalLayout_graph_controls.addWidget(self.pushButton_guide)

        self.pushButton_copy_to_clipboard = QPushButton(self.frame_scope_capture_button_bar)
        self.pushButton_copy_to_clipboard.setObjectName(u"pushButton_copy_to_clipboard")
        sizePolicy3.setHeightForWidth(self.pushButton_copy_to_clipboard.sizePolicy().hasHeightForWidth())
        self.pushButton_copy_to_clipboard.setSizePolicy(sizePolicy3)
        self.pushButton_copy_to_clipboard.setMinimumSize(QSize(16, 26))
        self.pushButton_copy_to_clipboard.setMaximumSize(QSize(30, 26))
        self.pushButton_copy_to_clipboard.setIcon(icon6)
        self.pushButton_copy_to_clipboard.setIconSize(QSize(24, 24))

        self.horizontalLayout_graph_controls.addWidget(self.pushButton_copy_to_clipboard)


        self.hboxLayout30.addLayout(self.horizontalLayout_graph_controls)


        self.gridLayout7.addWidget(self.frame_scope_capture_button_bar, 0, 0, 1, 1)


        self.vboxLayout67.addWidget(self.frame_scope_capture_buttons)

        self.readingProgressBar = QProgressBar(self.frame_scope_capture_middle_nest)
        self.readingProgressBar.setObjectName(u"readingProgressBar")
        self.readingProgressBar.setValue(0)
        self.readingProgressBar.setTextVisible(True)
        self.readingProgressBar.setInvertedAppearance(False)

        self.vboxLayout67.addWidget(self.readingProgressBar)

        self.frame_scope_capture_details_nest = QFrame(self.frame_scope_capture_middle_nest)
        self.frame_scope_capture_details_nest.setObjectName(u"frame_scope_capture_details_nest")
        sizePolicy13.setHeightForWidth(self.frame_scope_capture_details_nest.sizePolicy().hasHeightForWidth())
        self.frame_scope_capture_details_nest.setSizePolicy(sizePolicy13)
        self.frame_scope_capture_details_nest.setMinimumSize(QSize(200, 50))
        self.frame_scope_capture_details_nest.setMaximumSize(QSize(16777215, 16777215))
        self.frame_scope_capture_details_nest.setFrameShadow(QFrame.Shadow.Plain)
        self.frame_scope_capture_details_nest.setLineWidth(1)
        self.frame_scope_capture_details_nest.setProperty(u"wpBox", False)
        self.vboxLayout68 = QVBoxLayout(self.frame_scope_capture_details_nest)
        self.vboxLayout68.setSpacing(0)
        self.vboxLayout68.setObjectName(u"vboxLayout68")
        self.vboxLayout68.setContentsMargins(0, 0, 0, 0)
        self.frame_scope_capture_details_nest_over = QFrame(self.frame_scope_capture_details_nest)
        self.frame_scope_capture_details_nest_over.setObjectName(u"frame_scope_capture_details_nest_over")
        sizePolicy13.setHeightForWidth(self.frame_scope_capture_details_nest_over.sizePolicy().hasHeightForWidth())
        self.frame_scope_capture_details_nest_over.setSizePolicy(sizePolicy13)
        self.frame_scope_capture_details_nest_over.setStyleSheet(u"")
        self.frame_scope_capture_details_nest_over.setProperty(u"wpPanel", False)
        self.hboxLayout31 = QHBoxLayout(self.frame_scope_capture_details_nest_over)
        self.hboxLayout31.setSpacing(0)
        self.hboxLayout31.setObjectName(u"hboxLayout31")
        self.hboxLayout31.setContentsMargins(0, 0, 0, 0)
        self.stackedWidget_scope_capture_details = QStackedWidget(self.frame_scope_capture_details_nest_over)
        self.stackedWidget_scope_capture_details.setObjectName(u"stackedWidget_scope_capture_details")
        sizePolicy13.setHeightForWidth(self.stackedWidget_scope_capture_details.sizePolicy().hasHeightForWidth())
        self.stackedWidget_scope_capture_details.setSizePolicy(sizePolicy13)
        self.stackedWidget_scope_capture_details.setMaximumSize(QSize(16777215, 16777215))
        self.stackedWidget_scope_capture_details.setProperty(u"wpClear", False)
        self.page_scope_capture_details_design = QWidget()
        self.page_scope_capture_details_design.setObjectName(u"page_scope_capture_details_design")
        self.page_scope_capture_details_design.setStyleSheet(u"")
        self.hboxLayout32 = QHBoxLayout(self.page_scope_capture_details_design)
        self.hboxLayout32.setSpacing(0)
        self.hboxLayout32.setObjectName(u"hboxLayout32")
        self.hboxLayout32.setContentsMargins(0, 0, 0, 0)
        self.scrollArea_scope_capture_details = QScrollArea(self.page_scope_capture_details_design)
        self.scrollArea_scope_capture_details.setObjectName(u"scrollArea_scope_capture_details")
        sizePolicy6.setHeightForWidth(self.scrollArea_scope_capture_details.sizePolicy().hasHeightForWidth())
        self.scrollArea_scope_capture_details.setSizePolicy(sizePolicy6)
        self.scrollArea_scope_capture_details.setMaximumSize(QSize(16777215, 1677725))
        self.scrollArea_scope_capture_details.setStyleSheet(u"")
        self.scrollArea_scope_capture_details.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollArea_scope_capture_details.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollArea_scope_capture_details.setWidgetResizable(True)
        self.scrollAreaWidgetContents_rcdd_3 = QWidget()
        self.scrollAreaWidgetContents_rcdd_3.setObjectName(u"scrollAreaWidgetContents_rcdd_3")
        self.scrollAreaWidgetContents_rcdd_3.setGeometry(QRect(0, 0, 968, 297))
        self.scrollAreaWidgetContents_rcdd_3.setProperty(u"wpClear", False)
        self.vboxLayout69 = QVBoxLayout(self.scrollAreaWidgetContents_rcdd_3)
        self.vboxLayout69.setSpacing(6)
        self.vboxLayout69.setObjectName(u"vboxLayout69")
        self.vboxLayout69.setContentsMargins(0, 0, 0, 0)
        self.frame_scope_capture_details_spectrum = QFrame(self.scrollAreaWidgetContents_rcdd_3)
        self.frame_scope_capture_details_spectrum.setObjectName(u"frame_scope_capture_details_spectrum")
        sizePolicy13.setHeightForWidth(self.frame_scope_capture_details_spectrum.sizePolicy().hasHeightForWidth())
        self.frame_scope_capture_details_spectrum.setSizePolicy(sizePolicy13)
        self.frame_scope_capture_details_spectrum.setMinimumSize(QSize(0, 0))
        self.frame_scope_capture_details_spectrum.setMaximumSize(QSize(16777215, 16777215))
        self.frame_scope_capture_details_spectrum.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.frame_scope_capture_details_spectrum.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_scope_capture_details_spectrum.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_scope_capture_details_spectrum.setProperty(u"wpClear", False)
        self.gridLayout8 = QGridLayout(self.frame_scope_capture_details_spectrum)
        self.gridLayout8.setObjectName(u"gridLayout8")
        self.gridLayout8.setVerticalSpacing(7)
        self.gridLayout8.setContentsMargins(0, 0, 0, 0)
        self.stackedWidget_scope_capture_details_spectrum = QStackedWidget(self.frame_scope_capture_details_spectrum)
        self.stackedWidget_scope_capture_details_spectrum.setObjectName(u"stackedWidget_scope_capture_details_spectrum")
        sizePolicy13.setHeightForWidth(self.stackedWidget_scope_capture_details_spectrum.sizePolicy().hasHeightForWidth())
        self.stackedWidget_scope_capture_details_spectrum.setSizePolicy(sizePolicy13)
        self.stackedWidget_scope_capture_details_spectrum.setMinimumSize(QSize(0, 0))
        self.page_scope_capture_details_spectrum = QWidget()
        self.page_scope_capture_details_spectrum.setObjectName(u"page_scope_capture_details_spectrum")
        self.gridLayout9 = QGridLayout(self.page_scope_capture_details_spectrum)
        self.gridLayout9.setObjectName(u"gridLayout9")
        self.layout_scope_capture_graphs = QGridLayout()
        self.layout_scope_capture_graphs.setSpacing(0)
        self.layout_scope_capture_graphs.setObjectName(u"layout_scope_capture_graphs")
        self.layout_scope_capture_graphs.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)

        self.gridLayout9.addLayout(self.layout_scope_capture_graphs, 0, 0, 1, 1)

        self.stackedWidget_scope_capture_details_spectrum.addWidget(self.page_scope_capture_details_spectrum)

        self.gridLayout8.addWidget(self.stackedWidget_scope_capture_details_spectrum, 0, 0, 1, 1)


        self.vboxLayout69.addWidget(self.frame_scope_capture_details_spectrum)

        self.scrollArea_scope_capture_details.setWidget(self.scrollAreaWidgetContents_rcdd_3)

        self.hboxLayout32.addWidget(self.scrollArea_scope_capture_details)

        self.stackedWidget_scope_capture_details.addWidget(self.page_scope_capture_details_design)

        self.hboxLayout31.addWidget(self.stackedWidget_scope_capture_details)


        self.vboxLayout68.addWidget(self.frame_scope_capture_details_nest_over)


        self.vboxLayout67.addWidget(self.frame_scope_capture_details_nest)

        self.frame_scope_status_bar_white = QFrame(self.frame_scope_capture_middle_nest)
        self.frame_scope_status_bar_white.setObjectName(u"frame_scope_status_bar_white")
        self.frame_scope_status_bar_white.setMinimumSize(QSize(0, 0))
        self.frame_scope_status_bar_white.setProperty(u"wpBox", False)
        self.hboxLayout33 = QHBoxLayout(self.frame_scope_status_bar_white)
        self.hboxLayout33.setSpacing(0)
        self.hboxLayout33.setObjectName(u"hboxLayout33")
        self.hboxLayout33.setContentsMargins(0, 0, 0, 0)
        self.frame_scope_status_bar_black = QFrame(self.frame_scope_status_bar_white)
        self.frame_scope_status_bar_black.setObjectName(u"frame_scope_status_bar_black")
        self.frame_scope_status_bar_black.setProperty(u"wpGrad", False)
        self.hboxLayout34 = QHBoxLayout(self.frame_scope_status_bar_black)
        self.hboxLayout34.setObjectName(u"hboxLayout34")
        self.horizontalLayout_scope_status_bar = QHBoxLayout()
        self.horizontalLayout_scope_status_bar.setSpacing(0)
        self.horizontalLayout_scope_status_bar.setObjectName(u"horizontalLayout_scope_status_bar")
        self.label_StatusBar_min_name = QLabel(self.frame_scope_status_bar_black)
        self.label_StatusBar_min_name.setObjectName(u"label_StatusBar_min_name")
        sizePolicy20 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
        sizePolicy20.setHorizontalStretch(0)
        sizePolicy20.setVerticalStretch(0)
        sizePolicy20.setHeightForWidth(self.label_StatusBar_min_name.sizePolicy().hasHeightForWidth())
        self.label_StatusBar_min_name.setSizePolicy(sizePolicy20)

        self.horizontalLayout_scope_status_bar.addWidget(self.label_StatusBar_min_name)

        self.label_StatusBar_min_value = QLabel(self.frame_scope_status_bar_black)
        self.label_StatusBar_min_value.setObjectName(u"label_StatusBar_min_value")
        sizePolicy16.setHeightForWidth(self.label_StatusBar_min_value.sizePolicy().hasHeightForWidth())
        self.label_StatusBar_min_value.setSizePolicy(sizePolicy16)
        self.label_StatusBar_min_value.setMinimumSize(QSize(50, 0))
        self.label_StatusBar_min_value.setMaximumSize(QSize(100, 16777215))
        self.label_StatusBar_min_value.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.label_StatusBar_min_value.setIndent(-1)

        self.horizontalLayout_scope_status_bar.addWidget(self.label_StatusBar_min_value)

        self.label_StatusBar_max_name = QLabel(self.frame_scope_status_bar_black)
        self.label_StatusBar_max_name.setObjectName(u"label_StatusBar_max_name")
        sizePolicy20.setHeightForWidth(self.label_StatusBar_max_name.sizePolicy().hasHeightForWidth())
        self.label_StatusBar_max_name.setSizePolicy(sizePolicy20)

        self.horizontalLayout_scope_status_bar.addWidget(self.label_StatusBar_max_name)

        self.label_StatusBar_max_value = QLabel(self.frame_scope_status_bar_black)
        self.label_StatusBar_max_value.setObjectName(u"label_StatusBar_max_value")
        self.label_StatusBar_max_value.setEnabled(True)
        sizePolicy16.setHeightForWidth(self.label_StatusBar_max_value.sizePolicy().hasHeightForWidth())
        self.label_StatusBar_max_value.setSizePolicy(sizePolicy16)
        self.label_StatusBar_max_value.setMinimumSize(QSize(50, 0))
        self.label_StatusBar_max_value.setMaximumSize(QSize(100, 16777215))
        self.label_StatusBar_max_value.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_scope_status_bar.addWidget(self.label_StatusBar_max_value)

        self.label_StatusBar_mean_name = QLabel(self.frame_scope_status_bar_black)
        self.label_StatusBar_mean_name.setObjectName(u"label_StatusBar_mean_name")
        sizePolicy20.setHeightForWidth(self.label_StatusBar_mean_name.sizePolicy().hasHeightForWidth())
        self.label_StatusBar_mean_name.setSizePolicy(sizePolicy20)

        self.horizontalLayout_scope_status_bar.addWidget(self.label_StatusBar_mean_name)

        self.label_StatusBar_mean_value = QLabel(self.frame_scope_status_bar_black)
        self.label_StatusBar_mean_value.setObjectName(u"label_StatusBar_mean_value")
        sizePolicy16.setHeightForWidth(self.label_StatusBar_mean_value.sizePolicy().hasHeightForWidth())
        self.label_StatusBar_mean_value.setSizePolicy(sizePolicy16)
        self.label_StatusBar_mean_value.setMinimumSize(QSize(50, 0))
        self.label_StatusBar_mean_value.setMaximumSize(QSize(100, 16777215))
        self.label_StatusBar_mean_value.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_scope_status_bar.addWidget(self.label_StatusBar_mean_value)

        self.label_StatusBar_area_name = QLabel(self.frame_scope_status_bar_black)
        self.label_StatusBar_area_name.setObjectName(u"label_StatusBar_area_name")
        sizePolicy20.setHeightForWidth(self.label_StatusBar_area_name.sizePolicy().hasHeightForWidth())
        self.label_StatusBar_area_name.setSizePolicy(sizePolicy20)

        self.horizontalLayout_scope_status_bar.addWidget(self.label_StatusBar_area_name)

        self.label_StatusBar_area_value = QLabel(self.frame_scope_status_bar_black)
        self.label_StatusBar_area_value.setObjectName(u"label_StatusBar_area_value")
        sizePolicy16.setHeightForWidth(self.label_StatusBar_area_value.sizePolicy().hasHeightForWidth())
        self.label_StatusBar_area_value.setSizePolicy(sizePolicy16)
        self.label_StatusBar_area_value.setMinimumSize(QSize(80, 0))
        self.label_StatusBar_area_value.setMaximumSize(QSize(100, 16777215))
        self.label_StatusBar_area_value.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_scope_status_bar.addWidget(self.label_StatusBar_area_value)

        self.label_StatusBar_detector_temp_name = QLabel(self.frame_scope_status_bar_black)
        self.label_StatusBar_detector_temp_name.setObjectName(u"label_StatusBar_detector_temp_name")
        sizePolicy20.setHeightForWidth(self.label_StatusBar_detector_temp_name.sizePolicy().hasHeightForWidth())
        self.label_StatusBar_detector_temp_name.setSizePolicy(sizePolicy20)
        self.label_StatusBar_detector_temp_name.setMaximumSize(QSize(100, 16777215))

        self.horizontalLayout_scope_status_bar.addWidget(self.label_StatusBar_detector_temp_name)

        self.label_StatusBar_detector_temp_value = QLabel(self.frame_scope_status_bar_black)
        self.label_StatusBar_detector_temp_value.setObjectName(u"label_StatusBar_detector_temp_value")
        self.label_StatusBar_detector_temp_value.setMinimumSize(QSize(50, 0))
        self.label_StatusBar_detector_temp_value.setMaximumSize(QSize(100, 16777215))
        self.label_StatusBar_detector_temp_value.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_scope_status_bar.addWidget(self.label_StatusBar_detector_temp_value)

        self.label_StatusBar_laser_temp_name = QLabel(self.frame_scope_status_bar_black)
        self.label_StatusBar_laser_temp_name.setObjectName(u"label_StatusBar_laser_temp_name")
        sizePolicy20.setHeightForWidth(self.label_StatusBar_laser_temp_name.sizePolicy().hasHeightForWidth())
        self.label_StatusBar_laser_temp_name.setSizePolicy(sizePolicy20)
        self.label_StatusBar_laser_temp_name.setMaximumSize(QSize(100, 16777215))

        self.horizontalLayout_scope_status_bar.addWidget(self.label_StatusBar_laser_temp_name)

        self.label_StatusBar_laser_temp_value = QLabel(self.frame_scope_status_bar_black)
        self.label_StatusBar_laser_temp_value.setObjectName(u"label_StatusBar_laser_temp_value")
        self.label_StatusBar_laser_temp_value.setMinimumSize(QSize(50, 0))
        self.label_StatusBar_laser_temp_value.setMaximumSize(QSize(100, 16777215))
        self.label_StatusBar_laser_temp_value.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_scope_status_bar.addWidget(self.label_StatusBar_laser_temp_value)

        self.label_StatusBar_cursor_name = QLabel(self.frame_scope_status_bar_black)
        self.label_StatusBar_cursor_name.setObjectName(u"label_StatusBar_cursor_name")
        sizePolicy20.setHeightForWidth(self.label_StatusBar_cursor_name.sizePolicy().hasHeightForWidth())
        self.label_StatusBar_cursor_name.setSizePolicy(sizePolicy20)
        self.label_StatusBar_cursor_name.setMaximumSize(QSize(100, 16777215))

        self.horizontalLayout_scope_status_bar.addWidget(self.label_StatusBar_cursor_name)

        self.label_StatusBar_cursor_value = QLabel(self.frame_scope_status_bar_black)
        self.label_StatusBar_cursor_value.setObjectName(u"label_StatusBar_cursor_value")
        sizePolicy16.setHeightForWidth(self.label_StatusBar_cursor_value.sizePolicy().hasHeightForWidth())
        self.label_StatusBar_cursor_value.setSizePolicy(sizePolicy16)
        self.label_StatusBar_cursor_value.setMinimumSize(QSize(50, 0))
        self.label_StatusBar_cursor_value.setMaximumSize(QSize(80, 16777215))
        self.label_StatusBar_cursor_value.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_scope_status_bar.addWidget(self.label_StatusBar_cursor_value)

        self.label_StatusBar_count_name = QLabel(self.frame_scope_status_bar_black)
        self.label_StatusBar_count_name.setObjectName(u"label_StatusBar_count_name")
        sizePolicy20.setHeightForWidth(self.label_StatusBar_count_name.sizePolicy().hasHeightForWidth())
        self.label_StatusBar_count_name.setSizePolicy(sizePolicy20)

        self.horizontalLayout_scope_status_bar.addWidget(self.label_StatusBar_count_name)

        self.label_StatusBar_count_value = QLabel(self.frame_scope_status_bar_black)
        self.label_StatusBar_count_value.setObjectName(u"label_StatusBar_count_value")
        sizePolicy16.setHeightForWidth(self.label_StatusBar_count_value.sizePolicy().hasHeightForWidth())
        self.label_StatusBar_count_value.setSizePolicy(sizePolicy16)
        self.label_StatusBar_count_value.setMaximumSize(QSize(100, 16777215))
        self.label_StatusBar_count_value.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_scope_status_bar.addWidget(self.label_StatusBar_count_value)

        self.label_StatusBar_battery_name = QLabel(self.frame_scope_status_bar_black)
        self.label_StatusBar_battery_name.setObjectName(u"label_StatusBar_battery_name")
        sizePolicy20.setHeightForWidth(self.label_StatusBar_battery_name.sizePolicy().hasHeightForWidth())
        self.label_StatusBar_battery_name.setSizePolicy(sizePolicy20)

        self.horizontalLayout_scope_status_bar.addWidget(self.label_StatusBar_battery_name)

        self.label_StatusBar_battery_value = QLabel(self.frame_scope_status_bar_black)
        self.label_StatusBar_battery_value.setObjectName(u"label_StatusBar_battery_value")
        sizePolicy16.setHeightForWidth(self.label_StatusBar_battery_value.sizePolicy().hasHeightForWidth())
        self.label_StatusBar_battery_value.setSizePolicy(sizePolicy16)
        self.label_StatusBar_battery_value.setMaximumSize(QSize(100, 16777215))
        self.label_StatusBar_battery_value.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_scope_status_bar.addWidget(self.label_StatusBar_battery_value)


        self.hboxLayout34.addLayout(self.horizontalLayout_scope_status_bar)

        self.spacerItem24 = QSpacerItem(20, 20, QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Minimum)

        self.hboxLayout34.addItem(self.spacerItem24)

        self.status_bar_toolButton = QToolButton(self.frame_scope_status_bar_black)
        self.status_bar_toolButton.setObjectName(u"status_bar_toolButton")
        self.status_bar_toolButton.setCheckable(False)
        self.status_bar_toolButton.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

        self.hboxLayout34.addWidget(self.status_bar_toolButton)


        self.hboxLayout33.addWidget(self.frame_scope_status_bar_black)


        self.vboxLayout67.addWidget(self.frame_scope_status_bar_white)


        self.gridLayout6.addWidget(self.frame_scope_capture_middle_nest, 0, 1, 1, 1)


        self.vboxLayout66.addWidget(self.frame_scope_capture_middle)

        self.splitter_saves_vs_graph.addWidget(self.frame_new_scope_capture_holder)

        self.verticalLayout_new_splitter.addWidget(self.splitter_saves_vs_graph)

        self.stackedWidget_low.addWidget(self.page_scope)
        self.page_logging = QWidget()
        self.page_logging.setObjectName(u"page_logging")
        sizePolicy6.setHeightForWidth(self.page_logging.sizePolicy().hasHeightForWidth())
        self.page_logging.setSizePolicy(sizePolicy6)
        self.vboxLayout70 = QVBoxLayout(self.page_logging)
        self.vboxLayout70.setObjectName(u"vboxLayout70")
        self.hboxLayout35 = QHBoxLayout()
        self.hboxLayout35.setObjectName(u"hboxLayout35")
        self.hboxLayout35.setContentsMargins(-1, 0, -1, -1)
        self.checkBox_logging_verbose = QCheckBox(self.page_logging)
        self.checkBox_logging_verbose.setObjectName(u"checkBox_logging_verbose")
        sizePolicy14.setHeightForWidth(self.checkBox_logging_verbose.sizePolicy().hasHeightForWidth())
        self.checkBox_logging_verbose.setSizePolicy(sizePolicy14)
        self.checkBox_logging_verbose.setMinimumSize(QSize(0, 30))
        self.checkBox_logging_verbose.setMaximumSize(QSize(16777215, 30))

        self.hboxLayout35.addWidget(self.checkBox_logging_verbose)

        self.checkBox_logging_pause = QCheckBox(self.page_logging)
        self.checkBox_logging_pause.setObjectName(u"checkBox_logging_pause")

        self.hboxLayout35.addWidget(self.checkBox_logging_pause)

        self.checkBox_logging_firmware = QCheckBox(self.page_logging)
        self.checkBox_logging_firmware.setObjectName(u"checkBox_logging_firmware")

        self.hboxLayout35.addWidget(self.checkBox_logging_firmware)

        self.spacerItem25 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.hboxLayout35.addItem(self.spacerItem25)

        self.pushButton_copy_log_to_clipboard = QPushButton(self.page_logging)
        self.pushButton_copy_log_to_clipboard.setObjectName(u"pushButton_copy_log_to_clipboard")
        sizePolicy3.setHeightForWidth(self.pushButton_copy_log_to_clipboard.sizePolicy().hasHeightForWidth())
        self.pushButton_copy_log_to_clipboard.setSizePolicy(sizePolicy3)
        self.pushButton_copy_log_to_clipboard.setMinimumSize(QSize(16, 26))
        self.pushButton_copy_log_to_clipboard.setMaximumSize(QSize(30, 26))
        self.pushButton_copy_log_to_clipboard.setIcon(icon6)
        self.pushButton_copy_log_to_clipboard.setIconSize(QSize(24, 24))

        self.hboxLayout35.addWidget(self.pushButton_copy_log_to_clipboard)


        self.vboxLayout70.addLayout(self.hboxLayout35)

        self.frame_logging_white = QFrame(self.page_logging)
        self.frame_logging_white.setObjectName(u"frame_logging_white")
        self.frame_logging_white.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_logging_white.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_logging_white.setProperty(u"wpBox", False)
        self.vboxLayout71 = QVBoxLayout(self.frame_logging_white)
        self.vboxLayout71.setObjectName(u"vboxLayout71")
        self.vboxLayout71.setContentsMargins(0, 0, 0, 0)
        self.frame_logging_shaded = QFrame(self.frame_logging_white)
        self.frame_logging_shaded.setObjectName(u"frame_logging_shaded")
        self.frame_logging_shaded.setBaseSize(QSize(100, 100))
        self.frame_logging_shaded.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_logging_shaded.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_logging_shaded.setProperty(u"wpPanel", False)
        self.vboxLayout72 = QVBoxLayout(self.frame_logging_shaded)
        self.vboxLayout72.setObjectName(u"vboxLayout72")
        self.textEdit_log = QTextEdit(self.frame_logging_shaded)
        self.textEdit_log.setObjectName(u"textEdit_log")
        self.textEdit_log.setEnabled(True)
        sizePolicy6.setHeightForWidth(self.textEdit_log.sizePolicy().hasHeightForWidth())
        self.textEdit_log.setSizePolicy(sizePolicy6)
        self.textEdit_log.setMouseTracking(True)
        self.textEdit_log.setAcceptDrops(False)
        self.textEdit_log.setStyleSheet(u"background-color: transparent; border-color: transparent;")
        self.textEdit_log.setLineWidth(1)
        self.textEdit_log.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.textEdit_log.setDocumentTitle(u"")
        self.textEdit_log.setUndoRedoEnabled(False)
        self.textEdit_log.setHtml(u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'DejaVu Sans Mono';\"><br /></p></body></html>")
        self.textEdit_log.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByKeyboard|Qt.TextInteractionFlag.TextSelectableByMouse)
        self.textEdit_log.setPlaceholderText(u"")

        self.vboxLayout72.addWidget(self.textEdit_log)


        self.vboxLayout71.addWidget(self.frame_logging_shaded)


        self.vboxLayout70.addWidget(self.frame_logging_white)

        self.stackedWidget_low.addWidget(self.page_logging)
        self.splitter_left_vs_controls.addWidget(self.stackedWidget_low)
        self.controlWidget = QFrame(self.splitter_left_vs_controls)
        self.controlWidget.setObjectName(u"controlWidget")
        sizePolicy21 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy21.setHorizontalStretch(5)
        sizePolicy21.setVerticalStretch(0)
        sizePolicy21.setHeightForWidth(self.controlWidget.sizePolicy().hasHeightForWidth())
        self.controlWidget.setSizePolicy(sizePolicy21)
        self.controlWidget.setMaximumSize(QSize(260, 16777215))
        self.controlWidget_grid = QGridLayout(self.controlWidget)
        self.controlWidget_grid.setSpacing(0)
        self.controlWidget_grid.setObjectName(u"controlWidget_grid")
        self.controlWidget_grid.setContentsMargins(0, 3, 0, 0)
        self.controlWidget_shaded = QFrame(self.controlWidget)
        self.controlWidget_shaded.setObjectName(u"controlWidget_shaded")
        sizePolicy16.setHeightForWidth(self.controlWidget_shaded.sizePolicy().hasHeightForWidth())
        self.controlWidget_shaded.setSizePolicy(sizePolicy16)
        self.vboxLayout73 = QVBoxLayout(self.controlWidget_shaded)
        self.vboxLayout73.setObjectName(u"vboxLayout73")
        self.vboxLayout73.setContentsMargins(0, 0, 0, 4)
        self.frame_vcr_control_white = QFrame(self.controlWidget_shaded)
        self.frame_vcr_control_white.setObjectName(u"frame_vcr_control_white")
        sizePolicy16.setHeightForWidth(self.frame_vcr_control_white.sizePolicy().hasHeightForWidth())
        self.frame_vcr_control_white.setSizePolicy(sizePolicy16)
        self.frame_vcr_control_white.setProperty(u"wpBox", False)
        self.hboxLayout36 = QHBoxLayout(self.frame_vcr_control_white)
        self.hboxLayout36.setSpacing(0)
        self.hboxLayout36.setObjectName(u"hboxLayout36")
        self.hboxLayout36.setContentsMargins(0, 0, 0, 0)
        self.frame_vcr_control_shaded = QFrame(self.frame_vcr_control_white)
        self.frame_vcr_control_shaded.setObjectName(u"frame_vcr_control_shaded")
        self.frame_vcr_control_shaded.setProperty(u"wpGrad", False)
        self.hboxLayout37 = QHBoxLayout(self.frame_vcr_control_shaded)
        self.hboxLayout37.setSpacing(0)
        self.hboxLayout37.setObjectName(u"hboxLayout37")
        self.hboxLayout38 = QHBoxLayout()
        self.hboxLayout38.setSpacing(9)
        self.hboxLayout38.setObjectName(u"hboxLayout38")
        self.pushButton_scope_capture_play = QPushButton(self.frame_vcr_control_shaded)
        self.pushButton_scope_capture_play.setObjectName(u"pushButton_scope_capture_play")
        sizePolicy22 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy22.setHorizontalStretch(10)
        sizePolicy22.setVerticalStretch(0)
        sizePolicy22.setHeightForWidth(self.pushButton_scope_capture_play.sizePolicy().hasHeightForWidth())
        self.pushButton_scope_capture_play.setSizePolicy(sizePolicy22)
        self.pushButton_scope_capture_play.setMinimumSize(QSize(0, 32))
        self.pushButton_scope_capture_play.setMaximumSize(QSize(67, 40))
        self.pushButton_scope_capture_play.setBaseSize(QSize(67, 0))
        icon28 = QIcon()
        icon28.addFile(u":/greys/images/grey_icons/right_triangle.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_scope_capture_play.setIcon(icon28)
        self.pushButton_scope_capture_play.setIconSize(QSize(14, 14))

        self.hboxLayout38.addWidget(self.pushButton_scope_capture_play)

        self.pushButton_scope_capture_pause = QPushButton(self.frame_vcr_control_shaded)
        self.pushButton_scope_capture_pause.setObjectName(u"pushButton_scope_capture_pause")
        sizePolicy22.setHeightForWidth(self.pushButton_scope_capture_pause.sizePolicy().hasHeightForWidth())
        self.pushButton_scope_capture_pause.setSizePolicy(sizePolicy22)
        self.pushButton_scope_capture_pause.setMinimumSize(QSize(0, 32))
        self.pushButton_scope_capture_pause.setMaximumSize(QSize(67, 40))
        self.pushButton_scope_capture_pause.setBaseSize(QSize(67, 0))
        icon29 = QIcon()
        icon29.addFile(u":/greys/images/grey_icons/pause.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_scope_capture_pause.setIcon(icon29)
        self.pushButton_scope_capture_pause.setIconSize(QSize(30, 30))

        self.hboxLayout38.addWidget(self.pushButton_scope_capture_pause)

        self.pushButton_scope_capture_stop = QPushButton(self.frame_vcr_control_shaded)
        self.pushButton_scope_capture_stop.setObjectName(u"pushButton_scope_capture_stop")
        sizePolicy22.setHeightForWidth(self.pushButton_scope_capture_stop.sizePolicy().hasHeightForWidth())
        self.pushButton_scope_capture_stop.setSizePolicy(sizePolicy22)
        self.pushButton_scope_capture_stop.setMinimumSize(QSize(0, 32))
        self.pushButton_scope_capture_stop.setMaximumSize(QSize(67, 40))
        self.pushButton_scope_capture_stop.setBaseSize(QSize(67, 0))
        icon30 = QIcon()
        icon30.addFile(u":/greys/images/grey_icons/square.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_scope_capture_stop.setIcon(icon30)

        self.hboxLayout38.addWidget(self.pushButton_scope_capture_stop)

        self.pushButton_scope_capture_save = QPushButton(self.frame_vcr_control_shaded)
        self.pushButton_scope_capture_save.setObjectName(u"pushButton_scope_capture_save")
        sizePolicy22.setHeightForWidth(self.pushButton_scope_capture_save.sizePolicy().hasHeightForWidth())
        self.pushButton_scope_capture_save.setSizePolicy(sizePolicy22)
        self.pushButton_scope_capture_save.setMinimumSize(QSize(0, 32))
        self.pushButton_scope_capture_save.setMaximumSize(QSize(67, 40))
        self.pushButton_scope_capture_save.setBaseSize(QSize(67, 0))
        self.pushButton_scope_capture_save.setIcon(icon14)

        self.hboxLayout38.addWidget(self.pushButton_scope_capture_save)

        self.pushButton_scope_capture_step = QPushButton(self.frame_vcr_control_shaded)
        self.pushButton_scope_capture_step.setObjectName(u"pushButton_scope_capture_step")
        sizePolicy22.setHeightForWidth(self.pushButton_scope_capture_step.sizePolicy().hasHeightForWidth())
        self.pushButton_scope_capture_step.setSizePolicy(sizePolicy22)
        self.pushButton_scope_capture_step.setMinimumSize(QSize(0, 32))
        self.pushButton_scope_capture_step.setMaximumSize(QSize(67, 40))
        self.pushButton_scope_capture_step.setBaseSize(QSize(67, 0))
        icon31 = QIcon()
        icon31.addFile(u":/greys/images/grey_icons/step-forward.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_scope_capture_step.setIcon(icon31)
        self.pushButton_scope_capture_step.setIconSize(QSize(20, 16))

        self.hboxLayout38.addWidget(self.pushButton_scope_capture_step)

        self.pushButton_scope_capture_start_collection = QPushButton(self.frame_vcr_control_shaded)
        self.pushButton_scope_capture_start_collection.setObjectName(u"pushButton_scope_capture_start_collection")
        sizePolicy22.setHeightForWidth(self.pushButton_scope_capture_start_collection.sizePolicy().hasHeightForWidth())
        self.pushButton_scope_capture_start_collection.setSizePolicy(sizePolicy22)
        self.pushButton_scope_capture_start_collection.setMinimumSize(QSize(0, 32))
        self.pushButton_scope_capture_start_collection.setMaximumSize(QSize(67, 40))
        self.pushButton_scope_capture_start_collection.setBaseSize(QSize(67, 0))
        icon32 = QIcon()
        icon32.addFile(u":/greys/images/grey_icons/fast-forward.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_scope_capture_start_collection.setIcon(icon32)

        self.hboxLayout38.addWidget(self.pushButton_scope_capture_start_collection)

        self.pushButton_scope_capture_step_save = QPushButton(self.frame_vcr_control_shaded)
        self.pushButton_scope_capture_step_save.setObjectName(u"pushButton_scope_capture_step_save")
        sizePolicy22.setHeightForWidth(self.pushButton_scope_capture_step_save.sizePolicy().hasHeightForWidth())
        self.pushButton_scope_capture_step_save.setSizePolicy(sizePolicy22)
        self.pushButton_scope_capture_step_save.setMinimumSize(QSize(0, 32))
        self.pushButton_scope_capture_step_save.setMaximumSize(QSize(67, 40))
        self.pushButton_scope_capture_step_save.setBaseSize(QSize(67, 0))
        icon33 = QIcon()
        icon33.addFile(u":/greys/images/grey_icons/step-and-save.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_scope_capture_step_save.setIcon(icon33)

        self.hboxLayout38.addWidget(self.pushButton_scope_capture_step_save)


        self.hboxLayout37.addLayout(self.hboxLayout38)


        self.hboxLayout36.addWidget(self.frame_vcr_control_shaded)


        self.vboxLayout73.addWidget(self.frame_vcr_control_white)

        self.controlWidget_scrollArea = QScrollArea(self.controlWidget_shaded)
        self.controlWidget_scrollArea.setObjectName(u"controlWidget_scrollArea")
        self.controlWidget_scrollArea.setMinimumSize(QSize(0, 24))
        self.controlWidget_scrollArea.setWidgetResizable(True)
        self.controlWidget_inner = QWidget()
        self.controlWidget_inner.setObjectName(u"controlWidget_inner")
        self.controlWidget_inner.setGeometry(QRect(0, 0, 284, 3306))
        sizePolicy16.setHeightForWidth(self.controlWidget_inner.sizePolicy().hasHeightForWidth())
        self.controlWidget_inner.setSizePolicy(sizePolicy16)
        self.controlWidget_inner.setStyleSheet(u"")
        self.controlWidget_inner_vbox = QVBoxLayout(self.controlWidget_inner)
        self.controlWidget_inner_vbox.setSpacing(6)
        self.controlWidget_inner_vbox.setObjectName(u"controlWidget_inner_vbox")
        self.controlWidget_inner_vbox.setContentsMargins(0, 0, 0, 0)
        self.frame_multiSpecWidget = QFrame(self.controlWidget_inner)
        self.frame_multiSpecWidget.setObjectName(u"frame_multiSpecWidget")
        sizePolicy16.setHeightForWidth(self.frame_multiSpecWidget.sizePolicy().hasHeightForWidth())
        self.frame_multiSpecWidget.setSizePolicy(sizePolicy16)
        self.frame_multiSpecWidget.setMinimumSize(QSize(0, 0))
        self.vboxLayout74 = QVBoxLayout(self.frame_multiSpecWidget)
        self.vboxLayout74.setObjectName(u"vboxLayout74")
        self.vboxLayout74.setContentsMargins(0, 0, 0, 0)
        self.label_multiSpecWidget_title = QLabel(self.frame_multiSpecWidget)
        self.label_multiSpecWidget_title.setObjectName(u"label_multiSpecWidget_title")
        sizePolicy16.setHeightForWidth(self.label_multiSpecWidget_title.sizePolicy().hasHeightForWidth())
        self.label_multiSpecWidget_title.setSizePolicy(sizePolicy16)
        self.label_multiSpecWidget_title.setFont(font2)

        self.vboxLayout74.addWidget(self.label_multiSpecWidget_title)

        self.frame_multiSpecWidget_white = QFrame(self.frame_multiSpecWidget)
        self.frame_multiSpecWidget_white.setObjectName(u"frame_multiSpecWidget_white")
        sizePolicy16.setHeightForWidth(self.frame_multiSpecWidget_white.sizePolicy().hasHeightForWidth())
        self.frame_multiSpecWidget_white.setSizePolicy(sizePolicy16)
        self.frame_multiSpecWidget_white.setLineWidth(1)
        self.frame_multiSpecWidget_white.setProperty(u"wpBox", False)
        self.boxcarWidget_grid_5 = QGridLayout(self.frame_multiSpecWidget_white)
        self.boxcarWidget_grid_5.setSpacing(0)
        self.boxcarWidget_grid_5.setObjectName(u"boxcarWidget_grid_5")
        self.boxcarWidget_grid_5.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.boxcarWidget_grid_5.setContentsMargins(0, 0, 0, 0)
        self.frame_multiSpecWidget_black = QFrame(self.frame_multiSpecWidget_white)
        self.frame_multiSpecWidget_black.setObjectName(u"frame_multiSpecWidget_black")
        sizePolicy16.setHeightForWidth(self.frame_multiSpecWidget_black.sizePolicy().hasHeightForWidth())
        self.frame_multiSpecWidget_black.setSizePolicy(sizePolicy16)
        self.frame_multiSpecWidget_black.setLineWidth(1)
        self.frame_multiSpecWidget_black.setProperty(u"wpGrad", False)
        self.vboxLayout75 = QVBoxLayout(self.frame_multiSpecWidget_black)
        self.vboxLayout75.setSpacing(7)
        self.vboxLayout75.setObjectName(u"vboxLayout75")
        self.vboxLayout75.setContentsMargins(5, 5, 5, 5)
        self.horizontalLayout_multiSpec_colors_2 = QHBoxLayout()
        self.horizontalLayout_multiSpec_colors_2.setSpacing(0)
        self.horizontalLayout_multiSpec_colors_2.setObjectName(u"horizontalLayout_multiSpec_colors_2")
        self.comboBox_multiSpec = QComboBox(self.frame_multiSpecWidget_black)
        self.comboBox_multiSpec.addItem("")
        self.comboBox_multiSpec.setObjectName(u"comboBox_multiSpec")
        sizePolicy6.setHeightForWidth(self.comboBox_multiSpec.sizePolicy().hasHeightForWidth())
        self.comboBox_multiSpec.setSizePolicy(sizePolicy6)
        self.comboBox_multiSpec.setMinimumSize(QSize(0, 50))
        self.comboBox_multiSpec.setMaximumSize(QSize(16777215, 40))
        self.comboBox_multiSpec.setFont(font)
        self.comboBox_multiSpec.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.comboBox_multiSpec.setEditable(False)

        self.horizontalLayout_multiSpec_colors_2.addWidget(self.comboBox_multiSpec)

        self.pushButton_eject = QPushButton(self.frame_multiSpecWidget_black)
        self.pushButton_eject.setObjectName(u"pushButton_eject")
        sizePolicy16.setHeightForWidth(self.pushButton_eject.sizePolicy().hasHeightForWidth())
        self.pushButton_eject.setSizePolicy(sizePolicy16)
        self.pushButton_eject.setMinimumSize(QSize(30, 26))
        self.pushButton_eject.setMaximumSize(QSize(30, 26))
        icon34 = QIcon()
        icon34.addFile(u":/greys/images/grey_icons/eject.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_eject.setIcon(icon34)

        self.horizontalLayout_multiSpec_colors_2.addWidget(self.pushButton_eject)


        self.vboxLayout75.addLayout(self.horizontalLayout_multiSpec_colors_2)

        self.horizontalLayout_multiSpec_others = QHBoxLayout()
        self.horizontalLayout_multiSpec_others.setSpacing(0)
        self.horizontalLayout_multiSpec_others.setObjectName(u"horizontalLayout_multiSpec_others")
        self.checkBox_multiSpec_hide_others = QCheckBox(self.frame_multiSpecWidget_black)
        self.checkBox_multiSpec_hide_others.setObjectName(u"checkBox_multiSpec_hide_others")
        sizePolicy16.setHeightForWidth(self.checkBox_multiSpec_hide_others.sizePolicy().hasHeightForWidth())
        self.checkBox_multiSpec_hide_others.setSizePolicy(sizePolicy16)
        self.checkBox_multiSpec_hide_others.setMaximumSize(QSize(16777215, 50))

        self.horizontalLayout_multiSpec_others.addWidget(self.checkBox_multiSpec_hide_others)

        self.pushButton_multiSpec_lock = QPushButton(self.frame_multiSpecWidget_black)
        self.pushButton_multiSpec_lock.setObjectName(u"pushButton_multiSpec_lock")
        sizePolicy16.setHeightForWidth(self.pushButton_multiSpec_lock.sizePolicy().hasHeightForWidth())
        self.pushButton_multiSpec_lock.setSizePolicy(sizePolicy16)
        self.pushButton_multiSpec_lock.setMinimumSize(QSize(30, 26))
        self.pushButton_multiSpec_lock.setMaximumSize(QSize(30, 26))
        self.pushButton_multiSpec_lock.setIcon(icon15)

        self.horizontalLayout_multiSpec_others.addWidget(self.pushButton_multiSpec_lock)


        self.vboxLayout75.addLayout(self.horizontalLayout_multiSpec_others)

        self.horizontalLayout_multiSpec_colors = QHBoxLayout()
        self.horizontalLayout_multiSpec_colors.setSpacing(0)
        self.horizontalLayout_multiSpec_colors.setObjectName(u"horizontalLayout_multiSpec_colors")
        self.checkBox_multiSpec_autocolor = QCheckBox(self.frame_multiSpecWidget_black)
        self.checkBox_multiSpec_autocolor.setObjectName(u"checkBox_multiSpec_autocolor")
        sizePolicy16.setHeightForWidth(self.checkBox_multiSpec_autocolor.sizePolicy().hasHeightForWidth())
        self.checkBox_multiSpec_autocolor.setSizePolicy(sizePolicy16)
        self.checkBox_multiSpec_autocolor.setMaximumSize(QSize(16777215, 50))

        self.horizontalLayout_multiSpec_colors.addWidget(self.checkBox_multiSpec_autocolor)


        self.vboxLayout75.addLayout(self.horizontalLayout_multiSpec_colors)


        self.boxcarWidget_grid_5.addWidget(self.frame_multiSpecWidget_black, 0, 0, 1, 1)


        self.vboxLayout74.addWidget(self.frame_multiSpecWidget_white)


        self.controlWidget_inner_vbox.addWidget(self.frame_multiSpecWidget)

        self.frame_TechniqueWidget = QFrame(self.controlWidget_inner)
        self.frame_TechniqueWidget.setObjectName(u"frame_TechniqueWidget")
        sizePolicy16.setHeightForWidth(self.frame_TechniqueWidget.sizePolicy().hasHeightForWidth())
        self.frame_TechniqueWidget.setSizePolicy(sizePolicy16)
        self.vboxLayout76 = QVBoxLayout(self.frame_TechniqueWidget)
        self.vboxLayout76.setObjectName(u"vboxLayout76")
        self.vboxLayout76.setContentsMargins(0, 0, 0, 0)
        self.techniqueWidget_label = QLabel(self.frame_TechniqueWidget)
        self.techniqueWidget_label.setObjectName(u"techniqueWidget_label")
        sizePolicy16.setHeightForWidth(self.techniqueWidget_label.sizePolicy().hasHeightForWidth())
        self.techniqueWidget_label.setSizePolicy(sizePolicy16)
        self.techniqueWidget_label.setFont(font2)

        self.vboxLayout76.addWidget(self.techniqueWidget_label)

        self.frame_Technique_white = QFrame(self.frame_TechniqueWidget)
        self.frame_Technique_white.setObjectName(u"frame_Technique_white")
        sizePolicy16.setHeightForWidth(self.frame_Technique_white.sizePolicy().hasHeightForWidth())
        self.frame_Technique_white.setSizePolicy(sizePolicy16)
        self.frame_Technique_white.setLineWidth(1)
        self.frame_Technique_white.setProperty(u"wpBox", False)
        self.random_grid_1 = QGridLayout(self.frame_Technique_white)
        self.random_grid_1.setSpacing(0)
        self.random_grid_1.setObjectName(u"random_grid_1")
        self.random_grid_1.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.random_grid_1.setContentsMargins(0, 0, 0, 0)
        self.techniqueWidget_shaded = QFrame(self.frame_Technique_white)
        self.techniqueWidget_shaded.setObjectName(u"techniqueWidget_shaded")
        sizePolicy16.setHeightForWidth(self.techniqueWidget_shaded.sizePolicy().hasHeightForWidth())
        self.techniqueWidget_shaded.setSizePolicy(sizePolicy16)
        self.techniqueWidget_shaded.setMinimumSize(QSize(0, 0))
        self.techniqueWidget_shaded.setMaximumSize(QSize(16777215, 16777215))
        self.techniqueWidget_shaded.setLineWidth(1)
        self.techniqueWidget_shaded.setProperty(u"wpGrad", False)
        self.vboxLayout77 = QVBoxLayout(self.techniqueWidget_shaded)
        self.vboxLayout77.setObjectName(u"vboxLayout77")
        self.comboBox_technique = QComboBox(self.techniqueWidget_shaded)
        self.comboBox_technique.addItem("")
        self.comboBox_technique.addItem("")
        self.comboBox_technique.addItem("")
        self.comboBox_technique.setObjectName(u"comboBox_technique")
        sizePolicy16.setHeightForWidth(self.comboBox_technique.sizePolicy().hasHeightForWidth())
        self.comboBox_technique.setSizePolicy(sizePolicy16)
        self.comboBox_technique.setMinimumSize(QSize(80, 22))
        self.comboBox_technique.setFont(font)
        self.comboBox_technique.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.vboxLayout77.addWidget(self.comboBox_technique)


        self.random_grid_1.addWidget(self.techniqueWidget_shaded, 0, 0, 1, 1)


        self.vboxLayout76.addWidget(self.frame_Technique_white)


        self.controlWidget_inner_vbox.addWidget(self.frame_TechniqueWidget)

        self.frame_lightSourceControl = QFrame(self.controlWidget_inner)
        self.frame_lightSourceControl.setObjectName(u"frame_lightSourceControl")
        sizePolicy16.setHeightForWidth(self.frame_lightSourceControl.sizePolicy().hasHeightForWidth())
        self.frame_lightSourceControl.setSizePolicy(sizePolicy16)
        self.frame_lightSourceControl.setMinimumSize(QSize(0, 0))
        self.vboxLayout78 = QVBoxLayout(self.frame_lightSourceControl)
        self.vboxLayout78.setObjectName(u"vboxLayout78")
        self.vboxLayout78.setContentsMargins(0, 0, 0, 0)
        self.lightSourceWidget_label = QLabel(self.frame_lightSourceControl)
        self.lightSourceWidget_label.setObjectName(u"lightSourceWidget_label")
        sizePolicy16.setHeightForWidth(self.lightSourceWidget_label.sizePolicy().hasHeightForWidth())
        self.lightSourceWidget_label.setSizePolicy(sizePolicy16)
        self.lightSourceWidget_label.setMinimumSize(QSize(0, 17))
        self.lightSourceWidget_label.setMaximumSize(QSize(16777215, 9))
        self.lightSourceWidget_label.setFont(font2)

        self.vboxLayout78.addWidget(self.lightSourceWidget_label)

        self.lightSourceWidget_border = QFrame(self.frame_lightSourceControl)
        self.lightSourceWidget_border.setObjectName(u"lightSourceWidget_border")
        sizePolicy16.setHeightForWidth(self.lightSourceWidget_border.sizePolicy().hasHeightForWidth())
        self.lightSourceWidget_border.setSizePolicy(sizePolicy16)
        self.lightSourceWidget_border.setProperty(u"wpBox", False)
        self.lightSourceWidget_grid = QGridLayout(self.lightSourceWidget_border)
        self.lightSourceWidget_grid.setSpacing(0)
        self.lightSourceWidget_grid.setObjectName(u"lightSourceWidget_grid")
        self.lightSourceWidget_grid.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.lightSourceWidget_grid.setContentsMargins(0, 0, 0, 0)
        self.lightSourceWidget_shaded = QFrame(self.lightSourceWidget_border)
        self.lightSourceWidget_shaded.setObjectName(u"lightSourceWidget_shaded")
        sizePolicy16.setHeightForWidth(self.lightSourceWidget_shaded.sizePolicy().hasHeightForWidth())
        self.lightSourceWidget_shaded.setSizePolicy(sizePolicy16)
        self.lightSourceWidget_shaded.setMinimumSize(QSize(0, 0))
        self.lightSourceWidget_shaded.setMaximumSize(QSize(16777215, 16777215))
        self.lightSourceWidget_shaded.setLineWidth(1)
        self.lightSourceWidget_shaded.setProperty(u"wpGrad", False)
        self.vboxLayout79 = QVBoxLayout(self.lightSourceWidget_shaded)
        self.vboxLayout79.setObjectName(u"vboxLayout79")
        self.pushButton_laser_toggle = QPushButton(self.lightSourceWidget_shaded)
        self.pushButton_laser_toggle.setObjectName(u"pushButton_laser_toggle")
        sizePolicy1.setHeightForWidth(self.pushButton_laser_toggle.sizePolicy().hasHeightForWidth())
        self.pushButton_laser_toggle.setSizePolicy(sizePolicy1)
        self.pushButton_laser_toggle.setMinimumSize(QSize(0, 30))
        self.pushButton_laser_toggle.setFont(font)
        self.pushButton_laser_toggle.setIcon(icon2)
        self.pushButton_laser_toggle.setIconSize(QSize(28, 28))

        self.vboxLayout79.addWidget(self.pushButton_laser_toggle)

        self.hboxLayout39 = QHBoxLayout()
        self.hboxLayout39.setObjectName(u"hboxLayout39")
        self.verticalSlider_laser_power = QSlider(self.lightSourceWidget_shaded)
        self.verticalSlider_laser_power.setObjectName(u"verticalSlider_laser_power")
        sizePolicy16.setHeightForWidth(self.verticalSlider_laser_power.sizePolicy().hasHeightForWidth())
        self.verticalSlider_laser_power.setSizePolicy(sizePolicy16)
        self.verticalSlider_laser_power.setMaximumSize(QSize(30, 70))
        self.verticalSlider_laser_power.setMinimum(1)
        self.verticalSlider_laser_power.setMaximum(100)
        self.verticalSlider_laser_power.setValue(100)
        self.verticalSlider_laser_power.setOrientation(Qt.Orientation.Vertical)

        self.hboxLayout39.addWidget(self.verticalSlider_laser_power)

        self.vboxLayout80 = QVBoxLayout()
        self.vboxLayout80.setObjectName(u"vboxLayout80")
        self.hboxLayout40 = QHBoxLayout()
        self.hboxLayout40.setObjectName(u"hboxLayout40")
        self.pushButton_laser_power_dn = QPushButton(self.lightSourceWidget_shaded)
        self.pushButton_laser_power_dn.setObjectName(u"pushButton_laser_power_dn")
        sizePolicy1.setHeightForWidth(self.pushButton_laser_power_dn.sizePolicy().hasHeightForWidth())
        self.pushButton_laser_power_dn.setSizePolicy(sizePolicy1)
        self.pushButton_laser_power_dn.setMinimumSize(QSize(40, 40))
        self.pushButton_laser_power_dn.setMaximumSize(QSize(40, 40))
        self.pushButton_laser_power_dn.setIcon(icon14)
        self.pushButton_laser_power_dn.setIconSize(QSize(20, 20))
        self.pushButton_laser_power_dn.setAutoRepeat(True)

        self.hboxLayout40.addWidget(self.pushButton_laser_power_dn)

        self.pushButton_laser_power_up = QPushButton(self.lightSourceWidget_shaded)
        self.pushButton_laser_power_up.setObjectName(u"pushButton_laser_power_up")
        sizePolicy1.setHeightForWidth(self.pushButton_laser_power_up.sizePolicy().hasHeightForWidth())
        self.pushButton_laser_power_up.setSizePolicy(sizePolicy1)
        self.pushButton_laser_power_up.setMinimumSize(QSize(40, 40))
        self.pushButton_laser_power_up.setMaximumSize(QSize(40, 40))
        icon35 = QIcon()
        icon35.addFile(u":/greys/images/grey_icons/up_triangle.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_laser_power_up.setIcon(icon35)
        self.pushButton_laser_power_up.setIconSize(QSize(20, 20))
        self.pushButton_laser_power_up.setAutoRepeat(True)

        self.hboxLayout40.addWidget(self.pushButton_laser_power_up)


        self.vboxLayout80.addLayout(self.hboxLayout40)

        self.doubleSpinBox_laser_power = QDoubleSpinBox(self.lightSourceWidget_shaded)
        self.doubleSpinBox_laser_power.setObjectName(u"doubleSpinBox_laser_power")
        sizePolicy1.setHeightForWidth(self.doubleSpinBox_laser_power.sizePolicy().hasHeightForWidth())
        self.doubleSpinBox_laser_power.setSizePolicy(sizePolicy1)
        self.doubleSpinBox_laser_power.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.doubleSpinBox_laser_power.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.doubleSpinBox_laser_power.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.doubleSpinBox_laser_power.setKeyboardTracking(False)
        self.doubleSpinBox_laser_power.setDecimals(1)
        self.doubleSpinBox_laser_power.setSingleStep(10.000000000000000)
        self.doubleSpinBox_laser_power.setValue(100.000000000000000)

        self.vboxLayout80.addWidget(self.doubleSpinBox_laser_power)

        self.comboBox_laser_power_unit = QComboBox(self.lightSourceWidget_shaded)
        self.comboBox_laser_power_unit.addItem("")
        self.comboBox_laser_power_unit.addItem("")
        self.comboBox_laser_power_unit.setObjectName(u"comboBox_laser_power_unit")
        self.comboBox_laser_power_unit.setFont(font)

        self.vboxLayout80.addWidget(self.comboBox_laser_power_unit)


        self.hboxLayout39.addLayout(self.vboxLayout80)


        self.vboxLayout79.addLayout(self.hboxLayout39)

        self.formLayout_laser_control = QFormLayout()
        self.formLayout_laser_control.setObjectName(u"formLayout_laser_control")
        self.formLayout_laser_control.setLabelAlignment(Qt.AlignmentFlag.AlignCenter)
        self.formLayout_laser_control.setFormAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.formLayout_laser_control.setContentsMargins(-1, 0, -1, 0)
        self.doubleSpinBox_excitation_nm = QDoubleSpinBox(self.lightSourceWidget_shaded)
        self.doubleSpinBox_excitation_nm.setObjectName(u"doubleSpinBox_excitation_nm")
        sizePolicy1.setHeightForWidth(self.doubleSpinBox_excitation_nm.sizePolicy().hasHeightForWidth())
        self.doubleSpinBox_excitation_nm.setSizePolicy(sizePolicy1)
        self.doubleSpinBox_excitation_nm.setMinimumSize(QSize(100, 0))
        self.doubleSpinBox_excitation_nm.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.doubleSpinBox_excitation_nm.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.doubleSpinBox_excitation_nm.setDecimals(3)
        self.doubleSpinBox_excitation_nm.setMinimum(0.000000000000000)
        self.doubleSpinBox_excitation_nm.setMaximum(2500.000000000000000)
        self.doubleSpinBox_excitation_nm.setSingleStep(0.010000000000000)
        self.doubleSpinBox_excitation_nm.setValue(785.000000000000000)
        self.doubleSpinBox_excitation_nm.setProperty(u"initiallyVisible", False)

        self.formLayout_laser_control.setWidget(1, QFormLayout.ItemRole.LabelRole, self.doubleSpinBox_excitation_nm)

        self.label_lightSourceWidget_excitation_nm = QLabel(self.lightSourceWidget_shaded)
        self.label_lightSourceWidget_excitation_nm.setObjectName(u"label_lightSourceWidget_excitation_nm")
        sizePolicy16.setHeightForWidth(self.label_lightSourceWidget_excitation_nm.sizePolicy().hasHeightForWidth())
        self.label_lightSourceWidget_excitation_nm.setSizePolicy(sizePolicy16)
        self.label_lightSourceWidget_excitation_nm.setProperty(u"initiallyVisible", False)

        self.formLayout_laser_control.setWidget(1, QFormLayout.ItemRole.FieldRole, self.label_lightSourceWidget_excitation_nm)

        self.spinBox_laser_attenuator = QSpinBox(self.lightSourceWidget_shaded)
        self.spinBox_laser_attenuator.setObjectName(u"spinBox_laser_attenuator")
        sizePolicy1.setHeightForWidth(self.spinBox_laser_attenuator.sizePolicy().hasHeightForWidth())
        self.spinBox_laser_attenuator.setSizePolicy(sizePolicy1)
        self.spinBox_laser_attenuator.setMinimumSize(QSize(100, 0))
        self.spinBox_laser_attenuator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_laser_attenuator.setMinimum(0)
        self.spinBox_laser_attenuator.setMaximum(100)
        self.spinBox_laser_attenuator.setValue(0)

        self.formLayout_laser_control.setWidget(2, QFormLayout.ItemRole.LabelRole, self.spinBox_laser_attenuator)

        self.label_laser_control_attenuator = QLabel(self.lightSourceWidget_shaded)
        self.label_laser_control_attenuator.setObjectName(u"label_laser_control_attenuator")
        sizePolicy16.setHeightForWidth(self.label_laser_control_attenuator.sizePolicy().hasHeightForWidth())
        self.label_laser_control_attenuator.setSizePolicy(sizePolicy16)
        self.label_laser_control_attenuator.setProperty(u"initiallyVisible", False)

        self.formLayout_laser_control.setWidget(2, QFormLayout.ItemRole.FieldRole, self.label_laser_control_attenuator)

        self.spinBox_laser_watchdog_sec = QSpinBox(self.lightSourceWidget_shaded)
        self.spinBox_laser_watchdog_sec.setObjectName(u"spinBox_laser_watchdog_sec")
        sizePolicy1.setHeightForWidth(self.spinBox_laser_watchdog_sec.sizePolicy().hasHeightForWidth())
        self.spinBox_laser_watchdog_sec.setSizePolicy(sizePolicy1)
        self.spinBox_laser_watchdog_sec.setMinimumSize(QSize(100, 0))
        self.spinBox_laser_watchdog_sec.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_laser_watchdog_sec.setMinimum(3)
        self.spinBox_laser_watchdog_sec.setMaximum(1200)
        self.spinBox_laser_watchdog_sec.setValue(10)

        self.formLayout_laser_control.setWidget(3, QFormLayout.ItemRole.LabelRole, self.spinBox_laser_watchdog_sec)

        self.label_laser_watchdog_sec = QLabel(self.lightSourceWidget_shaded)
        self.label_laser_watchdog_sec.setObjectName(u"label_laser_watchdog_sec")
        sizePolicy16.setHeightForWidth(self.label_laser_watchdog_sec.sizePolicy().hasHeightForWidth())
        self.label_laser_watchdog_sec.setSizePolicy(sizePolicy16)

        self.formLayout_laser_control.setWidget(3, QFormLayout.ItemRole.FieldRole, self.label_laser_watchdog_sec)

        self.comboBox_laser_tec_mode = QComboBox(self.lightSourceWidget_shaded)
        self.comboBox_laser_tec_mode.addItem("")
        self.comboBox_laser_tec_mode.addItem("")
        self.comboBox_laser_tec_mode.addItem("")
        self.comboBox_laser_tec_mode.addItem("")
        self.comboBox_laser_tec_mode.setObjectName(u"comboBox_laser_tec_mode")
        sizePolicy1.setHeightForWidth(self.comboBox_laser_tec_mode.sizePolicy().hasHeightForWidth())
        self.comboBox_laser_tec_mode.setSizePolicy(sizePolicy1)
        self.comboBox_laser_tec_mode.setFont(font)

        self.formLayout_laser_control.setWidget(4, QFormLayout.ItemRole.LabelRole, self.comboBox_laser_tec_mode)

        self.label_laser_tec_mode = QLabel(self.lightSourceWidget_shaded)
        self.label_laser_tec_mode.setObjectName(u"label_laser_tec_mode")
        self.label_laser_tec_mode.setMaximumSize(QSize(16777215, 20))
        self.label_laser_tec_mode.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_laser_tec_mode.setWordWrap(True)

        self.formLayout_laser_control.setWidget(4, QFormLayout.ItemRole.FieldRole, self.label_laser_tec_mode)


        self.vboxLayout79.addLayout(self.formLayout_laser_control)

        self.checkBox_laser_watchdog = QCheckBox(self.lightSourceWidget_shaded)
        self.checkBox_laser_watchdog.setObjectName(u"checkBox_laser_watchdog")
        self.checkBox_laser_watchdog.setChecked(True)

        self.vboxLayout79.addWidget(self.checkBox_laser_watchdog)

        self.pushButton_auto_raman_measurement = QPushButton(self.lightSourceWidget_shaded)
        self.pushButton_auto_raman_measurement.setObjectName(u"pushButton_auto_raman_measurement")
        sizePolicy1.setHeightForWidth(self.pushButton_auto_raman_measurement.sizePolicy().hasHeightForWidth())
        self.pushButton_auto_raman_measurement.setSizePolicy(sizePolicy1)
        self.pushButton_auto_raman_measurement.setMinimumSize(QSize(0, 30))
        self.pushButton_auto_raman_measurement.setFont(font)
        self.pushButton_auto_raman_measurement.setIcon(icon1)
        self.pushButton_auto_raman_measurement.setIconSize(QSize(20, 20))

        self.vboxLayout79.addWidget(self.pushButton_auto_raman_measurement)

        self.comboBox_presets = QComboBox(self.lightSourceWidget_shaded)
        self.comboBox_presets.addItem("")
        self.comboBox_presets.addItem("")
        self.comboBox_presets.addItem("")
        self.comboBox_presets.setObjectName(u"comboBox_presets")
        self.comboBox_presets.setFont(font)

        self.vboxLayout79.addWidget(self.comboBox_presets)

        self.checkBox_auto_raman_config = QCheckBox(self.lightSourceWidget_shaded)
        self.checkBox_auto_raman_config.setObjectName(u"checkBox_auto_raman_config")
        sizePolicy1.setHeightForWidth(self.checkBox_auto_raman_config.sizePolicy().hasHeightForWidth())
        self.checkBox_auto_raman_config.setSizePolicy(sizePolicy1)

        self.vboxLayout79.addWidget(self.checkBox_auto_raman_config)

        self.frame_auto_raman_config = QFrame(self.lightSourceWidget_shaded)
        self.frame_auto_raman_config.setObjectName(u"frame_auto_raman_config")
        sizePolicy16.setHeightForWidth(self.frame_auto_raman_config.sizePolicy().hasHeightForWidth())
        self.frame_auto_raman_config.setSizePolicy(sizePolicy16)
        self.frame_auto_raman_config.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_auto_raman_config.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_auto_raman_config.setProperty(u"wpBox", False)
        self.formLayout9 = QFormLayout(self.frame_auto_raman_config)
        self.formLayout9.setObjectName(u"formLayout9")
        self.formLayout9.setLabelAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.formLayout9.setHorizontalSpacing(0)
        self.formLayout9.setVerticalSpacing(3)
        self.formLayout9.setContentsMargins(6, 6, 6, 9)
        self.spinBox_auto_raman_max_ms = QSpinBox(self.frame_auto_raman_config)
        self.spinBox_auto_raman_max_ms.setObjectName(u"spinBox_auto_raman_max_ms")
        sizePolicy1.setHeightForWidth(self.spinBox_auto_raman_max_ms.sizePolicy().hasHeightForWidth())
        self.spinBox_auto_raman_max_ms.setSizePolicy(sizePolicy1)
        self.spinBox_auto_raman_max_ms.setMinimumSize(QSize(100, 0))
        self.spinBox_auto_raman_max_ms.setMaximumSize(QSize(100, 16777215))
        self.spinBox_auto_raman_max_ms.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.spinBox_auto_raman_max_ms.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_auto_raman_max_ms.setMinimum(100)
        self.spinBox_auto_raman_max_ms.setMaximum(30000)
        self.spinBox_auto_raman_max_ms.setSingleStep(1000)
        self.spinBox_auto_raman_max_ms.setValue(10000)

        self.formLayout9.setWidget(0, QFormLayout.ItemRole.LabelRole, self.spinBox_auto_raman_max_ms)

        self.label_auto_raman_max_ms = QLabel(self.frame_auto_raman_config)
        self.label_auto_raman_max_ms.setObjectName(u"label_auto_raman_max_ms")
        sizePolicy16.setHeightForWidth(self.label_auto_raman_max_ms.sizePolicy().hasHeightForWidth())
        self.label_auto_raman_max_ms.setSizePolicy(sizePolicy16)
        self.label_auto_raman_max_ms.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        self.formLayout9.setWidget(0, QFormLayout.ItemRole.FieldRole, self.label_auto_raman_max_ms)

        self.spinBox_auto_raman_start_integ_ms = QSpinBox(self.frame_auto_raman_config)
        self.spinBox_auto_raman_start_integ_ms.setObjectName(u"spinBox_auto_raman_start_integ_ms")
        sizePolicy1.setHeightForWidth(self.spinBox_auto_raman_start_integ_ms.sizePolicy().hasHeightForWidth())
        self.spinBox_auto_raman_start_integ_ms.setSizePolicy(sizePolicy1)
        self.spinBox_auto_raman_start_integ_ms.setMinimumSize(QSize(100, 0))
        self.spinBox_auto_raman_start_integ_ms.setMaximumSize(QSize(100, 16777215))
        self.spinBox_auto_raman_start_integ_ms.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.spinBox_auto_raman_start_integ_ms.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_auto_raman_start_integ_ms.setMinimum(1)
        self.spinBox_auto_raman_start_integ_ms.setMaximum(2000)
        self.spinBox_auto_raman_start_integ_ms.setSingleStep(100)
        self.spinBox_auto_raman_start_integ_ms.setValue(100)

        self.formLayout9.setWidget(1, QFormLayout.ItemRole.LabelRole, self.spinBox_auto_raman_start_integ_ms)

        self.label_auto_raman_start_integ_ms = QLabel(self.frame_auto_raman_config)
        self.label_auto_raman_start_integ_ms.setObjectName(u"label_auto_raman_start_integ_ms")
        sizePolicy16.setHeightForWidth(self.label_auto_raman_start_integ_ms.sizePolicy().hasHeightForWidth())
        self.label_auto_raman_start_integ_ms.setSizePolicy(sizePolicy16)
        self.label_auto_raman_start_integ_ms.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        self.formLayout9.setWidget(1, QFormLayout.ItemRole.FieldRole, self.label_auto_raman_start_integ_ms)

        self.spinBox_auto_raman_start_gain_db = QSpinBox(self.frame_auto_raman_config)
        self.spinBox_auto_raman_start_gain_db.setObjectName(u"spinBox_auto_raman_start_gain_db")
        sizePolicy1.setHeightForWidth(self.spinBox_auto_raman_start_gain_db.sizePolicy().hasHeightForWidth())
        self.spinBox_auto_raman_start_gain_db.setSizePolicy(sizePolicy1)
        self.spinBox_auto_raman_start_gain_db.setMinimumSize(QSize(100, 0))
        self.spinBox_auto_raman_start_gain_db.setMaximumSize(QSize(100, 16777215))
        self.spinBox_auto_raman_start_gain_db.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.spinBox_auto_raman_start_gain_db.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_auto_raman_start_gain_db.setMinimum(0)
        self.spinBox_auto_raman_start_gain_db.setMaximum(31)
        self.spinBox_auto_raman_start_gain_db.setSingleStep(1)
        self.spinBox_auto_raman_start_gain_db.setValue(0)

        self.formLayout9.setWidget(2, QFormLayout.ItemRole.LabelRole, self.spinBox_auto_raman_start_gain_db)

        self.label_auto_raman_start_gain_db = QLabel(self.frame_auto_raman_config)
        self.label_auto_raman_start_gain_db.setObjectName(u"label_auto_raman_start_gain_db")
        sizePolicy16.setHeightForWidth(self.label_auto_raman_start_gain_db.sizePolicy().hasHeightForWidth())
        self.label_auto_raman_start_gain_db.setSizePolicy(sizePolicy16)
        self.label_auto_raman_start_gain_db.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        self.formLayout9.setWidget(2, QFormLayout.ItemRole.FieldRole, self.label_auto_raman_start_gain_db)

        self.spinBox_auto_raman_max_integ_ms = QSpinBox(self.frame_auto_raman_config)
        self.spinBox_auto_raman_max_integ_ms.setObjectName(u"spinBox_auto_raman_max_integ_ms")
        sizePolicy1.setHeightForWidth(self.spinBox_auto_raman_max_integ_ms.sizePolicy().hasHeightForWidth())
        self.spinBox_auto_raman_max_integ_ms.setSizePolicy(sizePolicy1)
        self.spinBox_auto_raman_max_integ_ms.setMinimumSize(QSize(100, 0))
        self.spinBox_auto_raman_max_integ_ms.setMaximumSize(QSize(100, 16777215))
        self.spinBox_auto_raman_max_integ_ms.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.spinBox_auto_raman_max_integ_ms.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_auto_raman_max_integ_ms.setMinimum(1)
        self.spinBox_auto_raman_max_integ_ms.setMaximum(10000)
        self.spinBox_auto_raman_max_integ_ms.setSingleStep(1000)
        self.spinBox_auto_raman_max_integ_ms.setValue(2000)

        self.formLayout9.setWidget(3, QFormLayout.ItemRole.LabelRole, self.spinBox_auto_raman_max_integ_ms)

        self.label_auto_raman_max_integ_ms = QLabel(self.frame_auto_raman_config)
        self.label_auto_raman_max_integ_ms.setObjectName(u"label_auto_raman_max_integ_ms")
        sizePolicy16.setHeightForWidth(self.label_auto_raman_max_integ_ms.sizePolicy().hasHeightForWidth())
        self.label_auto_raman_max_integ_ms.setSizePolicy(sizePolicy16)
        self.label_auto_raman_max_integ_ms.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        self.formLayout9.setWidget(3, QFormLayout.ItemRole.FieldRole, self.label_auto_raman_max_integ_ms)

        self.spinBox_auto_raman_min_integ_ms = QSpinBox(self.frame_auto_raman_config)
        self.spinBox_auto_raman_min_integ_ms.setObjectName(u"spinBox_auto_raman_min_integ_ms")
        sizePolicy1.setHeightForWidth(self.spinBox_auto_raman_min_integ_ms.sizePolicy().hasHeightForWidth())
        self.spinBox_auto_raman_min_integ_ms.setSizePolicy(sizePolicy1)
        self.spinBox_auto_raman_min_integ_ms.setMinimumSize(QSize(100, 0))
        self.spinBox_auto_raman_min_integ_ms.setMaximumSize(QSize(100, 16777215))
        self.spinBox_auto_raman_min_integ_ms.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.spinBox_auto_raman_min_integ_ms.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_auto_raman_min_integ_ms.setMinimum(1)
        self.spinBox_auto_raman_min_integ_ms.setMaximum(1000)
        self.spinBox_auto_raman_min_integ_ms.setSingleStep(1)
        self.spinBox_auto_raman_min_integ_ms.setValue(10)

        self.formLayout9.setWidget(4, QFormLayout.ItemRole.LabelRole, self.spinBox_auto_raman_min_integ_ms)

        self.label_auto_raman_min_integ_ms = QLabel(self.frame_auto_raman_config)
        self.label_auto_raman_min_integ_ms.setObjectName(u"label_auto_raman_min_integ_ms")
        sizePolicy16.setHeightForWidth(self.label_auto_raman_min_integ_ms.sizePolicy().hasHeightForWidth())
        self.label_auto_raman_min_integ_ms.setSizePolicy(sizePolicy16)
        self.label_auto_raman_min_integ_ms.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        self.formLayout9.setWidget(4, QFormLayout.ItemRole.FieldRole, self.label_auto_raman_min_integ_ms)

        self.spinBox_auto_raman_max_gain_db = QSpinBox(self.frame_auto_raman_config)
        self.spinBox_auto_raman_max_gain_db.setObjectName(u"spinBox_auto_raman_max_gain_db")
        sizePolicy1.setHeightForWidth(self.spinBox_auto_raman_max_gain_db.sizePolicy().hasHeightForWidth())
        self.spinBox_auto_raman_max_gain_db.setSizePolicy(sizePolicy1)
        self.spinBox_auto_raman_max_gain_db.setMinimumSize(QSize(100, 0))
        self.spinBox_auto_raman_max_gain_db.setMaximumSize(QSize(100, 16777215))
        self.spinBox_auto_raman_max_gain_db.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.spinBox_auto_raman_max_gain_db.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_auto_raman_max_gain_db.setMinimum(0)
        self.spinBox_auto_raman_max_gain_db.setMaximum(31)
        self.spinBox_auto_raman_max_gain_db.setSingleStep(1)
        self.spinBox_auto_raman_max_gain_db.setValue(30)

        self.formLayout9.setWidget(5, QFormLayout.ItemRole.LabelRole, self.spinBox_auto_raman_max_gain_db)

        self.label_auto_raman_max_gain_db = QLabel(self.frame_auto_raman_config)
        self.label_auto_raman_max_gain_db.setObjectName(u"label_auto_raman_max_gain_db")
        sizePolicy16.setHeightForWidth(self.label_auto_raman_max_gain_db.sizePolicy().hasHeightForWidth())
        self.label_auto_raman_max_gain_db.setSizePolicy(sizePolicy16)
        self.label_auto_raman_max_gain_db.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        self.formLayout9.setWidget(5, QFormLayout.ItemRole.FieldRole, self.label_auto_raman_max_gain_db)

        self.spinBox_auto_raman_min_gain_db = QSpinBox(self.frame_auto_raman_config)
        self.spinBox_auto_raman_min_gain_db.setObjectName(u"spinBox_auto_raman_min_gain_db")
        sizePolicy1.setHeightForWidth(self.spinBox_auto_raman_min_gain_db.sizePolicy().hasHeightForWidth())
        self.spinBox_auto_raman_min_gain_db.setSizePolicy(sizePolicy1)
        self.spinBox_auto_raman_min_gain_db.setMinimumSize(QSize(100, 0))
        self.spinBox_auto_raman_min_gain_db.setMaximumSize(QSize(100, 16777215))
        self.spinBox_auto_raman_min_gain_db.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.spinBox_auto_raman_min_gain_db.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_auto_raman_min_gain_db.setMinimum(0)
        self.spinBox_auto_raman_min_gain_db.setMaximum(31)
        self.spinBox_auto_raman_min_gain_db.setSingleStep(1)
        self.spinBox_auto_raman_min_gain_db.setValue(0)

        self.formLayout9.setWidget(6, QFormLayout.ItemRole.LabelRole, self.spinBox_auto_raman_min_gain_db)

        self.label_auto_raman_min_gain_db = QLabel(self.frame_auto_raman_config)
        self.label_auto_raman_min_gain_db.setObjectName(u"label_auto_raman_min_gain_db")
        sizePolicy16.setHeightForWidth(self.label_auto_raman_min_gain_db.sizePolicy().hasHeightForWidth())
        self.label_auto_raman_min_gain_db.setSizePolicy(sizePolicy16)
        self.label_auto_raman_min_gain_db.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        self.formLayout9.setWidget(6, QFormLayout.ItemRole.FieldRole, self.label_auto_raman_min_gain_db)

        self.spinBox_auto_raman_target_counts = QSpinBox(self.frame_auto_raman_config)
        self.spinBox_auto_raman_target_counts.setObjectName(u"spinBox_auto_raman_target_counts")
        sizePolicy1.setHeightForWidth(self.spinBox_auto_raman_target_counts.sizePolicy().hasHeightForWidth())
        self.spinBox_auto_raman_target_counts.setSizePolicy(sizePolicy1)
        self.spinBox_auto_raman_target_counts.setMinimumSize(QSize(100, 0))
        self.spinBox_auto_raman_target_counts.setMaximumSize(QSize(100, 16777215))
        self.spinBox_auto_raman_target_counts.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.spinBox_auto_raman_target_counts.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_auto_raman_target_counts.setMinimum(1000)
        self.spinBox_auto_raman_target_counts.setMaximum(60000)
        self.spinBox_auto_raman_target_counts.setSingleStep(1000)
        self.spinBox_auto_raman_target_counts.setValue(45000)

        self.formLayout9.setWidget(7, QFormLayout.ItemRole.LabelRole, self.spinBox_auto_raman_target_counts)

        self.label_auto_raman_target_counts = QLabel(self.frame_auto_raman_config)
        self.label_auto_raman_target_counts.setObjectName(u"label_auto_raman_target_counts")
        sizePolicy16.setHeightForWidth(self.label_auto_raman_target_counts.sizePolicy().hasHeightForWidth())
        self.label_auto_raman_target_counts.setSizePolicy(sizePolicy16)
        self.label_auto_raman_target_counts.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        self.formLayout9.setWidget(7, QFormLayout.ItemRole.FieldRole, self.label_auto_raman_target_counts)

        self.spinBox_auto_raman_max_counts = QSpinBox(self.frame_auto_raman_config)
        self.spinBox_auto_raman_max_counts.setObjectName(u"spinBox_auto_raman_max_counts")
        sizePolicy1.setHeightForWidth(self.spinBox_auto_raman_max_counts.sizePolicy().hasHeightForWidth())
        self.spinBox_auto_raman_max_counts.setSizePolicy(sizePolicy1)
        self.spinBox_auto_raman_max_counts.setMinimumSize(QSize(100, 0))
        self.spinBox_auto_raman_max_counts.setMaximumSize(QSize(100, 16777215))
        self.spinBox_auto_raman_max_counts.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.spinBox_auto_raman_max_counts.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_auto_raman_max_counts.setMinimum(5000)
        self.spinBox_auto_raman_max_counts.setMaximum(65000)
        self.spinBox_auto_raman_max_counts.setSingleStep(1000)
        self.spinBox_auto_raman_max_counts.setValue(50000)

        self.formLayout9.setWidget(8, QFormLayout.ItemRole.LabelRole, self.spinBox_auto_raman_max_counts)

        self.label_auto_raman_max_counts = QLabel(self.frame_auto_raman_config)
        self.label_auto_raman_max_counts.setObjectName(u"label_auto_raman_max_counts")
        sizePolicy16.setHeightForWidth(self.label_auto_raman_max_counts.sizePolicy().hasHeightForWidth())
        self.label_auto_raman_max_counts.setSizePolicy(sizePolicy16)
        self.label_auto_raman_max_counts.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        self.formLayout9.setWidget(8, QFormLayout.ItemRole.FieldRole, self.label_auto_raman_max_counts)

        self.spinBox_auto_raman_min_counts = QSpinBox(self.frame_auto_raman_config)
        self.spinBox_auto_raman_min_counts.setObjectName(u"spinBox_auto_raman_min_counts")
        sizePolicy1.setHeightForWidth(self.spinBox_auto_raman_min_counts.sizePolicy().hasHeightForWidth())
        self.spinBox_auto_raman_min_counts.setSizePolicy(sizePolicy1)
        self.spinBox_auto_raman_min_counts.setMinimumSize(QSize(100, 0))
        self.spinBox_auto_raman_min_counts.setMaximumSize(QSize(100, 16777215))
        self.spinBox_auto_raman_min_counts.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.spinBox_auto_raman_min_counts.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_auto_raman_min_counts.setMinimum(1000)
        self.spinBox_auto_raman_min_counts.setMaximum(60000)
        self.spinBox_auto_raman_min_counts.setSingleStep(1000)
        self.spinBox_auto_raman_min_counts.setValue(40000)

        self.formLayout9.setWidget(9, QFormLayout.ItemRole.LabelRole, self.spinBox_auto_raman_min_counts)

        self.label_auto_raman_min_counts = QLabel(self.frame_auto_raman_config)
        self.label_auto_raman_min_counts.setObjectName(u"label_auto_raman_min_counts")
        sizePolicy16.setHeightForWidth(self.label_auto_raman_min_counts.sizePolicy().hasHeightForWidth())
        self.label_auto_raman_min_counts.setSizePolicy(sizePolicy16)
        self.label_auto_raman_min_counts.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        self.formLayout9.setWidget(9, QFormLayout.ItemRole.FieldRole, self.label_auto_raman_min_counts)

        self.spinBox_auto_raman_max_factor = QSpinBox(self.frame_auto_raman_config)
        self.spinBox_auto_raman_max_factor.setObjectName(u"spinBox_auto_raman_max_factor")
        sizePolicy1.setHeightForWidth(self.spinBox_auto_raman_max_factor.sizePolicy().hasHeightForWidth())
        self.spinBox_auto_raman_max_factor.setSizePolicy(sizePolicy1)
        self.spinBox_auto_raman_max_factor.setMinimumSize(QSize(100, 0))
        self.spinBox_auto_raman_max_factor.setMaximumSize(QSize(100, 16777215))
        self.spinBox_auto_raman_max_factor.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.spinBox_auto_raman_max_factor.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_auto_raman_max_factor.setMinimum(2)
        self.spinBox_auto_raman_max_factor.setMaximum(20)
        self.spinBox_auto_raman_max_factor.setSingleStep(1)
        self.spinBox_auto_raman_max_factor.setValue(5)

        self.formLayout9.setWidget(10, QFormLayout.ItemRole.LabelRole, self.spinBox_auto_raman_max_factor)

        self.label_auto_raman_max_factor = QLabel(self.frame_auto_raman_config)
        self.label_auto_raman_max_factor.setObjectName(u"label_auto_raman_max_factor")
        sizePolicy16.setHeightForWidth(self.label_auto_raman_max_factor.sizePolicy().hasHeightForWidth())
        self.label_auto_raman_max_factor.setSizePolicy(sizePolicy16)
        self.label_auto_raman_max_factor.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        self.formLayout9.setWidget(10, QFormLayout.ItemRole.FieldRole, self.label_auto_raman_max_factor)

        self.doubleSpinBox_auto_raman_drop_factor = QDoubleSpinBox(self.frame_auto_raman_config)
        self.doubleSpinBox_auto_raman_drop_factor.setObjectName(u"doubleSpinBox_auto_raman_drop_factor")
        self.doubleSpinBox_auto_raman_drop_factor.setMinimumSize(QSize(100, 0))
        self.doubleSpinBox_auto_raman_drop_factor.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.doubleSpinBox_auto_raman_drop_factor.setAccelerated(True)
        self.doubleSpinBox_auto_raman_drop_factor.setKeyboardTracking(False)
        self.doubleSpinBox_auto_raman_drop_factor.setDecimals(1)
        self.doubleSpinBox_auto_raman_drop_factor.setMinimum(0.100000000000000)
        self.doubleSpinBox_auto_raman_drop_factor.setMaximum(0.900000000000000)
        self.doubleSpinBox_auto_raman_drop_factor.setSingleStep(0.100000000000000)
        self.doubleSpinBox_auto_raman_drop_factor.setValue(0.500000000000000)

        self.formLayout9.setWidget(11, QFormLayout.ItemRole.LabelRole, self.doubleSpinBox_auto_raman_drop_factor)

        self.label_auto_raman_drop_factor = QLabel(self.frame_auto_raman_config)
        self.label_auto_raman_drop_factor.setObjectName(u"label_auto_raman_drop_factor")
        sizePolicy16.setHeightForWidth(self.label_auto_raman_drop_factor.sizePolicy().hasHeightForWidth())
        self.label_auto_raman_drop_factor.setSizePolicy(sizePolicy16)
        self.label_auto_raman_drop_factor.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        self.formLayout9.setWidget(11, QFormLayout.ItemRole.FieldRole, self.label_auto_raman_drop_factor)

        self.spinBox_auto_raman_saturation = QSpinBox(self.frame_auto_raman_config)
        self.spinBox_auto_raman_saturation.setObjectName(u"spinBox_auto_raman_saturation")
        sizePolicy1.setHeightForWidth(self.spinBox_auto_raman_saturation.sizePolicy().hasHeightForWidth())
        self.spinBox_auto_raman_saturation.setSizePolicy(sizePolicy1)
        self.spinBox_auto_raman_saturation.setMinimumSize(QSize(100, 0))
        self.spinBox_auto_raman_saturation.setMaximumSize(QSize(100, 16777215))
        self.spinBox_auto_raman_saturation.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.spinBox_auto_raman_saturation.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_auto_raman_saturation.setMinimum(40000)
        self.spinBox_auto_raman_saturation.setMaximum(65000)
        self.spinBox_auto_raman_saturation.setSingleStep(1000)
        self.spinBox_auto_raman_saturation.setValue(65000)

        self.formLayout9.setWidget(12, QFormLayout.ItemRole.LabelRole, self.spinBox_auto_raman_saturation)

        self.label_auto_raman_saturation = QLabel(self.frame_auto_raman_config)
        self.label_auto_raman_saturation.setObjectName(u"label_auto_raman_saturation")
        sizePolicy16.setHeightForWidth(self.label_auto_raman_saturation.sizePolicy().hasHeightForWidth())
        self.label_auto_raman_saturation.setSizePolicy(sizePolicy16)
        self.label_auto_raman_saturation.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        self.formLayout9.setWidget(12, QFormLayout.ItemRole.FieldRole, self.label_auto_raman_saturation)

        self.spinBox_auto_raman_laser_warning_delay_sec = QSpinBox(self.frame_auto_raman_config)
        self.spinBox_auto_raman_laser_warning_delay_sec.setObjectName(u"spinBox_auto_raman_laser_warning_delay_sec")
        sizePolicy1.setHeightForWidth(self.spinBox_auto_raman_laser_warning_delay_sec.sizePolicy().hasHeightForWidth())
        self.spinBox_auto_raman_laser_warning_delay_sec.setSizePolicy(sizePolicy1)
        self.spinBox_auto_raman_laser_warning_delay_sec.setMinimumSize(QSize(100, 0))
        self.spinBox_auto_raman_laser_warning_delay_sec.setMaximumSize(QSize(100, 16777215))
        self.spinBox_auto_raman_laser_warning_delay_sec.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.spinBox_auto_raman_laser_warning_delay_sec.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_auto_raman_laser_warning_delay_sec.setMinimum(0)
        self.spinBox_auto_raman_laser_warning_delay_sec.setMaximum(5)
        self.spinBox_auto_raman_laser_warning_delay_sec.setSingleStep(1)
        self.spinBox_auto_raman_laser_warning_delay_sec.setValue(3)

        self.formLayout9.setWidget(13, QFormLayout.ItemRole.LabelRole, self.spinBox_auto_raman_laser_warning_delay_sec)

        self.label_auto_raman_laser_warning_delay_sec = QLabel(self.frame_auto_raman_config)
        self.label_auto_raman_laser_warning_delay_sec.setObjectName(u"label_auto_raman_laser_warning_delay_sec")
        sizePolicy16.setHeightForWidth(self.label_auto_raman_laser_warning_delay_sec.sizePolicy().hasHeightForWidth())
        self.label_auto_raman_laser_warning_delay_sec.setSizePolicy(sizePolicy16)
        self.label_auto_raman_laser_warning_delay_sec.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        self.formLayout9.setWidget(13, QFormLayout.ItemRole.FieldRole, self.label_auto_raman_laser_warning_delay_sec)

        self.spinBox_auto_raman_max_avg = QSpinBox(self.frame_auto_raman_config)
        self.spinBox_auto_raman_max_avg.setObjectName(u"spinBox_auto_raman_max_avg")
        sizePolicy1.setHeightForWidth(self.spinBox_auto_raman_max_avg.sizePolicy().hasHeightForWidth())
        self.spinBox_auto_raman_max_avg.setSizePolicy(sizePolicy1)
        self.spinBox_auto_raman_max_avg.setMinimumSize(QSize(100, 0))
        self.spinBox_auto_raman_max_avg.setMaximumSize(QSize(100, 16777215))
        self.spinBox_auto_raman_max_avg.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.spinBox_auto_raman_max_avg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_auto_raman_max_avg.setMinimum(1)
        self.spinBox_auto_raman_max_avg.setMaximum(1000)
        self.spinBox_auto_raman_max_avg.setSingleStep(1)
        self.spinBox_auto_raman_max_avg.setValue(100)

        self.formLayout9.setWidget(14, QFormLayout.ItemRole.LabelRole, self.spinBox_auto_raman_max_avg)

        self.label_auto_raman_max_avg = QLabel(self.frame_auto_raman_config)
        self.label_auto_raman_max_avg.setObjectName(u"label_auto_raman_max_avg")
        sizePolicy16.setHeightForWidth(self.label_auto_raman_max_avg.sizePolicy().hasHeightForWidth())
        self.label_auto_raman_max_avg.setSizePolicy(sizePolicy16)
        self.label_auto_raman_max_avg.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        self.formLayout9.setWidget(14, QFormLayout.ItemRole.FieldRole, self.label_auto_raman_max_avg)

        self.label_auto_raman_elapsed = QLabel(self.frame_auto_raman_config)
        self.label_auto_raman_elapsed.setObjectName(u"label_auto_raman_elapsed")
        sizePolicy16.setHeightForWidth(self.label_auto_raman_elapsed.sizePolicy().hasHeightForWidth())
        self.label_auto_raman_elapsed.setSizePolicy(sizePolicy16)
        self.label_auto_raman_elapsed.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        self.formLayout9.setWidget(15, QFormLayout.ItemRole.LabelRole, self.label_auto_raman_elapsed)

        self.label_auto_raman_elapsed_name = QLabel(self.frame_auto_raman_config)
        self.label_auto_raman_elapsed_name.setObjectName(u"label_auto_raman_elapsed_name")
        sizePolicy16.setHeightForWidth(self.label_auto_raman_elapsed_name.sizePolicy().hasHeightForWidth())
        self.label_auto_raman_elapsed_name.setSizePolicy(sizePolicy16)
        self.label_auto_raman_elapsed_name.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        self.formLayout9.setWidget(15, QFormLayout.ItemRole.FieldRole, self.label_auto_raman_elapsed_name)

        self.checkBox_auto_raman_retain_settings = QCheckBox(self.frame_auto_raman_config)
        self.checkBox_auto_raman_retain_settings.setObjectName(u"checkBox_auto_raman_retain_settings")
        sizePolicy1.setHeightForWidth(self.checkBox_auto_raman_retain_settings.sizePolicy().hasHeightForWidth())
        self.checkBox_auto_raman_retain_settings.setSizePolicy(sizePolicy1)

        self.formLayout9.setWidget(16, QFormLayout.ItemRole.SpanningRole, self.checkBox_auto_raman_retain_settings)

        self.checkBox_auto_raman_auto_save = QCheckBox(self.frame_auto_raman_config)
        self.checkBox_auto_raman_auto_save.setObjectName(u"checkBox_auto_raman_auto_save")
        sizePolicy1.setHeightForWidth(self.checkBox_auto_raman_auto_save.sizePolicy().hasHeightForWidth())
        self.checkBox_auto_raman_auto_save.setSizePolicy(sizePolicy1)

        self.formLayout9.setWidget(17, QFormLayout.ItemRole.SpanningRole, self.checkBox_auto_raman_auto_save)

        self.checkBox_auto_raman_onboard = QCheckBox(self.frame_auto_raman_config)
        self.checkBox_auto_raman_onboard.setObjectName(u"checkBox_auto_raman_onboard")
        sizePolicy1.setHeightForWidth(self.checkBox_auto_raman_onboard.sizePolicy().hasHeightForWidth())
        self.checkBox_auto_raman_onboard.setSizePolicy(sizePolicy1)

        self.formLayout9.setWidget(18, QFormLayout.ItemRole.SpanningRole, self.checkBox_auto_raman_onboard)


        self.vboxLayout79.addWidget(self.frame_auto_raman_config)


        self.lightSourceWidget_grid.addWidget(self.lightSourceWidget_shaded, 0, 0, 1, 1)


        self.vboxLayout78.addWidget(self.lightSourceWidget_border)


        self.controlWidget_inner_vbox.addWidget(self.frame_lightSourceControl)

        self.frame_acc_xl = QFrame(self.controlWidget_inner)
        self.frame_acc_xl.setObjectName(u"frame_acc_xl")
        sizePolicy16.setHeightForWidth(self.frame_acc_xl.sizePolicy().hasHeightForWidth())
        self.frame_acc_xl.setSizePolicy(sizePolicy16)
        self.frame_acc_xl.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_acc_xl.setFrameShadow(QFrame.Shadow.Raised)
        self.vboxLayout81 = QVBoxLayout(self.frame_acc_xl)
        self.vboxLayout81.setObjectName(u"vboxLayout81")
        self.vboxLayout81.setContentsMargins(0, 0, 0, 0)
        self.label201 = QLabel(self.frame_acc_xl)
        self.label201.setObjectName(u"label201")
        sizePolicy16.setHeightForWidth(self.label201.sizePolicy().hasHeightForWidth())
        self.label201.setSizePolicy(sizePolicy16)
        self.label201.setFont(font2)

        self.vboxLayout81.addWidget(self.label201)

        self.frame_acc_xl_white = QFrame(self.frame_acc_xl)
        self.frame_acc_xl_white.setObjectName(u"frame_acc_xl_white")
        sizePolicy16.setHeightForWidth(self.frame_acc_xl_white.sizePolicy().hasHeightForWidth())
        self.frame_acc_xl_white.setSizePolicy(sizePolicy16)
        self.frame_acc_xl_white.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_acc_xl_white.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_acc_xl_white.setProperty(u"wpBox", False)
        self.vboxLayout82 = QVBoxLayout(self.frame_acc_xl_white)
        self.vboxLayout82.setObjectName(u"vboxLayout82")
        self.vboxLayout82.setContentsMargins(0, 0, 0, 0)
        self.frame_acc_xl_grad = QFrame(self.frame_acc_xl_white)
        self.frame_acc_xl_grad.setObjectName(u"frame_acc_xl_grad")
        sizePolicy16.setHeightForWidth(self.frame_acc_xl_grad.sizePolicy().hasHeightForWidth())
        self.frame_acc_xl_grad.setSizePolicy(sizePolicy16)
        self.frame_acc_xl_grad.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_acc_xl_grad.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_acc_xl_grad.setProperty(u"wpGrad", False)
        self.vboxLayout83 = QVBoxLayout(self.frame_acc_xl_grad)
        self.vboxLayout83.setObjectName(u"vboxLayout83")
        self.checkBox_acc_xl_shutter = QCheckBox(self.frame_acc_xl_grad)
        self.checkBox_acc_xl_shutter.setObjectName(u"checkBox_acc_xl_shutter")
        sizePolicy1.setHeightForWidth(self.checkBox_acc_xl_shutter.sizePolicy().hasHeightForWidth())
        self.checkBox_acc_xl_shutter.setSizePolicy(sizePolicy1)

        self.vboxLayout83.addWidget(self.checkBox_acc_xl_shutter)

        self.checkBox_acc_xl_fan = QCheckBox(self.frame_acc_xl_grad)
        self.checkBox_acc_xl_fan.setObjectName(u"checkBox_acc_xl_fan")
        sizePolicy1.setHeightForWidth(self.checkBox_acc_xl_fan.sizePolicy().hasHeightForWidth())
        self.checkBox_acc_xl_fan.setSizePolicy(sizePolicy1)

        self.vboxLayout83.addWidget(self.checkBox_acc_xl_fan)


        self.vboxLayout82.addWidget(self.frame_acc_xl_grad)


        self.vboxLayout81.addWidget(self.frame_acc_xl_white)


        self.controlWidget_inner_vbox.addWidget(self.frame_acc_xl)

        self.detectorControlWidget = QFrame(self.controlWidget_inner)
        self.detectorControlWidget.setObjectName(u"detectorControlWidget")
        sizePolicy16.setHeightForWidth(self.detectorControlWidget.sizePolicy().hasHeightForWidth())
        self.detectorControlWidget.setSizePolicy(sizePolicy16)
        self.vboxLayout84 = QVBoxLayout(self.detectorControlWidget)
        self.vboxLayout84.setSpacing(6)
        self.vboxLayout84.setObjectName(u"vboxLayout84")
        self.vboxLayout84.setContentsMargins(0, 0, 0, 0)
        self.detectorControlWidget_label = QLabel(self.detectorControlWidget)
        self.detectorControlWidget_label.setObjectName(u"detectorControlWidget_label")
        sizePolicy16.setHeightForWidth(self.detectorControlWidget_label.sizePolicy().hasHeightForWidth())
        self.detectorControlWidget_label.setSizePolicy(sizePolicy16)
        self.detectorControlWidget_label.setFont(font2)

        self.vboxLayout84.addWidget(self.detectorControlWidget_label)

        self.detectorControlWidget_border = QFrame(self.detectorControlWidget)
        self.detectorControlWidget_border.setObjectName(u"detectorControlWidget_border")
        sizePolicy16.setHeightForWidth(self.detectorControlWidget_border.sizePolicy().hasHeightForWidth())
        self.detectorControlWidget_border.setSizePolicy(sizePolicy16)
        self.detectorControlWidget_border.setLineWidth(1)
        self.detectorControlWidget_border.setProperty(u"wpBox", False)
        self.detectorControlWidget_grid = QGridLayout(self.detectorControlWidget_border)
        self.detectorControlWidget_grid.setSpacing(0)
        self.detectorControlWidget_grid.setObjectName(u"detectorControlWidget_grid")
        self.detectorControlWidget_grid.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.detectorControlWidget_grid.setContentsMargins(0, 0, 0, 0)
        self.detectorControlWidget_shaded = QFrame(self.detectorControlWidget_border)
        self.detectorControlWidget_shaded.setObjectName(u"detectorControlWidget_shaded")
        sizePolicy16.setHeightForWidth(self.detectorControlWidget_shaded.sizePolicy().hasHeightForWidth())
        self.detectorControlWidget_shaded.setSizePolicy(sizePolicy16)
        self.detectorControlWidget_shaded.setLineWidth(1)
        self.detectorControlWidget_shaded.setProperty(u"wpGrad", False)
        self.vboxLayout85 = QVBoxLayout(self.detectorControlWidget_shaded)
        self.vboxLayout85.setSpacing(3)
        self.vboxLayout85.setObjectName(u"vboxLayout85")
        self.hboxLayout41 = QHBoxLayout()
        self.hboxLayout41.setObjectName(u"hboxLayout41")
        self.slider_integration_time_ms = QSlider(self.detectorControlWidget_shaded)
        self.slider_integration_time_ms.setObjectName(u"slider_integration_time_ms")
        sizePolicy16.setHeightForWidth(self.slider_integration_time_ms.sizePolicy().hasHeightForWidth())
        self.slider_integration_time_ms.setSizePolicy(sizePolicy16)
        self.slider_integration_time_ms.setMaximumSize(QSize(30, 70))
        self.slider_integration_time_ms.setMinimum(1)
        self.slider_integration_time_ms.setMaximum(100)
        self.slider_integration_time_ms.setValue(100)
        self.slider_integration_time_ms.setOrientation(Qt.Orientation.Vertical)

        self.hboxLayout41.addWidget(self.slider_integration_time_ms)

        self.vboxLayout86 = QVBoxLayout()
        self.vboxLayout86.setSpacing(3)
        self.vboxLayout86.setObjectName(u"vboxLayout86")
        self.detectorControlWidget_label_integrationTime = QLabel(self.detectorControlWidget_shaded)
        self.detectorControlWidget_label_integrationTime.setObjectName(u"detectorControlWidget_label_integrationTime")
        self.detectorControlWidget_label_integrationTime.setMaximumSize(QSize(16777215, 30))
        self.detectorControlWidget_label_integrationTime.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.detectorControlWidget_label_integrationTime.setWordWrap(True)

        self.vboxLayout86.addWidget(self.detectorControlWidget_label_integrationTime)

        self.hboxLayout42 = QHBoxLayout()
        self.hboxLayout42.setObjectName(u"hboxLayout42")
        self.pushButton_integration_time_ms_dn = QPushButton(self.detectorControlWidget_shaded)
        self.pushButton_integration_time_ms_dn.setObjectName(u"pushButton_integration_time_ms_dn")
        sizePolicy1.setHeightForWidth(self.pushButton_integration_time_ms_dn.sizePolicy().hasHeightForWidth())
        self.pushButton_integration_time_ms_dn.setSizePolicy(sizePolicy1)
        self.pushButton_integration_time_ms_dn.setMinimumSize(QSize(0, 40))
        self.pushButton_integration_time_ms_dn.setMaximumSize(QSize(40, 40))
        self.pushButton_integration_time_ms_dn.setIcon(icon14)
        self.pushButton_integration_time_ms_dn.setIconSize(QSize(20, 20))
        self.pushButton_integration_time_ms_dn.setAutoRepeat(True)

        self.hboxLayout42.addWidget(self.pushButton_integration_time_ms_dn)

        self.pushButton_integration_time_ms_up = QPushButton(self.detectorControlWidget_shaded)
        self.pushButton_integration_time_ms_up.setObjectName(u"pushButton_integration_time_ms_up")
        sizePolicy1.setHeightForWidth(self.pushButton_integration_time_ms_up.sizePolicy().hasHeightForWidth())
        self.pushButton_integration_time_ms_up.setSizePolicy(sizePolicy1)
        self.pushButton_integration_time_ms_up.setMinimumSize(QSize(0, 40))
        self.pushButton_integration_time_ms_up.setMaximumSize(QSize(40, 40))
        self.pushButton_integration_time_ms_up.setIcon(icon35)
        self.pushButton_integration_time_ms_up.setIconSize(QSize(20, 20))
        self.pushButton_integration_time_ms_up.setAutoRepeat(True)

        self.hboxLayout42.addWidget(self.pushButton_integration_time_ms_up)


        self.vboxLayout86.addLayout(self.hboxLayout42)

        self.spinBox_integration_time_ms = QSpinBox(self.detectorControlWidget_shaded)
        self.spinBox_integration_time_ms.setObjectName(u"spinBox_integration_time_ms")
        sizePolicy1.setHeightForWidth(self.spinBox_integration_time_ms.sizePolicy().hasHeightForWidth())
        self.spinBox_integration_time_ms.setSizePolicy(sizePolicy1)
        self.spinBox_integration_time_ms.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.spinBox_integration_time_ms.setWrapping(False)
        self.spinBox_integration_time_ms.setFrame(True)
        self.spinBox_integration_time_ms.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_integration_time_ms.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.spinBox_integration_time_ms.setAccelerated(True)
        self.spinBox_integration_time_ms.setKeyboardTracking(False)
        self.spinBox_integration_time_ms.setMinimum(1)
        self.spinBox_integration_time_ms.setMaximum(16777216)
        self.spinBox_integration_time_ms.setValue(100)

        self.vboxLayout86.addWidget(self.spinBox_integration_time_ms)


        self.hboxLayout41.addLayout(self.vboxLayout86)


        self.vboxLayout85.addLayout(self.hboxLayout41)

        self.hboxLayout43 = QHBoxLayout()
        self.hboxLayout43.setObjectName(u"hboxLayout43")
        self.hboxLayout43.setContentsMargins(0, 0, 0, 0)
        self.verticalSlider_detector_setpoint_degC = QSlider(self.detectorControlWidget_shaded)
        self.verticalSlider_detector_setpoint_degC.setObjectName(u"verticalSlider_detector_setpoint_degC")
        sizePolicy1.setHeightForWidth(self.verticalSlider_detector_setpoint_degC.sizePolicy().hasHeightForWidth())
        self.verticalSlider_detector_setpoint_degC.setSizePolicy(sizePolicy1)
        self.verticalSlider_detector_setpoint_degC.setMaximumSize(QSize(30, 70))
        self.verticalSlider_detector_setpoint_degC.setMinimum(-20)
        self.verticalSlider_detector_setpoint_degC.setMaximum(20)
        self.verticalSlider_detector_setpoint_degC.setValue(10)
        self.verticalSlider_detector_setpoint_degC.setOrientation(Qt.Orientation.Vertical)

        self.hboxLayout43.addWidget(self.verticalSlider_detector_setpoint_degC)

        self.vboxLayout87 = QVBoxLayout()
        self.vboxLayout87.setObjectName(u"vboxLayout87")
        self.detectorControlWidget_label_detectorTemperature = QLabel(self.detectorControlWidget_shaded)
        self.detectorControlWidget_label_detectorTemperature.setObjectName(u"detectorControlWidget_label_detectorTemperature")
        self.detectorControlWidget_label_detectorTemperature.setMaximumSize(QSize(16777215, 30))
        self.detectorControlWidget_label_detectorTemperature.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.detectorControlWidget_label_detectorTemperature.setWordWrap(True)

        self.vboxLayout87.addWidget(self.detectorControlWidget_label_detectorTemperature)

        self.hboxLayout44 = QHBoxLayout()
        self.hboxLayout44.setObjectName(u"hboxLayout44")
        self.temperatureWidget_pushButton_detector_setpoint_dn = QPushButton(self.detectorControlWidget_shaded)
        self.temperatureWidget_pushButton_detector_setpoint_dn.setObjectName(u"temperatureWidget_pushButton_detector_setpoint_dn")
        sizePolicy1.setHeightForWidth(self.temperatureWidget_pushButton_detector_setpoint_dn.sizePolicy().hasHeightForWidth())
        self.temperatureWidget_pushButton_detector_setpoint_dn.setSizePolicy(sizePolicy1)
        self.temperatureWidget_pushButton_detector_setpoint_dn.setMinimumSize(QSize(0, 40))
        self.temperatureWidget_pushButton_detector_setpoint_dn.setMaximumSize(QSize(40, 40))
        self.temperatureWidget_pushButton_detector_setpoint_dn.setIcon(icon14)
        self.temperatureWidget_pushButton_detector_setpoint_dn.setIconSize(QSize(20, 20))
        self.temperatureWidget_pushButton_detector_setpoint_dn.setAutoRepeat(True)

        self.hboxLayout44.addWidget(self.temperatureWidget_pushButton_detector_setpoint_dn)

        self.temperatureWidget_pushButton_detector_setpoint_up = QPushButton(self.detectorControlWidget_shaded)
        self.temperatureWidget_pushButton_detector_setpoint_up.setObjectName(u"temperatureWidget_pushButton_detector_setpoint_up")
        sizePolicy1.setHeightForWidth(self.temperatureWidget_pushButton_detector_setpoint_up.sizePolicy().hasHeightForWidth())
        self.temperatureWidget_pushButton_detector_setpoint_up.setSizePolicy(sizePolicy1)
        self.temperatureWidget_pushButton_detector_setpoint_up.setMinimumSize(QSize(0, 40))
        self.temperatureWidget_pushButton_detector_setpoint_up.setMaximumSize(QSize(40, 40))
        self.temperatureWidget_pushButton_detector_setpoint_up.setIcon(icon35)
        self.temperatureWidget_pushButton_detector_setpoint_up.setIconSize(QSize(20, 20))
        self.temperatureWidget_pushButton_detector_setpoint_up.setAutoRepeat(True)

        self.hboxLayout44.addWidget(self.temperatureWidget_pushButton_detector_setpoint_up)


        self.vboxLayout87.addLayout(self.hboxLayout44)

        self.spinBox_detector_setpoint_degC = QSpinBox(self.detectorControlWidget_shaded)
        self.spinBox_detector_setpoint_degC.setObjectName(u"spinBox_detector_setpoint_degC")
        sizePolicy1.setHeightForWidth(self.spinBox_detector_setpoint_degC.sizePolicy().hasHeightForWidth())
        self.spinBox_detector_setpoint_degC.setSizePolicy(sizePolicy1)
        self.spinBox_detector_setpoint_degC.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.spinBox_detector_setpoint_degC.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_detector_setpoint_degC.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.spinBox_detector_setpoint_degC.setMinimum(-200)
        self.spinBox_detector_setpoint_degC.setMaximum(20)
        self.spinBox_detector_setpoint_degC.setValue(10)

        self.vboxLayout87.addWidget(self.spinBox_detector_setpoint_degC)

        self.checkBox_detector_tec_enabled = QCheckBox(self.detectorControlWidget_shaded)
        self.checkBox_detector_tec_enabled.setObjectName(u"checkBox_detector_tec_enabled")
        sizePolicy1.setHeightForWidth(self.checkBox_detector_tec_enabled.sizePolicy().hasHeightForWidth())
        self.checkBox_detector_tec_enabled.setSizePolicy(sizePolicy1)
        self.checkBox_detector_tec_enabled.setStyleSheet(u"")

        self.vboxLayout87.addWidget(self.checkBox_detector_tec_enabled)


        self.hboxLayout43.addLayout(self.vboxLayout87)


        self.vboxLayout85.addLayout(self.hboxLayout43)

        self.checkBox_external_trigger_enabled = QCheckBox(self.detectorControlWidget_shaded)
        self.checkBox_external_trigger_enabled.setObjectName(u"checkBox_external_trigger_enabled")
        self.checkBox_external_trigger_enabled.setChecked(False)

        self.vboxLayout85.addWidget(self.checkBox_external_trigger_enabled)

        self.checkBox_high_gain_mode_enabled = QCheckBox(self.detectorControlWidget_shaded)
        self.checkBox_high_gain_mode_enabled.setObjectName(u"checkBox_high_gain_mode_enabled")
        self.checkBox_high_gain_mode_enabled.setEnabled(True)
        self.checkBox_high_gain_mode_enabled.setChecked(False)

        self.vboxLayout85.addWidget(self.checkBox_high_gain_mode_enabled)

        self.hboxLayout45 = QHBoxLayout()
        self.hboxLayout45.setObjectName(u"hboxLayout45")
        self.slider_gain = QSlider(self.detectorControlWidget_shaded)
        self.slider_gain.setObjectName(u"slider_gain")
        sizePolicy16.setHeightForWidth(self.slider_gain.sizePolicy().hasHeightForWidth())
        self.slider_gain.setSizePolicy(sizePolicy16)
        self.slider_gain.setMaximumSize(QSize(30, 70))
        self.slider_gain.setMinimum(0)
        self.slider_gain.setMaximum(72)
        self.slider_gain.setValue(8)
        self.slider_gain.setOrientation(Qt.Orientation.Vertical)

        self.hboxLayout45.addWidget(self.slider_gain)

        self.vboxLayout88 = QVBoxLayout()
        self.vboxLayout88.setSpacing(3)
        self.vboxLayout88.setObjectName(u"vboxLayout88")
        self.label_gainWidget_title = QLabel(self.detectorControlWidget_shaded)
        self.label_gainWidget_title.setObjectName(u"label_gainWidget_title")
        sizePolicy16.setHeightForWidth(self.label_gainWidget_title.sizePolicy().hasHeightForWidth())
        self.label_gainWidget_title.setSizePolicy(sizePolicy16)
        self.label_gainWidget_title.setMaximumSize(QSize(16777215, 20))
        self.label_gainWidget_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_gainWidget_title.setWordWrap(True)

        self.vboxLayout88.addWidget(self.label_gainWidget_title)

        self.hboxLayout46 = QHBoxLayout()
        self.hboxLayout46.setObjectName(u"hboxLayout46")
        self.pushButton_gain_dn = QPushButton(self.detectorControlWidget_shaded)
        self.pushButton_gain_dn.setObjectName(u"pushButton_gain_dn")
        sizePolicy1.setHeightForWidth(self.pushButton_gain_dn.sizePolicy().hasHeightForWidth())
        self.pushButton_gain_dn.setSizePolicy(sizePolicy1)
        self.pushButton_gain_dn.setMinimumSize(QSize(0, 40))
        self.pushButton_gain_dn.setMaximumSize(QSize(40, 40))
        self.pushButton_gain_dn.setIcon(icon14)
        self.pushButton_gain_dn.setIconSize(QSize(20, 20))
        self.pushButton_gain_dn.setAutoRepeat(True)

        self.hboxLayout46.addWidget(self.pushButton_gain_dn)

        self.pushButton_gain_up = QPushButton(self.detectorControlWidget_shaded)
        self.pushButton_gain_up.setObjectName(u"pushButton_gain_up")
        sizePolicy1.setHeightForWidth(self.pushButton_gain_up.sizePolicy().hasHeightForWidth())
        self.pushButton_gain_up.setSizePolicy(sizePolicy1)
        self.pushButton_gain_up.setMinimumSize(QSize(0, 40))
        self.pushButton_gain_up.setMaximumSize(QSize(40, 40))
        self.pushButton_gain_up.setIcon(icon35)
        self.pushButton_gain_up.setIconSize(QSize(20, 20))
        self.pushButton_gain_up.setAutoRepeat(True)

        self.hboxLayout46.addWidget(self.pushButton_gain_up)


        self.vboxLayout88.addLayout(self.hboxLayout46)

        self.doubleSpinBox_gain = QDoubleSpinBox(self.detectorControlWidget_shaded)
        self.doubleSpinBox_gain.setObjectName(u"doubleSpinBox_gain")
        sizePolicy1.setHeightForWidth(self.doubleSpinBox_gain.sizePolicy().hasHeightForWidth())
        self.doubleSpinBox_gain.setSizePolicy(sizePolicy1)
        self.doubleSpinBox_gain.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.doubleSpinBox_gain.setWrapping(False)
        self.doubleSpinBox_gain.setFrame(True)
        self.doubleSpinBox_gain.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.doubleSpinBox_gain.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.doubleSpinBox_gain.setAccelerated(True)
        self.doubleSpinBox_gain.setKeyboardTracking(False)
        self.doubleSpinBox_gain.setDecimals(1)

        self.vboxLayout88.addWidget(self.doubleSpinBox_gain)


        self.hboxLayout45.addLayout(self.vboxLayout88)


        self.vboxLayout85.addLayout(self.hboxLayout45)

        self.checkBox_edc_enabled = QCheckBox(self.detectorControlWidget_shaded)
        self.checkBox_edc_enabled.setObjectName(u"checkBox_edc_enabled")
        sizePolicy1.setHeightForWidth(self.checkBox_edc_enabled.sizePolicy().hasHeightForWidth())
        self.checkBox_edc_enabled.setSizePolicy(sizePolicy1)
        self.checkBox_edc_enabled.setStyleSheet(u"")

        self.vboxLayout85.addWidget(self.checkBox_edc_enabled)


        self.detectorControlWidget_grid.addWidget(self.detectorControlWidget_shaded, 0, 0, 1, 1)


        self.vboxLayout84.addWidget(self.detectorControlWidget_border)


        self.controlWidget_inner_vbox.addWidget(self.detectorControlWidget)

        self.displayAxisWidget_starts_here = QFrame(self.controlWidget_inner)
        self.displayAxisWidget_starts_here.setObjectName(u"displayAxisWidget_starts_here")
        sizePolicy16.setHeightForWidth(self.displayAxisWidget_starts_here.sizePolicy().hasHeightForWidth())
        self.displayAxisWidget_starts_here.setSizePolicy(sizePolicy16)
        self.vboxLayout89 = QVBoxLayout(self.displayAxisWidget_starts_here)
        self.vboxLayout89.setObjectName(u"vboxLayout89")
        self.vboxLayout89.setContentsMargins(0, 0, 0, 0)
        self.displayAxisWidget_label = QLabel(self.displayAxisWidget_starts_here)
        self.displayAxisWidget_label.setObjectName(u"displayAxisWidget_label")
        sizePolicy16.setHeightForWidth(self.displayAxisWidget_label.sizePolicy().hasHeightForWidth())
        self.displayAxisWidget_label.setSizePolicy(sizePolicy16)
        self.displayAxisWidget_label.setFont(font2)

        self.vboxLayout89.addWidget(self.displayAxisWidget_label)

        self.displayAxisWidget_border = QFrame(self.displayAxisWidget_starts_here)
        self.displayAxisWidget_border.setObjectName(u"displayAxisWidget_border")
        sizePolicy16.setHeightForWidth(self.displayAxisWidget_border.sizePolicy().hasHeightForWidth())
        self.displayAxisWidget_border.setSizePolicy(sizePolicy16)
        self.displayAxisWidget_border.setLineWidth(1)
        self.displayAxisWidget_border.setProperty(u"wpBox", False)
        self.displayAxisWidget_grid = QGridLayout(self.displayAxisWidget_border)
        self.displayAxisWidget_grid.setSpacing(0)
        self.displayAxisWidget_grid.setObjectName(u"displayAxisWidget_grid")
        self.displayAxisWidget_grid.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.displayAxisWidget_grid.setContentsMargins(0, 0, 0, 0)
        self.displayAxisWidget_shaded = QFrame(self.displayAxisWidget_border)
        self.displayAxisWidget_shaded.setObjectName(u"displayAxisWidget_shaded")
        sizePolicy16.setHeightForWidth(self.displayAxisWidget_shaded.sizePolicy().hasHeightForWidth())
        self.displayAxisWidget_shaded.setSizePolicy(sizePolicy16)
        self.displayAxisWidget_shaded.setMinimumSize(QSize(0, 0))
        self.displayAxisWidget_shaded.setMaximumSize(QSize(16777215, 16777215))
        self.displayAxisWidget_shaded.setLineWidth(1)
        self.displayAxisWidget_shaded.setProperty(u"wpGrad", False)
        self.vboxLayout90 = QVBoxLayout(self.displayAxisWidget_shaded)
        self.vboxLayout90.setObjectName(u"vboxLayout90")
        self.displayAxis_comboBox_axis = QComboBox(self.displayAxisWidget_shaded)
        self.displayAxis_comboBox_axis.addItem("")
        self.displayAxis_comboBox_axis.addItem("")
        self.displayAxis_comboBox_axis.addItem("")
        self.displayAxis_comboBox_axis.setObjectName(u"displayAxis_comboBox_axis")
        sizePolicy13.setHeightForWidth(self.displayAxis_comboBox_axis.sizePolicy().hasHeightForWidth())
        self.displayAxis_comboBox_axis.setSizePolicy(sizePolicy13)
        self.displayAxis_comboBox_axis.setMinimumSize(QSize(80, 22))
        self.displayAxis_comboBox_axis.setFont(font)
        self.displayAxis_comboBox_axis.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.vboxLayout90.addWidget(self.displayAxis_comboBox_axis)

        self.gridLayout10 = QGridLayout()
        self.gridLayout10.setObjectName(u"gridLayout10")
        self.doubleSpinBox_cursor_scope = QDoubleSpinBox(self.displayAxisWidget_shaded)
        self.doubleSpinBox_cursor_scope.setObjectName(u"doubleSpinBox_cursor_scope")
        self.doubleSpinBox_cursor_scope.setEnabled(False)
        sizePolicy23 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy23.setHorizontalStretch(1)
        sizePolicy23.setVerticalStretch(0)
        sizePolicy23.setHeightForWidth(self.doubleSpinBox_cursor_scope.sizePolicy().hasHeightForWidth())
        self.doubleSpinBox_cursor_scope.setSizePolicy(sizePolicy23)
        self.doubleSpinBox_cursor_scope.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.doubleSpinBox_cursor_scope.setStyleSheet(u"width: 110px; margin: 0; padding: 0; border: 0;")
        self.doubleSpinBox_cursor_scope.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.doubleSpinBox_cursor_scope.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.doubleSpinBox_cursor_scope.setAccelerated(False)
        self.doubleSpinBox_cursor_scope.setKeyboardTracking(False)
        self.doubleSpinBox_cursor_scope.setMinimum(0.000000000000000)
        self.doubleSpinBox_cursor_scope.setMaximum(4000.000000000000000)
        self.doubleSpinBox_cursor_scope.setValue(500.000000000000000)

        self.gridLayout10.addWidget(self.doubleSpinBox_cursor_scope, 1, 1, 1, 1)

        self.checkBox_graph_marker = QCheckBox(self.displayAxisWidget_shaded)
        self.checkBox_graph_marker.setObjectName(u"checkBox_graph_marker")
        sizePolicy1.setHeightForWidth(self.checkBox_graph_marker.sizePolicy().hasHeightForWidth())
        self.checkBox_graph_marker.setSizePolicy(sizePolicy1)

        self.gridLayout10.addWidget(self.checkBox_graph_marker, 0, 0, 1, 1)

        self.hboxLayout47 = QHBoxLayout()
        self.hboxLayout47.setObjectName(u"hboxLayout47")
        self.pushButton_cursor_dn = QPushButton(self.displayAxisWidget_shaded)
        self.pushButton_cursor_dn.setObjectName(u"pushButton_cursor_dn")
        self.pushButton_cursor_dn.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.pushButton_cursor_dn.sizePolicy().hasHeightForWidth())
        self.pushButton_cursor_dn.setSizePolicy(sizePolicy1)
        self.pushButton_cursor_dn.setMinimumSize(QSize(0, 40))
        self.pushButton_cursor_dn.setMaximumSize(QSize(40, 40))
        self.pushButton_cursor_dn.setIcon(icon14)
        self.pushButton_cursor_dn.setIconSize(QSize(20, 20))
        self.pushButton_cursor_dn.setAutoRepeat(True)

        self.hboxLayout47.addWidget(self.pushButton_cursor_dn)

        self.pushButton_cursor_up = QPushButton(self.displayAxisWidget_shaded)
        self.pushButton_cursor_up.setObjectName(u"pushButton_cursor_up")
        self.pushButton_cursor_up.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.pushButton_cursor_up.sizePolicy().hasHeightForWidth())
        self.pushButton_cursor_up.setSizePolicy(sizePolicy1)
        self.pushButton_cursor_up.setMinimumSize(QSize(0, 40))
        self.pushButton_cursor_up.setMaximumSize(QSize(40, 40))
        self.pushButton_cursor_up.setIcon(icon35)
        self.pushButton_cursor_up.setIconSize(QSize(20, 20))
        self.pushButton_cursor_up.setAutoRepeat(True)

        self.hboxLayout47.addWidget(self.pushButton_cursor_up)


        self.gridLayout10.addLayout(self.hboxLayout47, 0, 1, 1, 1)

        self.checkBox_cursor_scope_enabled = QCheckBox(self.displayAxisWidget_shaded)
        self.checkBox_cursor_scope_enabled.setObjectName(u"checkBox_cursor_scope_enabled")
        sizePolicy1.setHeightForWidth(self.checkBox_cursor_scope_enabled.sizePolicy().hasHeightForWidth())
        self.checkBox_cursor_scope_enabled.setSizePolicy(sizePolicy1)
        self.checkBox_cursor_scope_enabled.setChecked(False)

        self.gridLayout10.addWidget(self.checkBox_cursor_scope_enabled, 1, 0, 1, 1)

        self.checkBox_edit_horiz_roi = QCheckBox(self.displayAxisWidget_shaded)
        self.checkBox_edit_horiz_roi.setObjectName(u"checkBox_edit_horiz_roi")

        self.gridLayout10.addWidget(self.checkBox_edit_horiz_roi, 2, 0, 1, 2)


        self.vboxLayout90.addLayout(self.gridLayout10)


        self.displayAxisWidget_grid.addWidget(self.displayAxisWidget_shaded, 0, 0, 1, 1)


        self.vboxLayout89.addWidget(self.displayAxisWidget_border)


        self.controlWidget_inner_vbox.addWidget(self.displayAxisWidget_starts_here)

        self.frame_XD_1 = QFrame(self.controlWidget_inner)
        self.frame_XD_1.setObjectName(u"frame_XD_1")
        sizePolicy16.setHeightForWidth(self.frame_XD_1.sizePolicy().hasHeightForWidth())
        self.frame_XD_1.setSizePolicy(sizePolicy16)
        self.verticalLayout_XD_1 = QVBoxLayout(self.frame_XD_1)
        self.verticalLayout_XD_1.setObjectName(u"verticalLayout_XD_1")
        self.verticalLayout_XD_1.setContentsMargins(0, 0, 0, 0)
        self.label_XD_title = QLabel(self.frame_XD_1)
        self.label_XD_title.setObjectName(u"label_XD_title")
        sizePolicy16.setHeightForWidth(self.label_XD_title.sizePolicy().hasHeightForWidth())
        self.label_XD_title.setSizePolicy(sizePolicy16)
        self.label_XD_title.setFont(font2)

        self.verticalLayout_XD_1.addWidget(self.label_XD_title)

        self.frame_XD_2 = QFrame(self.frame_XD_1)
        self.frame_XD_2.setObjectName(u"frame_XD_2")
        sizePolicy16.setHeightForWidth(self.frame_XD_2.sizePolicy().hasHeightForWidth())
        self.frame_XD_2.setSizePolicy(sizePolicy16)
        self.frame_XD_2.setLineWidth(1)
        self.frame_XD_2.setProperty(u"wpBox", False)
        self.grid_XD_1 = QGridLayout(self.frame_XD_2)
        self.grid_XD_1.setSpacing(0)
        self.grid_XD_1.setObjectName(u"grid_XD_1")
        self.grid_XD_1.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.grid_XD_1.setContentsMargins(0, 0, 0, 0)
        self.frame_XD_form = QFrame(self.frame_XD_2)
        self.frame_XD_form.setObjectName(u"frame_XD_form")
        sizePolicy16.setHeightForWidth(self.frame_XD_form.sizePolicy().hasHeightForWidth())
        self.frame_XD_form.setSizePolicy(sizePolicy16)
        self.frame_XD_form.setProperty(u"wpGrad", False)
        self.frame_XD_form.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_XD_form.setFrameShadow(QFrame.Shadow.Raised)
        self.grid_XD_2 = QGridLayout(self.frame_XD_form)
        self.grid_XD_2.setObjectName(u"grid_XD_2")
        self.grid_XD_2.setHorizontalSpacing(0)
        self.grid_XD_2.setVerticalSpacing(3)
        self.grid_XD_2.setContentsMargins(6, 6, 6, 9)
        self.checkBox_XD_enable = QCheckBox(self.frame_XD_form)
        self.checkBox_XD_enable.setObjectName(u"checkBox_XD_enable")
        self.checkBox_XD_enable.setChecked(False)

        self.grid_XD_2.addWidget(self.checkBox_XD_enable, 0, 0, 1, 3)

        self.label_XD_model_label = QLabel(self.frame_XD_form)
        self.label_XD_model_label.setObjectName(u"label_XD_model_label")

        self.grid_XD_2.addWidget(self.label_XD_model_label, 1, 0, 1, 1)

        self.comboBox_XD_model = QComboBox(self.frame_XD_form)
        self.comboBox_XD_model.setObjectName(u"comboBox_XD_model")
        self.comboBox_XD_model.setMinimumSize(QSize(80, 0))
        self.comboBox_XD_model.setFont(font)
        self.comboBox_XD_model.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.grid_XD_2.addWidget(self.comboBox_XD_model, 1, 1, 1, 2)

        self.label_XD_left_trim_bool_label = QLabel(self.frame_XD_form)
        self.label_XD_left_trim_bool_label.setObjectName(u"label_XD_left_trim_bool_label")

        self.grid_XD_2.addWidget(self.label_XD_left_trim_bool_label, 2, 0, 1, 1)

        self.checkBox_XD_left_trim = QCheckBox(self.frame_XD_form)
        self.checkBox_XD_left_trim.setObjectName(u"checkBox_XD_left_trim")
        self.checkBox_XD_left_trim.setChecked(False)

        self.grid_XD_2.addWidget(self.checkBox_XD_left_trim, 2, 1, 1, 1)

        self.spinBox_XD_left_trim_wavenumber = QSpinBox(self.frame_XD_form)
        self.spinBox_XD_left_trim_wavenumber.setObjectName(u"spinBox_XD_left_trim_wavenumber")
        sizePolicy1.setHeightForWidth(self.spinBox_XD_left_trim_wavenumber.sizePolicy().hasHeightForWidth())
        self.spinBox_XD_left_trim_wavenumber.setSizePolicy(sizePolicy1)
        self.spinBox_XD_left_trim_wavenumber.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.spinBox_XD_left_trim_wavenumber.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_XD_left_trim_wavenumber.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)
        self.spinBox_XD_left_trim_wavenumber.setAccelerated(True)
        self.spinBox_XD_left_trim_wavenumber.setKeyboardTracking(False)
        self.spinBox_XD_left_trim_wavenumber.setMinimum(0)
        self.spinBox_XD_left_trim_wavenumber.setMaximum(4000)
        self.spinBox_XD_left_trim_wavenumber.setSingleStep(1)
        self.spinBox_XD_left_trim_wavenumber.setValue(750)

        self.grid_XD_2.addWidget(self.spinBox_XD_left_trim_wavenumber, 2, 2, 1, 1)

        self.label_XD_right_trim_bool_label = QLabel(self.frame_XD_form)
        self.label_XD_right_trim_bool_label.setObjectName(u"label_XD_right_trim_bool_label")

        self.grid_XD_2.addWidget(self.label_XD_right_trim_bool_label, 3, 0, 1, 1)

        self.checkBox_XD_right_trim = QCheckBox(self.frame_XD_form)
        self.checkBox_XD_right_trim.setObjectName(u"checkBox_XD_right_trim")
        self.checkBox_XD_right_trim.setChecked(False)

        self.grid_XD_2.addWidget(self.checkBox_XD_right_trim, 3, 1, 1, 1)

        self.spinBox_XD_right_trim_wavenumber = QSpinBox(self.frame_XD_form)
        self.spinBox_XD_right_trim_wavenumber.setObjectName(u"spinBox_XD_right_trim_wavenumber")
        sizePolicy1.setHeightForWidth(self.spinBox_XD_right_trim_wavenumber.sizePolicy().hasHeightForWidth())
        self.spinBox_XD_right_trim_wavenumber.setSizePolicy(sizePolicy1)
        self.spinBox_XD_right_trim_wavenumber.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.spinBox_XD_right_trim_wavenumber.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_XD_right_trim_wavenumber.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)
        self.spinBox_XD_right_trim_wavenumber.setAccelerated(True)
        self.spinBox_XD_right_trim_wavenumber.setKeyboardTracking(False)
        self.spinBox_XD_right_trim_wavenumber.setMinimum(0)
        self.spinBox_XD_right_trim_wavenumber.setMaximum(4000)
        self.spinBox_XD_right_trim_wavenumber.setSingleStep(1)
        self.spinBox_XD_right_trim_wavenumber.setValue(0)

        self.grid_XD_2.addWidget(self.spinBox_XD_right_trim_wavenumber, 3, 2, 1, 1)

        self.checkBox_XD_deconvolute = QCheckBox(self.frame_XD_form)
        self.checkBox_XD_deconvolute.setObjectName(u"checkBox_XD_deconvolute")
        self.checkBox_XD_deconvolute.setChecked(False)

        self.grid_XD_2.addWidget(self.checkBox_XD_deconvolute, 4, 1, 1, 2)

        self.checkBox_XD_external_laser = QCheckBox(self.frame_XD_form)
        self.checkBox_XD_external_laser.setObjectName(u"checkBox_XD_external_laser")
        self.checkBox_XD_external_laser.setChecked(False)

        self.grid_XD_2.addWidget(self.checkBox_XD_external_laser, 5, 1, 1, 2)


        self.grid_XD_1.addWidget(self.frame_XD_form, 0, 0, 1, 1)


        self.verticalLayout_XD_1.addWidget(self.frame_XD_2)


        self.controlWidget_inner_vbox.addWidget(self.frame_XD_1)

        self.frame_library_matching_1 = QFrame(self.controlWidget_inner)
        self.frame_library_matching_1.setObjectName(u"frame_library_matching_1")
        sizePolicy16.setHeightForWidth(self.frame_library_matching_1.sizePolicy().hasHeightForWidth())
        self.frame_library_matching_1.setSizePolicy(sizePolicy16)
        self.vboxLayout91 = QVBoxLayout(self.frame_library_matching_1)
        self.vboxLayout91.setObjectName(u"vboxLayout91")
        self.vboxLayout91.setContentsMargins(0, 0, 0, 0)
        self.label_library_matching_title = QLabel(self.frame_library_matching_1)
        self.label_library_matching_title.setObjectName(u"label_library_matching_title")
        sizePolicy16.setHeightForWidth(self.label_library_matching_title.sizePolicy().hasHeightForWidth())
        self.label_library_matching_title.setSizePolicy(sizePolicy16)
        self.label_library_matching_title.setFont(font2)

        self.vboxLayout91.addWidget(self.label_library_matching_title)

        self.frame_library_matching_2 = QFrame(self.frame_library_matching_1)
        self.frame_library_matching_2.setObjectName(u"frame_library_matching_2")
        sizePolicy16.setHeightForWidth(self.frame_library_matching_2.sizePolicy().hasHeightForWidth())
        self.frame_library_matching_2.setSizePolicy(sizePolicy16)
        self.frame_library_matching_2.setLineWidth(1)
        self.grid_library_matching_1 = QGridLayout(self.frame_library_matching_2)
        self.grid_library_matching_1.setSpacing(0)
        self.grid_library_matching_1.setObjectName(u"grid_library_matching_1")
        self.grid_library_matching_1.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.grid_library_matching_1.setContentsMargins(0, 0, 0, 0)
        self.frame_library_matching_3 = QFrame(self.frame_library_matching_2)
        self.frame_library_matching_3.setObjectName(u"frame_library_matching_3")
        sizePolicy16.setHeightForWidth(self.frame_library_matching_3.sizePolicy().hasHeightForWidth())
        self.frame_library_matching_3.setSizePolicy(sizePolicy16)
        self.frame_library_matching_3.setMinimumSize(QSize(0, 0))
        self.frame_library_matching_3.setMaximumSize(QSize(16777215, 16777215))
        self.frame_library_matching_3.setLineWidth(1)
        self.frame_library_matching_3.setProperty(u"wpGrad", False)
        self.vboxLayout92 = QVBoxLayout(self.frame_library_matching_3)
        self.vboxLayout92.setObjectName(u"vboxLayout92")
        self.checkBox_library_matching_enable = QCheckBox(self.frame_library_matching_3)
        self.checkBox_library_matching_enable.setObjectName(u"checkBox_library_matching_enable")
        self.checkBox_library_matching_enable.setChecked(False)

        self.vboxLayout92.addWidget(self.checkBox_library_matching_enable)

        self.pushButton_library_matching_select_library = QPushButton(self.frame_library_matching_3)
        self.pushButton_library_matching_select_library.setObjectName(u"pushButton_library_matching_select_library")
        sizePolicy1.setHeightForWidth(self.pushButton_library_matching_select_library.sizePolicy().hasHeightForWidth())
        self.pushButton_library_matching_select_library.setSizePolicy(sizePolicy1)
        self.pushButton_library_matching_select_library.setMinimumSize(QSize(0, 30))
        self.pushButton_library_matching_select_library.setFont(font)

        self.vboxLayout92.addWidget(self.pushButton_library_matching_select_library)

        self.formLayout_library_matching_options = QFormLayout()
        self.formLayout_library_matching_options.setObjectName(u"formLayout_library_matching_options")
        self.formLayout_library_matching_options.setLabelAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.formLayout_library_matching_options.setHorizontalSpacing(0)
        self.formLayout_library_matching_options.setVerticalSpacing(3)
        self.formLayout_library_matching_options.setContentsMargins(6, 6, 6, 9)
        self.label_library_matching_matched_compound_name_label = QLabel(self.frame_library_matching_3)
        self.label_library_matching_matched_compound_name_label.setObjectName(u"label_library_matching_matched_compound_name_label")
        font3 = QFont()
        font3.setPointSize(10)
        self.label_library_matching_matched_compound_name_label.setFont(font3)

        self.formLayout_library_matching_options.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_library_matching_matched_compound_name_label)

        self.label_library_matching_matched_compound_name = QLabel(self.frame_library_matching_3)
        self.label_library_matching_matched_compound_name.setObjectName(u"label_library_matching_matched_compound_name")
        self.label_library_matching_matched_compound_name.setFont(font3)

        self.formLayout_library_matching_options.setWidget(0, QFormLayout.ItemRole.FieldRole, self.label_library_matching_matched_compound_name)

        self.label_library_matching_matched_compound_score_label = QLabel(self.frame_library_matching_3)
        self.label_library_matching_matched_compound_score_label.setObjectName(u"label_library_matching_matched_compound_score_label")
        self.label_library_matching_matched_compound_score_label.setFont(font3)

        self.formLayout_library_matching_options.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_library_matching_matched_compound_score_label)

        self.label_library_matching_matched_compound_score = QLabel(self.frame_library_matching_3)
        self.label_library_matching_matched_compound_score.setObjectName(u"label_library_matching_matched_compound_score")
        self.label_library_matching_matched_compound_score.setFont(font3)

        self.formLayout_library_matching_options.setWidget(1, QFormLayout.ItemRole.FieldRole, self.label_library_matching_matched_compound_score)

        self.label_library_matching_min_score_label = QLabel(self.frame_library_matching_3)
        self.label_library_matching_min_score_label.setObjectName(u"label_library_matching_min_score_label")
        self.label_library_matching_min_score_label.setFont(font3)

        self.formLayout_library_matching_options.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_library_matching_min_score_label)

        self.doubleSpinBox_library_matching_min_score = QDoubleSpinBox(self.frame_library_matching_3)
        self.doubleSpinBox_library_matching_min_score.setObjectName(u"doubleSpinBox_library_matching_min_score")
        self.doubleSpinBox_library_matching_min_score.setMinimumSize(QSize(125, 0))
        self.doubleSpinBox_library_matching_min_score.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.doubleSpinBox_library_matching_min_score.setKeyboardTracking(False)
        self.doubleSpinBox_library_matching_min_score.setDecimals(2)
        self.doubleSpinBox_library_matching_min_score.setMinimum(0.050000000000000)
        self.doubleSpinBox_library_matching_min_score.setMaximum(0.950000000000000)
        self.doubleSpinBox_library_matching_min_score.setSingleStep(0.010000000000000)
        self.doubleSpinBox_library_matching_min_score.setValue(0.650000000000000)

        self.formLayout_library_matching_options.setWidget(2, QFormLayout.ItemRole.FieldRole, self.doubleSpinBox_library_matching_min_score)

        self.label_library_matching_max_results_label = QLabel(self.frame_library_matching_3)
        self.label_library_matching_max_results_label.setObjectName(u"label_library_matching_max_results_label")
        self.label_library_matching_max_results_label.setFont(font3)

        self.formLayout_library_matching_options.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label_library_matching_max_results_label)

        self.spinBox_library_matching_max_results = QSpinBox(self.frame_library_matching_3)
        self.spinBox_library_matching_max_results.setObjectName(u"spinBox_library_matching_max_results")
        sizePolicy1.setHeightForWidth(self.spinBox_library_matching_max_results.sizePolicy().hasHeightForWidth())
        self.spinBox_library_matching_max_results.setSizePolicy(sizePolicy1)
        self.spinBox_library_matching_max_results.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.spinBox_library_matching_max_results.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_library_matching_max_results.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)
        self.spinBox_library_matching_max_results.setAccelerated(True)
        self.spinBox_library_matching_max_results.setKeyboardTracking(False)
        self.spinBox_library_matching_max_results.setMinimum(0)
        self.spinBox_library_matching_max_results.setMaximum(99)
        self.spinBox_library_matching_max_results.setSingleStep(1)
        self.spinBox_library_matching_max_results.setValue(2)

        self.formLayout_library_matching_options.setWidget(3, QFormLayout.ItemRole.FieldRole, self.spinBox_library_matching_max_results)

        self.checkBox_library_matching_use_dist = QCheckBox(self.frame_library_matching_3)
        self.checkBox_library_matching_use_dist.setObjectName(u"checkBox_library_matching_use_dist")
        self.checkBox_library_matching_use_dist.setChecked(True)

        self.formLayout_library_matching_options.setWidget(4, QFormLayout.ItemRole.LabelRole, self.checkBox_library_matching_use_dist)

        self.label_library_matching_use_dist_label = QLabel(self.frame_library_matching_3)
        self.label_library_matching_use_dist_label.setObjectName(u"label_library_matching_use_dist_label")

        self.formLayout_library_matching_options.setWidget(4, QFormLayout.ItemRole.FieldRole, self.label_library_matching_use_dist_label)


        self.vboxLayout92.addLayout(self.formLayout_library_matching_options)

        self.pushButton_library_matching_save_to_library = QPushButton(self.frame_library_matching_3)
        self.pushButton_library_matching_save_to_library.setObjectName(u"pushButton_library_matching_save_to_library")
        sizePolicy1.setHeightForWidth(self.pushButton_library_matching_save_to_library.sizePolicy().hasHeightForWidth())
        self.pushButton_library_matching_save_to_library.setSizePolicy(sizePolicy1)
        self.pushButton_library_matching_save_to_library.setMinimumSize(QSize(0, 30))
        self.pushButton_library_matching_save_to_library.setFont(font)

        self.vboxLayout92.addWidget(self.pushButton_library_matching_save_to_library)


        self.grid_library_matching_1.addWidget(self.frame_library_matching_3, 0, 0, 1, 1)


        self.vboxLayout91.addWidget(self.frame_library_matching_2)


        self.controlWidget_inner_vbox.addWidget(self.frame_library_matching_1)

        self.label_plugin_selection_widget = QLabel(self.controlWidget_inner)
        self.label_plugin_selection_widget.setObjectName(u"label_plugin_selection_widget")
        sizePolicy16.setHeightForWidth(self.label_plugin_selection_widget.sizePolicy().hasHeightForWidth())
        self.label_plugin_selection_widget.setSizePolicy(sizePolicy16)
        self.label_plugin_selection_widget.setFont(font2)

        self.controlWidget_inner_vbox.addWidget(self.label_plugin_selection_widget)

        self.frame_plugin_option_white = QFrame(self.controlWidget_inner)
        self.frame_plugin_option_white.setObjectName(u"frame_plugin_option_white")
        self.frame_plugin_option_white.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_plugin_option_white.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_plugin_option_white.setProperty(u"wpBox", False)
        self.vboxLayout93 = QVBoxLayout(self.frame_plugin_option_white)
        self.vboxLayout93.setObjectName(u"vboxLayout93")
        self.vboxLayout93.setContentsMargins(0, 0, 0, 0)
        self.frame_plugin_option_black = QFrame(self.frame_plugin_option_white)
        self.frame_plugin_option_black.setObjectName(u"frame_plugin_option_black")
        self.frame_plugin_option_black.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_plugin_option_black.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_plugin_option_black.setProperty(u"wpPanel", False)
        self.frame_plugin_option_black.setProperty(u"wpGrad", False)
        self.vboxLayout94 = QVBoxLayout(self.frame_plugin_option_black)
        self.vboxLayout94.setObjectName(u"vboxLayout94")
        self.comboBox_plugin_module = QComboBox(self.frame_plugin_option_black)
        self.comboBox_plugin_module.setObjectName(u"comboBox_plugin_module")
        sizePolicy24 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        sizePolicy24.setHorizontalStretch(0)
        sizePolicy24.setVerticalStretch(0)
        sizePolicy24.setHeightForWidth(self.comboBox_plugin_module.sizePolicy().hasHeightForWidth())
        self.comboBox_plugin_module.setSizePolicy(sizePolicy24)
        self.comboBox_plugin_module.setMinimumSize(QSize(200, 0))
        self.comboBox_plugin_module.setMaximumSize(QSize(300, 16777215))
        self.comboBox_plugin_module.setFont(font)
        self.comboBox_plugin_module.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.vboxLayout94.addWidget(self.comboBox_plugin_module)

        self.checkBox_plugin_connected = QCheckBox(self.frame_plugin_option_black)
        self.checkBox_plugin_connected.setObjectName(u"checkBox_plugin_connected")

        self.vboxLayout94.addWidget(self.checkBox_plugin_connected)


        self.vboxLayout93.addWidget(self.frame_plugin_option_black)


        self.controlWidget_inner_vbox.addWidget(self.frame_plugin_option_white)

        self.frame_plugin_control = QFrame(self.controlWidget_inner)
        self.frame_plugin_control.setObjectName(u"frame_plugin_control")
        sizePolicy16.setHeightForWidth(self.frame_plugin_control.sizePolicy().hasHeightForWidth())
        self.frame_plugin_control.setSizePolicy(sizePolicy16)
        self.frame_plugin_control.setLineWidth(1)
        self.vboxLayout95 = QVBoxLayout(self.frame_plugin_control)
        self.vboxLayout95.setObjectName(u"vboxLayout95")
        self.vboxLayout95.setContentsMargins(0, 0, 0, 0)
        self.label_plugin_widget = QLabel(self.frame_plugin_control)
        self.label_plugin_widget.setObjectName(u"label_plugin_widget")
        sizePolicy16.setHeightForWidth(self.label_plugin_widget.sizePolicy().hasHeightForWidth())
        self.label_plugin_widget.setSizePolicy(sizePolicy16)
        self.label_plugin_widget.setFont(font2)

        self.vboxLayout95.addWidget(self.label_plugin_widget)

        self.pluginWidget_border = QFrame(self.frame_plugin_control)
        self.pluginWidget_border.setObjectName(u"pluginWidget_border")
        sizePolicy16.setHeightForWidth(self.pluginWidget_border.sizePolicy().hasHeightForWidth())
        self.pluginWidget_border.setSizePolicy(sizePolicy16)
        self.pluginWidget_border.setLineWidth(1)
        self.pluginWidget_border.setProperty(u"wpBox", False)
        self.temperatureWidget_grid_2 = QGridLayout(self.pluginWidget_border)
        self.temperatureWidget_grid_2.setSpacing(0)
        self.temperatureWidget_grid_2.setObjectName(u"temperatureWidget_grid_2")
        self.temperatureWidget_grid_2.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.temperatureWidget_grid_2.setContentsMargins(0, 0, 0, 0)
        self.pluginWidget_shaded = QFrame(self.pluginWidget_border)
        self.pluginWidget_shaded.setObjectName(u"pluginWidget_shaded")
        sizePolicy16.setHeightForWidth(self.pluginWidget_shaded.sizePolicy().hasHeightForWidth())
        self.pluginWidget_shaded.setSizePolicy(sizePolicy16)
        self.pluginWidget_shaded.setMinimumSize(QSize(0, 0))
        self.pluginWidget_shaded.setMaximumSize(QSize(16777215, 16777215))
        self.pluginWidget_shaded.setLineWidth(1)
        self.pluginWidget_shaded.setProperty(u"wpGrad", False)
        self.vboxLayout96 = QVBoxLayout(self.pluginWidget_shaded)
        self.vboxLayout96.setObjectName(u"vboxLayout96")
        self.label_plugin_title = QLabel(self.pluginWidget_shaded)
        self.label_plugin_title.setObjectName(u"label_plugin_title")
        sizePolicy16.setHeightForWidth(self.label_plugin_title.sizePolicy().hasHeightForWidth())
        self.label_plugin_title.setSizePolicy(sizePolicy16)
        self.label_plugin_title.setMaximumSize(QSize(16777215, 20))
        self.label_plugin_title.setFont(font2)
        self.label_plugin_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.vboxLayout96.addWidget(self.label_plugin_title)

        self.frame_plugin_fields = QFrame(self.pluginWidget_shaded)
        self.frame_plugin_fields.setObjectName(u"frame_plugin_fields")
        sizePolicy16.setHeightForWidth(self.frame_plugin_fields.sizePolicy().hasHeightForWidth())
        self.frame_plugin_fields.setSizePolicy(sizePolicy16)
        self.frame_plugin_fields.setMinimumSize(QSize(0, 20))
        self.frame_plugin_fields.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_plugin_fields.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_plugin_fields.setProperty(u"wpBox", False)
        self.vboxLayout97 = QVBoxLayout(self.frame_plugin_fields)
        self.vboxLayout97.setObjectName(u"vboxLayout97")
        self.verticalLayout_plugin_fields = QVBoxLayout()
        self.verticalLayout_plugin_fields.setObjectName(u"verticalLayout_plugin_fields")

        self.vboxLayout97.addLayout(self.verticalLayout_plugin_fields)


        self.vboxLayout96.addWidget(self.frame_plugin_fields)

        self.pushButton_plugin_process = QPushButton(self.pluginWidget_shaded)
        self.pushButton_plugin_process.setObjectName(u"pushButton_plugin_process")
        sizePolicy1.setHeightForWidth(self.pushButton_plugin_process.sizePolicy().hasHeightForWidth())
        self.pushButton_plugin_process.setSizePolicy(sizePolicy1)
        self.pushButton_plugin_process.setMinimumSize(QSize(0, 30))
        self.pushButton_plugin_process.setFont(font)

        self.vboxLayout96.addWidget(self.pushButton_plugin_process)


        self.temperatureWidget_grid_2.addWidget(self.pluginWidget_shaded, 0, 0, 1, 1)


        self.vboxLayout95.addWidget(self.pluginWidget_border)


        self.controlWidget_inner_vbox.addWidget(self.frame_plugin_control)

        self.frame_scanAveraging = QFrame(self.controlWidget_inner)
        self.frame_scanAveraging.setObjectName(u"frame_scanAveraging")
        self.vboxLayout98 = QVBoxLayout(self.frame_scanAveraging)
        self.vboxLayout98.setObjectName(u"vboxLayout98")
        self.vboxLayout98.setContentsMargins(0, 0, 0, 0)
        self.scanAveragingWidget_label = QLabel(self.frame_scanAveraging)
        self.scanAveragingWidget_label.setObjectName(u"scanAveragingWidget_label")
        sizePolicy16.setHeightForWidth(self.scanAveragingWidget_label.sizePolicy().hasHeightForWidth())
        self.scanAveragingWidget_label.setSizePolicy(sizePolicy16)
        self.scanAveragingWidget_label.setFont(font2)

        self.vboxLayout98.addWidget(self.scanAveragingWidget_label)

        self.scanAveragingWidget_border = QFrame(self.frame_scanAveraging)
        self.scanAveragingWidget_border.setObjectName(u"scanAveragingWidget_border")
        self.scanAveragingWidget_border.setLineWidth(1)
        self.scanAveragingWidget_border.setProperty(u"wpBox", False)
        self.scanAveragingWidget_grid = QGridLayout(self.scanAveragingWidget_border)
        self.scanAveragingWidget_grid.setSpacing(0)
        self.scanAveragingWidget_grid.setObjectName(u"scanAveragingWidget_grid")
        self.scanAveragingWidget_grid.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.scanAveragingWidget_grid.setContentsMargins(0, 0, 0, 0)
        self.scanAveragingWidget_shaded = QFrame(self.scanAveragingWidget_border)
        self.scanAveragingWidget_shaded.setObjectName(u"scanAveragingWidget_shaded")
        self.scanAveragingWidget_shaded.setLineWidth(1)
        self.scanAveragingWidget_shaded.setProperty(u"wpGrad", False)
        self.vboxLayout99 = QVBoxLayout(self.scanAveragingWidget_shaded)
        self.vboxLayout99.setSpacing(0)
        self.vboxLayout99.setObjectName(u"vboxLayout99")
        self.vboxLayout99.setContentsMargins(0, 5, 0, 5)
        self.hboxLayout48 = QHBoxLayout()
        self.hboxLayout48.setObjectName(u"hboxLayout48")
        self.hboxLayout48.setContentsMargins(9, -1, 9, -1)
        self.pushButton_scan_averaging_dn = QPushButton(self.scanAveragingWidget_shaded)
        self.pushButton_scan_averaging_dn.setObjectName(u"pushButton_scan_averaging_dn")
        sizePolicy1.setHeightForWidth(self.pushButton_scan_averaging_dn.sizePolicy().hasHeightForWidth())
        self.pushButton_scan_averaging_dn.setSizePolicy(sizePolicy1)
        self.pushButton_scan_averaging_dn.setMinimumSize(QSize(20, 40))
        self.pushButton_scan_averaging_dn.setMaximumSize(QSize(40, 40))
        self.pushButton_scan_averaging_dn.setIcon(icon14)
        self.pushButton_scan_averaging_dn.setIconSize(QSize(20, 20))
        self.pushButton_scan_averaging_dn.setAutoRepeat(True)

        self.hboxLayout48.addWidget(self.pushButton_scan_averaging_dn)

        self.spinBox_scan_averaging = QSpinBox(self.scanAveragingWidget_shaded)
        self.spinBox_scan_averaging.setObjectName(u"spinBox_scan_averaging")
        sizePolicy1.setHeightForWidth(self.spinBox_scan_averaging.sizePolicy().hasHeightForWidth())
        self.spinBox_scan_averaging.setSizePolicy(sizePolicy1)
        self.spinBox_scan_averaging.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.spinBox_scan_averaging.setWrapping(False)
        self.spinBox_scan_averaging.setFrame(True)
        self.spinBox_scan_averaging.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_scan_averaging.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.spinBox_scan_averaging.setAccelerated(True)
        self.spinBox_scan_averaging.setKeyboardTracking(False)
        self.spinBox_scan_averaging.setMinimum(1)
        self.spinBox_scan_averaging.setMaximum(1000)
        self.spinBox_scan_averaging.setValue(1)

        self.hboxLayout48.addWidget(self.spinBox_scan_averaging)

        self.pushButton_scan_averaging_up = QPushButton(self.scanAveragingWidget_shaded)
        self.pushButton_scan_averaging_up.setObjectName(u"pushButton_scan_averaging_up")
        sizePolicy1.setHeightForWidth(self.pushButton_scan_averaging_up.sizePolicy().hasHeightForWidth())
        self.pushButton_scan_averaging_up.setSizePolicy(sizePolicy1)
        self.pushButton_scan_averaging_up.setMinimumSize(QSize(20, 40))
        self.pushButton_scan_averaging_up.setMaximumSize(QSize(40, 40))
        self.pushButton_scan_averaging_up.setIcon(icon35)
        self.pushButton_scan_averaging_up.setIconSize(QSize(20, 20))
        self.pushButton_scan_averaging_up.setAutoRepeat(True)

        self.hboxLayout48.addWidget(self.pushButton_scan_averaging_up)


        self.vboxLayout99.addLayout(self.hboxLayout48)

        self.label_scan_averaging = QLabel(self.scanAveragingWidget_shaded)
        self.label_scan_averaging.setObjectName(u"label_scan_averaging")
        sizePolicy16.setHeightForWidth(self.label_scan_averaging.sizePolicy().hasHeightForWidth())
        self.label_scan_averaging.setSizePolicy(sizePolicy16)
        self.label_scan_averaging.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.vboxLayout99.addWidget(self.label_scan_averaging)


        self.scanAveragingWidget_grid.addWidget(self.scanAveragingWidget_shaded, 0, 0, 1, 1)


        self.vboxLayout98.addWidget(self.scanAveragingWidget_border)


        self.controlWidget_inner_vbox.addWidget(self.frame_scanAveraging)

        self.boxcarWidget = QFrame(self.controlWidget_inner)
        self.boxcarWidget.setObjectName(u"boxcarWidget")
        sizePolicy16.setHeightForWidth(self.boxcarWidget.sizePolicy().hasHeightForWidth())
        self.boxcarWidget.setSizePolicy(sizePolicy16)
        self.boxcarWidget.setMinimumSize(QSize(0, 0))
        self.vboxLayout100 = QVBoxLayout(self.boxcarWidget)
        self.vboxLayout100.setObjectName(u"vboxLayout100")
        self.vboxLayout100.setContentsMargins(0, 0, 0, 0)
        self.boxcarWidget_label = QLabel(self.boxcarWidget)
        self.boxcarWidget_label.setObjectName(u"boxcarWidget_label")
        sizePolicy16.setHeightForWidth(self.boxcarWidget_label.sizePolicy().hasHeightForWidth())
        self.boxcarWidget_label.setSizePolicy(sizePolicy16)
        self.boxcarWidget_label.setFont(font2)

        self.vboxLayout100.addWidget(self.boxcarWidget_label)

        self.boxcarWidget_border = QFrame(self.boxcarWidget)
        self.boxcarWidget_border.setObjectName(u"boxcarWidget_border")
        sizePolicy16.setHeightForWidth(self.boxcarWidget_border.sizePolicy().hasHeightForWidth())
        self.boxcarWidget_border.setSizePolicy(sizePolicy16)
        self.boxcarWidget_border.setLineWidth(1)
        self.boxcarWidget_border.setProperty(u"wpBox", False)
        self.boxcarWidget_grid = QGridLayout(self.boxcarWidget_border)
        self.boxcarWidget_grid.setSpacing(0)
        self.boxcarWidget_grid.setObjectName(u"boxcarWidget_grid")
        self.boxcarWidget_grid.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.boxcarWidget_grid.setContentsMargins(0, 0, 0, 0)
        self.boxcarWidget_shaded = QFrame(self.boxcarWidget_border)
        self.boxcarWidget_shaded.setObjectName(u"boxcarWidget_shaded")
        sizePolicy16.setHeightForWidth(self.boxcarWidget_shaded.sizePolicy().hasHeightForWidth())
        self.boxcarWidget_shaded.setSizePolicy(sizePolicy16)
        self.boxcarWidget_shaded.setMinimumSize(QSize(0, 0))
        self.boxcarWidget_shaded.setMaximumSize(QSize(16777215, 16777215))
        self.boxcarWidget_shaded.setLineWidth(1)
        self.boxcarWidget_shaded.setProperty(u"wpGrad", False)
        self.vboxLayout101 = QVBoxLayout(self.boxcarWidget_shaded)
        self.vboxLayout101.setSpacing(1)
        self.vboxLayout101.setObjectName(u"vboxLayout101")
        self.vboxLayout101.setContentsMargins(0, 5, 0, 5)
        self.hboxLayout49 = QHBoxLayout()
        self.hboxLayout49.setObjectName(u"hboxLayout49")
        self.hboxLayout49.setContentsMargins(9, -1, 9, -1)
        self.pushButton_boxcar_half_width_dn = QPushButton(self.boxcarWidget_shaded)
        self.pushButton_boxcar_half_width_dn.setObjectName(u"pushButton_boxcar_half_width_dn")
        sizePolicy1.setHeightForWidth(self.pushButton_boxcar_half_width_dn.sizePolicy().hasHeightForWidth())
        self.pushButton_boxcar_half_width_dn.setSizePolicy(sizePolicy1)
        self.pushButton_boxcar_half_width_dn.setMinimumSize(QSize(20, 40))
        self.pushButton_boxcar_half_width_dn.setMaximumSize(QSize(40, 40))
        self.pushButton_boxcar_half_width_dn.setIcon(icon14)
        self.pushButton_boxcar_half_width_dn.setIconSize(QSize(20, 20))
        self.pushButton_boxcar_half_width_dn.setAutoRepeat(True)

        self.hboxLayout49.addWidget(self.pushButton_boxcar_half_width_dn)

        self.spinBox_boxcar_half_width = QSpinBox(self.boxcarWidget_shaded)
        self.spinBox_boxcar_half_width.setObjectName(u"spinBox_boxcar_half_width")
        sizePolicy1.setHeightForWidth(self.spinBox_boxcar_half_width.sizePolicy().hasHeightForWidth())
        self.spinBox_boxcar_half_width.setSizePolicy(sizePolicy1)
        self.spinBox_boxcar_half_width.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.spinBox_boxcar_half_width.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_boxcar_half_width.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.spinBox_boxcar_half_width.setAccelerated(True)
        self.spinBox_boxcar_half_width.setKeyboardTracking(False)
        self.spinBox_boxcar_half_width.setMinimum(0)
        self.spinBox_boxcar_half_width.setMaximum(99)
        self.spinBox_boxcar_half_width.setSingleStep(1)
        self.spinBox_boxcar_half_width.setValue(0)

        self.hboxLayout49.addWidget(self.spinBox_boxcar_half_width)

        self.pushButton_boxcar_half_width_up = QPushButton(self.boxcarWidget_shaded)
        self.pushButton_boxcar_half_width_up.setObjectName(u"pushButton_boxcar_half_width_up")
        sizePolicy1.setHeightForWidth(self.pushButton_boxcar_half_width_up.sizePolicy().hasHeightForWidth())
        self.pushButton_boxcar_half_width_up.setSizePolicy(sizePolicy1)
        self.pushButton_boxcar_half_width_up.setMinimumSize(QSize(20, 40))
        self.pushButton_boxcar_half_width_up.setMaximumSize(QSize(40, 40))
        self.pushButton_boxcar_half_width_up.setIcon(icon35)
        self.pushButton_boxcar_half_width_up.setIconSize(QSize(20, 20))
        self.pushButton_boxcar_half_width_up.setAutoRepeat(True)

        self.hboxLayout49.addWidget(self.pushButton_boxcar_half_width_up)


        self.vboxLayout101.addLayout(self.hboxLayout49)


        self.boxcarWidget_grid.addWidget(self.boxcarWidget_shaded, 0, 0, 1, 1)


        self.vboxLayout100.addWidget(self.boxcarWidget_border)


        self.controlWidget_inner_vbox.addWidget(self.boxcarWidget)

        self.frame_baseline_correction = QFrame(self.controlWidget_inner)
        self.frame_baseline_correction.setObjectName(u"frame_baseline_correction")
        sizePolicy16.setHeightForWidth(self.frame_baseline_correction.sizePolicy().hasHeightForWidth())
        self.frame_baseline_correction.setSizePolicy(sizePolicy16)
        self.frame_baseline_correction.setMinimumSize(QSize(0, 0))
        self.vboxLayout102 = QVBoxLayout(self.frame_baseline_correction)
        self.vboxLayout102.setObjectName(u"vboxLayout102")
        self.vboxLayout102.setContentsMargins(0, 0, 0, 0)
        self.boxcarWidget_label_2 = QLabel(self.frame_baseline_correction)
        self.boxcarWidget_label_2.setObjectName(u"boxcarWidget_label_2")
        sizePolicy16.setHeightForWidth(self.boxcarWidget_label_2.sizePolicy().hasHeightForWidth())
        self.boxcarWidget_label_2.setSizePolicy(sizePolicy16)
        self.boxcarWidget_label_2.setFont(font2)

        self.vboxLayout102.addWidget(self.boxcarWidget_label_2)

        self.frame_baseline_correction_white = QFrame(self.frame_baseline_correction)
        self.frame_baseline_correction_white.setObjectName(u"frame_baseline_correction_white")
        sizePolicy16.setHeightForWidth(self.frame_baseline_correction_white.sizePolicy().hasHeightForWidth())
        self.frame_baseline_correction_white.setSizePolicy(sizePolicy16)
        self.frame_baseline_correction_white.setLineWidth(1)
        self.frame_baseline_correction_white.setProperty(u"wpBox", False)
        self.backgroundSubtractionWidget_grid = QGridLayout(self.frame_baseline_correction_white)
        self.backgroundSubtractionWidget_grid.setSpacing(0)
        self.backgroundSubtractionWidget_grid.setObjectName(u"backgroundSubtractionWidget_grid")
        self.backgroundSubtractionWidget_grid.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.backgroundSubtractionWidget_grid.setContentsMargins(0, 0, 0, 0)
        self.frame_baseline_correction_black = QFrame(self.frame_baseline_correction_white)
        self.frame_baseline_correction_black.setObjectName(u"frame_baseline_correction_black")
        sizePolicy16.setHeightForWidth(self.frame_baseline_correction_black.sizePolicy().hasHeightForWidth())
        self.frame_baseline_correction_black.setSizePolicy(sizePolicy16)
        self.frame_baseline_correction_black.setMinimumSize(QSize(0, 0))
        self.frame_baseline_correction_black.setMaximumSize(QSize(16777215, 16777215))
        self.frame_baseline_correction_black.setLineWidth(1)
        self.frame_baseline_correction_black.setProperty(u"wpGrad", False)
        self.vboxLayout103 = QVBoxLayout(self.frame_baseline_correction_black)
        self.vboxLayout103.setSpacing(6)
        self.vboxLayout103.setObjectName(u"vboxLayout103")
        self.vboxLayout103.setContentsMargins(9, 9, 9, 9)
        self.hboxLayout50 = QHBoxLayout()
        self.hboxLayout50.setObjectName(u"hboxLayout50")
        self.checkBox_baselineCorrection_enable = QCheckBox(self.frame_baseline_correction_black)
        self.checkBox_baselineCorrection_enable.setObjectName(u"checkBox_baselineCorrection_enable")
        sizePolicy1.setHeightForWidth(self.checkBox_baselineCorrection_enable.sizePolicy().hasHeightForWidth())
        self.checkBox_baselineCorrection_enable.setSizePolicy(sizePolicy1)

        self.hboxLayout50.addWidget(self.checkBox_baselineCorrection_enable)

        self.checkBox_baselineCorrection_show = QCheckBox(self.frame_baseline_correction_black)
        self.checkBox_baselineCorrection_show.setObjectName(u"checkBox_baselineCorrection_show")
        sizePolicy1.setHeightForWidth(self.checkBox_baselineCorrection_show.sizePolicy().hasHeightForWidth())
        self.checkBox_baselineCorrection_show.setSizePolicy(sizePolicy1)

        self.hboxLayout50.addWidget(self.checkBox_baselineCorrection_show)


        self.vboxLayout103.addLayout(self.hboxLayout50)

        self.comboBox_baselineCorrection_algo = QComboBox(self.frame_baseline_correction_black)
        self.comboBox_baselineCorrection_algo.addItem("")
        self.comboBox_baselineCorrection_algo.addItem("")
        self.comboBox_baselineCorrection_algo.setObjectName(u"comboBox_baselineCorrection_algo")
        sizePolicy1.setHeightForWidth(self.comboBox_baselineCorrection_algo.sizePolicy().hasHeightForWidth())
        self.comboBox_baselineCorrection_algo.setSizePolicy(sizePolicy1)
        self.comboBox_baselineCorrection_algo.setFont(font)
        self.comboBox_baselineCorrection_algo.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.vboxLayout103.addWidget(self.comboBox_baselineCorrection_algo)


        self.backgroundSubtractionWidget_grid.addWidget(self.frame_baseline_correction_black, 0, 0, 1, 1)


        self.vboxLayout102.addWidget(self.frame_baseline_correction_white)


        self.controlWidget_inner_vbox.addWidget(self.frame_baseline_correction)

        self.frame_post_processing = QFrame(self.controlWidget_inner)
        self.frame_post_processing.setObjectName(u"frame_post_processing")
        sizePolicy16.setHeightForWidth(self.frame_post_processing.sizePolicy().hasHeightForWidth())
        self.frame_post_processing.setSizePolicy(sizePolicy16)
        self.frame_post_processing.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_post_processing.setFrameShadow(QFrame.Shadow.Raised)
        self.vboxLayout104 = QVBoxLayout(self.frame_post_processing)
        self.vboxLayout104.setObjectName(u"vboxLayout104")
        self.vboxLayout104.setContentsMargins(0, 0, 0, 0)
        self.label_post_processing = QLabel(self.frame_post_processing)
        self.label_post_processing.setObjectName(u"label_post_processing")
        sizePolicy16.setHeightForWidth(self.label_post_processing.sizePolicy().hasHeightForWidth())
        self.label_post_processing.setSizePolicy(sizePolicy16)
        self.label_post_processing.setFont(font2)

        self.vboxLayout104.addWidget(self.label_post_processing)

        self.frame_widget_post_processing_white = QFrame(self.frame_post_processing)
        self.frame_widget_post_processing_white.setObjectName(u"frame_widget_post_processing_white")
        sizePolicy16.setHeightForWidth(self.frame_widget_post_processing_white.sizePolicy().hasHeightForWidth())
        self.frame_widget_post_processing_white.setSizePolicy(sizePolicy16)
        self.frame_widget_post_processing_white.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_widget_post_processing_white.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_widget_post_processing_white.setProperty(u"wpBox", False)
        self.vboxLayout105 = QVBoxLayout(self.frame_widget_post_processing_white)
        self.vboxLayout105.setObjectName(u"vboxLayout105")
        self.vboxLayout105.setContentsMargins(1, 1, 1, 1)
        self.frame_widget_post_processing_black = QFrame(self.frame_widget_post_processing_white)
        self.frame_widget_post_processing_black.setObjectName(u"frame_widget_post_processing_black")
        sizePolicy16.setHeightForWidth(self.frame_widget_post_processing_black.sizePolicy().hasHeightForWidth())
        self.frame_widget_post_processing_black.setSizePolicy(sizePolicy16)
        self.frame_widget_post_processing_black.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_widget_post_processing_black.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_widget_post_processing_black.setProperty(u"wpGrad", False)
        self.gridLayout11 = QGridLayout(self.frame_widget_post_processing_black)
        self.gridLayout11.setObjectName(u"gridLayout11")
        self.checkBox_richardson_lucy = QCheckBox(self.frame_widget_post_processing_black)
        self.checkBox_richardson_lucy.setObjectName(u"checkBox_richardson_lucy")
        sizePolicy1.setHeightForWidth(self.checkBox_richardson_lucy.sizePolicy().hasHeightForWidth())
        self.checkBox_richardson_lucy.setSizePolicy(sizePolicy1)

        self.gridLayout11.addWidget(self.checkBox_richardson_lucy, 0, 0, 1, 2)

        self.checkBox_etalon_correction = QCheckBox(self.frame_widget_post_processing_black)
        self.checkBox_etalon_correction.setObjectName(u"checkBox_etalon_correction")
        sizePolicy1.setHeightForWidth(self.checkBox_etalon_correction.sizePolicy().hasHeightForWidth())
        self.checkBox_etalon_correction.setSizePolicy(sizePolicy1)

        self.gridLayout11.addWidget(self.checkBox_etalon_correction, 1, 0, 1, 2)

        self.checkBox_ingaas_correction = QCheckBox(self.frame_widget_post_processing_black)
        self.checkBox_ingaas_correction.setObjectName(u"checkBox_ingaas_correction")
        sizePolicy1.setHeightForWidth(self.checkBox_ingaas_correction.sizePolicy().hasHeightForWidth())
        self.checkBox_ingaas_correction.setSizePolicy(sizePolicy1)

        self.gridLayout11.addWidget(self.checkBox_ingaas_correction, 2, 0, 1, 2)


        self.vboxLayout105.addWidget(self.frame_widget_post_processing_black)


        self.vboxLayout104.addWidget(self.frame_widget_post_processing_white)


        self.controlWidget_inner_vbox.addWidget(self.frame_post_processing)

        self.frame_area_scan_widget = QFrame(self.controlWidget_inner)
        self.frame_area_scan_widget.setObjectName(u"frame_area_scan_widget")
        sizePolicy16.setHeightForWidth(self.frame_area_scan_widget.sizePolicy().hasHeightForWidth())
        self.frame_area_scan_widget.setSizePolicy(sizePolicy16)
        self.frame_area_scan_widget.setMinimumSize(QSize(0, 0))
        self.vboxLayout106 = QVBoxLayout(self.frame_area_scan_widget)
        self.vboxLayout106.setObjectName(u"vboxLayout106")
        self.vboxLayout106.setContentsMargins(0, 0, 0, 0)
        self.label_area_scan_widget = QLabel(self.frame_area_scan_widget)
        self.label_area_scan_widget.setObjectName(u"label_area_scan_widget")
        sizePolicy16.setHeightForWidth(self.label_area_scan_widget.sizePolicy().hasHeightForWidth())
        self.label_area_scan_widget.setSizePolicy(sizePolicy16)
        self.label_area_scan_widget.setFont(font2)

        self.vboxLayout106.addWidget(self.label_area_scan_widget)

        self.frame_area_scan_widget_white = QFrame(self.frame_area_scan_widget)
        self.frame_area_scan_widget_white.setObjectName(u"frame_area_scan_widget_white")
        sizePolicy16.setHeightForWidth(self.frame_area_scan_widget_white.sizePolicy().hasHeightForWidth())
        self.frame_area_scan_widget_white.setSizePolicy(sizePolicy16)
        self.frame_area_scan_widget_white.setLineWidth(1)
        self.frame_area_scan_widget_white.setProperty(u"wpBox", False)
        self.boxcarWidget_grid_4_x = QGridLayout(self.frame_area_scan_widget_white)
        self.boxcarWidget_grid_4_x.setSpacing(0)
        self.boxcarWidget_grid_4_x.setObjectName(u"boxcarWidget_grid_4_x")
        self.boxcarWidget_grid_4_x.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.boxcarWidget_grid_4_x.setContentsMargins(0, 0, 0, 0)
        self.frame_area_scan_widget_black = QFrame(self.frame_area_scan_widget_white)
        self.frame_area_scan_widget_black.setObjectName(u"frame_area_scan_widget_black")
        sizePolicy16.setHeightForWidth(self.frame_area_scan_widget_black.sizePolicy().hasHeightForWidth())
        self.frame_area_scan_widget_black.setSizePolicy(sizePolicy16)
        self.frame_area_scan_widget_black.setMinimumSize(QSize(0, 0))
        self.frame_area_scan_widget_black.setMaximumSize(QSize(16777215, 16777215))
        self.frame_area_scan_widget_black.setLineWidth(1)
        self.frame_area_scan_widget_black.setProperty(u"wpGrad", False)
        self.vboxLayout107 = QVBoxLayout(self.frame_area_scan_widget_black)
        self.vboxLayout107.setSpacing(1)
        self.vboxLayout107.setObjectName(u"vboxLayout107")
        self.vboxLayout107.setContentsMargins(5, 5, 5, 5)
        self.formLayout10 = QFormLayout()
        self.formLayout10.setObjectName(u"formLayout10")
        self.formLayout10.setLabelAlignment(Qt.AlignmentFlag.AlignCenter)
        self.formLayout10.setFormAlignment(Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignTop)
        self.formLayout10.setContentsMargins(0, -1, 0, -1)
        self.checkBox_area_scan_enable = QCheckBox(self.frame_area_scan_widget_black)
        self.checkBox_area_scan_enable.setObjectName(u"checkBox_area_scan_enable")
        sizePolicy1.setHeightForWidth(self.checkBox_area_scan_enable.sizePolicy().hasHeightForWidth())
        self.checkBox_area_scan_enable.setSizePolicy(sizePolicy1)

        self.formLayout10.setWidget(0, QFormLayout.ItemRole.LabelRole, self.checkBox_area_scan_enable)

        self.label202 = QLabel(self.frame_area_scan_widget_black)
        self.label202.setObjectName(u"label202")
        sizePolicy16.setHeightForWidth(self.label202.sizePolicy().hasHeightForWidth())
        self.label202.setSizePolicy(sizePolicy16)

        self.formLayout10.setWidget(0, QFormLayout.ItemRole.FieldRole, self.label202)

        self.checkBox_area_scan_normalize = QCheckBox(self.frame_area_scan_widget_black)
        self.checkBox_area_scan_normalize.setObjectName(u"checkBox_area_scan_normalize")
        sizePolicy1.setHeightForWidth(self.checkBox_area_scan_normalize.sizePolicy().hasHeightForWidth())
        self.checkBox_area_scan_normalize.setSizePolicy(sizePolicy1)
        self.checkBox_area_scan_normalize.setChecked(True)

        self.formLayout10.setWidget(1, QFormLayout.ItemRole.LabelRole, self.checkBox_area_scan_normalize)

        self.label203 = QLabel(self.frame_area_scan_widget_black)
        self.label203.setObjectName(u"label203")
        sizePolicy16.setHeightForWidth(self.label203.sizePolicy().hasHeightForWidth())
        self.label203.setSizePolicy(sizePolicy16)

        self.formLayout10.setWidget(1, QFormLayout.ItemRole.FieldRole, self.label203)

        self.checkBox_area_scan_normalize_csv = QCheckBox(self.frame_area_scan_widget_black)
        self.checkBox_area_scan_normalize_csv.setObjectName(u"checkBox_area_scan_normalize_csv")
        sizePolicy1.setHeightForWidth(self.checkBox_area_scan_normalize_csv.sizePolicy().hasHeightForWidth())
        self.checkBox_area_scan_normalize_csv.setSizePolicy(sizePolicy1)
        self.checkBox_area_scan_normalize_csv.setChecked(True)

        self.formLayout10.setWidget(2, QFormLayout.ItemRole.LabelRole, self.checkBox_area_scan_normalize_csv)

        self.label204 = QLabel(self.frame_area_scan_widget_black)
        self.label204.setObjectName(u"label204")
        sizePolicy16.setHeightForWidth(self.label204.sizePolicy().hasHeightForWidth())
        self.label204.setSizePolicy(sizePolicy16)

        self.formLayout10.setWidget(2, QFormLayout.ItemRole.FieldRole, self.label204)

        self.label_area_scan_current_line = QLabel(self.frame_area_scan_widget_black)
        self.label_area_scan_current_line.setObjectName(u"label_area_scan_current_line")
        sizePolicy16.setHeightForWidth(self.label_area_scan_current_line.sizePolicy().hasHeightForWidth())
        self.label_area_scan_current_line.setSizePolicy(sizePolicy16)

        self.formLayout10.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label_area_scan_current_line)

        self.label205 = QLabel(self.frame_area_scan_widget_black)
        self.label205.setObjectName(u"label205")
        sizePolicy16.setHeightForWidth(self.label205.sizePolicy().hasHeightForWidth())
        self.label205.setSizePolicy(sizePolicy16)

        self.formLayout10.setWidget(3, QFormLayout.ItemRole.FieldRole, self.label205)

        self.label_area_scan_frame_count = QLabel(self.frame_area_scan_widget_black)
        self.label_area_scan_frame_count.setObjectName(u"label_area_scan_frame_count")
        sizePolicy16.setHeightForWidth(self.label_area_scan_frame_count.sizePolicy().hasHeightForWidth())
        self.label_area_scan_frame_count.setSizePolicy(sizePolicy16)

        self.formLayout10.setWidget(4, QFormLayout.ItemRole.LabelRole, self.label_area_scan_frame_count)

        self.label206 = QLabel(self.frame_area_scan_widget_black)
        self.label206.setObjectName(u"label206")
        sizePolicy16.setHeightForWidth(self.label206.sizePolicy().hasHeightForWidth())
        self.label206.setSizePolicy(sizePolicy16)

        self.formLayout10.setWidget(4, QFormLayout.ItemRole.FieldRole, self.label206)

        self.spinBox_area_scan_start_line = QSpinBox(self.frame_area_scan_widget_black)
        self.spinBox_area_scan_start_line.setObjectName(u"spinBox_area_scan_start_line")
        sizePolicy8.setHeightForWidth(self.spinBox_area_scan_start_line.sizePolicy().hasHeightForWidth())
        self.spinBox_area_scan_start_line.setSizePolicy(sizePolicy8)
        self.spinBox_area_scan_start_line.setMinimumSize(QSize(110, 0))
        self.spinBox_area_scan_start_line.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.spinBox_area_scan_start_line.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_area_scan_start_line.setMinimum(0)
        self.spinBox_area_scan_start_line.setMaximum(2000)
        self.spinBox_area_scan_start_line.setValue(1)

        self.formLayout10.setWidget(5, QFormLayout.ItemRole.LabelRole, self.spinBox_area_scan_start_line)

        self.label207 = QLabel(self.frame_area_scan_widget_black)
        self.label207.setObjectName(u"label207")
        sizePolicy16.setHeightForWidth(self.label207.sizePolicy().hasHeightForWidth())
        self.label207.setSizePolicy(sizePolicy16)

        self.formLayout10.setWidget(5, QFormLayout.ItemRole.FieldRole, self.label207)

        self.spinBox_area_scan_stop_line = QSpinBox(self.frame_area_scan_widget_black)
        self.spinBox_area_scan_stop_line.setObjectName(u"spinBox_area_scan_stop_line")
        sizePolicy8.setHeightForWidth(self.spinBox_area_scan_stop_line.sizePolicy().hasHeightForWidth())
        self.spinBox_area_scan_stop_line.setSizePolicy(sizePolicy8)
        self.spinBox_area_scan_stop_line.setMinimumSize(QSize(110, 0))
        self.spinBox_area_scan_stop_line.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.spinBox_area_scan_stop_line.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_area_scan_stop_line.setMaximum(2000)
        self.spinBox_area_scan_stop_line.setValue(70)

        self.formLayout10.setWidget(6, QFormLayout.ItemRole.LabelRole, self.spinBox_area_scan_stop_line)

        self.label208 = QLabel(self.frame_area_scan_widget_black)
        self.label208.setObjectName(u"label208")
        sizePolicy16.setHeightForWidth(self.label208.sizePolicy().hasHeightForWidth())
        self.label208.setSizePolicy(sizePolicy16)

        self.formLayout10.setWidget(6, QFormLayout.ItemRole.FieldRole, self.label208)

        self.spinBox_area_scan_line_step = QSpinBox(self.frame_area_scan_widget_black)
        self.spinBox_area_scan_line_step.setObjectName(u"spinBox_area_scan_line_step")
        sizePolicy8.setHeightForWidth(self.spinBox_area_scan_line_step.sizePolicy().hasHeightForWidth())
        self.spinBox_area_scan_line_step.setSizePolicy(sizePolicy8)
        self.spinBox_area_scan_line_step.setMinimumSize(QSize(110, 0))
        self.spinBox_area_scan_line_step.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.spinBox_area_scan_line_step.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_area_scan_line_step.setMinimum(1)
        self.spinBox_area_scan_line_step.setMaximum(255)
        self.spinBox_area_scan_line_step.setValue(1)

        self.formLayout10.setWidget(7, QFormLayout.ItemRole.LabelRole, self.spinBox_area_scan_line_step)

        self.label209 = QLabel(self.frame_area_scan_widget_black)
        self.label209.setObjectName(u"label209")
        sizePolicy16.setHeightForWidth(self.label209.sizePolicy().hasHeightForWidth())
        self.label209.setSizePolicy(sizePolicy16)

        self.formLayout10.setWidget(7, QFormLayout.ItemRole.FieldRole, self.label209)

        self.spinBox_area_scan_cursor = QSpinBox(self.frame_area_scan_widget_black)
        self.spinBox_area_scan_cursor.setObjectName(u"spinBox_area_scan_cursor")
        sizePolicy8.setHeightForWidth(self.spinBox_area_scan_cursor.sizePolicy().hasHeightForWidth())
        self.spinBox_area_scan_cursor.setSizePolicy(sizePolicy8)
        self.spinBox_area_scan_cursor.setMinimumSize(QSize(110, 0))
        self.spinBox_area_scan_cursor.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.spinBox_area_scan_cursor.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_area_scan_cursor.setMinimum(0)
        self.spinBox_area_scan_cursor.setMaximum(1080)
        self.spinBox_area_scan_cursor.setValue(0)

        self.formLayout10.setWidget(8, QFormLayout.ItemRole.LabelRole, self.spinBox_area_scan_cursor)

        self.label210 = QLabel(self.frame_area_scan_widget_black)
        self.label210.setObjectName(u"label210")
        sizePolicy16.setHeightForWidth(self.label210.sizePolicy().hasHeightForWidth())
        self.label210.setSizePolicy(sizePolicy16)

        self.formLayout10.setWidget(8, QFormLayout.ItemRole.FieldRole, self.label210)

        self.spinBox_area_scan_scale = QSpinBox(self.frame_area_scan_widget_black)
        self.spinBox_area_scan_scale.setObjectName(u"spinBox_area_scan_scale")
        sizePolicy8.setHeightForWidth(self.spinBox_area_scan_scale.sizePolicy().hasHeightForWidth())
        self.spinBox_area_scan_scale.setSizePolicy(sizePolicy8)
        self.spinBox_area_scan_scale.setMinimumSize(QSize(110, 0))
        self.spinBox_area_scan_scale.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.spinBox_area_scan_scale.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_area_scan_scale.setMinimum(1)
        self.spinBox_area_scan_scale.setMaximum(10)
        self.spinBox_area_scan_scale.setValue(1)

        self.formLayout10.setWidget(9, QFormLayout.ItemRole.LabelRole, self.spinBox_area_scan_scale)

        self.label211 = QLabel(self.frame_area_scan_widget_black)
        self.label211.setObjectName(u"label211")
        sizePolicy16.setHeightForWidth(self.label211.sizePolicy().hasHeightForWidth())
        self.label211.setSizePolicy(sizePolicy16)

        self.formLayout10.setWidget(9, QFormLayout.ItemRole.FieldRole, self.label211)

        self.checkBox_area_scan_fit = QCheckBox(self.frame_area_scan_widget_black)
        self.checkBox_area_scan_fit.setObjectName(u"checkBox_area_scan_fit")
        sizePolicy1.setHeightForWidth(self.checkBox_area_scan_fit.sizePolicy().hasHeightForWidth())
        self.checkBox_area_scan_fit.setSizePolicy(sizePolicy1)
        self.checkBox_area_scan_fit.setChecked(True)

        self.formLayout10.setWidget(10, QFormLayout.ItemRole.LabelRole, self.checkBox_area_scan_fit)

        self.label212 = QLabel(self.frame_area_scan_widget_black)
        self.label212.setObjectName(u"label212")
        sizePolicy16.setHeightForWidth(self.label212.sizePolicy().hasHeightForWidth())
        self.label212.setSizePolicy(sizePolicy16)

        self.formLayout10.setWidget(10, QFormLayout.ItemRole.FieldRole, self.label212)

        self.label_area_scan_frame_elapsed = QLabel(self.frame_area_scan_widget_black)
        self.label_area_scan_frame_elapsed.setObjectName(u"label_area_scan_frame_elapsed")
        sizePolicy16.setHeightForWidth(self.label_area_scan_frame_elapsed.sizePolicy().hasHeightForWidth())
        self.label_area_scan_frame_elapsed.setSizePolicy(sizePolicy16)

        self.formLayout10.setWidget(11, QFormLayout.ItemRole.LabelRole, self.label_area_scan_frame_elapsed)

        self.label213 = QLabel(self.frame_area_scan_widget_black)
        self.label213.setObjectName(u"label213")
        sizePolicy16.setHeightForWidth(self.label213.sizePolicy().hasHeightForWidth())
        self.label213.setSizePolicy(sizePolicy16)

        self.formLayout10.setWidget(11, QFormLayout.ItemRole.FieldRole, self.label213)


        self.vboxLayout107.addLayout(self.formLayout10)

        self.pushButton_area_scan_save = QPushButton(self.frame_area_scan_widget_black)
        self.pushButton_area_scan_save.setObjectName(u"pushButton_area_scan_save")
        sizePolicy1.setHeightForWidth(self.pushButton_area_scan_save.sizePolicy().hasHeightForWidth())
        self.pushButton_area_scan_save.setSizePolicy(sizePolicy1)
        self.pushButton_area_scan_save.setMinimumSize(QSize(0, 30))
        self.pushButton_area_scan_save.setFont(font)

        self.vboxLayout107.addWidget(self.pushButton_area_scan_save)


        self.boxcarWidget_grid_4_x.addWidget(self.frame_area_scan_widget_black, 0, 0, 1, 1)


        self.vboxLayout106.addWidget(self.frame_area_scan_widget_white)


        self.controlWidget_inner_vbox.addWidget(self.frame_area_scan_widget)

        self.frame_transmission_options = QFrame(self.controlWidget_inner)
        self.frame_transmission_options.setObjectName(u"frame_transmission_options")
        self.frame_transmission_options.setEnabled(True)
        sizePolicy16.setHeightForWidth(self.frame_transmission_options.sizePolicy().hasHeightForWidth())
        self.frame_transmission_options.setSizePolicy(sizePolicy16)
        self.frame_transmission_options.setMinimumSize(QSize(0, 0))
        self.vboxLayout108 = QVBoxLayout(self.frame_transmission_options)
        self.vboxLayout108.setObjectName(u"vboxLayout108")
        self.vboxLayout108.setContentsMargins(0, 0, 0, 0)
        self.label_trans_opt = QLabel(self.frame_transmission_options)
        self.label_trans_opt.setObjectName(u"label_trans_opt")
        sizePolicy16.setHeightForWidth(self.label_trans_opt.sizePolicy().hasHeightForWidth())
        self.label_trans_opt.setSizePolicy(sizePolicy16)
        self.label_trans_opt.setFont(font2)

        self.vboxLayout108.addWidget(self.label_trans_opt)

        self.frame_trans_opt_white = QFrame(self.frame_transmission_options)
        self.frame_trans_opt_white.setObjectName(u"frame_trans_opt_white")
        sizePolicy16.setHeightForWidth(self.frame_trans_opt_white.sizePolicy().hasHeightForWidth())
        self.frame_trans_opt_white.setSizePolicy(sizePolicy16)
        self.frame_trans_opt_white.setLineWidth(1)
        self.frame_trans_opt_white.setProperty(u"wpBox", False)
        self.boxcarWidget_grid_4 = QGridLayout(self.frame_trans_opt_white)
        self.boxcarWidget_grid_4.setSpacing(0)
        self.boxcarWidget_grid_4.setObjectName(u"boxcarWidget_grid_4")
        self.boxcarWidget_grid_4.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.boxcarWidget_grid_4.setContentsMargins(0, 0, 0, 0)
        self.frame_trans_opt_black = QFrame(self.frame_trans_opt_white)
        self.frame_trans_opt_black.setObjectName(u"frame_trans_opt_black")
        sizePolicy16.setHeightForWidth(self.frame_trans_opt_black.sizePolicy().hasHeightForWidth())
        self.frame_trans_opt_black.setSizePolicy(sizePolicy16)
        self.frame_trans_opt_black.setMinimumSize(QSize(0, 0))
        self.frame_trans_opt_black.setMaximumSize(QSize(16777215, 16777215))
        self.frame_trans_opt_black.setLineWidth(1)
        self.frame_trans_opt_black.setProperty(u"wpGrad", False)
        self.vboxLayout109 = QVBoxLayout(self.frame_trans_opt_black)
        self.vboxLayout109.setSpacing(1)
        self.vboxLayout109.setObjectName(u"vboxLayout109")
        self.vboxLayout109.setContentsMargins(5, 5, 5, 5)
        self.hboxLayout51 = QHBoxLayout()
        self.hboxLayout51.setObjectName(u"hboxLayout51")
        self.hboxLayout51.setContentsMargins(0, -1, 0, -1)
        self.checkBox_enable_max_transmission = QCheckBox(self.frame_trans_opt_black)
        self.checkBox_enable_max_transmission.setObjectName(u"checkBox_enable_max_transmission")
        sizePolicy1.setHeightForWidth(self.checkBox_enable_max_transmission.sizePolicy().hasHeightForWidth())
        self.checkBox_enable_max_transmission.setSizePolicy(sizePolicy1)

        self.hboxLayout51.addWidget(self.checkBox_enable_max_transmission)

        self.spinBox_max_transmission_perc = QSpinBox(self.frame_trans_opt_black)
        self.spinBox_max_transmission_perc.setObjectName(u"spinBox_max_transmission_perc")
        sizePolicy1.setHeightForWidth(self.spinBox_max_transmission_perc.sizePolicy().hasHeightForWidth())
        self.spinBox_max_transmission_perc.setSizePolicy(sizePolicy1)
        self.spinBox_max_transmission_perc.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.spinBox_max_transmission_perc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_max_transmission_perc.setMinimum(1)
        self.spinBox_max_transmission_perc.setMaximum(10000)
        self.spinBox_max_transmission_perc.setValue(120)

        self.hboxLayout51.addWidget(self.spinBox_max_transmission_perc)


        self.vboxLayout109.addLayout(self.hboxLayout51)


        self.boxcarWidget_grid_4.addWidget(self.frame_trans_opt_black, 0, 0, 1, 1)


        self.vboxLayout108.addWidget(self.frame_trans_opt_white)


        self.controlWidget_inner_vbox.addWidget(self.frame_transmission_options)

        self.frame_xs_acc = QFrame(self.controlWidget_inner)
        self.frame_xs_acc.setObjectName(u"frame_xs_acc")
        sizePolicy16.setHeightForWidth(self.frame_xs_acc.sizePolicy().hasHeightForWidth())
        self.frame_xs_acc.setSizePolicy(sizePolicy16)
        self.frame_xs_acc.setLineWidth(1)
        self.vboxLayout110 = QVBoxLayout(self.frame_xs_acc)
        self.vboxLayout110.setObjectName(u"vboxLayout110")
        self.vboxLayout110.setContentsMargins(0, 0, 0, 0)
        self.label214 = QLabel(self.frame_xs_acc)
        self.label214.setObjectName(u"label214")
        sizePolicy16.setHeightForWidth(self.label214.sizePolicy().hasHeightForWidth())
        self.label214.setSizePolicy(sizePolicy16)
        self.label214.setFont(font2)

        self.vboxLayout110.addWidget(self.label214)

        self.frame3 = QFrame(self.frame_xs_acc)
        self.frame3.setObjectName(u"frame3")
        sizePolicy16.setHeightForWidth(self.frame3.sizePolicy().hasHeightForWidth())
        self.frame3.setSizePolicy(sizePolicy16)
        self.frame3.setLineWidth(1)
        self.frame3.setProperty(u"wpBox", False)
        self.vboxLayout111 = QVBoxLayout(self.frame3)
        self.vboxLayout111.setObjectName(u"vboxLayout111")
        self.vboxLayout111.setContentsMargins(0, 0, 0, 0)
        self.frame4 = QFrame(self.frame3)
        self.frame4.setObjectName(u"frame4")
        sizePolicy16.setHeightForWidth(self.frame4.sizePolicy().hasHeightForWidth())
        self.frame4.setSizePolicy(sizePolicy16)
        self.frame4.setMinimumSize(QSize(0, 0))
        self.frame4.setMaximumSize(QSize(16777215, 16777215))
        self.frame4.setLineWidth(1)
        self.frame4.setProperty(u"wpGrad", False)
        self.layout_xs_acc = QVBoxLayout(self.frame4)
        self.layout_xs_acc.setObjectName(u"layout_xs_acc")
        self.checkBox_xs_acc_gpio_enable = QCheckBox(self.frame4)
        self.checkBox_xs_acc_gpio_enable.setObjectName(u"checkBox_xs_acc_gpio_enable")

        self.layout_xs_acc.addWidget(self.checkBox_xs_acc_gpio_enable)

        self.checkBox_xs_acc_5V_enable = QCheckBox(self.frame4)
        self.checkBox_xs_acc_5V_enable.setObjectName(u"checkBox_xs_acc_5V_enable")

        self.layout_xs_acc.addWidget(self.checkBox_xs_acc_5V_enable)

        self.label_xs_acc_gpio1 = QLabel(self.frame4)
        self.label_xs_acc_gpio1.setObjectName(u"label_xs_acc_gpio1")
        sizePolicy16.setHeightForWidth(self.label_xs_acc_gpio1.sizePolicy().hasHeightForWidth())
        self.label_xs_acc_gpio1.setSizePolicy(sizePolicy16)
        self.label_xs_acc_gpio1.setFont(font2)

        self.layout_xs_acc.addWidget(self.label_xs_acc_gpio1)

        self.frame_xs_acc_gpio1 = QFrame(self.frame4)
        self.frame_xs_acc_gpio1.setObjectName(u"frame_xs_acc_gpio1")
        sizePolicy16.setHeightForWidth(self.frame_xs_acc_gpio1.sizePolicy().hasHeightForWidth())
        self.frame_xs_acc_gpio1.setSizePolicy(sizePolicy16)
        self.frame_xs_acc_gpio1.setMinimumSize(QSize(0, 20))
        self.frame_xs_acc_gpio1.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_xs_acc_gpio1.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_xs_acc_gpio1.setProperty(u"wpBox", False)
        self.formLayout11 = QFormLayout(self.frame_xs_acc_gpio1)
        self.formLayout11.setObjectName(u"formLayout11")
        self.label215 = QLabel(self.frame_xs_acc_gpio1)
        self.label215.setObjectName(u"label215")

        self.formLayout11.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label215)

        self.comboBox_xs_acc_gpio1_mode = QComboBox(self.frame_xs_acc_gpio1)
        self.comboBox_xs_acc_gpio1_mode.addItem("")
        self.comboBox_xs_acc_gpio1_mode.addItem("")
        self.comboBox_xs_acc_gpio1_mode.setObjectName(u"comboBox_xs_acc_gpio1_mode")
        sizePolicy16.setHeightForWidth(self.comboBox_xs_acc_gpio1_mode.sizePolicy().hasHeightForWidth())
        self.comboBox_xs_acc_gpio1_mode.setSizePolicy(sizePolicy16)
        self.comboBox_xs_acc_gpio1_mode.setMinimumSize(QSize(80, 22))
        self.comboBox_xs_acc_gpio1_mode.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.formLayout11.setWidget(0, QFormLayout.ItemRole.FieldRole, self.comboBox_xs_acc_gpio1_mode)

        self.label216 = QLabel(self.frame_xs_acc_gpio1)
        self.label216.setObjectName(u"label216")

        self.formLayout11.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label216)

        self.comboBox_xs_acc_gpio1_dir = QComboBox(self.frame_xs_acc_gpio1)
        self.comboBox_xs_acc_gpio1_dir.addItem("")
        self.comboBox_xs_acc_gpio1_dir.addItem("")
        self.comboBox_xs_acc_gpio1_dir.setObjectName(u"comboBox_xs_acc_gpio1_dir")
        sizePolicy16.setHeightForWidth(self.comboBox_xs_acc_gpio1_dir.sizePolicy().hasHeightForWidth())
        self.comboBox_xs_acc_gpio1_dir.setSizePolicy(sizePolicy16)
        self.comboBox_xs_acc_gpio1_dir.setMinimumSize(QSize(80, 22))
        self.comboBox_xs_acc_gpio1_dir.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.formLayout11.setWidget(1, QFormLayout.ItemRole.FieldRole, self.comboBox_xs_acc_gpio1_dir)

        self.label217 = QLabel(self.frame_xs_acc_gpio1)
        self.label217.setObjectName(u"label217")

        self.formLayout11.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label217)

        self.comboBox_xs_acc_gpio1_function = QComboBox(self.frame_xs_acc_gpio1)
        self.comboBox_xs_acc_gpio1_function.addItem("")
        self.comboBox_xs_acc_gpio1_function.addItem("")
        self.comboBox_xs_acc_gpio1_function.addItem("")
        self.comboBox_xs_acc_gpio1_function.setObjectName(u"comboBox_xs_acc_gpio1_function")
        sizePolicy16.setHeightForWidth(self.comboBox_xs_acc_gpio1_function.sizePolicy().hasHeightForWidth())
        self.comboBox_xs_acc_gpio1_function.setSizePolicy(sizePolicy16)
        self.comboBox_xs_acc_gpio1_function.setMinimumSize(QSize(80, 22))
        self.comboBox_xs_acc_gpio1_function.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.formLayout11.setWidget(2, QFormLayout.ItemRole.FieldRole, self.comboBox_xs_acc_gpio1_function)

        self.label218 = QLabel(self.frame_xs_acc_gpio1)
        self.label218.setObjectName(u"label218")

        self.formLayout11.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label218)

        self.comboBox_xs_acc_gpio1_value = QComboBox(self.frame_xs_acc_gpio1)
        self.comboBox_xs_acc_gpio1_value.addItem("")
        self.comboBox_xs_acc_gpio1_value.addItem("")
        self.comboBox_xs_acc_gpio1_value.setObjectName(u"comboBox_xs_acc_gpio1_value")
        sizePolicy16.setHeightForWidth(self.comboBox_xs_acc_gpio1_value.sizePolicy().hasHeightForWidth())
        self.comboBox_xs_acc_gpio1_value.setSizePolicy(sizePolicy16)
        self.comboBox_xs_acc_gpio1_value.setMinimumSize(QSize(80, 22))
        self.comboBox_xs_acc_gpio1_value.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.formLayout11.setWidget(3, QFormLayout.ItemRole.FieldRole, self.comboBox_xs_acc_gpio1_value)


        self.layout_xs_acc.addWidget(self.frame_xs_acc_gpio1)

        self.label_xs_acc_gpio2 = QLabel(self.frame4)
        self.label_xs_acc_gpio2.setObjectName(u"label_xs_acc_gpio2")
        sizePolicy16.setHeightForWidth(self.label_xs_acc_gpio2.sizePolicy().hasHeightForWidth())
        self.label_xs_acc_gpio2.setSizePolicy(sizePolicy16)
        self.label_xs_acc_gpio2.setFont(font2)

        self.layout_xs_acc.addWidget(self.label_xs_acc_gpio2)

        self.frame_xs_acc_gpio2 = QFrame(self.frame4)
        self.frame_xs_acc_gpio2.setObjectName(u"frame_xs_acc_gpio2")
        sizePolicy16.setHeightForWidth(self.frame_xs_acc_gpio2.sizePolicy().hasHeightForWidth())
        self.frame_xs_acc_gpio2.setSizePolicy(sizePolicy16)
        self.frame_xs_acc_gpio2.setMinimumSize(QSize(0, 20))
        self.frame_xs_acc_gpio2.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_xs_acc_gpio2.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_xs_acc_gpio2.setProperty(u"wpBox", False)
        self.formLayout12 = QFormLayout(self.frame_xs_acc_gpio2)
        self.formLayout12.setObjectName(u"formLayout12")
        self.label219 = QLabel(self.frame_xs_acc_gpio2)
        self.label219.setObjectName(u"label219")

        self.formLayout12.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label219)

        self.comboBox_xs_acc_gpio2_mode = QComboBox(self.frame_xs_acc_gpio2)
        self.comboBox_xs_acc_gpio2_mode.addItem("")
        self.comboBox_xs_acc_gpio2_mode.addItem("")
        self.comboBox_xs_acc_gpio2_mode.setObjectName(u"comboBox_xs_acc_gpio2_mode")
        sizePolicy16.setHeightForWidth(self.comboBox_xs_acc_gpio2_mode.sizePolicy().hasHeightForWidth())
        self.comboBox_xs_acc_gpio2_mode.setSizePolicy(sizePolicy16)
        self.comboBox_xs_acc_gpio2_mode.setMinimumSize(QSize(80, 22))
        self.comboBox_xs_acc_gpio2_mode.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.formLayout12.setWidget(0, QFormLayout.ItemRole.FieldRole, self.comboBox_xs_acc_gpio2_mode)

        self.label220 = QLabel(self.frame_xs_acc_gpio2)
        self.label220.setObjectName(u"label220")

        self.formLayout12.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label220)

        self.comboBox_xs_acc_gpio2_dir = QComboBox(self.frame_xs_acc_gpio2)
        self.comboBox_xs_acc_gpio2_dir.addItem("")
        self.comboBox_xs_acc_gpio2_dir.addItem("")
        self.comboBox_xs_acc_gpio2_dir.setObjectName(u"comboBox_xs_acc_gpio2_dir")
        sizePolicy16.setHeightForWidth(self.comboBox_xs_acc_gpio2_dir.sizePolicy().hasHeightForWidth())
        self.comboBox_xs_acc_gpio2_dir.setSizePolicy(sizePolicy16)
        self.comboBox_xs_acc_gpio2_dir.setMinimumSize(QSize(80, 22))
        self.comboBox_xs_acc_gpio2_dir.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.formLayout12.setWidget(1, QFormLayout.ItemRole.FieldRole, self.comboBox_xs_acc_gpio2_dir)

        self.label221 = QLabel(self.frame_xs_acc_gpio2)
        self.label221.setObjectName(u"label221")

        self.formLayout12.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label221)

        self.comboBox_xs_acc_gpio2_function = QComboBox(self.frame_xs_acc_gpio2)
        self.comboBox_xs_acc_gpio2_function.addItem("")
        self.comboBox_xs_acc_gpio2_function.addItem("")
        self.comboBox_xs_acc_gpio2_function.addItem("")
        self.comboBox_xs_acc_gpio2_function.addItem("")
        self.comboBox_xs_acc_gpio2_function.setObjectName(u"comboBox_xs_acc_gpio2_function")
        sizePolicy16.setHeightForWidth(self.comboBox_xs_acc_gpio2_function.sizePolicy().hasHeightForWidth())
        self.comboBox_xs_acc_gpio2_function.setSizePolicy(sizePolicy16)
        self.comboBox_xs_acc_gpio2_function.setMinimumSize(QSize(80, 22))
        self.comboBox_xs_acc_gpio2_function.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.formLayout12.setWidget(2, QFormLayout.ItemRole.FieldRole, self.comboBox_xs_acc_gpio2_function)

        self.label222 = QLabel(self.frame_xs_acc_gpio2)
        self.label222.setObjectName(u"label222")

        self.formLayout12.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label222)

        self.comboBox_xs_acc_gpio2_value = QComboBox(self.frame_xs_acc_gpio2)
        self.comboBox_xs_acc_gpio2_value.addItem("")
        self.comboBox_xs_acc_gpio2_value.addItem("")
        self.comboBox_xs_acc_gpio2_value.setObjectName(u"comboBox_xs_acc_gpio2_value")
        sizePolicy16.setHeightForWidth(self.comboBox_xs_acc_gpio2_value.sizePolicy().hasHeightForWidth())
        self.comboBox_xs_acc_gpio2_value.setSizePolicy(sizePolicy16)
        self.comboBox_xs_acc_gpio2_value.setMinimumSize(QSize(80, 22))
        self.comboBox_xs_acc_gpio2_value.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.formLayout12.setWidget(3, QFormLayout.ItemRole.FieldRole, self.comboBox_xs_acc_gpio2_value)


        self.layout_xs_acc.addWidget(self.frame_xs_acc_gpio2)

        self.label_xs_acc_cont_strobe = QLabel(self.frame4)
        self.label_xs_acc_cont_strobe.setObjectName(u"label_xs_acc_cont_strobe")
        sizePolicy16.setHeightForWidth(self.label_xs_acc_cont_strobe.sizePolicy().hasHeightForWidth())
        self.label_xs_acc_cont_strobe.setSizePolicy(sizePolicy16)
        self.label_xs_acc_cont_strobe.setFont(font2)

        self.layout_xs_acc.addWidget(self.label_xs_acc_cont_strobe)

        self.frame_xs_acc_cont_strobe = QFrame(self.frame4)
        self.frame_xs_acc_cont_strobe.setObjectName(u"frame_xs_acc_cont_strobe")
        sizePolicy16.setHeightForWidth(self.frame_xs_acc_cont_strobe.sizePolicy().hasHeightForWidth())
        self.frame_xs_acc_cont_strobe.setSizePolicy(sizePolicy16)
        self.frame_xs_acc_cont_strobe.setMinimumSize(QSize(0, 20))
        self.frame_xs_acc_cont_strobe.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_xs_acc_cont_strobe.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_xs_acc_cont_strobe.setProperty(u"wpBox", False)
        self.formLayout13 = QFormLayout(self.frame_xs_acc_cont_strobe)
        self.formLayout13.setObjectName(u"formLayout13")
        self.label223 = QLabel(self.frame_xs_acc_cont_strobe)
        self.label223.setObjectName(u"label223")

        self.formLayout13.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label223)

        self.spinBox_xs_acc_cont_strobe_period_us = QSpinBox(self.frame_xs_acc_cont_strobe)
        self.spinBox_xs_acc_cont_strobe_period_us.setObjectName(u"spinBox_xs_acc_cont_strobe_period_us")
        self.spinBox_xs_acc_cont_strobe_period_us.setMinimumSize(QSize(125, 0))
        self.spinBox_xs_acc_cont_strobe_period_us.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_xs_acc_cont_strobe_period_us.setKeyboardTracking(False)
        self.spinBox_xs_acc_cont_strobe_period_us.setMinimum(2)
        self.spinBox_xs_acc_cont_strobe_period_us.setMaximum(999999999)
        self.spinBox_xs_acc_cont_strobe_period_us.setSingleStep(1000)
        self.spinBox_xs_acc_cont_strobe_period_us.setValue(1000000)

        self.formLayout13.setWidget(0, QFormLayout.ItemRole.FieldRole, self.spinBox_xs_acc_cont_strobe_period_us)

        self.label224 = QLabel(self.frame_xs_acc_cont_strobe)
        self.label224.setObjectName(u"label224")

        self.formLayout13.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label224)

        self.spinBox_xs_acc_cont_strobe_width_us = QSpinBox(self.frame_xs_acc_cont_strobe)
        self.spinBox_xs_acc_cont_strobe_width_us.setObjectName(u"spinBox_xs_acc_cont_strobe_width_us")
        self.spinBox_xs_acc_cont_strobe_width_us.setMinimumSize(QSize(125, 0))
        self.spinBox_xs_acc_cont_strobe_width_us.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_xs_acc_cont_strobe_width_us.setKeyboardTracking(False)
        self.spinBox_xs_acc_cont_strobe_width_us.setMinimum(1)
        self.spinBox_xs_acc_cont_strobe_width_us.setMaximum(999999999)
        self.spinBox_xs_acc_cont_strobe_width_us.setSingleStep(1000)
        self.spinBox_xs_acc_cont_strobe_width_us.setValue(100000)

        self.formLayout13.setWidget(1, QFormLayout.ItemRole.FieldRole, self.spinBox_xs_acc_cont_strobe_width_us)

        self.label225 = QLabel(self.frame_xs_acc_cont_strobe)
        self.label225.setObjectName(u"label225")

        self.formLayout13.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label225)

        self.spinBox_xs_acc_cont_strobe_delay_us = QSpinBox(self.frame_xs_acc_cont_strobe)
        self.spinBox_xs_acc_cont_strobe_delay_us.setObjectName(u"spinBox_xs_acc_cont_strobe_delay_us")
        self.spinBox_xs_acc_cont_strobe_delay_us.setMinimumSize(QSize(125, 0))
        self.spinBox_xs_acc_cont_strobe_delay_us.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_xs_acc_cont_strobe_delay_us.setKeyboardTracking(False)
        self.spinBox_xs_acc_cont_strobe_delay_us.setMinimum(0)
        self.spinBox_xs_acc_cont_strobe_delay_us.setMaximum(999999999)
        self.spinBox_xs_acc_cont_strobe_delay_us.setSingleStep(1000)
        self.spinBox_xs_acc_cont_strobe_delay_us.setValue(0)

        self.formLayout13.setWidget(2, QFormLayout.ItemRole.FieldRole, self.spinBox_xs_acc_cont_strobe_delay_us)

        self.label226 = QLabel(self.frame_xs_acc_cont_strobe)
        self.label226.setObjectName(u"label226")

        self.formLayout13.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label226)

        self.spinBox_xs_acc_cont_strobe_count = QSpinBox(self.frame_xs_acc_cont_strobe)
        self.spinBox_xs_acc_cont_strobe_count.setObjectName(u"spinBox_xs_acc_cont_strobe_count")
        self.spinBox_xs_acc_cont_strobe_count.setMinimumSize(QSize(125, 0))
        self.spinBox_xs_acc_cont_strobe_count.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinBox_xs_acc_cont_strobe_count.setKeyboardTracking(False)
        self.spinBox_xs_acc_cont_strobe_count.setMinimum(0)
        self.spinBox_xs_acc_cont_strobe_count.setMaximum(999999999)
        self.spinBox_xs_acc_cont_strobe_count.setSingleStep(10)
        self.spinBox_xs_acc_cont_strobe_count.setValue(0)

        self.formLayout13.setWidget(3, QFormLayout.ItemRole.FieldRole, self.spinBox_xs_acc_cont_strobe_count)


        self.layout_xs_acc.addWidget(self.frame_xs_acc_cont_strobe)


        self.vboxLayout111.addWidget(self.frame4)


        self.vboxLayout110.addWidget(self.frame3)


        self.controlWidget_inner_vbox.addWidget(self.frame_xs_acc)

        self.spacerItem26 = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.controlWidget_inner_vbox.addItem(self.spacerItem26)

        self.controlWidget_scrollArea.setWidget(self.controlWidget_inner)

        self.vboxLayout73.addWidget(self.controlWidget_scrollArea)

        self.systemStatusWidget = QFrame(self.controlWidget_shaded)
        self.systemStatusWidget.setObjectName(u"systemStatusWidget")
        sizePolicy16.setHeightForWidth(self.systemStatusWidget.sizePolicy().hasHeightForWidth())
        self.systemStatusWidget.setSizePolicy(sizePolicy16)
        self.systemStatusWidget.setMinimumSize(QSize(0, 80))
        self.vboxLayout112 = QVBoxLayout(self.systemStatusWidget)
        self.vboxLayout112.setSpacing(0)
        self.vboxLayout112.setObjectName(u"vboxLayout112")
        self.vboxLayout112.setContentsMargins(0, 0, 18, 0)
        self.systemStatusWidget_label = QLabel(self.systemStatusWidget)
        self.systemStatusWidget_label.setObjectName(u"systemStatusWidget_label")
        sizePolicy16.setHeightForWidth(self.systemStatusWidget_label.sizePolicy().hasHeightForWidth())
        self.systemStatusWidget_label.setSizePolicy(sizePolicy16)
        self.systemStatusWidget_label.setFont(font2)

        self.vboxLayout112.addWidget(self.systemStatusWidget_label)

        self.systemStatusWidget_white = QFrame(self.systemStatusWidget)
        self.systemStatusWidget_white.setObjectName(u"systemStatusWidget_white")
        sizePolicy16.setHeightForWidth(self.systemStatusWidget_white.sizePolicy().hasHeightForWidth())
        self.systemStatusWidget_white.setSizePolicy(sizePolicy16)
        self.systemStatusWidget_white.setFrameShape(QFrame.Shape.StyledPanel)
        self.systemStatusWidget_white.setFrameShadow(QFrame.Shadow.Raised)
        self.systemStatusWidget_white.setProperty(u"wpBox", False)
        self.vboxLayout113 = QVBoxLayout(self.systemStatusWidget_white)
        self.vboxLayout113.setSpacing(0)
        self.vboxLayout113.setObjectName(u"vboxLayout113")
        self.vboxLayout113.setContentsMargins(0, 0, 0, 0)
        self.systemStatusWidget_shaded = QFrame(self.systemStatusWidget_white)
        self.systemStatusWidget_shaded.setObjectName(u"systemStatusWidget_shaded")
        sizePolicy16.setHeightForWidth(self.systemStatusWidget_shaded.sizePolicy().hasHeightForWidth())
        self.systemStatusWidget_shaded.setSizePolicy(sizePolicy16)
        self.systemStatusWidget_shaded.setMinimumSize(QSize(100, 0))
        self.systemStatusWidget_shaded.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.systemStatusWidget_shaded.setMidLineWidth(0)
        self.systemStatusWidget_shaded.setProperty(u"wpPanel", False)
        self.hboxLayout52 = QHBoxLayout(self.systemStatusWidget_shaded)
        self.hboxLayout52.setSpacing(0)
        self.hboxLayout52.setObjectName(u"hboxLayout52")
        self.hboxLayout52.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.hboxLayout52.setContentsMargins(9, -1, -1, -1)
        self.systemStatusWidget_pushButton_hardware = QPushButton(self.systemStatusWidget_shaded)
        self.systemStatusWidget_pushButton_hardware.setObjectName(u"systemStatusWidget_pushButton_hardware")
        sizePolicy25 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        sizePolicy25.setHorizontalStretch(7)
        sizePolicy25.setVerticalStretch(0)
        sizePolicy25.setHeightForWidth(self.systemStatusWidget_pushButton_hardware.sizePolicy().hasHeightForWidth())
        self.systemStatusWidget_pushButton_hardware.setSizePolicy(sizePolicy25)
        self.systemStatusWidget_pushButton_hardware.setMinimumSize(QSize(0, 30))
        self.systemStatusWidget_pushButton_hardware.setMaximumSize(QSize(300, 30))
        self.systemStatusWidget_pushButton_hardware.setFont(font)

        self.hboxLayout52.addWidget(self.systemStatusWidget_pushButton_hardware)

        self.systemStatusWidget_pushButton_light = QPushButton(self.systemStatusWidget_shaded)
        self.systemStatusWidget_pushButton_light.setObjectName(u"systemStatusWidget_pushButton_light")
        sizePolicy26 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy26.setHorizontalStretch(7)
        sizePolicy26.setVerticalStretch(0)
        sizePolicy26.setHeightForWidth(self.systemStatusWidget_pushButton_light.sizePolicy().hasHeightForWidth())
        self.systemStatusWidget_pushButton_light.setSizePolicy(sizePolicy26)
        self.systemStatusWidget_pushButton_light.setMaximumSize(QSize(300, 30))
        self.systemStatusWidget_pushButton_light.setFont(font)
        self.systemStatusWidget_pushButton_light.setStyleSheet(u"border: none;")
        self.systemStatusWidget_pushButton_light.setChecked(False)

        self.hboxLayout52.addWidget(self.systemStatusWidget_pushButton_light)

        self.systemStatusWidget_pushButton_temperature = QPushButton(self.systemStatusWidget_shaded)
        self.systemStatusWidget_pushButton_temperature.setObjectName(u"systemStatusWidget_pushButton_temperature")
        sizePolicy26.setHeightForWidth(self.systemStatusWidget_pushButton_temperature.sizePolicy().hasHeightForWidth())
        self.systemStatusWidget_pushButton_temperature.setSizePolicy(sizePolicy26)
        self.systemStatusWidget_pushButton_temperature.setMaximumSize(QSize(300, 30))
        self.systemStatusWidget_pushButton_temperature.setFont(font)

        self.hboxLayout52.addWidget(self.systemStatusWidget_pushButton_temperature)


        self.vboxLayout113.addWidget(self.systemStatusWidget_shaded)


        self.vboxLayout112.addWidget(self.systemStatusWidget_white)


        self.vboxLayout73.addWidget(self.systemStatusWidget)


        self.controlWidget_grid.addWidget(self.controlWidget_shaded, 0, 0, 1, 1)

        self.splitter_left_vs_controls.addWidget(self.controlWidget)

        self.gridLayout.addWidget(self.splitter_left_vs_controls, 2, 0, 1, 1)

        self.frame_drawer_white = QFrame(self.centralwidget)
        self.frame_drawer_white.setObjectName(u"frame_drawer_white")
        sizePolicy27 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        sizePolicy27.setHorizontalStretch(0)
        sizePolicy27.setVerticalStretch(0)
        sizePolicy27.setHeightForWidth(self.frame_drawer_white.sizePolicy().hasHeightForWidth())
        self.frame_drawer_white.setSizePolicy(sizePolicy27)
        self.frame_drawer_white.setMaximumSize(QSize(16777215, 45))
        self.frame_drawer_white.setProperty(u"wpBox", False)
        self.vboxLayout114 = QVBoxLayout(self.frame_drawer_white)
        self.vboxLayout114.setSpacing(0)
        self.vboxLayout114.setObjectName(u"vboxLayout114")
        self.vboxLayout114.setContentsMargins(0, 0, 0, 0)
        self.frame_drawer_black = QFrame(self.frame_drawer_white)
        self.frame_drawer_black.setObjectName(u"frame_drawer_black")
        sizePolicy27.setHeightForWidth(self.frame_drawer_black.sizePolicy().hasHeightForWidth())
        self.frame_drawer_black.setSizePolicy(sizePolicy27)
        self.frame_drawer_black.setProperty(u"wpPanel", False)
        self.hboxLayout53 = QHBoxLayout(self.frame_drawer_black)
        self.hboxLayout53.setObjectName(u"hboxLayout53")
        self.hboxLayout53.setContentsMargins(9, 4, -1, 4)
        self.spacerItem27 = QSpacerItem(20, 20, QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Minimum)

        self.hboxLayout53.addItem(self.spacerItem27)

        self.label_drawer = QLabel(self.frame_drawer_black)
        self.label_drawer.setObjectName(u"label_drawer")
        self.label_drawer.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.label_drawer.setMouseTracking(True)
        self.label_drawer.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.label_drawer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_drawer.setWordWrap(True)
        self.label_drawer.setOpenExternalLinks(True)
        self.label_drawer.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)

        self.hboxLayout53.addWidget(self.label_drawer)

        self.pushButton_marquee_close = QPushButton(self.frame_drawer_black)
        self.pushButton_marquee_close.setObjectName(u"pushButton_marquee_close")
        self.pushButton_marquee_close.setMaximumSize(QSize(20, 16777215))
        icon36 = QIcon()
        icon36.addFile(u":/greys/images/grey_icons/no_xicon.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_marquee_close.setIcon(icon36)

        self.hboxLayout53.addWidget(self.pushButton_marquee_close)


        self.vboxLayout114.addWidget(self.frame_drawer_black)


        self.gridLayout.addWidget(self.frame_drawer_white, 1, 0, 1, 1)

        self.gridLayout.setRowStretch(2, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        QWidget.setTabOrder(self.lineEdit_scope_capture_save_prefix, self.lineEdit_scope_capture_save_suffix)
        QWidget.setTabOrder(self.lineEdit_scope_capture_save_suffix, self.lineEdit_scope_capture_save_note)
        QWidget.setTabOrder(self.lineEdit_scope_capture_save_note, self.lineEdit_ee_wavelength_coeff_0)
        QWidget.setTabOrder(self.lineEdit_ee_wavelength_coeff_0, self.lineEdit_ee_wavelength_coeff_1)
        QWidget.setTabOrder(self.lineEdit_ee_wavelength_coeff_1, self.lineEdit_ee_wavelength_coeff_2)
        QWidget.setTabOrder(self.lineEdit_ee_wavelength_coeff_2, self.lineEdit_ee_wavelength_coeff_3)
        QWidget.setTabOrder(self.lineEdit_ee_wavelength_coeff_3, self.lineEdit_ee_wavelength_coeff_4)

        self.retranslateUi(MainWindow)

        self.stackedWidget_high.setCurrentIndex(0)
        self.stackedWidget_low.setCurrentIndex(3)
        self.tabWidget_advanced_features.setCurrentIndex(1)
        self.stackedWidget_scope_capture_save.setCurrentIndex(0)
        self.stackedWidget_scope_capture_details.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"ENLIGHTEN", None))
#if QT_CONFIG(tooltip)
        MainWindow.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.label_application_logo.setText("")
        self.comboBox_view.setItemText(0, QCoreApplication.translate("MainWindow", u"Scope", None))
        self.comboBox_view.setItemText(1, QCoreApplication.translate("MainWindow", u"Settings", None))
        self.comboBox_view.setItemText(2, QCoreApplication.translate("MainWindow", u"Hardware", None))
        self.comboBox_view.setItemText(3, QCoreApplication.translate("MainWindow", u"Log", None))

        self.comboBox_view.setCurrentText(QCoreApplication.translate("MainWindow", u"Scope", None))
        self.pushButton_raman.setText(QCoreApplication.translate("MainWindow", u"Raman", None))
        self.pushButton_non_raman.setText(QCoreApplication.translate("MainWindow", u"Non-Raman", None))
        self.pushButton_expert.setText(QCoreApplication.translate("MainWindow", u"Expert", None))
        self.pushButton_auto_raman_convenience.setText("")
#if QT_CONFIG(tooltip)
        self.pushButton_auto_raman_convenience.setToolTip(QCoreApplication.translate("MainWindow", u"Automatically take one averaged dark-corrected Raman measurement scaled to fill the detector's dynamic range", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.pushButton_laser_convenience.setToolTip(QCoreApplication.translate("MainWindow", u"Convenience laser toggle", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_laser_convenience.setText("")
#if QT_CONFIG(tooltip)
        self.pushButton_dark_mode.setToolTip(QCoreApplication.translate("MainWindow", u"Seek the light!", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_dark_mode.setText("")
#if QT_CONFIG(tooltip)
        self.pushButton_whats_this.setToolTip(QCoreApplication.translate("MainWindow", u"Enable \"What's This?\" help mode", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_whats_this.setText("")
#if QT_CONFIG(tooltip)
        self.pushButton_help.setToolTip(QCoreApplication.translate("MainWindow", u"Got questions? (F1)", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_help.setText("")
        self.label_serial.setText(QCoreApplication.translate("MainWindow", u"Serial Number", None))
        self.label_product_image.setText("")
        self.searchLabel.setText(QCoreApplication.translate("MainWindow", u"Search", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"EEPROM Contents", None))
#if QT_CONFIG(tooltip)
        self.pushButton_eeprom_clipboard.setToolTip(QCoreApplication.translate("MainWindow", u"Copy EEPROM and key settings to clipboard", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_eeprom_clipboard.setText("")
        self.label1.setText(QCoreApplication.translate("MainWindow", u"EEPROM Page 0", None))
        self.lineEdit_ee_serial_number.setText(QCoreApplication.translate("MainWindow", u"sn", None))
        self.label2.setText(QCoreApplication.translate("MainWindow", u"Serial Number", None))
        self.lineEdit_ee_model.setText(QCoreApplication.translate("MainWindow", u"model", None))
        self.label3.setText(QCoreApplication.translate("MainWindow", u"Model", None))
        self.checkBox_ee_has_cooling.setText("")
        self.label4.setText(QCoreApplication.translate("MainWindow", u"Cooling Available", None))
        self.checkBox_ee_has_battery.setText("")
        self.label5.setText(QCoreApplication.translate("MainWindow", u"Battery Available", None))
        self.checkBox_ee_has_laser.setText("")
        self.label6.setText(QCoreApplication.translate("MainWindow", u"Laser Available", None))
        self.checkBox_ee_invert_x_axis.setText("")
        self.label7.setText(QCoreApplication.translate("MainWindow", u"Invert X-Axis", None))
        self.checkBox_ee_horiz_binning_enabled.setText("")
        self.label8.setText(QCoreApplication.translate("MainWindow", u"Enable Horizontal Binning", None))
        self.checkBox_ee_gen15.setText("")
        self.label9.setText(QCoreApplication.translate("MainWindow", u"Gen 1.5", None))
        self.checkBox_ee_cutoff_filter_installed.setText("")
        self.label10.setText(QCoreApplication.translate("MainWindow", u"Cutoff Filter Installed", None))
        self.checkBox_ee_hardware_even_odd.setText("")
        self.label11.setText(QCoreApplication.translate("MainWindow", u"Hardware Even/Odd Correction", None))
        self.checkBox_ee_sig_laser_tec.setText("")
        self.label12.setText(QCoreApplication.translate("MainWindow", u"SiG Laser TEC", None))
        self.checkBox_ee_has_interlock_feedback.setText("")
        self.label13.setText(QCoreApplication.translate("MainWindow", u"Interlock Feedback", None))
        self.checkBox_ee_has_shutter.setText("")
        self.label14.setText(QCoreApplication.translate("MainWindow", u"Internal Shutter", None))
        self.checkBox_ee_disable_ble_power.setText("")
        self.label15.setText(QCoreApplication.translate("MainWindow", u"Disable Bluetooth\u00ae LE", None))
        self.checkBox_ee_disable_laser_armed_indicator.setText("")
        self.label16.setText(QCoreApplication.translate("MainWindow", u"Disable Laser Armed Indicator", None))
        self.label17.setText(QCoreApplication.translate("MainWindow", u"Excitation (nm)", None))
        self.label18.setText(QCoreApplication.translate("MainWindow", u"Slit Size (\u00b5m)", None))
        self.label19.setText(QCoreApplication.translate("MainWindow", u"Startup Integration Time (ms)", None))
#if QT_CONFIG(tooltip)
        self.label20.setToolTip(QCoreApplication.translate("MainWindow", u"\u00b0C for detectors (X/XM/XL), or raw DAC for lasers (XS)", None))
#endif // QT_CONFIG(tooltip)
        self.label20.setText(QCoreApplication.translate("MainWindow", u"Startup TEC Setpoint", None))
        self.label21.setText(QCoreApplication.translate("MainWindow", u"Startup Triggering Scheme", None))
        self.label22.setText(QCoreApplication.translate("MainWindow", u"Detector Gain (InGaAs even)", None))
        self.label23.setText(QCoreApplication.translate("MainWindow", u"Detector Offset (InGaAs even)", None))
        self.label24.setText(QCoreApplication.translate("MainWindow", u"Detector Gain (InGaAs odd)", None))
        self.label25.setText(QCoreApplication.translate("MainWindow", u"Detector Offset (InGaAs odd)", None))
        self.label26.setText(QCoreApplication.translate("MainWindow", u"Startup Laser TEC Setpoint (raw)", None))
        self.label_ee_format.setText(QCoreApplication.translate("MainWindow", u"fmt", None))
        self.label27.setText(QCoreApplication.translate("MainWindow", u"Format", None))
        self.label28.setText(QCoreApplication.translate("MainWindow", u"EEPROM Page 1", None))
        self.lineEdit_ee_wavelength_coeff_0.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label29.setText(QCoreApplication.translate("MainWindow", u"Wavecal Coeff0", None))
        self.label30.setText(QCoreApplication.translate("MainWindow", u"Wavecal Coeff1", None))
        self.label31.setText(QCoreApplication.translate("MainWindow", u"Wavecal Coeff2", None))
        self.label32.setText(QCoreApplication.translate("MainWindow", u"Wavecal Coeff3", None))
        self.label33.setText(QCoreApplication.translate("MainWindow", u"TEC Coeff0 (\u00b0C \u2192 DAC)", None))
        self.label34.setText(QCoreApplication.translate("MainWindow", u"TEC Coeff1", None))
        self.label35.setText(QCoreApplication.translate("MainWindow", u"TEC Coeff2", None))
        self.label36.setText(QCoreApplication.translate("MainWindow", u"Max Temp (\u00b0C)", None))
        self.label37.setText(QCoreApplication.translate("MainWindow", u"Min Temp (\u00b0C)", None))
        self.label38.setText(QCoreApplication.translate("MainWindow", u"Thermistor Coeff0 (ADC \u2192 \u00b0C)", None))
        self.label39.setText(QCoreApplication.translate("MainWindow", u"Thermistor Coeff1", None))
        self.label40.setText(QCoreApplication.translate("MainWindow", u"Thermistor Coeff2", None))
        self.label41.setText(QCoreApplication.translate("MainWindow", u"Thermistor Resistance at 298K", None))
        self.label42.setText(QCoreApplication.translate("MainWindow", u"Thermistor Beta Value", None))
        self.label43.setText(QCoreApplication.translate("MainWindow", u"Manufacture Date", None))
        self.label44.setText(QCoreApplication.translate("MainWindow", u"Technician", None))
        self.lineEdit_ee_wavelength_coeff_1.setText(QCoreApplication.translate("MainWindow", u"1", None))
        self.lineEdit_ee_wavelength_coeff_2.setText(QCoreApplication.translate("MainWindow", u"2", None))
        self.lineEdit_ee_wavelength_coeff_3.setText(QCoreApplication.translate("MainWindow", u"3", None))
        self.lineEdit_ee_degC_to_dac_coeff_0.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.lineEdit_ee_degC_to_dac_coeff_1.setText(QCoreApplication.translate("MainWindow", u"1", None))
        self.lineEdit_ee_degC_to_dac_coeff_2.setText(QCoreApplication.translate("MainWindow", u"2", None))
        self.lineEdit_ee_adc_to_degC_coeff_0.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.lineEdit_ee_adc_to_degC_coeff_1.setText(QCoreApplication.translate("MainWindow", u"1", None))
        self.lineEdit_ee_adc_to_degC_coeff_2.setText(QCoreApplication.translate("MainWindow", u"2", None))
        self.lineEdit_ee_calibration_date.setText(QCoreApplication.translate("MainWindow", u"today", None))
        self.lineEdit_ee_calibrated_by.setText(QCoreApplication.translate("MainWindow", u"Wilson", None))
        self.lineEdit_ee_wavelength_coeff_4.setText(QCoreApplication.translate("MainWindow", u"4", None))
        self.label45.setText(QCoreApplication.translate("MainWindow", u"Wavecal Coeff4", None))
        self.label46.setText(QCoreApplication.translate("MainWindow", u"EEPROM Page 2", None))
        self.lineEdit_ee_detector.setText(QCoreApplication.translate("MainWindow", u"S16010", None))
        self.label47.setText(QCoreApplication.translate("MainWindow", u"Detector Name", None))
        self.label48.setText(QCoreApplication.translate("MainWindow", u"Active Pixels (Horiz)", None))
        self.label49.setText(QCoreApplication.translate("MainWindow", u"Active Pixels (Vertical)", None))
        self.label50.setText(QCoreApplication.translate("MainWindow", u"Actual Horiz Pixels", None))
        self.label51.setText(QCoreApplication.translate("MainWindow", u"ROI Horiz Start", None))
        self.label52.setText(QCoreApplication.translate("MainWindow", u"ROI Horiz End", None))
        self.label53.setText(QCoreApplication.translate("MainWindow", u"ROI Vertical Region 1 Start", None))
        self.label54.setText(QCoreApplication.translate("MainWindow", u"ROI Vertical Region 1 End", None))
        self.label55.setText(QCoreApplication.translate("MainWindow", u"ROI Vertical Region 2 Start", None))
        self.label56.setText(QCoreApplication.translate("MainWindow", u"ROI Vertical Region 2 End", None))
        self.label57.setText(QCoreApplication.translate("MainWindow", u"ROI Vertical Region 3 Start", None))
        self.label58.setText(QCoreApplication.translate("MainWindow", u"ROI Vertical Region 3 End", None))
        self.label59.setText(QCoreApplication.translate("MainWindow", u"Laser Warmup Time (sec)", None))
        self.label60.setText(QCoreApplication.translate("MainWindow", u"EEPROM Page 3", None))
        self.label61.setText(QCoreApplication.translate("MainWindow", u"Max Laser Temperature (\u00b0C)", None))
        self.lineEdit_ee_laser_power_coeff_0.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label62.setText(QCoreApplication.translate("MainWindow", u"Laser Power Coeff0", None))
        self.lineEdit_ee_laser_power_coeff_1.setText(QCoreApplication.translate("MainWindow", u"1", None))
        self.label63.setText(QCoreApplication.translate("MainWindow", u"Laser Power Coeff1", None))
        self.lineEdit_ee_laser_power_coeff_2.setText(QCoreApplication.translate("MainWindow", u"2", None))
        self.label64.setText(QCoreApplication.translate("MainWindow", u"Laser Power Coeff2", None))
        self.lineEdit_ee_laser_power_coeff_3.setText(QCoreApplication.translate("MainWindow", u"3", None))
        self.label65.setText(QCoreApplication.translate("MainWindow", u"Laser Power Coeff3", None))
        self.label66.setText(QCoreApplication.translate("MainWindow", u"Max Laser Power (mW)", None))
        self.label67.setText(QCoreApplication.translate("MainWindow", u"Min Laser Power (mW)", None))
        self.label68.setText(QCoreApplication.translate("MainWindow", u"Max Integration Time (ms)", None))
        self.label69.setText(QCoreApplication.translate("MainWindow", u"Min Integration Time (ms)", None))
        self.label70.setText(QCoreApplication.translate("MainWindow", u"Average Resolution (FWHM)", None))
        self.label71.setText(QCoreApplication.translate("MainWindow", u"Laser Watchdog (sec)", None))
        self.label72.setText(QCoreApplication.translate("MainWindow", u"Light Source Type", None))
        self.label73.setText(QCoreApplication.translate("MainWindow", u"Power Timeout Sec", None))
        self.label74.setText(QCoreApplication.translate("MainWindow", u"Detector Timeout Sec", None))
        self.label75.setText(QCoreApplication.translate("MainWindow", u"Horizontal Binning Mode", None))
        self.label76.setText(QCoreApplication.translate("MainWindow", u"Startup Scans to Average", None))
        self.label77.setText(QCoreApplication.translate("MainWindow", u"XS Laser Attenuator", None))
        self.label78.setText(QCoreApplication.translate("MainWindow", u"EEPROM Page 4", None))
        self.label79.setText(QCoreApplication.translate("MainWindow", u"User Data", None))
        self.lineEdit_ee_user_text.setText(QCoreApplication.translate("MainWindow", u"foo", None))
        self.label80.setText(QCoreApplication.translate("MainWindow", u"EEPROM Page 5", None))
        self.label81.setText(QCoreApplication.translate("MainWindow", u"Bad Pixel 1", None))
        self.label82.setText(QCoreApplication.translate("MainWindow", u"Bad Pixel 2", None))
        self.label83.setText(QCoreApplication.translate("MainWindow", u"Bad Pixel 3", None))
        self.label84.setText(QCoreApplication.translate("MainWindow", u"Bad Pixel 4", None))
        self.label85.setText(QCoreApplication.translate("MainWindow", u"Bad Pixel 5", None))
        self.label86.setText(QCoreApplication.translate("MainWindow", u"Bad Pixel 6", None))
        self.label87.setText(QCoreApplication.translate("MainWindow", u"Bad Pixel 7", None))
        self.label88.setText(QCoreApplication.translate("MainWindow", u"Bad Pixel 8", None))
        self.label89.setText(QCoreApplication.translate("MainWindow", u"Bad Pixel 9", None))
        self.label90.setText(QCoreApplication.translate("MainWindow", u"Bad Pixel 10", None))
        self.label91.setText(QCoreApplication.translate("MainWindow", u"Bad Pixel 11", None))
        self.label92.setText(QCoreApplication.translate("MainWindow", u"Bad Pixel 12", None))
        self.label93.setText(QCoreApplication.translate("MainWindow", u"Bad Pixel 13", None))
        self.label94.setText(QCoreApplication.translate("MainWindow", u"Bad Pixel 14", None))
        self.label95.setText(QCoreApplication.translate("MainWindow", u"Bad Pixel 15", None))
        self.lineEdit_ee_assembly_revision_packed.setInputMask(QCoreApplication.translate("MainWindow", u"\\0\\xHHHHHH", None))
        self.label96.setText(QCoreApplication.translate("MainWindow", u"Assembly Revision Packed", None))
        self.label97.setText(QCoreApplication.translate("MainWindow", u"Page 6-7 Subformat", None))
        self.label98.setText(QCoreApplication.translate("MainWindow", u"EEPROM Page 6 (SRM Calibration)", None))
        self.lineEdit_ee_raman_intensity_coeff_0.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.lineEdit_ee_raman_intensity_coeff_1.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.lineEdit_ee_raman_intensity_coeff_2.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.lineEdit_ee_raman_intensity_coeff_3.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.lineEdit_ee_raman_intensity_coeff_4.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.lineEdit_ee_raman_intensity_coeff_5.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.lineEdit_ee_raman_intensity_coeff_6.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label99.setText(QCoreApplication.translate("MainWindow", u"Raman Intensity Coeff0", None))
        self.label100.setText(QCoreApplication.translate("MainWindow", u"Raman Intensity Coeff1", None))
        self.label101.setText(QCoreApplication.translate("MainWindow", u"Raman Intensity Coeff2", None))
        self.label102.setText(QCoreApplication.translate("MainWindow", u"Raman Intensity Coeff3", None))
        self.label103.setText(QCoreApplication.translate("MainWindow", u"Raman Intensity Coeff4", None))
        self.label104.setText(QCoreApplication.translate("MainWindow", u"Raman Intensity Coeff5", None))
        self.label105.setText(QCoreApplication.translate("MainWindow", u"Raman Intensity Coeff6", None))
        self.label106.setText(QCoreApplication.translate("MainWindow", u"EEPROM Page 7 (Untethered)", None))
        self.label107.setText(QCoreApplication.translate("MainWindow", u"Library Type", None))
        self.label108.setText(QCoreApplication.translate("MainWindow", u"Library ID", None))
        self.label109.setText(QCoreApplication.translate("MainWindow", u"Scans to Average", None))
        self.label110.setText(QCoreApplication.translate("MainWindow", u"Min Ramp Pixels", None))
        self.label111.setText(QCoreApplication.translate("MainWindow", u"Min Peak Height", None))
        self.label112.setText(QCoreApplication.translate("MainWindow", u"Match Threshold", None))
        self.label113.setText(QCoreApplication.translate("MainWindow", u"Library Count", None))
        self.label114.setText(QCoreApplication.translate("MainWindow", u"EEPROM Pages 4, 6, 7 (Spline)", None))
        self.label115.setText(QCoreApplication.translate("MainWindow", u"Spline Point Count", None))
        self.label116.setText(QCoreApplication.translate("MainWindow", u"Wavelength Min", None))
        self.label117.setText(QCoreApplication.translate("MainWindow", u"Wavelength Max", None))
        self.label118.setText(QCoreApplication.translate("MainWindow", u"Y2", None))
        self.label119.setText(QCoreApplication.translate("MainWindow", u"Wavelength", None))
        self.label120.setText(QCoreApplication.translate("MainWindow", u"Y", None))
        self.label121.setText(QCoreApplication.translate("MainWindow", u"EEPROM Page 7 (Multi-Wavelength Raman)", None))
        self.label122.setText(QCoreApplication.translate("MainWindow", u"2nd Excitation Wavelength (nm)", None))
        self.label123.setText(QCoreApplication.translate("MainWindow", u"2nd Wavelength Coeff 0", None))
        self.lineEdit_ee_sub5_wavelength_coeff_0.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label124.setText(QCoreApplication.translate("MainWindow", u"2nd Wavelength Coeff 1", None))
        self.lineEdit_ee_sub5_wavelength_coeff_1.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label125.setText(QCoreApplication.translate("MainWindow", u"2nd Wavelength Coeff 2", None))
        self.lineEdit_ee_sub5_wavelength_coeff_2.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label126.setText(QCoreApplication.translate("MainWindow", u"2nd Wavelength Coeff 3", None))
        self.lineEdit_ee_sub5_wavelength_coeff_3.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label127.setText(QCoreApplication.translate("MainWindow", u"2nd Wavelength Coeff 4", None))
        self.lineEdit_ee_sub5_wavelength_coeff_4.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label128.setText(QCoreApplication.translate("MainWindow", u"2nd Horizontal ROI Start Pixel", None))
        self.label129.setText(QCoreApplication.translate("MainWindow", u"2nd Horizontal ROI End Pixel", None))
        self.label130.setText(QCoreApplication.translate("MainWindow", u"2nd Average FWHM", None))
        self.label131.setText(QCoreApplication.translate("MainWindow", u"2nd Raman Intensity Coeff0", None))
        self.lineEdit_ee_sub5_raman_intensity_coeff_0.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label132.setText(QCoreApplication.translate("MainWindow", u"2nd Raman Intensity Coeff1", None))
        self.lineEdit_ee_sub5_raman_intensity_coeff_1.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label133.setText(QCoreApplication.translate("MainWindow", u"2nd Raman Intensity Coeff2", None))
        self.lineEdit_ee_sub5_raman_intensity_coeff_2.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label134.setText(QCoreApplication.translate("MainWindow", u"2nd Raman Intensity Coeff3", None))
        self.lineEdit_ee_sub5_raman_intensity_coeff_3.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label135.setText(QCoreApplication.translate("MainWindow", u"2nd Raman Intensity Coeff4", None))
        self.lineEdit_ee_sub5_raman_intensity_coeff_4.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label136.setText(QCoreApplication.translate("MainWindow", u"2nd Raman Intensity Coeff5", None))
        self.lineEdit_ee_sub5_raman_intensity_coeff_5.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label137.setText(QCoreApplication.translate("MainWindow", u"2nd Raman Intensity Coeff6", None))
        self.lineEdit_ee_sub5_raman_intensity_coeff_6.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label138.setText(QCoreApplication.translate("MainWindow", u"2nd Horizontal Binning Mode", None))
        self.label139.setText(QCoreApplication.translate("MainWindow", u"EEPROM Page 8", None))
        self.label140.setText(QCoreApplication.translate("MainWindow", u"XS Laser Password", None))
        self.label141.setText(QCoreApplication.translate("MainWindow", u"BLE Door Sensor", None))
        self.label142.setText(QCoreApplication.translate("MainWindow", u"External Laser Control", None))
        self.label143.setText(QCoreApplication.translate("MainWindow", u"Aux Button can enable laser", None))
        self.label144.setText(QCoreApplication.translate("MainWindow", u"Disable laser sub-system", None))
        self.label145.setText(QCoreApplication.translate("MainWindow", u"Leave ACC_5V_OUT powered on disconnect", None))
        self.label146.setText(QCoreApplication.translate("MainWindow", u"Disable Detector", None))
        self.lineEdit_ee_acc_state.setInputMask(QCoreApplication.translate("MainWindow", u"\\0\\xHHHH", None))
        self.label147.setText(QCoreApplication.translate("MainWindow", u"Accessory State", None))
        self.lineEdit_ee_acc_state_gpio1.setInputMask(QCoreApplication.translate("MainWindow", u"\\0\\xHH", None))
        self.label148.setText(QCoreApplication.translate("MainWindow", u"Acc. GPIO1 State", None))
        self.lineEdit_ee_acc_state_gpio2.setInputMask(QCoreApplication.translate("MainWindow", u"\\0\\xHH", None))
        self.label149.setText(QCoreApplication.translate("MainWindow", u"Acc. GPIO2 State", None))
        self.label150.setText(QCoreApplication.translate("MainWindow", u"Acc. Cont. Strobe Period (\u00b5s)", None))
        self.label151.setText(QCoreApplication.translate("MainWindow", u"Acc. Cont. Strobe Width (\u00b5s)", None))
        self.label152.setText(QCoreApplication.translate("MainWindow", u"Acc. Cont. Strobe Delay (\u00b5s)", None))
        self.label153.setText(QCoreApplication.translate("MainWindow", u"Acc. Cont. Strobe Count", None))
        self.label154.setText(QCoreApplication.translate("MainWindow", u"Max Battery Temp (Celsius)", None))
        self.label155.setText(QCoreApplication.translate("MainWindow", u"Pixel Correction Type", None))
        self.label156.setText(QCoreApplication.translate("MainWindow", u"USB Manufacturer Name", None))
        self.label157.setText(QCoreApplication.translate("MainWindow", u"Aux Button Function", None))
        self.label158.setText(QCoreApplication.translate("MainWindow", u"Aux Button Param", None))
        self.lineEdit_ee_latched_hardware_failures.setInputMask(QCoreApplication.translate("MainWindow", u"\\0\\xHH", None))
        self.label159.setText(QCoreApplication.translate("MainWindow", u"Latched Hardware Failures", None))
        self.label160.setText(QCoreApplication.translate("MainWindow", u"FPGA Compilation Options", None))
        self.label_fpga_integration_time_resolution.setText(QCoreApplication.translate("MainWindow", u"1ms", None))
        self.label161.setText(QCoreApplication.translate("MainWindow", u"Integration Time Resolution", None))
        self.label_fpga_data_header.setText(QCoreApplication.translate("MainWindow", u"None", None))
        self.label162.setText(QCoreApplication.translate("MainWindow", u"Data Header", None))
        self.label_fpga_has_cf_select.setText(QCoreApplication.translate("MainWindow", u"False", None))
        self.label163.setText(QCoreApplication.translate("MainWindow", u"Has CF_SELECT", None))
        self.label_fpga_laser_type.setText(QCoreApplication.translate("MainWindow", u"None", None))
        self.label164.setText(QCoreApplication.translate("MainWindow", u"Laser Type", None))
        self.label_fpga_laser_control.setText(QCoreApplication.translate("MainWindow", u"None", None))
        self.label165.setText(QCoreApplication.translate("MainWindow", u"Laser Control", None))
        self.label_has_area_scan.setText(QCoreApplication.translate("MainWindow", u"False", None))
        self.label166.setText(QCoreApplication.translate("MainWindow", u"Has Area Scan", None))
        self.label_has_actual_integration_time.setText(QCoreApplication.translate("MainWindow", u"False", None))
        self.label167.setText(QCoreApplication.translate("MainWindow", u"Has Actual Integration Time", None))
        self.label_has_horizontal_binning.setText(QCoreApplication.translate("MainWindow", u"False", None))
        self.label168.setText(QCoreApplication.translate("MainWindow", u"Has Horizontal Binning", None))
        self.label169.setText(QCoreApplication.translate("MainWindow", u"Miscellaneous Settings", None))
        self.label_microcontroller_firmware_version.setText(QCoreApplication.translate("MainWindow", u"unknown", None))
        self.label170.setText(QCoreApplication.translate("MainWindow", u"Microcontroller Firmware", None))
        self.label_fpga_firmware_version.setText(QCoreApplication.translate("MainWindow", u"unknown", None))
        self.label171.setText(QCoreApplication.translate("MainWindow", u"FPGA Firmware", None))
        self.label_ble_firmware_version.setText(QCoreApplication.translate("MainWindow", u"unknown", None))
        self.label172.setText(QCoreApplication.translate("MainWindow", u"Bluetooth\u00ae LE Firmware Version", None))
        self.label_microcontroller_serial_number.setText(QCoreApplication.translate("MainWindow", u"none", None))
        self.label173.setText(QCoreApplication.translate("MainWindow", u"Microcontroller Serial Number", None))
        self.label174.setText(QCoreApplication.translate("MainWindow", u"Detector Serial Number", None))
        self.label_battery_static.setText(QCoreApplication.translate("MainWindow", u"Battery", None))
        self.label_hw_view_power_connection_state.setText("")
        self.label175.setText(QCoreApplication.translate("MainWindow", u"Power Connection State", None))
        self.label_assembly_revision.setText("")
        self.label176.setText(QCoreApplication.translate("MainWindow", u"Assembly Revision", None))
        self.label177.setText(QCoreApplication.translate("MainWindow", u"Python Settings", None))
        self.label_python_version.setText(QCoreApplication.translate("MainWindow", u"unknown", None))
        self.label178.setText(QCoreApplication.translate("MainWindow", u"Python Version", None))
        self.label_process_size_mb.setText(QCoreApplication.translate("MainWindow", u"0MB", None))
        self.label179.setText(QCoreApplication.translate("MainWindow", u"Process Size (RSS)", None))
        self.label_process_growth_mb.setText(QCoreApplication.translate("MainWindow", u"0MB", None))
        self.label180.setText(QCoreApplication.translate("MainWindow", u"Process Growth", None))
#if QT_CONFIG(tooltip)
        self.pushButton_save_ini.setToolTip(QCoreApplication.translate("MainWindow", u"Stores your edits locally in enlighten.ini (per-computer settings which override EEPROM values)", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_save_ini.setText(QCoreApplication.translate("MainWindow", u"Save .ini File", None))
        self.label_save_ini_result.setText(QCoreApplication.translate("MainWindow", u"/path/to/enlighten.ini", None))
#if QT_CONFIG(tooltip)
        self.pushButton_admin_login.setToolTip(QCoreApplication.translate("MainWindow", u"Login to access administrative features (ctrl-A)", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_admin_login.setText(QCoreApplication.translate("MainWindow", u"&Advanced Users", None))
#if QT_CONFIG(tooltip)
        self.pushButton_write_eeprom.setToolTip(QCoreApplication.translate("MainWindow", u"MAY VOID WARRANTY: Store any manual edits to the spectrometer\u2019s internal EEPROM", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_write_eeprom.setText(QCoreApplication.translate("MainWindow", u"Write EEPROM", None))
#if QT_CONFIG(tooltip)
        self.pushButton_importEEPROM.setToolTip(QCoreApplication.translate("MainWindow", u"Load a previously-exported EEPROM file (does not automatically \u2018write')", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_importEEPROM.setText(QCoreApplication.translate("MainWindow", u"Import EEPROM", None))
#if QT_CONFIG(tooltip)
        self.pushButton_exportEEPROM.setToolTip(QCoreApplication.translate("MainWindow", u"Export EEPROM values to a file for later importing to the same or different unit", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_exportEEPROM.setText(QCoreApplication.translate("MainWindow", u"Export EEPROM", None))
#if QT_CONFIG(tooltip)
        self.pushButton_restore_eeprom.setToolTip(QCoreApplication.translate("MainWindow", u"Reset EEPROM to factory settings by loading from cloud", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_restore_eeprom.setText(QCoreApplication.translate("MainWindow", u"Restore EEPROM", None))
#if QT_CONFIG(tooltip)
        self.pushButton_reset_fpga.setToolTip(QCoreApplication.translate("MainWindow", u"Attempt to \"reboot\" the spectrometer's FPGA if spectra are frozen", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_reset_fpga.setText(QCoreApplication.translate("MainWindow", u"Reset FPGA", None))
        self.label181.setText(QCoreApplication.translate("MainWindow", u"Firmware Updates", None))
        self.pushButton_mfg_dfu.setText(QCoreApplication.translate("MainWindow", u"Enable DFU", None))
        self.checkBox_diagnostic_mode.setText(QCoreApplication.translate("MainWindow", u"Developer diagnostic mode", None))
        self.tabWidget_advanced_features.setTabText(self.tabWidget_advanced_features.indexOf(self.tab_manufacturing), QCoreApplication.translate("MainWindow", u"Manufacturing", None))
        self.label182.setText(QCoreApplication.translate("MainWindow", u"Graph Control", None))
        self.checkBox_graph_alternating_pixels.setText(QCoreApplication.translate("MainWindow", u"Graph Alternating Pixels", None))
        self.checkBox_swap_alternating_pixels.setText(QCoreApplication.translate("MainWindow", u"Swap Alternating Pixels", None))
        self.tabWidget_advanced_features.setTabText(self.tabWidget_advanced_features.indexOf(self.tab_oem), QCoreApplication.translate("MainWindow", u"OEM", None))
        self.progressBar_area_scan.setFormat(QCoreApplication.translate("MainWindow", u"%v of %m ms", None))
        self.label_rssd_timestamp_69.setText(QCoreApplication.translate("MainWindow", u"Measurement Naming", None))
        self.label183.setText(QCoreApplication.translate("MainWindow", u"Save Directory", None))
#if QT_CONFIG(tooltip)
        self.label_scope_setup_save_location.setToolTip(QCoreApplication.translate("MainWindow", u"Where new measurements will be saved", None))
#endif // QT_CONFIG(tooltip)
        self.label_scope_setup_save_location.setText(QCoreApplication.translate("MainWindow", u"C:\\path\\to\\EnlightenSpectra", None))
#if QT_CONFIG(tooltip)
        self.pushButton_scope_setup_change_save_location.setToolTip(QCoreApplication.translate("MainWindow", u"Where to save spectra (settings, plugins, log etc remain in EnlightenSpectra)", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_scope_setup_change_save_location.setText(QCoreApplication.translate("MainWindow", u"Change", None))
#if QT_CONFIG(tooltip)
        self.lineEdit_save_filename_template.setToolTip(QCoreApplication.translate("MainWindow", u"Template for the filename of newly saved measurements", None))
#endif // QT_CONFIG(tooltip)
        self.lineEdit_save_filename_template.setText(QCoreApplication.translate("MainWindow", u"{measurement_id}", None))
#if QT_CONFIG(tooltip)
        self.lineEdit_save_label_template.setToolTip(QCoreApplication.translate("MainWindow", u"Template for the \"label\" of newly saved measurements", None))
#endif // QT_CONFIG(tooltip)
        self.lineEdit_save_label_template.setText(QCoreApplication.translate("MainWindow", u"{time} {serial_number}", None))
        self.label_foo_baz.setText(QCoreApplication.translate("MainWindow", u"New Filename Template", None))
        self.label_foo_baz2.setText(QCoreApplication.translate("MainWindow", u"New Label Template", None))
#if QT_CONFIG(tooltip)
        self.checkBox_save_filename_as_label.setToolTip(QCoreApplication.translate("MainWindow", u"If checked, the measurement filename will be used for on-screen label", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_save_filename_as_label.setText(QCoreApplication.translate("MainWindow", u"Use filename as label", None))
#if QT_CONFIG(tooltip)
        self.checkBox_load_raw.setToolTip(QCoreApplication.translate("MainWindow", u"Load \"raw\" rather than \"processed\" and apply current settings", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_load_raw.setText(QCoreApplication.translate("MainWindow", u"Load raw spectra and re-process", None))
        self.label_Saved_Data_Options.setText(QCoreApplication.translate("MainWindow", u"Saved Data Options", None))
        self.label184.setText(QCoreApplication.translate("MainWindow", u"File Formats", None))
        self.label185.setText(QCoreApplication.translate("MainWindow", u"Optional Fields", None))
        self.checkBox_save_csv.setText(QCoreApplication.translate("MainWindow", u"Save CSV", None))
        self.groupBox_csv_direction.setTitle("")
        self.radioButton_save_by_row.setText(QCoreApplication.translate("MainWindow", u"by row", None))
        self.radioButton_save_by_column.setText(QCoreApplication.translate("MainWindow", u"by column", None))
        self.checkBox_save_pixel.setText(QCoreApplication.translate("MainWindow", u"pixel index", None))
        self.checkBox_save_raw.setText(QCoreApplication.translate("MainWindow", u"raw", None))
        self.checkBox_save_excel.setText(QCoreApplication.translate("MainWindow", u"Save XLS", None))
        self.checkBox_save_data_append.setText(QCoreApplication.translate("MainWindow", u"append", None))
        self.checkBox_save_wavelength.setText(QCoreApplication.translate("MainWindow", u"wavelength", None))
        self.checkBox_save_dark.setText(QCoreApplication.translate("MainWindow", u"dark", None))
        self.checkBox_save_text.setText(QCoreApplication.translate("MainWindow", u"Save TXT", None))
        self.checkBox_save_wavenumber.setText(QCoreApplication.translate("MainWindow", u"wavenumber", None))
        self.checkBox_save_reference.setText(QCoreApplication.translate("MainWindow", u"reference", None))
        self.checkBox_save_spc.setText(QCoreApplication.translate("MainWindow", u"Save SPC", None))
        self.checkBox_save_json.setText(QCoreApplication.translate("MainWindow", u"Save JSON", None))
        self.checkBox_save_cloud.setText(QCoreApplication.translate("MainWindow", u"cloud upload", None))
        self.checkBox_save_dx.setText(QCoreApplication.translate("MainWindow", u"Save JCAMP-DX", None))
#if QT_CONFIG(tooltip)
        self.checkBox_save_all.setToolTip(QCoreApplication.translate("MainWindow", u"When saving spectra, include all connected spectrometers rather than just \"selected\"", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_save_all.setText(QCoreApplication.translate("MainWindow", u"All spectrometers", None))
#if QT_CONFIG(tooltip)
        self.checkBox_allow_rename_files.setToolTip(QCoreApplication.translate("MainWindow", u"When checked, editing a spectrum's label will rename the file", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_allow_rename_files.setText(QCoreApplication.translate("MainWindow", u"Rename files", None))
#if QT_CONFIG(tooltip)
        self.checkBox_save_collated.setToolTip(QCoreApplication.translate("MainWindow", u"If checked, exported CSVs will be grouped by MEASUREMENT, with processed, raw, dark, reference together in consecutive columns. If unchecked, exported CSVs will be grouped by COMPONENT, with all exported processed columns together, then all raw, all darks, all references etc. Consider how a copy machine \"collates\" documents by printing pages 1-4 together, then another copy of pages 1-4, etc, versus the \"un-collated\" behavior of printing N copies of page 1, followed by N copies of page 2 and so forth.", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_save_collated.setText(QCoreApplication.translate("MainWindow", u"Collated Export", None))
        self.label_interpolation_title.setText(QCoreApplication.translate("MainWindow", u"Interpolation", None))
        self.checkBox_save_interpolation_enabled.setText(QCoreApplication.translate("MainWindow", u"Enabled", None))
        self.label186.setText(QCoreApplication.translate("MainWindow", u"Start X", None))
        self.radioButton_save_interpolation_wavelength.setText(QCoreApplication.translate("MainWindow", u"wavelength", None))
        self.label187.setText(QCoreApplication.translate("MainWindow", u"End X", None))
        self.radioButton_save_interpolation_wavenumber.setText(QCoreApplication.translate("MainWindow", u"wavenumber", None))
        self.label188.setText(QCoreApplication.translate("MainWindow", u"X Increment", None))
        self.label189.setText(QCoreApplication.translate("MainWindow", u"Wavenumber Correction", None))
        self.label190.setText(QCoreApplication.translate("MainWindow", u"ASTM Standard", None))
        self.checkBox_ramanCorrection_visible.setText(QCoreApplication.translate("MainWindow", u"Visible", None))
        self.label_BatchCollection_title.setText(QCoreApplication.translate("MainWindow", u"Batch Data Collection", None))
#if QT_CONFIG(tooltip)
        self.checkBox_BatchCollection_enabled.setToolTip(QCoreApplication.translate("MainWindow", u"Enable \"start batch collection\" button on the Scope VCR-style buttons", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_BatchCollection_enabled.setText(QCoreApplication.translate("MainWindow", u"Batch Mode Enabled", None))
        self.label_BatchCollection_explain.setText(QCoreApplication.translate("MainWindow", u"Explain this", None))
        self.label191.setText(QCoreApplication.translate("MainWindow", u"Measurement Count", None))
#if QT_CONFIG(tooltip)
        self.spinBox_BatchCollection_measurement_count.setToolTip(QCoreApplication.translate("MainWindow", u"Number of measurements in a batch", None))
#endif // QT_CONFIG(tooltip)
        self.spinBox_BatchCollection_measurement_count.setSuffix("")
        self.label192.setText(QCoreApplication.translate("MainWindow", u"Measurement Period", None))
#if QT_CONFIG(tooltip)
        self.spinBox_BatchCollection_measurement_period_ms.setToolTip(QCoreApplication.translate("MainWindow", u"How often to take acquisitions, start-to-start (zero to acquire all in rapid succession)", None))
#endif // QT_CONFIG(tooltip)
        self.spinBox_BatchCollection_measurement_period_ms.setSuffix(QCoreApplication.translate("MainWindow", u" ms", None))
        self.label193.setText(QCoreApplication.translate("MainWindow", u"Batch Count", None))
#if QT_CONFIG(tooltip)
        self.spinBox_BatchCollection_batch_count.setToolTip(QCoreApplication.translate("MainWindow", u"How many batches to take before stopping (zero to loop indefinitely)", None))
#endif // QT_CONFIG(tooltip)
        self.label194.setText(QCoreApplication.translate("MainWindow", u"Batch Period", None))
#if QT_CONFIG(tooltip)
        self.spinBox_BatchCollection_batch_period_sec.setToolTip(QCoreApplication.translate("MainWindow", u"How long between batches, start to start (zero to loop with no delay)", None))
#endif // QT_CONFIG(tooltip)
        self.spinBox_BatchCollection_batch_period_sec.setSuffix(QCoreApplication.translate("MainWindow", u" sec", None))
        self.spinBox_BatchCollection_batch_period_sec.setPrefix("")
        self.label195.setText(QCoreApplication.translate("MainWindow", u"Collection Timeout", None))
#if QT_CONFIG(tooltip)
        self.spinBox_BatchCollection_collection_timeout.setToolTip(QCoreApplication.translate("MainWindow", u"How long a collection will perform. After this period it will stop even if measurements in a batch, or batches are remaining.", None))
#endif // QT_CONFIG(tooltip)
        self.spinBox_BatchCollection_collection_timeout.setSuffix(QCoreApplication.translate("MainWindow", u" sec", None))
        self.spinBox_BatchCollection_collection_timeout.setPrefix("")
        self.checkBox_BatchCollection_clear_before_batch.setText(QCoreApplication.translate("MainWindow", u"Clear thumbnails before batch", None))
        self.checkBox_BatchCollection_export_after_batch.setText(QCoreApplication.translate("MainWindow", u"Export thumbnails after batch", None))
#if QT_CONFIG(tooltip)
        self.checkBox_BatchCollection_dark_before_batch.setToolTip(QCoreApplication.translate("MainWindow", u"Take a fresh dark at the start of each batch (before turning on laser)", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_BatchCollection_dark_before_batch.setText(QCoreApplication.translate("MainWindow", u"Take dark before enabling laser", None))
#if QT_CONFIG(tooltip)
        self.checkBox_BatchCollection_save_area_scan.setToolTip(QCoreApplication.translate("MainWindow", u"Save an Area Scan of each measurement (Area Scan must be enabled before starting batch)", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_BatchCollection_save_area_scan.setText(QCoreApplication.translate("MainWindow", u"Save Area Scan with each measurement", None))
        self.groupBox_BatchCollection_laser_mode.setTitle(QCoreApplication.translate("MainWindow", u"Laser Mode", None))
#if QT_CONFIG(tooltip)
        self.radioButton_BatchCollection_laser_manual.setToolTip(QCoreApplication.translate("MainWindow", u"No automated laser control", None))
#endif // QT_CONFIG(tooltip)
        self.radioButton_BatchCollection_laser_manual.setText(QCoreApplication.translate("MainWindow", u"Manual", None))
#if QT_CONFIG(tooltip)
        self.radioButton_BatchCollection_laser_spectrum.setToolTip(QCoreApplication.translate("MainWindow", u"Turn laser on before each acquisition, then off after measurement", None))
#endif // QT_CONFIG(tooltip)
        self.radioButton_BatchCollection_laser_spectrum.setText(QCoreApplication.translate("MainWindow", u"Spectrum", None))
#if QT_CONFIG(tooltip)
        self.radioButton_BatchCollection_laser_batch.setToolTip(QCoreApplication.translate("MainWindow", u"Turn laser on at start of each batch, then off when batch completes", None))
#endif // QT_CONFIG(tooltip)
        self.radioButton_BatchCollection_laser_batch.setText(QCoreApplication.translate("MainWindow", u"Batch", None))
#if QT_CONFIG(tooltip)
        self.radioButton_BatchCollection_laser_auto_raman.setToolTip(QCoreApplication.translate("MainWindow", u"Use Auto-Raman for every measurement", None))
#endif // QT_CONFIG(tooltip)
        self.radioButton_BatchCollection_laser_auto_raman.setText(QCoreApplication.translate("MainWindow", u"Auto-Raman", None))
        self.label196.setText(QCoreApplication.translate("MainWindow", u"Warm-up", None))
#if QT_CONFIG(tooltip)
        self.spinBox_BatchCollection_laser_warmup_ms.setToolTip(QCoreApplication.translate("MainWindow", u"After turning on laser, wait this long for stabilization before acquiring", None))
#endif // QT_CONFIG(tooltip)
        self.spinBox_BatchCollection_laser_warmup_ms.setSuffix(QCoreApplication.translate("MainWindow", u" ms", None))
        self.label_BatchCollection_title_2.setText(QCoreApplication.translate("MainWindow", u"Cloud Connectivity", None))
        self.checkBox_cloud_config_download_enabled.setText(QCoreApplication.translate("MainWindow", u"Configuration Download Enabled", None))
        self.label_Theme.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Theme</p></body></html>", None))
        self.label197.setText(QCoreApplication.translate("MainWindow", u"Additional themes beyond light and dark", None))
        self.checkBox_sound_enable.setText(QCoreApplication.translate("MainWindow", u"Enable audible feedback", None))
        self.label_Live_Preview_Unprocessed.setText(QCoreApplication.translate("MainWindow", u"Live Spectrum (uncorrected)", None))
#if QT_CONFIG(tooltip)
        self.stackedWidget_scope_setup_live_spectrum.setToolTip(QCoreApplication.translate("MainWindow", u"Live spectra has no scan averaging, boxcar or post-processing applied", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.pushButton_dark_store.setToolTip(QCoreApplication.translate("MainWindow", u"ctrl-D to toggle", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_dark_store.setText(QCoreApplication.translate("MainWindow", u"Take Dark", None))
#if QT_CONFIG(tooltip)
        self.pushButton_reference_store.setToolTip(QCoreApplication.translate("MainWindow", u"ctrl-R to toggle", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_reference_store.setText(QCoreApplication.translate("MainWindow", u"Take Reference", None))
        self.label_rsrd_label_header_3.setText(QCoreApplication.translate("MainWindow", u"Dark Spectrum", None))
#if QT_CONFIG(tooltip)
        self.pushButton_dark_clear.setToolTip(QCoreApplication.translate("MainWindow", u"ctrl-D to toggle", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_dark_clear.setText(QCoreApplication.translate("MainWindow", u"Clear", None))
        self.pushButton_dark_load.setText(QCoreApplication.translate("MainWindow", u"Load", None))
        self.label_dark_timestamp.setText(QCoreApplication.translate("MainWindow", u"2016-11-28 16:01:30", None))
        self.label_tsrl_label_header_3.setText(QCoreApplication.translate("MainWindow", u"Reference Spectrum", None))
#if QT_CONFIG(tooltip)
        self.pushButton_reference_clear.setToolTip(QCoreApplication.translate("MainWindow", u"ctrl-R to toggle", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_reference_clear.setText(QCoreApplication.translate("MainWindow", u"Clear", None))
        self.pushButton_reference_load.setText(QCoreApplication.translate("MainWindow", u"Load", None))
        self.label_reference_timestamp.setText(QCoreApplication.translate("MainWindow", u"2016-11-28 16:01:30", None))
        self.label_scope_capture_save_title.setText(QCoreApplication.translate("MainWindow", u"Clipboard", None))
#if QT_CONFIG(tooltip)
        self.pushButton_erase_captures.setToolTip(QCoreApplication.translate("MainWindow", u"Clear list (does not permanently delete from hard drive)", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_erase_captures.setText("")
#if QT_CONFIG(tooltip)
        self.pushButton_resize_captures.setToolTip(QCoreApplication.translate("MainWindow", u"Expand/collapse thumbnails", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_resize_captures.setText("")
#if QT_CONFIG(tooltip)
        self.pushButton_resort_captures.setToolTip(QCoreApplication.translate("MainWindow", u"Reverse sort order", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_resort_captures.setText("")
        self.label_rcsd_timestamp_9.setText(QCoreApplication.translate("MainWindow", u"2016-11-28 13:28:35", None))
        self.label_session_count.setText(QCoreApplication.translate("MainWindow", u"0 Session Spectra", None))
        self.pushButton_scope_capture_load.setText(QCoreApplication.translate("MainWindow", u"Load", None))
        self.pushButton_export_session.setText(QCoreApplication.translate("MainWindow", u"Export", None))
        self.label_correction_status_title.setText(QCoreApplication.translate("MainWindow", u"Correction Status", None))
#if QT_CONFIG(tooltip)
        self.pushButton_correction_status_minimize.setToolTip(QCoreApplication.translate("MainWindow", u"Show/hide correction status", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_correction_status_minimize.setText("")
        self.label_correction_status_raman_shift_label.setText(QCoreApplication.translate("MainWindow", u"Raman Shift Correction", None))
        self.label_correction_status_raman_shift.setText(QCoreApplication.translate("MainWindow", u"OFF", None))
        self.label_correction_status_edc_label.setText(QCoreApplication.translate("MainWindow", u"Electrical Dark Correction", None))
        self.label_correction_status_edc.setText(QCoreApplication.translate("MainWindow", u"OFF", None))
        self.label_correction_status_ingaas_label.setText(QCoreApplication.translate("MainWindow", u"InGaAs Pixel Correction", None))
        self.label_correction_status_ingaas.setText(QCoreApplication.translate("MainWindow", u"OFF", None))
        self.label_correction_status_etalon_label.setText(QCoreApplication.translate("MainWindow", u"Etalon Correction", None))
        self.label_correction_status_etalon.setText(QCoreApplication.translate("MainWindow", u"OFF", None))
        self.label_correction_status_srm_label.setText(QCoreApplication.translate("MainWindow", u"Raman Intensity Correction", None))
        self.label_correction_status_srm.setText(QCoreApplication.translate("MainWindow", u"OFF", None))
        self.label_correction_status_XD_label.setText(QCoreApplication.translate("MainWindow", u"XD", None))
        self.label_correction_status_XD.setText(QCoreApplication.translate("MainWindow", u"OFF", None))
        self.label_correction_status_baseline_label.setText(QCoreApplication.translate("MainWindow", u"Baseline Correction", None))
        self.label_correction_status_baseline.setText(QCoreApplication.translate("MainWindow", u"OFF", None))
        self.label198.setText(QCoreApplication.translate("MainWindow", u"Prefix", None))
        self.lineEdit_scope_capture_save_prefix.setText(QCoreApplication.translate("MainWindow", u"enlighten", None))
        self.label199.setText(QCoreApplication.translate("MainWindow", u"Note", None))
#if QT_CONFIG(tooltip)
        self.lineEdit_scope_capture_save_note.setToolTip(QCoreApplication.translate("MainWindow", u"added to saved metadata (ctrl-N)", None))
#endif // QT_CONFIG(tooltip)
        self.lineEdit_scope_capture_save_note.setText(QCoreApplication.translate("MainWindow", u"processed", None))
        self.label200.setText(QCoreApplication.translate("MainWindow", u"Suffix", None))
#if QT_CONFIG(tooltip)
        self.pushButton_lock_axes.setToolTip(QCoreApplication.translate("MainWindow", u"Freeze Axes", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_lock_axes.setText("")
#if QT_CONFIG(tooltip)
        self.pushButton_zoom_graph.setToolTip(QCoreApplication.translate("MainWindow", u"Zoom graph", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_zoom_graph.setText("")
#if QT_CONFIG(tooltip)
        self.pushButton_graphGrid.setToolTip(QCoreApplication.translate("MainWindow", u"Toggle grid display", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_graphGrid.setText("")
#if QT_CONFIG(tooltip)
        self.pushButton_invert_x_axis.setToolTip(QCoreApplication.translate("MainWindow", u"Invert x-axis", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_invert_x_axis.setText("")
#if QT_CONFIG(tooltip)
        self.pushButton_roi_toggle.setToolTip(QCoreApplication.translate("MainWindow", u"toggle horizontal Region of Interest", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_roi_toggle.setText(QCoreApplication.translate("MainWindow", u"ROI", None))
#if QT_CONFIG(tooltip)
        self.pushButton_interp_toggle.setToolTip(QCoreApplication.translate("MainWindow", u"Toggle interpolation of x-axis", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_interp_toggle.setText("")
#if QT_CONFIG(tooltip)
        self.pushButton_scope_toggle_dark.setToolTip(QCoreApplication.translate("MainWindow", u"Take Dark (ctrl-D)", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.pushButton_scope_toggle_reference.setToolTip(QCoreApplication.translate("MainWindow", u"Take Reference", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.pushButton_ramanCorrection.setToolTip(QCoreApplication.translate("MainWindow", u"X-Axis Calibration", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.pushButton_ingaas_correction.setToolTip(QCoreApplication.translate("MainWindow", u"toggle InGaAs linear correction", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_ingaas_correction.setText("")
#if QT_CONFIG(tooltip)
        self.pushButton_etalon_correction.setToolTip(QCoreApplication.translate("MainWindow", u"toggle etalon correction", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_etalon_correction.setText("")
#if QT_CONFIG(tooltip)
        self.pushButton_raman_intensity_correction_tristate.setToolTip(QCoreApplication.translate("MainWindow", u"toggle Raman Intensity Correction", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.pushButton_XD_toggle.setToolTip(QCoreApplication.translate("MainWindow", u"toggle XD processing", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.pushButton_library_matching_toggle.setToolTip(QCoreApplication.translate("MainWindow", u"toggle library matching", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.pushButton_show_ble_selector.setToolTip(QCoreApplication.translate("MainWindow", u"Scan for Bluetooth\u00ae LE spectrometers", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_show_ble_selector.setText("")
#if QT_CONFIG(tooltip)
        self.pushButton_guide.setToolTip(QCoreApplication.translate("MainWindow", u"Provide spectroscopy usage tips", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_guide.setText("")
#if QT_CONFIG(tooltip)
        self.pushButton_copy_to_clipboard.setToolTip(QCoreApplication.translate("MainWindow", u"copy to clipboard (ctrl-C)", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_copy_to_clipboard.setText("")
        self.scrollArea_scope_capture_details.setProperty(u"comment", QCoreApplication.translate("MainWindow", u"MZ: why is there a scrollArea here?", None))
        self.stackedWidget_scope_capture_details_spectrum.setProperty(u"Comment", QCoreApplication.translate("MainWindow", u"MZ: pyqtgraph widgets are inserted here", None))
        self.label_StatusBar_min_name.setText(QCoreApplication.translate("MainWindow", u"Min:", None))
        self.label_StatusBar_min_value.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_StatusBar_max_name.setText(QCoreApplication.translate("MainWindow", u"Max:", None))
        self.label_StatusBar_max_value.setText(QCoreApplication.translate("MainWindow", u"65535", None))
        self.label_StatusBar_mean_name.setText(QCoreApplication.translate("MainWindow", u"Mean:", None))
        self.label_StatusBar_mean_value.setText(QCoreApplication.translate("MainWindow", u"100.3", None))
        self.label_StatusBar_area_name.setText(QCoreApplication.translate("MainWindow", u"Area:", None))
        self.label_StatusBar_area_value.setText(QCoreApplication.translate("MainWindow", u"100.3", None))
        self.label_StatusBar_detector_temp_name.setText(QCoreApplication.translate("MainWindow", u"Det. Temp:", None))
        self.label_StatusBar_detector_temp_value.setText(QCoreApplication.translate("MainWindow", u"0.0", None))
        self.label_StatusBar_laser_temp_name.setText(QCoreApplication.translate("MainWindow", u"Laser Temp:", None))
        self.label_StatusBar_laser_temp_value.setText(QCoreApplication.translate("MainWindow", u"0.0", None))
        self.label_StatusBar_cursor_name.setText(QCoreApplication.translate("MainWindow", u"Cursor Y:", None))
        self.label_StatusBar_cursor_value.setText(QCoreApplication.translate("MainWindow", u"0.0", None))
        self.label_StatusBar_count_name.setText(QCoreApplication.translate("MainWindow", u"Frame:", None))
        self.label_StatusBar_count_value.setText(QCoreApplication.translate("MainWindow", u"0.0", None))
        self.label_StatusBar_battery_name.setText(QCoreApplication.translate("MainWindow", u"Battery:", None))
        self.label_StatusBar_battery_value.setText(QCoreApplication.translate("MainWindow", u"none", None))
#if QT_CONFIG(tooltip)
        self.status_bar_toolButton.setToolTip(QCoreApplication.translate("MainWindow", u"Pick which fields should appear on the Status Bar", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.status_bar_toolButton.setStatusTip("")
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(whatsthis)
        self.status_bar_toolButton.setWhatsThis(QCoreApplication.translate("MainWindow", u"Allows you to enable or disable different fields for the Status Bar, as reflect your needs and screen size. Selections are persisted across sessions in enlighten.ini.", None))
#endif // QT_CONFIG(whatsthis)
        self.status_bar_toolButton.setText(QCoreApplication.translate("MainWindow", u". . .", None))
        self.checkBox_logging_verbose.setText(QCoreApplication.translate("MainWindow", u"verbose logging", None))
        self.checkBox_logging_pause.setText(QCoreApplication.translate("MainWindow", u"pause logging", None))
        self.checkBox_logging_firmware.setText(QCoreApplication.translate("MainWindow", u"firmware", None))
#if QT_CONFIG(tooltip)
        self.pushButton_copy_log_to_clipboard.setToolTip(QCoreApplication.translate("MainWindow", u"copy to clipboard (ctrl-C)", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_copy_log_to_clipboard.setText("")
#if QT_CONFIG(tooltip)
        self.pushButton_scope_capture_play.setToolTip(QCoreApplication.translate("MainWindow", u"Start continuous acquisition", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_scope_capture_play.setText("")
#if QT_CONFIG(tooltip)
        self.pushButton_scope_capture_pause.setToolTip(QCoreApplication.translate("MainWindow", u"Pause continuous acquisition", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_scope_capture_pause.setText("")
#if QT_CONFIG(tooltip)
        self.pushButton_scope_capture_stop.setToolTip(QCoreApplication.translate("MainWindow", u"Cancel current operation", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_scope_capture_stop.setText("")
#if QT_CONFIG(tooltip)
        self.pushButton_scope_capture_save.setToolTip(QCoreApplication.translate("MainWindow", u"Save on-screen measurement", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_scope_capture_save.setText("")
#if QT_CONFIG(tooltip)
        self.pushButton_scope_capture_step.setToolTip(QCoreApplication.translate("MainWindow", u"Take one measurement", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_scope_capture_step.setText("")
#if QT_CONFIG(tooltip)
        self.pushButton_scope_capture_start_collection.setToolTip(QCoreApplication.translate("MainWindow", u"Start batch collection", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_scope_capture_start_collection.setText("")
#if QT_CONFIG(tooltip)
        self.pushButton_scope_capture_step_save.setToolTip(QCoreApplication.translate("MainWindow", u"Take and save one measurement", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_scope_capture_step_save.setText("")
        self.label_multiSpecWidget_title.setText(QCoreApplication.translate("MainWindow", u"Spectrometer", None))
        self.comboBox_multiSpec.setItemText(0, QCoreApplication.translate("MainWindow", u"WP-00000", None))

#if QT_CONFIG(tooltip)
        self.comboBox_multiSpec.setToolTip(QCoreApplication.translate("MainWindow", u"Select spectrometer to control", None))
#endif // QT_CONFIG(tooltip)
        self.comboBox_multiSpec.setCurrentText(QCoreApplication.translate("MainWindow", u"WP-00000", None))
#if QT_CONFIG(tooltip)
        self.pushButton_eject.setToolTip(QCoreApplication.translate("MainWindow", u"Eject the current spectrometer.", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_eject.setText("")
#if QT_CONFIG(tooltip)
        self.checkBox_multiSpec_hide_others.setToolTip(QCoreApplication.translate("MainWindow", u"Only graph selected spectrometer", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_multiSpec_hide_others.setText(QCoreApplication.translate("MainWindow", u"Hide Others", None))
#if QT_CONFIG(tooltip)
        self.pushButton_multiSpec_lock.setToolTip(QCoreApplication.translate("MainWindow", u"Apply changes to all spectrometers", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_multiSpec_lock.setText("")
#if QT_CONFIG(tooltip)
        self.checkBox_multiSpec_autocolor.setToolTip(QCoreApplication.translate("MainWindow", u"Tint graph lines by model", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_multiSpec_autocolor.setText(QCoreApplication.translate("MainWindow", u"Auto Colors", None))
        self.techniqueWidget_label.setText(QCoreApplication.translate("MainWindow", u"Technique", None))
        self.comboBox_technique.setItemText(0, QCoreApplication.translate("MainWindow", u"Emission/Raman", None))
        self.comboBox_technique.setItemText(1, QCoreApplication.translate("MainWindow", u"Absorbance", None))
        self.comboBox_technique.setItemText(2, QCoreApplication.translate("MainWindow", u"Trans/Refl", None))

        self.comboBox_technique.setProperty(u"Comment", QCoreApplication.translate("MainWindow", u"MZ: keep aligned with common.axis enum", None))
        self.lightSourceWidget_label.setText(QCoreApplication.translate("MainWindow", u"Laser Control", None))
#if QT_CONFIG(tooltip)
        self.pushButton_laser_toggle.setToolTip(QCoreApplication.translate("MainWindow", u"Fire laser (ctrl-L)", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_laser_toggle.setText(QCoreApplication.translate("MainWindow", u"Turn Laser On", None))
        self.verticalSlider_laser_power.setProperty(u"Comment", QCoreApplication.translate("MainWindow", u"MZ: change to horizontalSlider", None))
        self.pushButton_laser_power_dn.setText("")
        self.pushButton_laser_power_up.setText("")
        self.doubleSpinBox_laser_power.setPrefix("")
        self.doubleSpinBox_laser_power.setSuffix(QCoreApplication.translate("MainWindow", u"%", None))
        self.comboBox_laser_power_unit.setItemText(0, QCoreApplication.translate("MainWindow", u"milliWatts (mW)", None))
        self.comboBox_laser_power_unit.setItemText(1, QCoreApplication.translate("MainWindow", u"percentage (%)", None))

#if QT_CONFIG(tooltip)
        self.comboBox_laser_power_unit.setToolTip(QCoreApplication.translate("MainWindow", u"whether laser power should be controlled through mW or percentage", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(whatsthis)
        self.comboBox_laser_power_unit.setWhatsThis(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>In general, all spectrometers with multi-mode lasers (<b>MML</b>) receive laser power calibrations, and are therefore recommended for control through mW. Spectrometers with single-mode lasers (<b>SML</b>) typically do not receive laser power calibrations, and are therefore recommended for control through pulse-modulation width (<b>PWM</b>) duty-cycle, i.e. a rough percentage of full power.</p><p>Therefore, most MML and SML spectrometers will not see this option, and will not be given the option to configure how laser power is controlled.</p><p>The special case is for Integrated Laser with Interchangeable Coupling (<b>ILC</b>) models, which have an MML exposed through a fiber and probe.  Although these units will receive a laser power calibration in the factory, and therefore are able to set power in mW, the user may elect to use a different fiber and probe than was used to generate the calibration.</p><p>In such cases the calibration, although present, is invalid, and we need to give the "
                        "user the ability to control the laser through percentage as well.</p></body></html>", None))
#endif // QT_CONFIG(whatsthis)
#if QT_CONFIG(tooltip)
        self.doubleSpinBox_excitation_nm.setToolTip(QCoreApplication.translate("MainWindow", u"Adjust laser wavelength", None))
#endif // QT_CONFIG(tooltip)
        self.label_lightSourceWidget_excitation_nm.setText(QCoreApplication.translate("MainWindow", u"Excitation (nm)", None))
        self.spinBox_laser_attenuator.setSuffix(QCoreApplication.translate("MainWindow", u" %", None))
        self.label_laser_control_attenuator.setText(QCoreApplication.translate("MainWindow", u"Attenuation", None))
        self.label_laser_watchdog_sec.setText(QCoreApplication.translate("MainWindow", u"Watchdog (sec)", None))
        self.comboBox_laser_tec_mode.setItemText(0, QCoreApplication.translate("MainWindow", u"Off", None))
        self.comboBox_laser_tec_mode.setItemText(1, QCoreApplication.translate("MainWindow", u"On", None))
        self.comboBox_laser_tec_mode.setItemText(2, QCoreApplication.translate("MainWindow", u"Auto", None))
        self.comboBox_laser_tec_mode.setItemText(3, QCoreApplication.translate("MainWindow", u"Auto-On", None))

        self.label_laser_tec_mode.setText(QCoreApplication.translate("MainWindow", u"TEC mode", None))
        self.checkBox_laser_watchdog.setText(QCoreApplication.translate("MainWindow", u"Enable Watchdog", None))
#if QT_CONFIG(tooltip)
        self.pushButton_auto_raman_measurement.setToolTip(QCoreApplication.translate("MainWindow", u"Automatically take one averaged dark-corrected Raman measurement scaled to fill the detector's dynamic range", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_auto_raman_measurement.setText(QCoreApplication.translate("MainWindow", u"Auto-Raman", None))
        self.comboBox_presets.setItemText(0, QCoreApplication.translate("MainWindow", u"Select One", None))
        self.comboBox_presets.setItemText(1, QCoreApplication.translate("MainWindow", u"Create new...", None))
        self.comboBox_presets.setItemText(2, QCoreApplication.translate("MainWindow", u"Remove...", None))

#if QT_CONFIG(tooltip)
        self.comboBox_presets.setToolTip(QCoreApplication.translate("MainWindow", u"Presets allow you to save and re-apply key acquisition parameters including integration time, gain dB, scan averaging, boxcar, baseline subtraction and Raman intensity correction.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.checkBox_auto_raman_config.setToolTip(QCoreApplication.translate("MainWindow", u"Expose various low-level configuration options for the Auto-Raman feature, which may be assigned to named Presets", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_auto_raman_config.setText(QCoreApplication.translate("MainWindow", u"Configure Auto-Raman", None))
        self.label_auto_raman_max_ms.setText(QCoreApplication.translate("MainWindow", u"Max (ms)", None))
        self.label_auto_raman_start_integ_ms.setText(QCoreApplication.translate("MainWindow", u"Start Integ (ms)", None))
        self.label_auto_raman_start_gain_db.setText(QCoreApplication.translate("MainWindow", u"Start Gain (dB)", None))
        self.label_auto_raman_max_integ_ms.setText(QCoreApplication.translate("MainWindow", u"Max Integ (ms)", None))
        self.label_auto_raman_min_integ_ms.setText(QCoreApplication.translate("MainWindow", u"Min Integ (ms)", None))
        self.label_auto_raman_max_gain_db.setText(QCoreApplication.translate("MainWindow", u"Max Gain (dB)", None))
        self.label_auto_raman_min_gain_db.setText(QCoreApplication.translate("MainWindow", u"Min Gain (dB)", None))
        self.label_auto_raman_target_counts.setText(QCoreApplication.translate("MainWindow", u"Target Counts", None))
        self.label_auto_raman_max_counts.setText(QCoreApplication.translate("MainWindow", u"Max Counts", None))
        self.label_auto_raman_min_counts.setText(QCoreApplication.translate("MainWindow", u"Min Counts", None))
        self.label_auto_raman_max_factor.setText(QCoreApplication.translate("MainWindow", u"Max Factor", None))
        self.label_auto_raman_drop_factor.setText(QCoreApplication.translate("MainWindow", u"Drop Factor", None))
        self.label_auto_raman_saturation.setText(QCoreApplication.translate("MainWindow", u"Saturation", None))
        self.label_auto_raman_laser_warning_delay_sec.setText(QCoreApplication.translate("MainWindow", u"Laser Warning (sec)", None))
        self.label_auto_raman_max_avg.setText(QCoreApplication.translate("MainWindow", u"Max Averaging", None))
        self.label_auto_raman_elapsed_name.setText(QCoreApplication.translate("MainWindow", u"Elapsed Time", None))
        self.checkBox_auto_raman_retain_settings.setText(QCoreApplication.translate("MainWindow", u"Retain Auto-Raman Settings", None))
        self.checkBox_auto_raman_auto_save.setText(QCoreApplication.translate("MainWindow", u"Automatically Save", None))
        self.checkBox_auto_raman_onboard.setText(QCoreApplication.translate("MainWindow", u"Onboard", None))
        self.label201.setText(QCoreApplication.translate("MainWindow", u"Accessory Control", None))
        self.checkBox_acc_xl_shutter.setText(QCoreApplication.translate("MainWindow", u"Shutter Open", None))
        self.checkBox_acc_xl_fan.setText(QCoreApplication.translate("MainWindow", u"Fan Enable", None))
        self.detectorControlWidget_label.setText(QCoreApplication.translate("MainWindow", u"Detector Control", None))
        self.slider_integration_time_ms.setProperty(u"Comment", QCoreApplication.translate("MainWindow", u"MZ: change to horizontalSlider", None))
        self.detectorControlWidget_label_integrationTime.setText(QCoreApplication.translate("MainWindow", u"Integration Time", None))
        self.pushButton_integration_time_ms_dn.setText("")
        self.pushButton_integration_time_ms_up.setText("")
#if QT_CONFIG(tooltip)
        self.spinBox_integration_time_ms.setToolTip(QCoreApplication.translate("MainWindow", u"set integration time in ms (ctrl-T)", None))
#endif // QT_CONFIG(tooltip)
        self.spinBox_integration_time_ms.setSuffix(QCoreApplication.translate("MainWindow", u" ms", None))
        self.spinBox_integration_time_ms.setPrefix("")
        self.detectorControlWidget_label_detectorTemperature.setText(QCoreApplication.translate("MainWindow", u"Detector Temperature", None))
        self.temperatureWidget_pushButton_detector_setpoint_dn.setText("")
        self.temperatureWidget_pushButton_detector_setpoint_up.setText("")
        self.spinBox_detector_setpoint_degC.setSuffix(QCoreApplication.translate("MainWindow", u"\u00b0C", None))
        self.spinBox_detector_setpoint_degC.setPrefix("")
#if QT_CONFIG(tooltip)
        self.checkBox_detector_tec_enabled.setToolTip(QCoreApplication.translate("MainWindow", u"Control the detector's Thermo-Electric Cooler (TEC)", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_detector_tec_enabled.setText(QCoreApplication.translate("MainWindow", u"TEC Enabled", None))
#if QT_CONFIG(tooltip)
        self.checkBox_external_trigger_enabled.setToolTip(QCoreApplication.translate("MainWindow", u"Freeze acquisition until an external hardware trigger signal is applied", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_external_trigger_enabled.setText(QCoreApplication.translate("MainWindow", u"External Trigger", None))
#if QT_CONFIG(tooltip)
        self.checkBox_high_gain_mode_enabled.setToolTip(QCoreApplication.translate("MainWindow", u"Control High Gain Mode on InGaAs NIR detectors", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_high_gain_mode_enabled.setText(QCoreApplication.translate("MainWindow", u"High-Gain Mode", None))
        self.slider_gain.setProperty(u"Comment", QCoreApplication.translate("MainWindow", u"MZ: change to horizontalSlider", None))
        self.label_gainWidget_title.setText(QCoreApplication.translate("MainWindow", u"Gain", None))
        self.pushButton_gain_dn.setText("")
        self.pushButton_gain_up.setText("")
#if QT_CONFIG(tooltip)
        self.doubleSpinBox_gain.setToolTip(QCoreApplication.translate("MainWindow", u"change gain in dB (ctrl-G)", None))
#endif // QT_CONFIG(tooltip)
        self.doubleSpinBox_gain.setSuffix(QCoreApplication.translate("MainWindow", u" dB", None))
#if QT_CONFIG(tooltip)
        self.checkBox_edc_enabled.setToolTip(QCoreApplication.translate("MainWindow", u"Electrical Dark Correction", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_edc_enabled.setText(QCoreApplication.translate("MainWindow", u"EDC Enabled", None))
        self.displayAxisWidget_label.setText(QCoreApplication.translate("MainWindow", u"X Axis", None))
        self.displayAxis_comboBox_axis.setItemText(0, QCoreApplication.translate("MainWindow", u"Pixel", None))
        self.displayAxis_comboBox_axis.setItemText(1, QCoreApplication.translate("MainWindow", u"Wavelength", None))
        self.displayAxis_comboBox_axis.setItemText(2, QCoreApplication.translate("MainWindow", u"Wavenumber", None))

        self.displayAxis_comboBox_axis.setProperty(u"Comment", QCoreApplication.translate("MainWindow", u"MZ: keep aligned with common.axis enum", None))
        self.doubleSpinBox_cursor_scope.setSuffix(QCoreApplication.translate("MainWindow", u" nm", None))
        self.checkBox_graph_marker.setText(QCoreApplication.translate("MainWindow", u"Marker", None))
        self.pushButton_cursor_dn.setText("")
        self.pushButton_cursor_up.setText("")
#if QT_CONFIG(tooltip)
        self.checkBox_cursor_scope_enabled.setToolTip(QCoreApplication.translate("MainWindow", u"Dis/enable a horizontal sliding cursor on the x-axis", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_cursor_scope_enabled.setText(QCoreApplication.translate("MainWindow", u"Cursor", None))
#if QT_CONFIG(whatsthis)
        self.checkBox_edit_horiz_roi.setWhatsThis(QCoreApplication.translate("MainWindow", u"In Expert Mode, allows you to configure the horizontal Region-of-Interest (ROI) used to crop the ends of the spectrum.", None))
#endif // QT_CONFIG(whatsthis)
        self.checkBox_edit_horiz_roi.setText(QCoreApplication.translate("MainWindow", u"Edit Horiz ROI", None))
        self.label_XD_title.setText(QCoreApplication.translate("MainWindow", u"XD", None))
        self.checkBox_XD_enable.setText("")
        self.checkBox_XD_enable.setText(QCoreApplication.translate("MainWindow", u"Enabled", None))
        self.label_XD_model_label.setText(QCoreApplication.translate("MainWindow", u"Model", None))
        self.label_XD_left_trim_bool_label.setText(QCoreApplication.translate("MainWindow", u"Left Trim", None))
        self.spinBox_XD_left_trim_wavenumber.setSuffix(QCoreApplication.translate("MainWindow", u" cm\u207b\u00b9", None))
        self.label_XD_right_trim_bool_label.setText(QCoreApplication.translate("MainWindow", u"Right Trim", None))
        self.checkBox_XD_right_trim.setText("")
        self.spinBox_XD_right_trim_wavenumber.setSuffix(QCoreApplication.translate("MainWindow", u" cm\u207b\u00b9", None))
        self.checkBox_XD_deconvolute.setText("")
        self.checkBox_XD_deconvolute.setText(QCoreApplication.translate("MainWindow", u"Deconvolute", None))
        self.checkBox_XD_external_laser.setText("")
        self.checkBox_XD_external_laser.setText(QCoreApplication.translate("MainWindow", u"External Laser", None))
#if QT_CONFIG(tooltip)
        self.checkBox_XD_external_laser.setToolTip(QCoreApplication.translate("MainWindow", u"Assume external laser is connected to Raman probe, and apply XD processing regardless of internal laser controls.", None))
#endif // QT_CONFIG(tooltip)
        self.label_library_matching_title.setText(QCoreApplication.translate("MainWindow", u"Library Matching", None))
        self.checkBox_library_matching_enable.setText(QCoreApplication.translate("MainWindow", u"Enabled", None))
        self.pushButton_library_matching_select_library.setText(QCoreApplication.translate("MainWindow", u"Select Library", None))
#if QT_CONFIG(tooltip)
        self.pushButton_library_matching_select_library.setToolTip(QCoreApplication.translate("MainWindow", u"Select folder containing spectra of known compounds", None))
#endif // QT_CONFIG(tooltip)
        self.label_library_matching_matched_compound_name_label.setText(QCoreApplication.translate("MainWindow", u"Compound", None))
        self.label_library_matching_matched_compound_name.setText(QCoreApplication.translate("MainWindow", u"None", None))
        self.label_library_matching_matched_compound_score_label.setText(QCoreApplication.translate("MainWindow", u"Score", None))
        self.label_library_matching_matched_compound_score.setText(QCoreApplication.translate("MainWindow", u"0.00", None))
        self.label_library_matching_min_score_label.setText(QCoreApplication.translate("MainWindow", u"Min Score", None))
        self.label_library_matching_max_results_label.setText(QCoreApplication.translate("MainWindow", u"Max Results", None))
        self.checkBox_library_matching_use_dist.setText("")
        self.label_library_matching_use_dist_label.setText(QCoreApplication.translate("MainWindow", u"Use standard library", None))
        self.pushButton_library_matching_save_to_library.setText(QCoreApplication.translate("MainWindow", u"Save to Library", None))
#if QT_CONFIG(tooltip)
        self.pushButton_library_matching_save_to_library.setToolTip(QCoreApplication.translate("MainWindow", u"Add current sample spectrum to matching library", None))
#endif // QT_CONFIG(tooltip)
        self.label_plugin_selection_widget.setText(QCoreApplication.translate("MainWindow", u"Plugins", None))
#if QT_CONFIG(tooltip)
        self.checkBox_plugin_connected.setToolTip(QCoreApplication.translate("MainWindow", u"Loads and \"starts\" the selected plug-in", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_plugin_connected.setText(QCoreApplication.translate("MainWindow", u"Connect", None))
        self.label_plugin_widget.setText(QCoreApplication.translate("MainWindow", u"Plugin Control", None))
        self.label_plugin_title.setText(QCoreApplication.translate("MainWindow", u"Plugin Name", None))
        self.pushButton_plugin_process.setText(QCoreApplication.translate("MainWindow", u"Process", None))
        self.scanAveragingWidget_label.setText(QCoreApplication.translate("MainWindow", u"Scan Averaging", None))
        self.pushButton_scan_averaging_dn.setText("")
        self.spinBox_scan_averaging.setSuffix(QCoreApplication.translate("MainWindow", u" samples", None))
        self.pushButton_scan_averaging_up.setText("")
        self.label_scan_averaging.setText(QCoreApplication.translate("MainWindow", u"Collecting: 1 of 5", None))
        self.boxcarWidget_label.setText(QCoreApplication.translate("MainWindow", u"Boxcar Smoothing", None))
        self.pushButton_boxcar_half_width_dn.setText("")
#if QT_CONFIG(tooltip)
        self.spinBox_boxcar_half_width.setToolTip(QCoreApplication.translate("MainWindow", u"half-width", None))
#endif // QT_CONFIG(tooltip)
        self.spinBox_boxcar_half_width.setSuffix(QCoreApplication.translate("MainWindow", u" pixels", None))
        self.spinBox_boxcar_half_width.setPrefix("")
        self.pushButton_boxcar_half_width_up.setText("")
        self.boxcarWidget_label_2.setText(QCoreApplication.translate("MainWindow", u"Baseline Correction", None))
#if QT_CONFIG(tooltip)
        self.checkBox_baselineCorrection_enable.setToolTip(QCoreApplication.translate("MainWindow", u"Subtract a dynamically-computed baseline", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_baselineCorrection_enable.setText(QCoreApplication.translate("MainWindow", u"Enable", None))
#if QT_CONFIG(tooltip)
        self.checkBox_baselineCorrection_show.setToolTip(QCoreApplication.translate("MainWindow", u"Show the computed baseline which would be removed if enabled", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_baselineCorrection_show.setText(QCoreApplication.translate("MainWindow", u"Show baseline", None))
        self.comboBox_baselineCorrection_algo.setItemText(0, QCoreApplication.translate("MainWindow", u"Algo One", None))
        self.comboBox_baselineCorrection_algo.setItemText(1, QCoreApplication.translate("MainWindow", u"Algo Two", None))

        self.label_post_processing.setText(QCoreApplication.translate("MainWindow", u"Advanced Options", None))
        self.checkBox_richardson_lucy.setText(QCoreApplication.translate("MainWindow", u"Sharpen peaks", None))
        self.checkBox_etalon_correction.setText(QCoreApplication.translate("MainWindow", u"Etalon correction", None))
        self.checkBox_ingaas_correction.setText(QCoreApplication.translate("MainWindow", u"InGaAs correction", None))
        self.label_area_scan_widget.setText(QCoreApplication.translate("MainWindow", u"Area Scan", None))
        self.checkBox_area_scan_enable.setText("")
        self.label202.setText(QCoreApplication.translate("MainWindow", u"Enable", None))
        self.checkBox_area_scan_normalize.setText("")
        self.label203.setText(QCoreApplication.translate("MainWindow", u"Normalize", None))
        self.checkBox_area_scan_normalize_csv.setText("")
        self.label204.setText(QCoreApplication.translate("MainWindow", u"Normalize CSV", None))
        self.label_area_scan_current_line.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label205.setText(QCoreApplication.translate("MainWindow", u"Current Line", None))
        self.label_area_scan_frame_count.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label206.setText(QCoreApplication.translate("MainWindow", u"Frame Count", None))
        self.label207.setText(QCoreApplication.translate("MainWindow", u"Start Line", None))
        self.label208.setText(QCoreApplication.translate("MainWindow", u"Stop Line", None))
        self.label209.setText(QCoreApplication.translate("MainWindow", u"Line Step", None))
#if QT_CONFIG(tooltip)
        self.spinBox_area_scan_cursor.setToolTip(QCoreApplication.translate("MainWindow", u"if positive, draw a horizontal cursor across the image", None))
#endif // QT_CONFIG(tooltip)
        self.label210.setText(QCoreApplication.translate("MainWindow", u"Cursor Line", None))
        self.label211.setText(QCoreApplication.translate("MainWindow", u"Image Scale", None))
        self.checkBox_area_scan_fit.setText("")
        self.label212.setText(QCoreApplication.translate("MainWindow", u"Fit", None))
        self.label_area_scan_frame_elapsed.setText("")
        self.label213.setText(QCoreApplication.translate("MainWindow", u"Elapsed sec", None))
        self.pushButton_area_scan_save.setText(QCoreApplication.translate("MainWindow", u"Save", None))
        self.label_trans_opt.setText(QCoreApplication.translate("MainWindow", u"Transmission Options", None))
#if QT_CONFIG(tooltip)
        self.checkBox_enable_max_transmission.setToolTip(QCoreApplication.translate("MainWindow", u"Cap transmission", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_enable_max_transmission.setText(QCoreApplication.translate("MainWindow", u"Enforce max", None))
        self.spinBox_max_transmission_perc.setSuffix(QCoreApplication.translate("MainWindow", u"%", None))
        self.label214.setText(QCoreApplication.translate("MainWindow", u"XS Accessory Connector", None))
        self.checkBox_xs_acc_gpio_enable.setText(QCoreApplication.translate("MainWindow", u"GPIO Enable", None))
#if QT_CONFIG(tooltip)
        self.checkBox_xs_acc_gpio_enable.setToolTip(QCoreApplication.translate("MainWindow", u"all GPIO pins remain inactive until the GPIO feature is enabled", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_xs_acc_5V_enable.setText(QCoreApplication.translate("MainWindow", u"5V Supply Enable", None))
#if QT_CONFIG(tooltip)
        self.checkBox_xs_acc_5V_enable.setToolTip(QCoreApplication.translate("MainWindow", u"the 5V output supply is inactive until explicitly enabled", None))
#endif // QT_CONFIG(tooltip)
        self.label_xs_acc_gpio1.setText(QCoreApplication.translate("MainWindow", u"GPIO1", None))
        self.label215.setText(QCoreApplication.translate("MainWindow", u"Mode", None))
        self.comboBox_xs_acc_gpio1_mode.setItemText(0, QCoreApplication.translate("MainWindow", u"Manual", None))
        self.comboBox_xs_acc_gpio1_mode.setItemText(1, QCoreApplication.translate("MainWindow", u"Function", None))

        self.label216.setText(QCoreApplication.translate("MainWindow", u"Direction", None))
        self.comboBox_xs_acc_gpio1_dir.setItemText(0, QCoreApplication.translate("MainWindow", u"Input", None))
        self.comboBox_xs_acc_gpio1_dir.setItemText(1, QCoreApplication.translate("MainWindow", u"Output", None))

        self.label217.setText(QCoreApplication.translate("MainWindow", u"Function", None))
        self.comboBox_xs_acc_gpio1_function.setItemText(0, QCoreApplication.translate("MainWindow", u"Disabled", None))
        self.comboBox_xs_acc_gpio1_function.setItemText(1, QCoreApplication.translate("MainWindow", u"Ext Trigger", None))
        self.comboBox_xs_acc_gpio1_function.setItemText(2, QCoreApplication.translate("MainWindow", u"Laser Override", None))

        self.label218.setText(QCoreApplication.translate("MainWindow", u"Value", None))
        self.comboBox_xs_acc_gpio1_value.setItemText(0, QCoreApplication.translate("MainWindow", u"Low", None))
        self.comboBox_xs_acc_gpio1_value.setItemText(1, QCoreApplication.translate("MainWindow", u"High", None))

        self.label_xs_acc_gpio2.setText(QCoreApplication.translate("MainWindow", u"GPIO2", None))
        self.label219.setText(QCoreApplication.translate("MainWindow", u"Mode", None))
        self.comboBox_xs_acc_gpio2_mode.setItemText(0, QCoreApplication.translate("MainWindow", u"Manual", None))
        self.comboBox_xs_acc_gpio2_mode.setItemText(1, QCoreApplication.translate("MainWindow", u"Function", None))

        self.label220.setText(QCoreApplication.translate("MainWindow", u"Direction", None))
        self.comboBox_xs_acc_gpio2_dir.setItemText(0, QCoreApplication.translate("MainWindow", u"Input", None))
        self.comboBox_xs_acc_gpio2_dir.setItemText(1, QCoreApplication.translate("MainWindow", u"Output", None))

        self.label221.setText(QCoreApplication.translate("MainWindow", u"Function", None))
        self.comboBox_xs_acc_gpio2_function.setItemText(0, QCoreApplication.translate("MainWindow", u"Disabled", None))
        self.comboBox_xs_acc_gpio2_function.setItemText(1, QCoreApplication.translate("MainWindow", u"Cont Strobe", None))
        self.comboBox_xs_acc_gpio2_function.setItemText(2, QCoreApplication.translate("MainWindow", u"Data Ready", None))
        self.comboBox_xs_acc_gpio2_function.setItemText(3, QCoreApplication.translate("MainWindow", u"Laser Mirror", None))

        self.label222.setText(QCoreApplication.translate("MainWindow", u"Value", None))
        self.comboBox_xs_acc_gpio2_value.setItemText(0, QCoreApplication.translate("MainWindow", u"Low", None))
        self.comboBox_xs_acc_gpio2_value.setItemText(1, QCoreApplication.translate("MainWindow", u"High", None))

        self.label_xs_acc_cont_strobe.setText(QCoreApplication.translate("MainWindow", u"Continuous Strobe", None))
        self.label223.setText(QCoreApplication.translate("MainWindow", u"Period", None))
        self.spinBox_xs_acc_cont_strobe_period_us.setSuffix(QCoreApplication.translate("MainWindow", u" \u00b5s", None))
        self.label224.setText(QCoreApplication.translate("MainWindow", u"Width", None))
        self.spinBox_xs_acc_cont_strobe_width_us.setSuffix(QCoreApplication.translate("MainWindow", u" \u00b5s", None))
        self.label225.setText(QCoreApplication.translate("MainWindow", u"Delay", None))
        self.spinBox_xs_acc_cont_strobe_delay_us.setSuffix(QCoreApplication.translate("MainWindow", u" \u00b5s", None))
        self.label226.setText(QCoreApplication.translate("MainWindow", u"Count", None))
        self.systemStatusWidget_label.setText(QCoreApplication.translate("MainWindow", u"System Status", None))
        self.systemStatusWidget_pushButton_hardware.setText(QCoreApplication.translate("MainWindow", u"HW", None))
        self.systemStatusWidget_pushButton_light.setText(QCoreApplication.translate("MainWindow", u"Light", None))
        self.systemStatusWidget_pushButton_light.setProperty(u"comment", QCoreApplication.translate("MainWindow", u"MZ: why is this not a QLabel?", None))
        self.systemStatusWidget_pushButton_temperature.setText(QCoreApplication.translate("MainWindow", u"Temp", None))
        self.label_drawer.setText(QCoreApplication.translate("MainWindow", u"Marquee messages go here", None))
        self.pushButton_marquee_close.setText("")
    # retranslateUi

