
import locale
import os.path
import logging

import wx

from controls.prefsDialog import PrefsDialog
from controls.symbolSizeViewerFrame import SymbolSizeViewerFrame

from models.objectFile import ObjectFile
from models.fileWatcher import FileWatcher
from models.prefsModel import PrefsModel
from models.binUtilsOutputFiles import ParseError
from guiHelpers import Event, getRelativePath

logger = logging.getLogger(__name__)


class SymbolSizeViewer(object):
    numberFormatters = {
        "decimal": lambda x: locale.format_string("%d", x, grouping=True),
        "hex": lambda x: "0x%x"% x,
        }

    ICON_FILE = getRelativePath(__file__, "../icon.png")
    CONFIG_FILENAME = "config"

    def __init__(self, app, objectFileName=None):
        app.SetAppName("Symbol Size Viewer")

        locale.setlocale(locale.LC_ALL, "")

        paths = wx.StandardPaths.Get()
        self._prefsFileLocation = os.path.join(paths.GetUserDataDir(), self.CONFIG_FILENAME)
        logger.info(f"Loading prefs from: {self._prefsFileLocation}")

        self._prefs = PrefsModel()
        self._prefs.prefsChangedEvent.addHandler(self._onPrefsModelChanged)

        self._fileWatcher = FileWatcher(lambda *args: wx.CallAfter(self._onObjectFileChanged, *args))

        self._mainWindow = SymbolSizeViewerFrame()
        self._mainWindow.openFileEvent.addHandler(self._onOpenObjectFile)
        self._mainWindow.prefsChangedEvent.addHandler(self._onPrefsChanged)
        self._mainWindow.openPrefsDialogEvent.addHandler(self._onOpenPrefsDialog)
        self._mainWindow.windowClosingEvent.addHandler(self._onAppClosing)
        self._mainWindow.SetIcon(wx.Icon(self.ICON_FILE, wx.BITMAP_TYPE_PNG))

        self._prefs.loadFromFile(self._prefsFileLocation)

        if objectFileName is not None:
            self._onOpenObjectFile(os.path.abspath(objectFileName))
        elif self._prefs["reopenLastFile"].get():
            lastFile = self._prefs["lastOpenedFile"].get()
            if lastFile:
                self._onOpenObjectFile(os.path.abspath(lastFile))

        self._mainWindow.Show()

    def _onOpenObjectFile(self, path):
        if os.path.isfile(path):
            self._fileWatcher.setFileToWatch(path)
            self._prefs.set("lastOpenedFile", path)
            self._onObjectFileChanged(path, True)
        else:
            self._mainWindow.setMessage(path + " not found")

    def _onObjectFileChanged(self, path, stillExists):
        logger.info(f"loading object file: {path}")
        if not stillExists:
            #Input file has been deleted, don't clear out the data, nobody wants that
            self._mainWindow.setMessage(path + " not found")
            return

        try:
            objectFile = ObjectFile(
                self._prefs["sizeExeLocation"].get(),
                self._prefs["nmExeLocation"].get(),
                path
            )
        except Exception as e:
            self._mainWindow.setMessage(str(e))
        else:
            self._mainWindow.setMessage(None)
            self._mainWindow.updateObjectFile(objectFile)

    def _onPrefsModelChanged(self, prefs):
        prefs = self._prefs

        formatValue = prefs["numberFormat"].get()
        self._mainWindow.setNumberFormatProperty(formatValue)
        formatter = self.numberFormatters.get(formatValue, self.numberFormatters["decimal"])
        self._mainWindow.setNumberFormatter(formatter)

        self._mainWindow.setTotalFlashSize(prefs["totalFlashSize"].get())
        self._mainWindow.setTotalMemorySize(prefs["totalMemorySize"].get())
        lastOpenedFile = prefs["lastOpenedFile"].get()
        if lastOpenedFile:
            self._mainWindow.setLastOpenedDirectory(os.path.dirname(lastOpenedFile))

        if prefs["watchFileForChanges"].get():
            self._fileWatcher.startWatching()
        else:
            self._fileWatcher.stopWatching()

    def _onOpenPrefsDialog(self):
        prefsDialog = PrefsDialog(self._prefs.getAll())
        if prefsDialog.ShowModal() == wx.ID_OK:
            self._onPrefsChanged(prefsDialog.getPreferences())
        prefsDialog.Destroy()

    def _onPrefsChanged(self, changed):
        for name, value in changed.items():
            self._prefs.set(name, value)

    def _onAppClosing(self):
        self._prefs.saveToFile(self._prefsFileLocation)
        self._fileWatcher.stopWatching()


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO)

    if len(sys.argv) > 1:
        objectFile = sys.argv[1]
    else:
        objectFile = None

    app = wx.App()
    gui = SymbolSizeViewer(app, objectFile)
    app.MainLoop()
