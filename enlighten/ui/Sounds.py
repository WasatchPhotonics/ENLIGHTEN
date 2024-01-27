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

##
# Encapsulates ENLIGHTEN's limited audio capabilities.
#
# @note At this time, we only support sound on Windows 
class Sounds:

    ##
    # This prevents uncollectable garbage
    def clear(self):
        for name in self.sounds:
            self.sounds[name].parent = None
        self.sounds = None
    
    def __init__(self, 
            checkbox,
            config,
            path):

        self.checkbox = checkbox
        self.config   = config
        self.path     = path

        self.sounds = {}
        self.enabled = False
        self.last_sound_name = None
        self.last_sound_start = None

        # Enforce at least this much time between playing of sequential sounds.
        # Extra sound events requested within this interval are DISCARDED, NOT QUEUED.
        self.min_interval_sec = 3

        # find all supported audio files
        log.debug("searching for sounds in %s", path)
        for root, dirs, files in os.walk(path):
            for filename in files:
                name, ext = os.path.splitext(filename)
                ext = ext[1:] # trim period
                # log.debug("examining %s [%s]", name, ext)
                # MZ: had trouble with ethanol.aiff and .mp3
                if ext in ["wav", "flac", "m4a", "mp3", "aiff"]:
                    pathname = os.path.join(root, filename)
                    name = name.lower()
                    self.sounds[name] = Sound(pathname, parent=self)
                    # log.debug("found %s -> %s", name, pathname)

        # bindings
        checkbox.stateChanged.connect(self.checkbox_callback)

        # initialization
        checkbox.setChecked(self.config.get("sound", "enable").lower() == "true")

    def checkbox_callback(self):
        self.enabled = self.checkbox.isChecked()
        self.config.set("sound", "enable", self.enabled)

    def is_enabled(self):
        return HAVE_SOUND and self.enabled

    def get(self, name):
        if name in self.sounds:
            return self.sounds[name]
        return None

    def getNames(self):
        names = list(self.sounds.keys())
        names.extend(["asterisk", "question", "exclamation"])
        return list(sorted(set(names)))

    def stop(self):
        if not self.is_enabled():
            return
        winsound.PlaySound(None, winsound.SND_PURGE)

    def reset_repeat(self):
        log.debug("Sound.reset_repeat")
        self.last_sound_name = None

    def play(self, name, repeat=True):
        if not self.is_enabled():
            log.debug("silencing %s", name)
            return

        if self.last_sound_start is not None:
            now = time.time()
            interval_sec = abs(int(now - self.last_sound_start))
            if interval_sec < self.min_interval_sec:
                log.debug("too soon for new sound %s (last was %s at %s, only %d sec)", name, self.last_sound_name, self.last_sound_start, interval_sec)
                return
            else:
                log.debug("okay to start new sound (now %s is %d sec after %s)", now, interval_sec, self.last_sound_start)
        else:
            log.debug("first sound")

        if self.last_sound_name is not None and self.last_sound_name == name:
            if not repeat:
                log.debug("not repeating %s", name)
                return
            else:
                log.debug("okay to repeat %s", name)
        else:
            log.debug("not a repeat %s (last was %s)", name, self.last_sound_name)

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
            log.error("unknown sound %s", name)
            return

        self.last_sound_name  = name
        self.last_sound_start = time.time()

    def playAll(self):
        for filename in self.getNames():
            sound = self.sounds[filename]
            sound.play()

##
# A single playable sound (.wav file, etc)
#
# This has a parent-reference to Sounds so that an individual sounds will know 
# if the overall sound-system is enabled.
class Sound:
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
