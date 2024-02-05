
# last run 2023-08-08
# - no log messages
# - no indication of RamanID.exe subproc


import re
import os
import json
import numpy as np
import pandas as pd
import logging
import datetime
import traceback

from pexpect.popen_spawn import PopenSpawn 
import common from enlighten

from EnlightenPlugin import EnlightenPluginBase,    \
                            EnlightenPluginField,    \
                            EnlightenPluginResponse,  \
                            EnlightenPluginConfiguration

log = logging.getLogger(__name__)

##
# This is a sample ENLIGHTEN plugin which relays spectra to an external 
# executable for Raman identification.
#
# It is important to understand the following:
#
# - This plugin is not, in and of itself, capable of performing Raman 
#   identification. 
# - This plugin COMMUNICATES with an external program providing Raman 
#   identification. 
# - Specifically, this program passes ENLIGHTEN spectra to the external 
#   program, reads back the declared compound name / score (if any), and 
#   displays them on the ENLIGHTEN GUI.
#
# - A sample C/C++ RamanID application is provided here, for demonstration
#   purposes: [Enlighten-Simple-RamanID](https://github.com/WasatchPhotonics/Enlighten-Simple-RamanID)
# - That program includes a pre-compiled Windows installer here:
#   [MSI Installer](https://github.com/WasatchPhotonics/Enlighten-Simple-RamanID/tree/main/releases)
#
# @par External Client
#
# The external executable path is hardcoded.  I'm not sure it's reasonable to
# have an ENLIGHTEN plug-in which can be arbitrarily pointed to any executable,
# given the API between the plugin and executable will be highly specific. That
# said, this plugin can be used with any executable which can be installed at 
# that path and obeys the described protocol.
#
# The executable is spawned within a Pexpect subshell (forked process). All comms
# with the client process are via UTF-8 strings. JSON-encoded records are 
# exchanged using NDJSON (linefeed at end of record).
#
# Essentially, once the client is spawned and handshaking complete, the two
# processes will communicate by:
#
# 1. plugin receives EnlightenPluginRequest from ENLIGHTEN
# 2. plugin converts request spectrum into NDJSON string
# 3. plugin write JSON string to executable over stdout
# 4. executable reads JSON string at stdin
# 5. executable performs matching
# 6. executable returns match results in NDJSON line at client's stdout
# 7. plugin reads match results at plugin stdin
# 8. plugin demarshalls JSON and populates EnlightenPluginResponse
#
# A sample external client meeting this specification is provided here for reference:
#
# - https://github.com/WasatchPhotonics/Enlighten-Simple-RamanID
# 
# @par ENLIGHTEN Blocking
#
# The EnlightenPluginConfiguration specifies block_enlighten=True.  That means
# that when ENLIGHTEN acquires a new Reading from the spectrometer, the ENLIGHTEN
# GUI will block (freeze) until this plugin has completed processing (sync, not
# async). 
#
# This was done so that metadata fields output by the plugin (Declared Compound,
# Declared Score) could be added to the new ProcessedReading BEFORE any 
# Measurement files were saved.  
#
# The "pro" is that if you save a Measurement from ENLIGHTEN (which was processed
# by this plugin), the results from the plugin will appear in the saved file(s).
#
# The "con" is that if this plugin, or the child executable, take a long time to
# process a spectrum (or crash), ENLIGHTEN will appear to be frozen.  For this 
# reason, ENLIGHTEN enforces a hard timeout of ONE SECOND on all plugins which
# "block_enlighten".
#
# In initial testing, this plugin (and the RamanID.exe it was designed against)
# were regularly processing spectra in less than 0.1sec, so it should be okay
# (as a prototype).
#
# @par Executable Design
#
# Some Raman ID algorithms are proprietary, but as design guidance note that the
# [simdjson](https://github.com/simdjson/simdjson) JSON library is gratifyingly
# performant.
# 
# @par Path Forward
#
# A more flexible approach to block_enlighten might use MeasurementID or a 
# putative ProcessedReadingID to associate "future" plugin results with saved 
# measurements which can then be updated on-disk after results are complete.
#
# Or, for ProcessedReadings in which it is anticipated that saved Measurements 
# will be required (TakeOneSave), we could add a ProcessedReading.save_when_complete 
# flag such that the post-plugin ProcessedReading will be automatically saved 
# after the plugin response is received.
#
class RamanID(EnlightenPluginBase):

    ## hardcoded path to external executable
    RAMAN_ID_EXE = "C:\Program Files\Wasatch Photonics\Raman ID Algorithm\RamanID.exe"

    ## contains transcript of all strings exchanged with client subprocess (in EnlightenSpectra)
    PEXPECT_LOGFILE = "RamanID-pexpect.log"

    ## contains debug logs of external executable (in EnlightenSpectra)
    EXECUTABLE_LOGFILE = "RamanID-debug.log"

    # ##########################################################################
    # lifecycle
    # ##########################################################################

    def __init__(self, ctl):
        super().__init__(ctl)
        self.library_dir = None
        self.count = 0

    def get_configuration(self):
        fields = []

        # the name of the highest-scoring compound
        fields.append(EnlightenPluginField(
            name = "Compound",
            datatype = str,
            tooltip = "Declared matching compound"))

        # the unknown threshold (0-100)
        fields.append(EnlightenPluginField(
            name = "Unk Thresh",
            direction = "input",
            datatype = int,
            initial=95,
            minimum=0,
            maximum=100,))

        # the computed match score (0-100)
        fields.append(EnlightenPluginField(
            name = "Score",
            datatype = float,
            precision = 2))

        # minimum score to declare a match
        fields.append(EnlightenPluginField(
            name="Min Score",
            direction="input",
            datatype=int,
            initial=20,
            minimum=0,
            maximum=100,
            tooltip="Only report matches with this score or above"))

        # maximum number of declared matches
        fields.append(EnlightenPluginField(
            name="Max Results",
            direction="input",
            datatype=int,
            initial=4,
            minimum=1,
            maximum=20,
            tooltip="Only report this many matches"))

        # on-screen counter (to track plugin progress)
        fields.append(EnlightenPluginField(
            name="Processed",
            datatype=int,
            tooltip="How many spectra have been processed by the plugin"))

        # table of all matching compounds
        fields.append(EnlightenPluginField(
            name = "Results",
            datatype = "pandas"))

        return EnlightenPluginConfiguration(
            name            = "RamanID", 
            block_enlighten = True,
            fields          = fields)

    ##
    # 1. prompt for library (can "default" from persistence but they still have 
    #    to select it)
    # 2. kick-off background subprocess to binary executable
    # 3. confirm executable has indicated "ready for streaming"
    #
    # @returns True if connected and ready to process requests
    def connect(self, enlighten_info):
        super().connect(enlighten_info)

        # init from configuration
        log.debug("todo: initalize from persisted settings")

        # TODO: add "Select Library" button (see OEM plugin for example)
        self.library_dir = os.path.join(common.get_default_data_dir(), "Raman Library")
        self.creation_time = datetime.datetime.now()
        if self.library_dir is None:
            return self.report_error("missing dependency: Library Directory")
        elif not os.path.exists(self.library_dir):
            return self.report_error(f"library directory not found: '{self.library_dir}'")
        log.debug(f"using library dir: {self.library_dir}")

        # kick-off the stream processor
        ready_for_streaming = False
        try:
            log.debug("calling spawn_subprocess")
            ready_for_streaming = self.spawn_subprocess()
            log.debug("back from spawn_subprocess")
        except:
            return self.report_error("failed to spawn subprocess: %s" % traceback.format_exc())

        if not ready_for_streaming:
            return self.report_error("subprocess not ready for streaming")

        log.debug("believed connected and ready for streaming")
        return True

    def disconnect(self):
        if self.child is not None:
            log.debug("disconnect: closing child")
            self.child.sendeof() 
            self.child = None

        super().disconnect()

    # ##########################################################################
    # request processing
    # ##########################################################################

    def process_request(self, request):
        try:
            # process request in child subprocess
            match_result = self.generate_match_result(request)
            if match_result is None:
                log.debug("ignoring null response for now")
                return EnlightenPluginResponse(request)

            # extract matches from child response
            compounds = []
            scores    = []
            for result in match_result:
                compounds.append(result["Name"])
                scores.append(result["Score"])

            # generate the table of all compounds and scores
            df = pd.DataFrame(data = {
                'Compound': compounds,
                'Score'   : scores
            }).round(2)
            
            # generate metadata to add to saved measurements from this processed reading
            metadata = { 
                "Declared Compound": "Unknown",
                "Declared Score": 0,

                # extra non-standard metadata for testing
                "Elapsed Sec": (datetime.datetime.now() - self.creation_time).total_seconds()
            }
            if len(compounds) > 0:
                metadata["Declared Compound"] = compounds[0]
                metadata["Declared Score"]    = scores[0]

            self.count += 1
            outputs = {
                "Compound":     metadata["Declared Compound"],
                "Score":        metadata["Declared Score"],
                "Processed":    self.count,
                "Results":      df
            }
            return EnlightenPluginResponse(request, outputs=outputs, metadata=metadata)
        except:
            self.report_error("caught exception during process_request: %s" % traceback.format_exc())
            return None

    # ##########################################################################
    # private methods
    # ##########################################################################

    ##
    # 1. spawns subprocess
    # 2. performs handshaking (checks for "ready")
    # 
    # @returns True if successfully spawned and ready to stream spectra.
    def spawn_subprocess(self):
        log.debug("preparing to spawn {RamanID.RAMAN_ID_EXE}")

        # open a logfile for the subprocess
        pexpect_log = os.path.join(self.enlighten_info.get_save_path(), RamanID.PEXPECT_LOGFILE)
        debug_log   = os.path.join(self.enlighten_info.get_save_path(), RamanID.EXECUTABLE_LOGFILE)
        log.debug(f"Pexpect will log to {pexpect_log}")
        log.debug(f"{RamanID.RAMAN_ID_EXE} will log to {debug_log}")

        # open pexpect logfile, so we can pass it to pexpect
        logfile = open(pexpect_log, "w") 

        # this is the shell command we'll execute in pexpect
        cmd = f'"{RamanID.RAMAN_ID_EXE}" --verbose --logfile "{debug_log}" --streaming --library "{self.library_dir}" 2>nul'
        cmd.replace('\\', '/')

        # need to compare this to PluginWorker's timeout on connect()
        timeout_sec = 10 

        # spawn the child process 
        log.debug("spawn_subprocess: spawning %s", cmd)
        child = PopenSpawn(
            cmd, 
            logfile  = logfile, 
            timeout  = timeout_sec,
            maxread  = 65535,           # not sure if this limit will affect us
            encoding = 'utf-8')         # for compound names, or Python str in general?
        if not child:
            log.critical("failed to launch external executable: %s", cmd)
            return False

        # confirm the external executable launches correctly
        log.debug("spawn_subprocess: checking child has started")
        try:
            # look for a case-insensitive line containing "ready" 
            # (and consume everything up to the next linefeed)
            child.expect("(?i)ready[^\r\n]*\r\n")
            log.debug("spawn_subprocess: stream processing confirmed")
        except:
            log.critical("Failed to confirm stream processing in %d sec", timeout_sec)
            return False

        # retain a handle to the open child
        self.child = child
        return True

    ## 
    # 1. converts EnlightenPluginRequest into flattened JSON string
    # 2. sends JSON request to child
    # 3. looks for JSON response containing "MatchResult"
    # 4. converts JSON response to dict
    #
    # @returns MatchResponse dict on success, None otherwise
    def generate_match_result(self, request):
        # JSON requires Python lists, and also benefits from enforced precision
        wavenumbers = np.array(request.settings.wavenumbers,        dtype=np.float32).round(2).tolist()
        spectrum    = np.array(request.processed_reading.processed, dtype=np.float32).round(2).tolist()

        if wavenumbers is None:
            log.error("missing wavenumbers")
            return

        if len(spectrum) != len(wavenumbers):
            log.error("len spectrum %d != len wavenumbers %d", len(spectrum), len(wavenumbers))
            return

        # note that this obviously isn't an EnlightenPluginRequest, it's a request object
        # specific to the external RamanID executable in the subprocess
        stream_request = {
            "min_confidence": request.fields["Min Score"], # 0-100
            "unk_thresh": request.fields["Unk Thresh"]/100.0,
            "max_results": request.fields["Max Results"],
            "wavenumbers": wavenumbers,
            "spectrum": spectrum
        }

        timeout_sec = 10 # early testing using 1024px, 4-compound library and jute ~3sec

        # sort keys so client can be deterministic (also simdjson runs faster if 
        # keys checked in order)
        request_json = json.dumps(stream_request, sort_keys=True)
        request_json = re.sub(r"\bNaN\b", "null", request_json) # just in case

        log.debug("sending: %s", request_json)
        try:
            self.child.sendline(request_json)
        except:
            log.error("stream_request: error sending request to external app", exc_info=1)
            log.debug(request_json)
            return

        log.debug("waiting on subprocess response")
        try:
            # expect a single line in response
            self.child.expect('\r\n', timeout=timeout_sec)
        except Exception as e:
            log.error(f"expecting single response error of {e}")
            return

        log.debug("received subprocess response")

        if self.child.before is None or len(self.child.before) < 1:
            log.error("received empty response")
            return

        response_json = self.child.before
        log.debug("response_json = [%s]", response_json)

        try:
            log.debug("converting JSON to dict")
            response = json.loads(response_json)
        except:
            # This may be a case where the external program was unable to 
            # return properly-formed JSON (internal error, warning, whatever).
            log.error("unable to parse subprocess response JSON: %s", response_json, exc_info=1)
            return 

        log.debug("parsed subprocess response: %s", response)

        log.debug("checking for MatchResult")
        if "MatchResult" not in response:
            log.error("didn't find MatchResult in subprocess response: %s", response_json)
            return
            
        log.debug("returning MatchResult")
        return response["MatchResult"]

    def report_error(self, msg):
        self.log("error: " + str(msg))

