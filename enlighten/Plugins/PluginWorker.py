import time
import logging
import threading
import traceback

log = logging.getLogger(__name__)

##
# This is the lightweight Thread object which "owns and runs" an actual plugin in
# the background.  It is created with input (request) and output (response) queues,
# which remain connected to the PluginController which spawned the worker.  The
# run() method loops indefinitely, relaying requests and responses between the 
# Controller and plugin, until closed by a poison-pill from either end.
class PluginWorker(threading.Thread):

    ##
    # Actually instantiates the plugin.
    def __init__(self,
            request_queue,
            response_queue, 
            module_info,
            enlighten_info):

        threading.Thread.__init__(self)

        self.request_queue  = request_queue
        self.response_queue = response_queue
        self.module_info    = module_info
        self.has_event_responses = True
        self.enlighten_info = enlighten_info
        self.error_message  = None

        if self.module_info is None:
            log.critical("module_info cannot be None")
            return

    def run(self):
        if self.module_info is None or self.module_info.instance is None:
            return

        plugin = self.module_info.instance
        module_name = self.module_info.module_name
        shutdown = False

        ok = False
        try:
            log.debug(f"plugin {module_name} connecting")
            ok = plugin.connect(self.enlighten_info)
        except:
            log.critical("PluginWorker[%s] caught exception", exc_info=1)
            # retain exception trace so caller can display to script author
            self.error_message = traceback.format_exc()

        if not ok:
            self.error_message = plugin.error_message
            log.error(f"plugin {module_name} failed to connect (error_message = {self.error_message}")
            return

        log.debug(f"connected successfully")

        while True:
            time.sleep(0.01)

            if self.has_event_responses:
                try:
                    event_responses = plugin.get_event_responses()
                    if len(event_responses) > 0:
                        log.info(f"for event responses, got response list of {event_responses}")
                        for event in event_responses:
                            self.response_queue.put_nowait(event)
                    plugin.clear_event_responses()
                except Exception as e:
                    # If an error occurs default assume not implemented so stop trying
                    log.error(f"Error {e} trying to handle event responses, ignoring future attempts")
                    self.has_event_responses = False

            if self.request_queue.empty():
                continue

            request = self.request_queue.get_nowait()
            if request == None:
                log.critical("PluginWorker[%s] received poison-pill", module_name)
                plugin.disconnect()
                break

            # This is currently blocking on the response to each request.  This 
            # is probably the simplest behavior, but at some point we may want a
            # more complex model where, for instance, Responses may take several
            # seconds to complete, but multiple Requests can be
            # processed in parallel, such that:
            #
            #   (where A = request and B = response)
            #
            #    A1  A2  A3  A4  A5  A6  A7  A8...
            # t------------------------------------>
            #              B1  B2  B3  B4  B5  B6...
            #
            log.debug("PluginWorker[%s] sending request %d", module_name, request.request_id)
            response = None
            try:
                # make the following available to plugin utility functions (functional-api)
                plugin.settings = request.settings
                plugin.spectrum = request.processed_reading.get_processed()

                log.debug("about to call plugin's process request")
                response = plugin.process_request_obj(request)
            except:
                log.critical("PluginWorker[%s] caught exception processing request %d, closing",
                    module_name, request.request_id, exc_info=1)
                self.error_message = traceback.format_exc()
                shutdown = True

            if shutdown:
                # tell plugin to release any resources (assuming that plugin 
                # shutdown sequence blocks on this function call)
                plugin.disconnect() 

                # tell PluginController the worker thread is exiting
                self.response_queue.put_nowait(None)
                break

            log.debug("PluginWorker[%s] received response for request %d", module_name, response.request.request_id)
            self.response_queue.put_nowait(response)

        log.info("PluginWorker[%s] done", module_name)
