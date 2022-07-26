import os
import json
import socket
import logging
#import urllib.request

from typing import Optional
from decimal import Decimal

import boto3
from botocore.config import Config

from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtWidgets import QInputDialog, QLineEdit, QMessageBox, QPushButton

from .common import get_default_data_dir
from .EEPROMEditor import EEPROMEditor
from . import util

log = logging.getLogger(__name__)

try:
    from .keys import *
    DISABLED = False
except Exception as e:
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
    """

    def __init__(self, 
                 restore_button: QPushButton, 
                 eeprom_editor: EEPROMEditor) -> None:

        self.restore_button = restore_button
        self.eeprom_editor = eeprom_editor

        self.session = None
        self.dynamo_resource = None

        if DISABLED:
            log.info("No keys, so not initializing cloud manager class")
            return

        if "ENLIGHTEN_DISABLE_INTERNET" in os.environ:
            log.info("Internet access disabled")
            return

        self.result_message = QMessageBox(self.restore_button)
        self.result_message.setWindowTitle("Restore EEPROM Result")
        self.result_message.setStandardButtons(QMessageBox.Ok)

        self.restore_button.clicked.connect(self.perform_restore)

    def get_andor_eeprom(self, detector_serial: str) -> dict:
        if self.session is None or self.dynamo_resource is None:
            self.setup_connection()
        if self.session is None or detector_serial is None:
            return {}

        log.debug(f"loading Andor EEPROM for detector {detector_serial}")
        andor_table = self.dynamo_resource.Table("andor_EEPROM")
        response = andor_table.get_item(Key={"detector_serial_number": detector_serial})
        eeprom_response = response["Item"]
        dict_response = dict(eeprom_response)
        util.normalize_decimal(dict_response)
        return dict_response

    def perform_restore(self) -> None:
        serial_number = self.prompt_for_serial()
        if self.session is None or self.dynamo_resource is None:
            self.setup_connection()
        if serial_number is not None and self.session is not None:
            local_file, download_result = self.attempt_download(serial_number)
            if download_result:
                log.debug(f"succeeded in downloading cloud file {serial_number}")
                import_result = self.eeprom_editor.import_eeprom(file_name=local_file)
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
        except socket.error as ex:
            log.error("internet is not available")
            return False

    def setup_connection(self) -> None:
        if DISABLED:
            log.error("CloudManager disabled")
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
        local_file = ''
        try:
            log.debug(f"downloading EEPROM for serial {serial_number}")
            local_file = os.path.join(get_default_data_dir(), "eeprom_backups", f"{serial_number}.json")
            response = self.eeprom_table.get_item(Key={"serialNumber": serial_number})
            eeprom_response = response["Item"]
            # default is required, see function definition
            eeprom = self.eeprom_editor.parse_wpsc_report(dict(eeprom_response))
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
        text, ok = QInputDialog().getText(self.restore_button, 
                                          "Enter Spectrometer Serial Number",
                                          "Serial Number",
                                          QLineEdit.Normal)
        if not ok:
            return
        
        return text

    def create_session(self) -> boto3.Session:

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
