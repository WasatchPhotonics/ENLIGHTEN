import os
import sys
import time
import pexpect 
import logging
import datetime
import threading
from queue import Queue

from pexpect.popen_spawn import PopenSpawn 

from wasatch import applog

from .. import common

log = logging.getLogger(__name__)

## Arguments passed to continuous_poll() when spawning the subprocess.
class SubprocessArgs:
    def __init__(self, 
          executable_pathname,
          library_pathname,
          log_level, 
          log_queue, 
          q_child,
          q_parent):
        self.executable_pathname = executable_pathname
        self.library_pathname    = library_pathname
        self.log_level           = log_level
        self.log_queue           = log_queue
        self.q_child             = q_child
        self.q_parent            = q_parent

## An inbound request being passed from Wrapper to the subprocess for writing to KIAConsole.
class MatchRequest:
    def __init__(self, x, y, max_results=20, min_score=0.80, measurement_id=None):
        self.x = x
        self.y = y
        self.max_results = max_results
        self.min_score = min_score
        self.measurement_id = measurement_id

## An outbound response generated from the subprocess and passed back to Feature.
#  Note that this is essentially just a list of the matches passed back from 
#  KIAConsole...it does NOT attempt to declare a "winner" (such higher-level 
#  processing is left to KnowItAll.Feature).
class MatchResponse:
    def __init__(self, request, disconnect=False):
        self.disconnect = disconnect

        if request is not None:
            self.measurement_id = request.measurement_id
        else:
            self.measurement_id = None

        self.complete = False
        self.match_count = 0
        self.entries = None
        self.expired = False

## One entry of many representing a compound potentially matched by KIAConsole within a larger MatchResult.
class MatchResultEntry:
    def __init__(self, compound_name, score):
        self.compound_name = compound_name
        self.score         = score

