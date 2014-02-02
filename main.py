from models import binUtilsParsers
import locale
import os.path
import wx

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
		self._prefs.prefsChangedEvent.addHandler(self._onPrefsChanged)
		
		self._objectFile = ObjectFileModel()
		self._objectFile.fileChangedEvent.addHandler(lambda x, y: wx.CallAfter(self._onObjectFileChanged, x, y))
		
		self._mainWindow = SymbolSizeVisualiserFrame(self._prefs)
		self._mainWindow.openFileEvent.addHandler(self._onOpenObjectFile)
		self._mainWindow.prefsChangedEvent.addHandler(self._onPrefsDialogEdited)
		self._mainWindow.windowClosingEvent.addHandler(self._onAppClosing)
		
		self._prefs.loadFromFile(self._prefsFileLocation)
		
		if objectFileName is not None:
			self._onOpenObjectFile(objectFileName)
			
		self._mainWindow.Show()
	
	def _onOpenObjectFile(self, path):
		self._prefs.lastOpenedDirectory = os.path.dirname(path)
		self._mainWindow.setLastOpenedDirectory(self._prefs.lastOpenedDirectory) # shouldn't really be doing this here
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
		
		print binUtilsParsers.NmParser.prettyPrintSymbolList(symbolInfo)
		self._mainWindow.updateObjectFile(sizeInfo, codeSymbols, initDataSymbols, roDataSymbols, objectFile.path)
	
	def _onPrefsChanged(self, prefs):
		formatter = self.numberFormatters.get(prefs.numberFormat, self.numberFormatters["decimal"])
		self._mainWindow.setNumberFormatter(formatter)
		self._mainWindow.setTotalFlashSize(prefs.totalFlashSize)
		self._mainWindow.setLastOpenedDirectory(prefs.lastOpenedDirectory)
		
		self._objectFile.setNmExeLocation(prefs.nmExeLocation)
		self._objectFile.setSizeExeLocation(prefs.sizeExeLocation)
		self._objectFile.setWatchFileFileForChanges(self._prefs.watchFileForChanges)
	
	def _onPrefsDialogEdited(self, prefs):
		for k, v in prefs.items():
			setattr(self._prefs, k, v)
		self._prefs.prefsChangedEvent(self._prefs)
	
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
