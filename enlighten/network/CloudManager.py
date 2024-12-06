import os
import json
import socket
import logging

from typing import Optional
from decimal import Decimal

import boto3
from botocore.config import Config

from enlighten import common
from enlighten import util

if common.use_pyside2():
    from PySide2.QtWidgets import QInputDialog, QLineEdit, QMessageBox
else:
    from PySide6.QtWidgets import QInputDialog, QLineEdit, QMessageBox

log = logging.getLogger(__name__)

try:
    from .keys import *
    DISABLED = False
except:
    DISABLED = True
    log.error("No AWS keys found. Cloud eeprom restore disabled")

# response contains decimals that cannot be converted to JSON
# need to handle those cases
# see https://stackoverflow.com/questions/51614177/requesting-help-triggering-a-lambda-function-from-dynamodb
def handle_decimal_type(obj):
  if isinstance(obj, Decimal):
      if float(obj).is_integer():
         return int(obj)
      else:
         return float(obj)
  raise TypeError

class CloudManager:
    """
    Encapsulates access to AWS-backed cloud features.

    All internet access is opt-in, so unless the user has manually checked the 
    "Enable Cloud Access" options in Setup, all internet access will be blocked.

    @todo this whole class needs reviewed.
    """

    CONFIG_SECTION = "Cloud"

    def __init__(self, ctl):
        self.ctl = ctl
        cfu = ctl.form.ui

        self.cb_enabled = cfu.checkBox_cloud_config_download_enabled
        self.bt_restore = cfu.pushButton_restore_eeprom

        self.session = None
        self.dynamo_resource = None

        if DISABLED:
            log.info("No keys, so not initializing CloudManager")
            return

        self.init_from_config()

        # @todo move to common.msgbox
        self.result_message = QMessageBox(self.bt_restore)
        self.result_message.setWindowTitle("Restore EEPROM Result")
        self.result_message.setStandardButtons(QMessageBox.Ok)

        self.bt_restore    .clicked      .connect(self.restore_callback)
        self.cb_enabled    .stateChanged .connect(self.enable_callback)

    def init_from_config(self):
        self.cb_enabled.setChecked(self.ctl.config.get_bool(self.CONFIG_SECTION, "enabled"))

    def save_config(self):
        self.ctl.config.set(self.CONFIG_SECTION, "enabled", self.enabled())

    def enabled(self) -> bool:
        if DISABLED or not self.cb_enabled.isChecked():
            log.debug("Cloud access disabled")
            return False
        return True

    def enable_callback(self):
        self.ctl.config.set(self.CONFIG_SECTION, "enabled", self.cb_enabled.isChecked())
        self.save_config()

    def get_andor_eeprom(self, detector_serial: str) -> dict:
        """
        If you have the proper credentials enabled, this does the equivalent of 
        the following command-line:

        $ aws dynamodb get-item --table-name andor_EEPROM --key '{ "detector_serial_number": { "S": "CCD-29849" } }'
        """

        if not self.enabled():
            self.ctl.marquee.error(f"enable cloud connectivity to download EEPROM for detector {detector_serial}")
            return {}
        if self.session is None or self.dynamo_resource is None:
            self.setup_connection()
        if self.session is None or detector_serial is None:
            return {}

        self.ctl.marquee.info(f"downloading EEPROM for detector {detector_serial}")

        andor_table = self.dynamo_resource.Table("andor_EEPROM")
        response = andor_table.get_item(Key={"detector_serial_number": detector_serial})
        eeprom_response = response["Item"]
        dict_response = dict(eeprom_response)
        util.normalize_decimal(dict_response)
        return dict_response

    def download_andor_eeprom(self, device):
        eeprom = device.settings.eeprom

        # attempt to backfill missing EEPROM settings from cloud
        # (allow overrides from local configuration file)
        log.debug("attempting to download EEPROM")
        andor_eeprom = self.get_andor_eeprom(eeprom.detector_serial_number)
        if andor_eeprom:
            log.debug(f"before defaults: andor_eeprom {andor_eeprom}")

            def default_missing(local_name, empty_value=None, cloud_name=None):
                if cloud_name is None:
                    cloud_name = local_name
                current_value = eeprom.multi_wavelength_calibration.get(local_name)
                if current_value != empty_value:
                    log.debug(f"keeping non-default {local_name} {current_value}")
                else:
                    if cloud_name in andor_eeprom:
                        cloud_value = andor_eeprom[cloud_name]
                        log.info(f"using cloud-recommended default of {local_name} {cloud_value}")
                        eeprom.multi_wavelength_calibration.set(local_name, cloud_value)

            default_missing("excitation_nm_float", 0)
            default_missing("wavelength_coeffs",  [0, 1, 0, 0, 0])
            default_missing("model", None, "wp_model")
            default_missing("detector", "iDus")
            default_missing("serial_number", eeprom.detector_serial_number, "wp_serial_number")
            default_missing("raman_intensity_coeffs", [])
            default_missing("invert_x_axis", False)
            default_missing("roi_horizontal_start", 0)
            default_missing("roi_horizontal_end", 0)
            default_missing("roi_vertical_region_1_start", 0)
            default_missing("roi_vertical_region_1_end", 0)

            eeprom.stubbed = False

            log.debug(f"after defaults: andor_eeprom {andor_eeprom}")

            log.debug(f"calling save_config with: {eeprom}")
            device.change_setting("save_config", eeprom)

            self.ctl.marquee.info(f"successfully downloaded EEPROM for {eeprom.serial_number}")
        else:
            log.error(f"Could not load Andor EEPROM for {eeprom.detector_serial_number}")

    def restore_callback(self):
        if not self.enabled():
            return 

        serial_number = self.prompt_for_serial()
        if self.session is None or self.dynamo_resource is None:
            self.setup_connection()
        if serial_number is not None and self.session is not None:
            local_file, download_result = self.attempt_download(serial_number)
            if download_result:
                log.debug(f"succeeded in downloading cloud file {serial_number}")
                import_result = self.ctl.eeprom_editor.import_eeprom(file_name=local_file)
                if not import_result:
                    log.error("Error in eeprom editor import")
                    self.result_message.setText("EEPROM Writing Error.")
                    self.result_message.setIcon(QMessageBox.Critical)
                    self.result_message.exec_()
                self.result_message.setText("EEPROM Restore successful. Write EEPROM to complete.")
                self.result_message.setIcon(QMessageBox.NoIcon)
                self.result_message.exec_()

    def is_internet_available(self):
        """
        This completes in a few milliseconds in my testing.

        Host: 8.8.8.8 (google-public-dns-a.google.com)
        OpenPort: 53/tcp
        Service: domain (DNS/TCP)

        @see https://stackoverflow.com/a/33117579/11615696
        """
        log.debug("checking if internet available")
        try:
            # This can be slower than you'd expect:
            # urllib.request.urlopen("http://www.google.com", timeout=2) 

            socket.setdefaulttimeout(1)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
            log.info("internet is available")
            return True
        except socket.error:
            log.error("internet is not available")
            return False

    def setup_connection(self) -> None:
        if not self.enabled():
            return 
        if not self.is_internet_available():
            return

        # boto seems to log a lot of exception and stack-traces even during "successful" connections
        logging.getLogger('botocore.utils').setLevel(logging.INFO)

        try:
            log.debug("creating cloud session")
            self.session = self.create_session()
            self.dynamo_resource = self.session.resource("dynamodb")
            self.eeprom_table = self.dynamo_resource.Table("WPSCReports")
            log.debug("Finished setting up connection to cloud provider")
        except:
            log.error("failed to create session", exc_info=1)
            self.session = None
            self.result_message.setText("Error connecting to cloud. Using locally cached configuration.")
            self.result_message.setIcon(QMessageBox.Critical)
            self.result_message.exec_()

    def attempt_download(self, serial_number: str) -> tuple[str, bool]:
        if not self.enabled():
            return 

        local_file = ''
        try:
            log.debug(f"downloading EEPROM for serial {serial_number}")
            local_file = os.path.join(common.get_default_data_dir(), "eeprom_backups", f"{serial_number}.json")
            response = self.eeprom_table.get_item(Key={"serialNumber": serial_number})
            eeprom_response = response["Item"]
            # default is required, see function definition
            eeprom = self.ctl.eeprom_editor.parse_wpsc_report(dict(eeprom_response))
            json_response = json.dumps(eeprom, default=handle_decimal_type)
            with open(local_file, 'w') as f:
                f.write(str(json_response))
        except Exception as e:
            log.error(f"Ran into error trying to download cloud eeprom file of {e}")
            self.result_message.setText("Error retrieving EEPROM file from server.")
            self.result_message.setIcon(QMessageBox.Critical)
            self.result_message.exec_()
            return (local_file, False)
        return (local_file, True)

    def prompt_for_serial(self) -> Optional[str]:
        text, ok = QInputDialog().getText(self.cb_restore, 
                                          "Enter Spectrometer Serial Number",
                                          "Serial Number",
                                          QLineEdit.Normal)
        return text if ok else None

    def create_session(self) -> boto3.Session:
        if not self.enabled():
            return

        config = Config(
           retries = {
              'max_attempts': 1,
              'mode': 'standard'
           }
        )

        log.debug("instantiating boto3 client")
        client = boto3.client("cognito-identity", region_name="us-east-1", config=config)

        log.debug("getting client credentials")
        try:
            response = client.get_id(IdentityPoolId=ID_POOL_ID)
        except:
            log.error("unable to connect to cloud reponsitory", exc_info=1)
            return

        log.debug("getting client credentials for identity")
        response_cred = client.get_credentials_for_identity(IdentityId=response["IdentityId"])

        log.debug("Parsing credentials")
        try:
            access_id = response_cred["Credentials"]["AccessKeyId"]
            access_secret = response_cred["Credentials"]["SecretKey"]
            access_session = response_cred["Credentials"]["SessionToken"]

            log.debug("instantiating client session")
            s3_session = boto3.Session(
                aws_access_key_id=access_id,
                aws_secret_access_key=access_secret,
                aws_session_token=access_session,
                region_name=DYNAMO_REGION,
                )
            log.debug("Created client session")
        except:
            log.error("exception creating client session", exc_info=1)
            return 
        return s3_session
