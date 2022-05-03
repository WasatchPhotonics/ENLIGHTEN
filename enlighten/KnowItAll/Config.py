import logging
import json
import os

from .. import common

log = logging.getLogger(__name__)

## Configuration of the KnowItAll module.
#
# Tracks aliases, benigns, hazards and suppressed compound names.
#
# Note that KIA compound names may include single- and double-quotes, 
# apostrophes, backticks, Greek, TM symbols and who-knows-what-else, so hopefully
# the JSON module does a good job of quoting unicode.
#
class Config(object):
    def __init__(self, pathname=None):
        self.pathname = pathname

        self.aliases = {}
        self.unalias = {}
        self.benigns = set()
        self.hazards = set()
        self.suppressed = set()
        self.external = {}

        self.load()

    def get_pathname(self):
        if self.pathname is None:
            self.pathname = os.path.join(common.get_default_data_dir(), "KnowItAll.json")
        return self.pathname

    def load(self):
        pathname = self.get_pathname()
        if not os.path.exists(pathname):
            log.error("Not found: %s", pathname)
            return

        try:
            with open(pathname, encoding='utf-8') as infile:
                text = infile.read()
        except:
            log.info("not found: %s", pathname, exc_info=1)
            return False

        log.info("parsing JSON: %s", pathname)
        try:
            config = json.loads(text)
        except:
            log.error("error parsing %s\n%s", pathname, text, exc_info=1)
            return False

        log.debug("json: %s", text)
        if "aliases" in config:
            try:
                for orig in config["aliases"]:
                    alias = config["aliases"][orig]
                    self.aliases[orig] = alias
                    if alias not in self.unalias:
                        self.unalias[alias] = orig
                    else:
                        log.error("KIAConfig.load: both %s and %s are aliased to %s, making reverse lookups impossible",
                            orig, self.unalias[alias], alias)
            except:
                log.error("error parsing %s: corrupt aliases dict", exc_info=1)

        if "benigns" in config:
            try:
                self.benigns = set(config["benigns"])
            except:
                log.error("error parsing %s: corrupt benigns set", exc_info=1)

        self.hazards = set()
        if "hazards" in config:
            try:
                self.hazards = set(config["hazards"])
            except:
                log.error("error parsing %s: corrupt hazards set", exc_info=1)

        self.suppressed = set()
        if "suppressed" in config:
            try:
                self.suppressed = set(config["suppressed"])
            except:
                log.error("error parsing %s: corrupt suppressed set", exc_info=1)

        if "external" in config:
            self.external = config["external"]

        return True

    def save(self):
        pathname = self.get_pathname()
        try:
            with open(pathname, "w", encoding='utf-8') as outfile:
                log.debug("saving %s", pathname)
                text = json.dumps( 
                    { 
                        "aliases": self.aliases, 
                        "benigns": list(self.benigns), 
                        "hazards": list(self.hazards),
                        "suppressed": list(self.suppressed),
                        "external": self.external
                    }, 
                    sort_keys=True, 
                    indent=4)
                outfile.write(text)
        except:
            log.critical("failed to write %s", pathname, exc_info=1)

