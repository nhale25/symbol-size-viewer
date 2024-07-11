
from configparser import ConfigParser
from guiHelpers import Event
import os
import os.path
import errno
import logging

logger = logging.getLogger(__name__)


class PrefsHelpers:

    @staticmethod
    def stringToPath(string):
        return string #FIXME: do something about backslashes on windows, maybe?

    @staticmethod
    def stringToBool(string):
        return string.lower() in ["true", "t", "yes", "y", "1"]

class Preference(object):
    def __init__(self, default, formatter=str):
        self._value = default
        self._default = default
        self._formatter = formatter

    def set(self, value):
        self._value = str(value)

    def getAsString(self):
        return self._value

    def get(self):
        return self._formatter(self._value)

class PrefsModel:
    def __init__(self, fileName=None):
        self._prefs = {
            "nmExeLocation": 		Preference("", PrefsHelpers.stringToPath),
            "sizeExeLocation":		Preference("", PrefsHelpers.stringToPath),
            "numberFormat": 		Preference("decimal"),
            "totalFlashSize": 		Preference(""),
            "totalMemorySize": 		Preference(""),
            "lastOpenedFile":       Preference("", PrefsHelpers.stringToPath),
            "watchFileForChanges":	Preference("true", PrefsHelpers.stringToBool),
            "reopenLastFile": 		Preference("true", PrefsHelpers.stringToBool),
        }

        self.prefsChangedEvent = Event()

        if fileName is not None:
            self.loadFromFile(fileName)

    def __getitem__(self, key):
        return self._prefs[key]

    def __setitem__(self, key, value):
        self._prefs[key].set(value)

    def get(self, name):
        return self._prefs[name]

    def getAll(self):
        return self._prefs

    def set(self, name, value):
        self.setMany({name: value})

    def setMany(self, dictionary):
        for name, value in dictionary.items():
            self._prefs[name].set(value)

        changed = dict([(name, self._prefs[name]) for name in dictionary.keys()])
        self.prefsChangedEvent(changed)

    def loadFromFile(self, fileName):
        config = ConfigParser()

        try:
            with open(fileName) as f:
                config.readfp(f)

            for name, pref in self._prefs.items():
                value = config.get("DEFAULT", name)
                pref.set(value)

            self.prefsChangedEvent(self._prefs)

        except Exception as e:
            logger.warning(f"Failed reading config file: {e}")

    def saveToFile(self, fileName):
        config = ConfigParser()
        for name, pref in self._prefs.items():
            value = pref.getAsString()
            config.set("DEFAULT", name, value)

        try:
            os.makedirs(os.path.dirname(fileName))
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

        with open(fileName, "w") as f:
            config.write(f)
