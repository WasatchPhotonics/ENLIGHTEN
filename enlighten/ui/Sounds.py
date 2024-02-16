import logging
import time
import os

log = logging.getLogger(__name__)

# import audio library where available
try:
    import winsound 
    HAVE_SOUND = True
except ImportError:
    print("winsound library not found - audio disabled")
    HAVE_SOUND = False

class Sounds:
    """
    Encapsulates ENLIGHTEN's limited audio capabilities.
    
    @note At this time, we only support sound on Windows 
    @todo Allow user sound overrides in EnlightenSpectra/sounds (basename = event)
    """
    PATH = "enlighten/assets/example_data/sounds"

    def clear(self):
        for name in self.sounds:
            self.sounds[name].parent = None
        self.sounds = None
    
    def __init__(self, ctl):
        self.ctl = ctl
        cfu = ctl.form.ui

        self.cb_enable = cfu.checkBox_sound_enable

        self.sounds = {}
        self.enabled = False
        self.last_sound_name = None

        # Enforce at least this much time between playing of sequential sounds.
        # Extra sound events requested within this interval are DISCARDED, NOT QUEUED.
        self.min_interval_sec = 3

        # find all supported audio files
        log.debug(f"searching for sounds in {self.PATH}")
        for root, _, files in os.walk(self.PATH):
            for filename in sorted(files):
                name, ext = os.path.splitext(filename)
                ext = ext[1:] # trim period
                if ext in ["wav", "flac", "m4a", "mp3", "aiff"]:
                    pathname = os.path.join(root, filename)
                    name = name.lower()
                    self.sounds[name] = Sound(pathname, parent=self)
                    log.debug(f"found sound {name} -> {pathname}")

        # bindings
        self.cb_enable.stateChanged.connect(self.enable_callback)
        self.cb_enable.setWhatsThis("Some users like sound effects. Who knew?\n\n" +
                                    "(Also, some laser safety protocols may require " +
                                    "audible as well as visual feedback of potentially " +
                                    "hazardous events.)")

        # initialization
        self.cb_enable.setChecked(self.ctl.config.get_bool("sound", "enable"))

    def enable_callback(self):
        self.enabled = self.cb_enable.isChecked()
        self.ctl.config.set("sound", "enable", self.enabled)

    def is_enabled(self):
        return HAVE_SOUND and self.enabled

    def get(self, name):
        if name in self.sounds:
            return self.sounds[name]
        return None

    def stop(self):
        if not self.is_enabled():
            return
        winsound.PlaySound(None, winsound.SND_PURGE)

    def reset_repeat(self):  # MZ: used?
        self.last_sound_name = None

    def play(self, name, repeat=True):
        if not self.is_enabled():
            return

        if self.last_sound_name is not None and self.last_sound_name == name:
            if not repeat:
                log.debug(f"declining to repeat {name}")
                return

        self.stop()

        if name.lower() in self.sounds:
            self.sounds[name.lower()].playAsync()
        elif name.lower() == "asterisk":
            winsound.PlaySound('SystemAsterisk', winsound.SND_ALIAS)
        elif name.lower() == "question":
            winsound.PlaySound('SystemQuestion', winsound.SND_ALIAS)
        elif name.lower() == "exclamation":
            winsound.PlaySound('SystemExclamation', winsound.SND_ALIAS)
        else:
            log.warn("unknown sound %s", name)
            return

        self.last_sound_name  = name

class Sound:
    """
    A single playable sound (.wav file, etc)
    
    This has a parent-reference to Sounds so that an individual sounds will know 
    if the overall sound-system is enabled.
    """
    def __del__(self):
        del self.parent
        del self.pathname

    def __init__(self, pathname, parent=None):
        self.pathname = pathname
        self.parent = parent

    def is_enabled(self):
        return HAVE_SOUND and self.parent and self.parent.enabled

    def play(self, mask=None):
        if not self.is_enabled():
            log.debug("silencing %s", self.pathname)
            return

        if mask is None:
            mask = winsound.SND_FILENAME

        log.debug("playing %s", self.pathname)
        try:
            winsound.PlaySound(self.pathname, mask)
        except:
            log.error("Can't play %s", self.pathname, exc_info=1)

    def playAsync(self):
        if not self.is_enabled():
            log.debug("silencing %s", self.pathname)
            return

        log.debug("playing async %s", self.pathname)
        self.play(winsound.SND_FILENAME | winsound.SND_ASYNC)
