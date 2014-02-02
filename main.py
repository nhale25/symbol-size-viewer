from models import binUtilsParsers
import locale
import os.path
import wx

from controls.prefsDialog import PrefsDialog
from controls.symbolSizeVisualiserFrame import SymbolSizeVisualiserFrame
from models.objectFileModel import ObjectFileModel
from models.prefsModel import PrefsModel
from guiHelpers import Event

class FlashUsageAnalyserGui(object):
	numberFormatters = {
		"decimal": lambda x: locale.format("%d", x, grouping=True),
		"hex": lambda x: "0x%x"% x,
		}
	
	def __init__(self, app, objectFileName=None):
		paths = wx.StandardPaths.Get()
		self._prefsFileLocation = os.path.join(paths.GetUserDataDir(), "config")
		
		self._prefs = PrefsModel()
		self._prefs.prefsChangedEvent.addHandler(self._onPrefsModelChanged)
		
		self._objectFile = ObjectFileModel()
		self._objectFile.fileChangedEvent.addHandler(lambda x, y: wx.CallAfter(self._onObjectFileChanged, x, y))
		
		self._mainWindow = SymbolSizeVisualiserFrame()
		self._mainWindow.openFileEvent.addHandler(self._onOpenObjectFile)
		self._mainWindow.prefsChangedEvent.addHandler(self._onPrefsChanged)
		self._mainWindow.openPrefsDialogEvent.addHandler(self._onOpenPrefsDialog)
		self._mainWindow.windowClosingEvent.addHandler(self._onAppClosing)
		
		self._prefs.loadFromFile(self._prefsFileLocation)
		
		if objectFileName is not None:
			self._onOpenObjectFile(objectFileName)
			
		self._mainWindow.Show()
	
	def _onOpenObjectFile(self, path):
		self._prefs.set("lastOpenedDirectory", os.path.dirname(path))
		self._objectFile.setFile(path)
	
	def _onObjectFileChanged(self, objectFile, stillExists):
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
		elfFile = sys.argv[1]
	else:
		elfFile = None
	
	app = wx.App()
	app.SetAppName("Symbol Size Visualiser")
	gui = FlashUsageAnalyserGui(app, elfFile)
	app.MainLoop() 
