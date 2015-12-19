
import locale
import os.path
import wx

from controls.prefsDialog import PrefsDialog
from controls.symbolSizeViewerFrame import SymbolSizeViewerFrame

from models.objectFile import ObjectFile
from models.fileWatcher import FileWatcher
from models.prefsModel import PrefsModel
from models.binUtilsOutputFiles import ParseError
from guiHelpers import Event, getRelativePath


class SymbolSizeViewer(object):
    numberFormatters = {
        "decimal": lambda x: locale.format("%d", x, grouping=True),
        "hex": lambda x: "0x%x"% x,
        }

    ICON_FILE = getRelativePath(__file__, "../icon.png")
    CONFIG_FILENAME = "config"

    def __init__(self, app, objectFileName=None):
        app.SetAppName("Symbol Size Viewer")

        paths = wx.StandardPaths.Get()
        self._prefsFileLocation = os.path.join(paths.GetUserDataDir(), self.CONFIG_FILENAME)

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
            self._onOpenObjectFile(objectFileName)

        self._mainWindow.Show()

    def _onOpenObjectFile(self, path):
        self._fileWatcher.setFileToWatch(path)
        self._prefs.set("lastOpenedDirectory", os.path.dirname(path))
        self._onObjectFileChanged(path, True)

    def _onObjectFileChanged(self, path, stillExists):
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
        except ParseError as e:
            self._mainWindow.setMessage(e.message)
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
        self._mainWindow.setLastOpenedDirectory(prefs["lastOpenedDirectory"].get())
        self._mainWindow.showColorKey(prefs["showColorKey"].get())

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

    if len(sys.argv) > 1:
        objectFile = sys.argv[1]
    else:
        objectFile = None

    app = wx.App()
    gui = SymbolSizeViewer(app, objectFile)
    app.MainLoop()
