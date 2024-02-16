import hashlib
import logging
import time

from enlighten import common

if common.use_pyside2():
    from PySide2 import QtWidgets
else:
    from PySide6 import QtWidgets

log = logging.getLogger(__name__)

class Authentication:
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

    def __init__(self, ctl):
        self.ctl = ctl

        cfu = ctl.form.ui

        self.button_login   = cfu.pushButton_admin_login
        self.combo_view     = cfu.comboBox_view

        self.level = self.BASIC
        self.error_count = 0

        self.observers = set()

        self.button_login.clicked.connect(self.login)
        self.button_login.setWhatsThis("Lets you 'login' to ENLIGHTEN™ with passwords enabling additional features.")

        self._update_widgets()

    def register_observer(self, callback):
        self.observers.add(callback)

    def login(self):
        """
        The user has clicked "Advanced Features" or pressed "Ctrl-A," so display
        the login pop-up, get their password, compare it to supported values and
        update features accordingly.
        """
        (password, _) = QtWidgets.QInputDialog.getText(
            self.ctl.form, 
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
            self.ctl.marquee.error("invalid password")
            time.sleep(self.error_count * 2)
            self.error_count += 1

        self.ctl.gui.colorize_button(self.button_login, self.level != self.BASIC)
        self._update_widgets()

        # remove Factory from comboBox if it was already there
        try:
            self.combo_view.removeItem(self.combo_view.findText("Factory"))
        except:
            pass

        # re-add Factory at the bottom if appropriate
        if self.level > self.BASIC:
            self.combo_view.addItem("Factory")

        for callback in self.observers:
            callback()

    def _update_auth_widget(self, widget, auth):
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
        widget.setEnabled(auth)
        initiallyVisible = widget.property("initiallyVisible")
        if initiallyVisible is not None and isinstance(initiallyVisible, bool):
            widget.setVisible(initiallyVisible or auth)

    def _update_widgets(self):
        cfu = self.ctl.form.ui
        for w in [ cfu.tabWidget_advanced_features ]:
            self._update_auth_widget(w, self.has_advanced_rights())
        for w in [ cfu.pushButton_write_eeprom, 
                   cfu.pushButton_importEEPROM, 
                   cfu.pushButton_exportEEPROM, 
                   cfu.pushButton_restore_eeprom, 
                   cfu.pushButton_reset_fpga ]:
            self._update_auth_widget(w, self.has_oem_rights())
        for w in [ ]:
            self._update_auth_widget(w, self.has_production_rights())

    def has_production_rights(self):
        return self.level >= self.PRODUCTION

    def has_advanced_rights(self):
        return self.level >= self.ADVANCED

    def has_oem_rights(self):
        return self.level >= self.OEM
