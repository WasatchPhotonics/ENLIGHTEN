import hashlib
import logging
import os

from enlighten import common

if common.use_pyside2():
    from PySide2 import QtWidgets
else:
    from PySide6 import QtWidgets

log = logging.getLogger(__name__)

class EEPROMWriter:
    """
    Encapsulate reflashing the EEPROM to the device.
    """
    def __init__(self, ctl):
        self.ctl = ctl

        b = ctl.form.ui.pushButton_write_eeprom
        b.setVisible(False)
        b.clicked.connect(self.write)

    def write(self, verify=True):
        log.debug("asked to write EEPROM (verify %s)", verify)

        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            log.error("can't write EEPROM (no Spectrometer)")
            return
        if spec.settings is None:
            log.error("can't write EEPROM (no SpectrometerSettings)")
            return

        if spec.settings.eeprom_backup is None:
            sn = spec.settings.eeprom.serial_number
        else:
            sn = spec.settings.eeprom_backup.serial_number
        label = spec.label

        ########################################################################
        # Display a confirmation dialog
        ########################################################################

        if verify:
            box = QtWidgets.QMessageBox()
            box.setIcon(QtWidgets.QMessageBox.Warning)
            box.setWindowTitle(label)
            box.setText("Do you wish to update your EEPROM? " + 
                "Misconfiguration could 'brick' your spectrometer and require manufacturer RMA. ")
            box.setInformativeText("Incorrect usage of the EEPROM may void warranty.")
            box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Cancel)

            retval = box.exec_()

            if retval != QtWidgets.QMessageBox.Yes:
                log.debug("user declined to write EEPROM on %s", label)
                self.ctl.marquee.clear(token="eeprom")
                return

        log.debug("user elected to write EEPROM on %s", label)

        # send the contents of the new/updated EEPROM to the subprocess,
        # first so the subprocess will USE the new settings, but also so
        # that the following command can tell the subprocess to WRITE its
        # cached copy to the hardware.
        if not self.send_to_subprocess():
            self.ctl.marquee.error("failed to send EEPROM to subprocess")
            return

        # now take a backup of the EEPROM, just to be paranoid
        if not self.backup():
            self.ctl.marquee.error("failed to backup EEPROM")
            return

        # we're now ready to actually send the "write" command to the subprocess
        self.ctl.marquee.info("writing EEPROM")
        spec.change_device_setting("write_eeprom", (sn, spec.settings.eeprom))
        self.ctl.clear_response_errors(spec)

    def send_to_subprocess(self):
        log.debug("sending EEPROM to subprocess")

        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return

        if spec.settings.eeprom_backup is None:
            sn = spec.settings.eeprom.serial_number
        else:
            sn = spec.settings.eeprom_backup.serial_number

        # note that the order of these checks is significant
        if self.ctl.authentication.has_production_rights():
            # update all EEPROM fields
            log.debug("sending 'replace_eeprom'")
            spec.change_device_setting("replace_eeprom", (sn, spec.settings.eeprom))
        elif self.ctl.authentication.has_advanced_rights():
            # update editable EEPROM fields
            spec.change_device_setting("update_eeprom", (sn, spec.settings.eeprom))
        else:
            # log.critical("authentication error")
            # return False
            
            # okay, we previously didn't let people update the EEPROM at all without
            # some level of login, but I guess we have to for FieldWavecalFeature
            spec.change_device_setting("update_eeprom", (sn, spec.settings.eeprom))

        return True

    def backup(self, output_path=None):
        """
        This will write the current spectrometer's EEPROM's contents in JSON format
        to EnlightenSpectra/eeprom_backups/EEPROM-SERIAL-SHA1.json.  Every time a
        spectrometer is connected, EEPROM will backup the EEPROM in this manner.  
        New writes will simply overwrite the old AS LONG AS the digest is unchanged.
        Older versions can be distinguished from inode timestamp.  
        
        It is recognized that reducing a digest in this way risks collisions, but 
        typically the number of EEPROM changes to a given unit are few.
        
        Note: with FieldWavecalFeature, the number of EEPROM changes is likely to,
        increase, and we may want to revisit this behavior.
        
        If at any point we wanted to provide a "restore EEPROM" feature (whether in 
        ENLIGHTEN, a Python script etc), easiest path is just to use the "buffers" 
        which are fully preserved.
        
        @param output_path[in] if provided, should be a scalar string pathname of an existing directory
        """
        log.debug("backing up EEPROM")

        spec = self.ctl.multispec.current_spectrometer()
        try:
            text = spec.settings.eeprom_backup.json()
            digest = hashlib.sha1(text.encode("UTF-8")).hexdigest()
            digest_short = digest[:10]

            root_dir = os.path.join(os.path.expanduser(common.get_default_data_dir()), "eeprom_backups")
            if not os.path.isdir(root_dir):
                os.makedirs(root_dir)
            if output_path is None:
                output_path = os.path.join(root_dir, "EEPROM-%s-%s.json" % (spec.settings.eeprom.serial_number, digest_short))
            log.debug("backing up EEPROM to %s", output_path)
            with open(output_path, "w", newline="") as outfile: 
                outfile.write(text)
            return True
        except:
            log.error("could not backup EEPROM", exc_info=1)
            return False