##
# This class encapsulates ENLIGHTEN's interface to KnowItAll
#
# @par Design Considerations
#
# This needs to be in a background thread, so we can process newly acquired 
# spectra when there is no pending match in-progress.  Therefore, we're borrowing
# some architecture from WasatchDeviceWrapper.
#
# The subprocess will communicate with KIAConsole via the text protocol used by
# KIAConsole.  The subprocess will communicate with the MainProcess.KnowItAllWrapper
# via picklable Python objects.
#
# Currently no attempt has been made to integrate this into the RamanMatching
# class as an alternate matching engine, though it certainly should be.  Right
# now I'm just providing a quick "proof-of-concept" integration to show that
# the executable and linked library and signature database can indeed be 
# accessed from within ENLIGHTEN in timely fashion.
#
# @par Multiprocessing Shenanigans
#
# Note that multiprocessing.Process().start() explodes if the Wrapper contains
# callbacks to Controller.  (Controller is a QThingy that can't be pickled.)
#
# @todo support authentication (look for "expected" within match results)
# @todo support good/bad (look for known-good and known-bad results, returning binary indicator)
#
class Wrapper:

    # ##########################################################################
    # Constants
    # ##########################################################################

    ## How long the subprocess should sleep before checking to see if a new 
    #  request has been passed down the interprocess pipe.  (Is there an event-
    #  oriented Python message queue?)
    POLLER_WAIT_SEC = 1 

    CONNECTION_TIMEOUT_SEC = 15

    # enum
    CONNECTION_NOT_STARTED          = 0
    CONNECTION_PENDING_VERIFICATION = 1
    CONNECTION_VERIFIED             = 2
    CONNECTION_ERROR                = 3

    # ##########################################################################
    # Lifecycle
    # ##########################################################################

    def __init__(self, 
            executable_pathname,
            library_pathname,
            log_level,
            log_queue):

        self.executable_pathname = executable_pathname
        self.library_pathname    = library_pathname
        self.log_level           = log_level
        self.log_queue           = log_queue

        self.reset()

    def reset(self):
        self.poller             = None
        self.connection_status  = Wrapper.CONNECTION_NOT_STARTED
        self.time_connection_started = None

        self.pipe_parent        = None
        self.pipe_child         = None

    ## 
    # Spawn the sub-process which actually communicates with our KIAConsole.exe via stdin/out
    # in a background thread (so that KIAConsole processing delays, which can be considerable,
    # do not affect the ENLIGHTEN GUI response time).
    #
    # This is essentially a private method, as the initial connect is driven by the "enable"
    # checkbox.
    def connect(self):
        if self.poller is not None:
            log.critical("KnowItAll.Wrapper already connected!")
            return False

        try:
            # create the bidirectional Pipe we'll use to communicate
            self.q_parent = Queue() 
            self.q_child = Queue()

            # Spawn a child process running the continuous_poll() method on this
            # object instance.  
            args = SubprocessArgs(
                executable_pathname = self.executable_pathname,
                library_pathname    = self.library_pathname,
                log_level           = self.log_level, 
                log_queue           = self.log_queue,               #           subprocess ---> log
                q_child             = self.q_child,
                q_parent            = self.q_parent)              # Main <--> subprocess <--> executable

            # instantiate subprocess
            log.debug("connect: instantiating Process")
            self.poller = threading.Thread(target=self.continuous_poll, args=(args,), name="KIA.Wrapper", daemon=False)

            # spawn subprocess
            log.debug("connect: starting subprocess")
            self.poller.start()

            log.debug("connect: status = pending verification")
            self.connection_status = Wrapper.CONNECTION_PENDING_VERIFICATION
            self.time_connection_started = datetime.datetime.now()
            return True
        except:
            log.error("connect: exception in connection", exc_info=1)
            self.poller = None
            return False

    ## check to confirm subprocess spawns okay, by checking for exactly one 
    # "True" object on the response pipeline
    def verify_connection(self):
        if not self.poller or not self.q_parent:
            return False

        if self.connection_status >= Wrapper.CONNECTION_VERIFIED:
            return True

        if not self.q_parent.empty():
            obj = self.q_parent.get_nowait() 
            if obj is not None:
                log.debug("verify_connection: received ACK: %s", obj)
                self.connection_status = Wrapper.CONNECTION_VERIFIED
                return True
            else:
                log.error("verify_connection: received NACK, closing")
        elif (datetime.datetime.now() - self.time_connection_started).total_seconds() > Wrapper.CONNECTION_TIMEOUT_SEC:
            log.error("verify_connection: exceeded %d sec connection timeout", Wrapper.CONNECTION_TIMEOUT_SEC)
        else:
            log.debug("verify_connection: still pending verification")
            return False

        # to get this far, apparently we received a NACK or timeout...either way
        # we should abort the connection
        log.warn("verify_connection: sending poison pill to poller")
        if self.q_child:
            self.q_child.put_nowait(None) 

        log.warn("verify_connection: releasing poller")
        self.poller = None
        return False

    ## 
    # Kill the subprocess by passing a "poison-pill" request downstream.
    #
    # This is a public method, called by the Controller.
    def disconnect(self):
        if not self.verify_connection():
            log.debug("disconnect: connection not verified...ignoring")
            return True

        # send poison pill to the subprocess
        try:
            if self.q_child:
                self.q_child.put_nowait(None) 
        except:
            pass

        log.debug("disconenct: joining poller")
        try:
            self.poller.join()
            log.debug("disconnect: joined poller")
        except AssertionError as exc:
            log.warn("disconnect: Poller never successfully connected?", exc_info=1)
        except NameError as exc:
            log.warn("disconnect: Poller previously disconnected?", exc_info=1)
        except Exception as exc:
            log.critical("disconnect: Cannot join poller", exc_info=1)

        log.debug("disconnect: resetting")
        self.reset()

    # ##########################################################################
    # Callbacks
    # ##########################################################################

    ##
    # enlighten.Controller calls this to identify the last-collected spectrum.
    #
    # x should be in wavenumbers, since KIAConsole is hard-coded to use
    # KIA's Raman module.  This function packages the request into a request
    # object and then sends to the subprocess for matching.  
    #
    # Only one request can be active at once, so if a pending request is already
    # in-process, this request is rejected outright (not queued, as ENLIGHTEN can
    # collect data far faster than KIA can process it).
    #
    # @todo address use-case of identifying loaded spectra, perhaps via a 
    #       process(x, y) method
    def send_request(self, x_axis, spectrum, max_results, min_score, measurement_id=None):
        if not self.verify_connection():
            return False

        if x_axis is None or spectrum is None:
            log.error("send_request: missing inputs")
            return False

        if len(x_axis) != len(spectrum):
            log.error("send_request: x_axis of %d elements doesn't match spectrum of %d elements",
                len(x_axis), len(spectrum))
            return False

        log.debug("send_request: sending request to subprocess")
        request = MatchRequest(
            x              = x_axis, 
            y              = spectrum, 
            max_results    = max_results, 
            min_score      = min_score, 
            measurement_id = measurement_id)
        self.q_child.put_nowait(request)
        return True

    ##
    # Feature calls this to fetch the latest KIA response, if there is one. 
    def get_response(self):
        if not self.q_parent:
            return

        # has the connection been verified?
        if self.connection_status != Wrapper.CONNECTION_VERIFIED:
            return

        # is there a response?
        if self.q_parent.empty():
            return 

        # get the response
        log.debug("get_response: reading response")
        response = self.q_parent.get_nowait()

        # is the child shutting down?
        if response is None:
            log.critical("received poison pill from child...disconnecting")
            self.disconnect()
            return MatchResponse(request=None, disconnect=True)

        # was there an error downstream?
        if not response.complete or response.entries is None:
            log.error("Wrapper: failed to process request")
            self.disconnect()
            return MatchResponse(request=None, disconnect=True)

        log.debug("get_response: returning MatchResponse of %d entries", len(response.entries))
        return response

    # ##########################################################################
    # Sub-Process
    # ##########################################################################

    def continuous_poll(self, args):
        # We have just forked into a new process, so the first thing is to
        # configure logging for this process.  Although we've been passed-in
        # args.log_level, let's start with DEBUG so we can always capture
        # connect() activity.
        log.info("continuous_poll: start")

        # open a logfile for the executable process (hardcode name and path for now)
        logpath = os.path.join(common.get_default_data_dir(), "raman_id.log")
        log.debug("Raman ID logging to %s", logpath)
        logfile = open(logpath, "w") 

        # spawn the shell process 
        # (instead of pexpect, we could probably use PySide.QtCore.QProcess if need be)
        cmd = "%s --streaming" % args.executable_pathname
        if args.library_pathname:
            cmd += " --library %s" % args.library_pathname
        log.debug("continuous_poll: spawning %s", cmd)
        child = PopenSpawn(cmd, logfile=logfile, timeout=10, maxread=65535, encoding='utf-8')
        if not child:
            log.critical("failed to launch KIAConsole (popen)")
            args.q_parent.put_nowait(None)
            return

        # confirm the KIAConsole executable launches correctly
        log.debug("continuous_poll: checking child has started")
        timeout_sec = 30
        try:
            child.expect("Starting stream processing", timeout=timeout_sec)

            # send the "success" confirmation upstream to confirm we're live
            log.debug("continuous_poll: stream processing confirmed")
            args.q_parent.put_nowait(True)
        except:
            log.critical("Failed to confirm stream processing in %d sec", timeout_sec)
            args.q_parent.put_nowait(None)
            return
        
        # downlevel logging level to whatever ENLIGHTEN is using
        logging.getLogger().setLevel(args.log_level)

        # Enter the runtime loop in which the sub-process continually checks for
        # new requests from ENLIGHTEN; and if found, passes them to KIAConsole
        # for processing and reads-back the results.  This loop terminates when
        # KIAConsole encounters an error, or ENLIGHTEN sends a poison-pill.  
        # Currently there is no "re-try" or "re-connect" logic if KIAConsole 
        # experiences an error.
        while True:
            time.sleep(Wrapper.POLLER_WAIT_SEC)

            # wait for a request from ENLIGHTEN
            if args.q_child.empty():
                log.debug("continuous_poll: no request found")
                continue

            # read the request
            log.debug("continuous_poll: receiving request")
            request = args.q_child.get_nowait()

            # was this a poison-pill?
            if request is None:
                log.info("continuous_poll: poison-pill received, shutting down")
                break

            # stub an empty response (defaults to failure)
            response = MatchResponse(request)

            # parse the request
            pixels = len(request.x)
            log.debug("continuous_poll: received request: %d pixels, min_score %.2f, max_results %d, wavenumbers (%.2f, %.2f)", 
                pixels, request.min_score, request.max_results, request.x[0], request.x[-1])

            # send the request to KIA
            try:
                child.sendline("REQUEST_START")
                child.sendline("pixels, %d" % pixels)
                child.sendline("max_results, %d" % request.max_results)
                child.sendline("min_score, %.2f" % request.min_score)
                for i in range(pixels):
                    child.sendline("%.2f, %.2f" % (request.x[i], request.y[i]))
                child.sendline("REQUEST_END")
            except:
                log.error("continuous_poll: error sending request to KIA", exc_info=1)
                args.q_parent.put_nowait(response)
                continue

            # wait for KIA response
            timeout_sec = 30
            pattern = r"Finished loading measurement"
            try:
                log.debug("continuous_poll: waiting for: %s", pattern)
                child.expect(pattern, timeout=timeout_sec)
                log.debug("continuous_poll: found request receipt")
            except:
                # on error, send the default response, which is implicitly incomplete and no matches
                log.error("continuous_poll: failed to find: %s", pattern, exc_info=1)
                args.q_parent.put_nowait(response)
                continue
            log.debug("continuous_poll: matched: %s", child.match.group(0))

            pattern = r"Found ([0-9]+) matches in"
            try:
                log.debug("continuous_poll: waiting for: %s", pattern)
                child.expect(pattern, timeout=timeout_sec)
                match_count = int(child.match.group(1))
                log.debug("continuous_poll: found match count: %d", match_count)
            except:
                # on error, send the default response, which is implicitly incomplete and no matches
                # log.error("continuous_poll: failed to find: %s", pattern, exc_info=1)
                # args.pipe_child.send(response)
                # continue

                # let's self-destruct
                log.error("KIAConsole error...self-destructing")
                args.q_parent.put_nowait(None)
                break

            log.debug("continuous_poll: matched: %s", child.match.group(0))

            # was a compound matched?
            if match_count == 0:
                # no, so send back an empty result (complete, as there was no error)
                response.complete = True
                response.entries = []
                args.q_parent.put_nowait(response)
                continue

            # read KIA response
            results = []
            read_count = 0
            try:
                for i in range(match_count):
                    # use linefeeds to lock the pattern to a single line, as compound names
                    # have varied length, embedded punctuation and frequent Unicode, making
                    # delimination uncertain
                    pattern = r"Match %d: ([^\n]+) with ([0-9.]+)%% (?:score|confidence) \(([^\n]+)\)" % i
                    log.debug("continuous_poll: waiting for: %s", pattern)
                    child.expect(pattern, timeout=timeout_sec)

                    compound_name =       child.match.group(1).strip()
                    score         = float(child.match.group(2))
                    license       =       child.match.group(3)

                    results.append(MatchResultEntry(compound_name, score))
                    read_count += 1

                    if license.lower() == "expired" or compound_name == "(null)":
                        response.expired = True
            except:
                log.error("continuous_poll: failed to find match result %d of %d", read_count, match_count, exc_info=1)
                if read_count == 0:
                    continue
                else:
                    # we got some data...just go with it
                    pass

            if match_count != len(results):
                log.error("continuous_poll: match count mismatch (%d != %d)", match_count, len(results))
                match_count = len(results)

            # to get this far, we have a non-empty list of results, so the 
            # response is "complete" -- populate the results
            response.complete = True
            response.match_count = match_count
            response.entries = results

            # send the response back to ENLIGHTEN
            args.q_parent.put_nowait(response)

        log.debug("continuous_poll: closing child")
        child.sendline("QUIT")
        child.sendeof() 

        log.critical("continuous_poll: exiting")
