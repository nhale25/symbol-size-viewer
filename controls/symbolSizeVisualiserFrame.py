
import datetime
import wx

from guiHelpers import Event
from objectList import ObjectList
from prefsDialog import PrefsDialog
from totalFlashUsage import TotalFlashUsage
from colorKey import ColorKey

class SymbolSizeVisualiserFrame(wx.Frame):
	def __init__(self, prefs, *args, **kwds):
		kwds["title"] = wx.GetApp().GetAppName()
		wx.Frame.__init__(self, None, *args, **kwds)
		self._prefs = prefs
		self.openFileEvent = Event()
		self.prefsChangedEvent = Event()
		self.windowClosingEvent = Event()
		
		self.initUi()

	def initUi(self):
		self.Bind(wx.EVT_CLOSE, self._onClose)
		
		menuBar = wx.MenuBar()
		fileMenu = wx.Menu()
		menuItem_Open = fileMenu.Append(wx.ID_OPEN)
		self.Bind(wx.EVT_MENU, self._onOpen, menuItem_Open)
		fileMenu.AppendSeparator()
		menuItem_Exit = fileMenu.Append(wx.ID_EXIT)
		self.Bind(wx.EVT_MENU, self._onClose, menuItem_Exit)
		menuBar.Append(fileMenu, "File")
		prefsMenu = wx.Menu()
		menuItem_Prefs = prefsMenu.Append(wx.ID_PREFERENCES)
		self.Bind(wx.EVT_MENU, self._onShowPrefs, menuItem_Prefs)
		menuBar.Append(prefsMenu, "Preferences")
		self.SetMenuBar(menuBar)
		
		self._statusBar = self.CreateStatusBar(2)
		
		panel = wx.Panel(self)
		self.colorKey = ColorKey(panel)
		self.totalFlash = TotalFlashUsage(panel)
		self.objectList = ObjectList(panel)
		
		vBox = wx.BoxSizer(wx.VERTICAL)
		vBox.Add(self.colorKey, 0, wx.ALL | wx.ALIGN_RIGHT, 4)
		vBox.Add(self.totalFlash, 0, wx.EXPAND | wx.ALL, 4)
		vBox.Add(self.objectList, 1, wx.EXPAND | wx.ALL, 4)
		panel.SetSizer(vBox)
	
	def _onClose(self, event):
		self.Destroy()
		self.windowClosingEvent()
	
	def _onShowPrefs(self, event):
		prefsDialog = PrefsDialog(self._prefs)
		if prefsDialog.ShowModal() == wx.ID_OK:
			newPrefs = {
				"nmExeLocation": prefsDialog.txt_nmExeLoc.GetValue(),
				"sizeExeLocation": prefsDialog.txt_sizeExeLoc.GetValue(),
				"totalFlashSizeStr": prefsDialog.txt_flashSize.GetValue(),
				"numberFormat": "decimal" if prefsDialog.rb_sizeDec.GetValue() else "hex",
				"watchFileForChanges": prefsDialog.chk_autoUpdate.GetValue()
				}
			self.prefsChangedEvent(newPrefs)
		prefsDialog.Destroy()
	
	def _onOpen(self, event):
		openFileDialog = wx.FileDialog(self, "Open ELF file", self._lastOpenedDirectory, "",
                                       "ELF files (*.elf)|*.elf|All files|*", 
                                       wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
		if openFileDialog.ShowModal() == wx.ID_OK:
			path = openFileDialog.GetPath()
			self.openFileEvent(path)
	
	def updateObjectFile(self, sizeInfo, codeSymbols, initDataSymbols, roDataSymbols, path):
		roDataSize = sum([sym.size for sym in roDataSymbols])
		self.totalFlash.updateInfo(sizeInfo, roDataSize)
		self.objectList.updateInfo(codeSymbols, initDataSymbols, roDataSymbols)
		
		now = datetime.datetime.now()
		lastLoadStr = now.strftime("Loaded at %H:%M:%S")
		self._statusBar.SetStatusText(path, 0)
		self._statusBar.SetStatusText(lastLoadStr, 1)
	
	def setNumberFormatter(self, formatter):
		self.totalFlash.setNumberFormatter(formatter)
		self.objectList.setNumberFormatter(formatter)
	
	def setTotalFlashSize(self, size):
		self.totalFlash.setTotalFlashSize(size)
	
	def setLastOpenedDirectory(self, dir):
		self._lastOpenedDirectory = dir
