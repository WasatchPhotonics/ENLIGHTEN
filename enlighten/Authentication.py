from PySide2 import QtCore, QtGui, QtWidgets

import hashlib
import logging
import time

log = logging.getLogger(__name__)

class Authentication(object):
    """
    This class encapsulates the process of "logging-in" to ENLIGHTEN and enabling
    or displaying GUI widgets which should only be exposed to certain user classes.
    
    Currently there are four levels setup:
    
    - BASIC 
        - default, no authentication required
        - user cannot edit ANY of the fields in the EEPROMEditor (display-only)
        - user can "save .ini", and edit desired fields directly in that file 
          (only affects their PC, in their Documents directory)
        - cannot write EEPROM
    
    - ADVANCED    
        - password "wasatch" (hardcoded)
        - enables "Advanced Users" controls 
            - some manufacturing tests and experimental features
            - excitation spinner on Laser Control Widget
        - allows user to edit "safe" fields in the EEPROM editor (see EEPROM.is_editable)
        - editted "safe" fields can be saved to .ini
        - still cannot write EEPROM
    
    - OEM
        - password "wasatchoem" (hardcoded)
        - displays "Save EEPROM" button
        - EEPROM can be written, but EEPROM.write_eeprom() method will only update
          "is_editable" fields in the page buffers before writing
    
    - PRODUCTION
        - password NOT hardcoded (ask Zieg or production team)
        - all EEPROM fields editable
        - EEPROM can be written
    
    You'll note we're not too worried about security, hard-coding passwords and
    hashes and all.  The truth is that our full USB API is (deliberately) published
    for application developers in ENG-0001, and the full EEPROM layout is defined 
    publicly in ENG-0034, so essentially any knowledgable user can do anything 
    anyway.  This is more a matter of keeping dangerous / confusing / experimental 
    options on a high shelf so new users don't randomly click buttons just to see 
    what they do.
    
    @par Relationship to Advanced Options
    
    They are disconnected and orthogonal (see Advanced Options docs).
    """

    BASIC      = 0
    ADVANCED   = 1
    OEM        = 2
    PRODUCTION = 3

    PRODUCTION_DIGEST = '830147906ad1e20efe9a12b5d0b5242f'

    def __init__(self, 
            gui,
            marquee,
            parent,

            button_login, 

            oem_widgets         = None,
            advanced_widgets    = None,
            production_widgets  = None):

        self.gui                                = gui
        self.parent                             = parent
        self.marquee                            = marquee

        self.button_login                       = button_login

        self.oem_widgets                        = oem_widgets
        self.advanced_widgets                   = advanced_widgets
        self.production_widgets                 = production_widgets

        self.level = self.BASIC
        self.error_count = 0

        self.observers = set()

        self.button_login.clicked.connect(self.login)

        self.update_widgets()

    def register_observer(self, callback):
        self.observers.add(callback)

    def login(self):
        """
        The user has clicked "Advanced Features", so display the login pop-up,
        get their password, compare it to supported values and update features 
        accordingly.
        """
        (password, ok) = QtWidgets.QInputDialog.getText(
            self.parent, 
            "Admin Login", 
            "Password:", 
            QtWidgets.QLineEdit.Password)

        if password is None:
            self.level = self.BASIC
        elif password.lower() == "wasatch":
            self.level = self.ADVANCED
        elif password.lower() == "wasatchoem":
            self.level = self.OEM
        elif hashlib.md5(password.encode('utf-8')).hexdigest() == self.PRODUCTION_DIGEST:
            self.level = self.PRODUCTION
        else:
            self.level = self.BASIC
            self.marquee.error("invalid password")
            time.sleep(self.error_count * 2)
            self.error_count += 1

        self.gui.colorize_button(self.button_login, self.level != self.BASIC)
        self.update_widgets()

        for callback in self.observers:
            callback()

    def update_auth_widgets(self, widgets, auth):
        """
        If you want a hidden widget to become VISIBLE if the user is logged-in, 
        use the Qt Designer to give the widget a boolean "custom property" called 
        "initiallyVisible" and set it False.
        
        By default, Authentication just determines whether a widget is ENABLED, not
        VISIBLE (think EEPROMEditor fields).  Widgets lacking this custom property 
        will be visible at all times, and only their ENABLED status will change.
        
        (Obviously, in addition to the custom property, you must also add such 
        widgets to the constructor lists passed to this object.)
        """
        if widgets:
            for widget in widgets:
                widget.setEnabled(auth)
                initiallyVisible = widget.property("initiallyVisible")
                if initiallyVisible is not None and isinstance(initiallyVisible, bool):
                    widget.setVisible(initiallyVisible or auth)

    def update_widgets(self):
        self.update_auth_widgets(self.advanced_widgets,   self.has_advanced_rights())
        self.update_auth_widgets(self.oem_widgets,        self.has_oem_rights())
        self.update_auth_widgets(self.production_widgets, self.has_production_rights())

    def has_production_rights(self):
        return self.level >= self.PRODUCTION

    def has_advanced_rights(self):
        return self.level >= self.ADVANCED

    def has_oem_rights(self):
        return self.level >= self.OEM
