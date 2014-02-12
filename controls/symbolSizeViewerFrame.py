
import datetime
import os.path
import wx

from guiHelpers import Event
from symbolList import SymbolList
from totalFlashUsage import TotalFlashUsage
from colorKey import ColorKey
from objectFileSummary import ObjectFileSummary

class SymbolSizeViewerFrame(wx.Frame):
	def __init__(self, *args, **kwds):
		kwds["title"] = wx.GetApp().GetAppName()
		wx.Frame.__init__(self, None, *args, **kwds)
		
		self.openFileEvent = Event()
		self.prefsChangedEvent = Event()
		self.openPrefsDialogEvent = Event()
		self.windowClosingEvent = Event()
		
		self._initUi()
	
	def _initMenu(self):
		menuBar = wx.MenuBar()
		self.SetMenuBar(menuBar)
		
		#file menu
		fileMenu = wx.Menu()
		menuItem_Open = fileMenu.Append(wx.ID_OPEN)
		self.Bind(wx.EVT_MENU, self._onOpen, menuItem_Open)
		fileMenu.AppendSeparator()
		menuItem_Exit = fileMenu.Append(wx.ID_EXIT)
		self.Bind(wx.EVT_MENU, self._onClose, menuItem_Exit)
		menuBar.Append(fileMenu, "File")
		
		#view menu
		viewMenu = wx.Menu()
		numberFormatMenu = wx.Menu()
		self.menuItem_decimal = numberFormatMenu.Append(wx.ID_ANY, "Decimal", kind=wx.ITEM_RADIO)
		self.menuItem_hex = numberFormatMenu.Append(wx.ID_ANY, "Hex", kind=wx.ITEM_RADIO)
		self.Bind(wx.EVT_MENU, lambda e: self.prefsChangedEvent({"numberFormat":"decimal"}), self.menuItem_decimal)
		self.Bind(wx.EVT_MENU, lambda e: self.prefsChangedEvent({"numberFormat":"hex"}), self.menuItem_hex)
		viewMenu.AppendMenu(wx.ID_ANY, "Number format", numberFormatMenu)
		self.menuItem_showKey = viewMenu.Append(wx.ID_ANY, "Show colour key", kind=wx.ITEM_CHECK)
		self.Bind(wx.EVT_MENU, lambda e: self.prefsChangedEvent({"showColorKey":self.menuItem_showKey.IsChecked()}), self.menuItem_showKey)
		menuBar.Append(viewMenu, "View")
		
		#preferences menu
		prefsMenu = wx.Menu()
		menuItem_Prefs = prefsMenu.Append(wx.ID_PREFERENCES)
		self.Bind(wx.EVT_MENU, lambda e: self.openPrefsDialogEvent(), menuItem_Prefs)
		menuBar.Append(prefsMenu, "Preferences")
		
	def _initUi(self):
		self._initMenu()
		self.Bind(wx.EVT_CLOSE, self._onClose)
		self._statusBar = self.CreateStatusBar(2)
		
		panel = wx.Panel(self)
		self.colorKey = ColorKey(panel)
		self.totalFlash = TotalFlashUsage(panel)
		
		notebook = wx.Notebook(panel)
		self.summary = ObjectFileSummary(notebook)
		self.symbolList = SymbolList(notebook)
		notebook.AddPage(self.summary, "Summary")
		notebook.AddPage(self.symbolList, "Symbols")
		
		vBox = wx.BoxSizer(wx.VERTICAL)
		vBox.Add(self.colorKey, 0, wx.ALL | wx.ALIGN_RIGHT, 4)
		vBox.Add(self.totalFlash, 0, wx.EXPAND | wx.ALL, 4)
		vBox.Add(notebook, 1, wx.EXPAND | wx.ALL, 4)
		panel.SetSizer(vBox)
	
	def _onClose(self, event):
		self.Destroy()
		self.windowClosingEvent()
	
	def _onOpen(self, event):
		openFileDialog = wx.FileDialog(self, "Open ELF file", self._lastOpenedDirectory, "",
                                       "Object files (*.elf; *.o)|*.elf;*.o|All files|*", 
                                       wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
		if openFileDialog.ShowModal() == wx.ID_OK:
			path = openFileDialog.GetPath()
			self.openFileEvent(path)
	
	def updateObjectFile(self, sizeInfo, codeSymbols, initDataSymbols, roDataSymbols, path):
		roDataSize = sum([sym.size for sym in roDataSymbols])
		self.totalFlash.updateInfo(sizeInfo, roDataSize)
		self.summary.updateInfo(sizeInfo, codeSymbols, roDataSymbols)
		self.symbolList.updateInfo(codeSymbols, initDataSymbols, roDataSymbols)
		
		now = datetime.datetime.now()
		lastLoadStr = now.strftime("Loaded at %H:%M:%S")
		self._statusBar.SetStatusText(path, 0)
		self._statusBar.SetStatusText(lastLoadStr, 1)
		
		fileName = os.path.basename(path)
		appName = wx.GetApp().GetAppName()
		self.SetTitle("%s - %s"% (fileName, appName))
	
	def setNumberFormatter(self, formatter):
		self.totalFlash.setNumberFormatter(formatter)
		self.symbolList.setNumberFormatter(formatter)
		self.summary.setNumberFormatter(formatter)
	
	def setNumberFormatProperty(self, value):
		if value == "decimal":
			self.menuItem_decimal.Check(True)
		elif value == "hex":
			self.menuItem_hex.Check(True)
	
	def setTotalFlashSize(self, size):
		self.totalFlash.setTotalFlashSize(size)
	
	def setLastOpenedDirectory(self, dir):
		self._lastOpenedDirectory = dir
	
	def showColorKey(self, show):
		if show:
			self.colorKey.Show()
		else:
			self.colorKey.Hide()
		self.menuItem_showKey.Check(show)
		self.colorKey.GetParent().Layout()
