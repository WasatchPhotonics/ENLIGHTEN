import logging

log = logging.getLogger(__name__)

class LoggingFeature:

    def __init__(self,
            cb_verbose,
            config,
            level,
            queue):

        self.cb_verbose = cb_verbose
        self.config     = config
        self.level      = level
        self.queue      = queue

        self.cb_verbose.setVisible(True)

        self.cb_verbose.stateChanged.connect(self.verbose_callback)

        # if verbose logging was specified at the command-line OR 
        # previously set via .ini, use that
        if log.isEnabledFor(logging.DEBUG) or self.config.get_bool("logging", "verbose"):
            self.cb_verbose.setChecked(True)

    def verbose_callback(self):
        enabled = self.cb_verbose.isChecked()

        if enabled:
            log.info("enabling verbose logging")
            logging.getLogger().setLevel(logging.DEBUG)
            self.config.set("logging", "verbose", "True")
            self.level = "DEBUG"
        else:
            log.info("disabling verbose logging")
            logging.getLogger().setLevel(logging.INFO)
            self.config.set("logging", "verbose", "False")
            self.level = "INFO"
