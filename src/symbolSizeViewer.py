from models import binUtilsParsers
import locale
import os.path
import wx

from controls.prefsDialog import PrefsDialog
from controls.symbolSizeViewerFrame import SymbolSizeViewerFrame
from models.objectFileModel import ObjectFileModel
from models.prefsModel import PrefsModel
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
		
		self._objectFile = ObjectFileModel()
		self._objectFile.fileChangedEvent.addHandler(lambda x, y: wx.CallAfter(self._onObjectFileChanged, x, y))
		
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
		self._prefs.set("lastOpenedDirectory", os.path.dirname(path))
		self._objectFile.setFile(path)
	
	def _onObjectFileChanged(self, objectFile, stillExists):
		if not stillExists:
			#Input file has been deleted, don't clear out the data, nobody wants that
			return
		
		try:
			sizeInfo = objectFile.getSizeInfo()
		except ValueError as e:
			print e
			sizeInfo = None
		
		try:
			symbolInfo = objectFile.getSymbolInfo()
		except ValueError as e:
			print e
			symbolInfo = None
			
		if symbolInfo:
			codeSymbols = [sym for sym in symbolInfo if sym.type.code.lower() in "t"]
			initDataSymbols = [sym for sym in symbolInfo if sym.type.code.lower() in "gd"]
			roDataSymbols = [sym for sym in symbolInfo if sym.type.code.lower() in "r"]
		else:
			codeSymbols = None
			initDataSymbols = None
			roDataSymbols = None
		
		self._mainWindow.updateObjectFile(sizeInfo, codeSymbols, initDataSymbols, roDataSymbols, objectFile.path)
	
	def _onPrefsModelChanged(self, prefs):
		prefs = self._prefs
		
		formatValue = prefs["numberFormat"].get()
		self._mainWindow.setNumberFormatProperty(formatValue)
		formatter = self.numberFormatters.get(formatValue, self.numberFormatters["decimal"])
		self._mainWindow.setNumberFormatter(formatter)
		
		self._mainWindow.setTotalFlashSize(prefs["totalFlashSize"].get())
		self._mainWindow.setLastOpenedDirectory(prefs["lastOpenedDirectory"].get())
		self._mainWindow.showColorKey(prefs["showColorKey"].get())
		
		self._objectFile.setNmExeLocation(prefs["nmExeLocation"].get())
		self._objectFile.setSizeExeLocation(prefs["sizeExeLocation"].get())
		self._objectFile.setWatchFileFileForChanges(prefs["watchFileForChanges"].get())
	
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
		self._objectFile.setWatchFileFileForChanges(False)

if __name__ == "__main__":
	import sys
	
	if len(sys.argv) > 1:
		objectFile = sys.argv[1]
	else:
		objectFile = None
	
	app = wx.App()
	gui = SymbolSizeViewer(app, objectFile)
	app.MainLoop() 
