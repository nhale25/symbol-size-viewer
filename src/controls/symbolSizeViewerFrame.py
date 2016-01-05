
import datetime
import os.path
import wx

from guiHelpers import Event
from symbolList import SymbolList
from colorKey import ColorKey
from objectFileSummary import ObjectFileSummary
from messagePanel import MessagePanel
from graphs import CodeTotalGraph, MemoryTotalGraph
from models.symbolTypes import CodeSymbol, RoDataSymbol, InitDataSymbol, UninitDataSymbol


def unknownBaseStringToInt(s):
    s = s.lower()
    if s.startswith("0x"):
        base = 16
    elif s.startswith("0b"):
        base = 2
    else:
        base = 10

    return int(s, base)


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
        numberFormatMenu = wx.Menu()
        self.menuItem_decimal = numberFormatMenu.Append(wx.ID_ANY, "Decimal", kind=wx.ITEM_RADIO)
        self.menuItem_hex = numberFormatMenu.Append(wx.ID_ANY, "Hexadecimal", kind=wx.ITEM_RADIO)
        self.Bind(wx.EVT_MENU, lambda e: self.prefsChangedEvent({"numberFormat":"decimal"}), self.menuItem_decimal)
        self.Bind(wx.EVT_MENU, lambda e: self.prefsChangedEvent({"numberFormat":"hex"}), self.menuItem_hex)

        viewMenu = wx.Menu()
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
        self._statusBar.SetStatusWidths([-1, 200])

        panel = wx.Panel(self)

        self.colorKey = ColorKey(panel)
        self.totalCode = CodeTotalGraph(panel)
        self.totalMemory = MemoryTotalGraph(panel)
        self.message = MessagePanel(None, panel)

        notebook = wx.Notebook(panel)
        self.summary = ObjectFileSummary(notebook)
        self.flashSymbolList = SymbolList(notebook)
        self.ramSymbolList = SymbolList(notebook)
        notebook.AddPage(self.summary, "Summary")
        notebook.AddPage(self.flashSymbolList, "Flash Symbols")
        notebook.AddPage(self.ramSymbolList, "RAM Symbols")

        self.txt_codeSize = wx.TextCtrl(panel, size=(80, -1))
        self.Bind(wx.EVT_TEXT, lambda e: self.prefsChangedEvent(
            {"totalFlashSize": self.txt_codeSize.GetValue()}), self.txt_codeSize)

        self.txt_memorySize = wx.TextCtrl(panel, size=(80, -1))
        self.Bind(wx.EVT_TEXT, lambda e: self.prefsChangedEvent(
            {"totalMemorySize": self.txt_memorySize.GetValue()}), self.txt_memorySize)

        hBox = wx.BoxSizer(wx.HORIZONTAL)
        hBox.AddMany([
            wx.StaticText(panel, label="Code size limit: "), self.txt_codeSize,
            ((10,1), 0), #spacer
            wx.StaticText(panel, label="Memory size limit: "), self.txt_memorySize,
            ((10,1), 0), #spacer
            ((1,1), 1), #expanding spacer
            self.colorKey,
        ])

        vBox = wx.BoxSizer(wx.VERTICAL)
        vBox.Add(hBox, 0, wx.EXPAND | wx.ALL, 4)
        vBox.Add(self.totalCode, 0, wx.EXPAND | wx.ALL, 4)
        vBox.Add(self.totalMemory, 0, wx.EXPAND | wx.ALL, 4)
        vBox.Add(self.message, 0, wx.EXPAND | wx.ALL, 4)
        vBox.Add(notebook, 1, wx.EXPAND | wx.ALL, 4)
        
        panel.SetSizerAndFit(vBox)
        self.Fit()
        vBox.SetSizeHints(self)
        

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

    def updateObjectFile(self, objectFile):
        symbols = objectFile.getSymbols()
        codeSymbols = [sym for sym in symbols if sym.basicType is CodeSymbol]
        initDataSymbols = [sym for sym in symbols if sym.basicType is InitDataSymbol]
        roDataSymbols = [sym for sym in symbols if sym.basicType is RoDataSymbol]
        uninitDataSymbols = [sym for sym in symbols if sym.basicType is UninitDataSymbol]

        roDataSize = sum([sym.size for sym in roDataSymbols])
        codeSize = objectFile.textSize - roDataSize

        self.summary.updateInfo(objectFile.textSize, roDataSize, objectFile.dataSize, objectFile.bssSize)
        self.flashSymbolList.updateSymbols(codeSymbols + initDataSymbols + roDataSymbols)
        self.ramSymbolList.updateSymbols(initDataSymbols + uninitDataSymbols)
        self.totalCode.setCategoryValues(codeSize, roDataSize, objectFile.dataSize)
        self.totalMemory.setCategoryValues(objectFile.dataSize, objectFile.bssSize)

        #update status bar
        now = datetime.datetime.now()
        lastLoadStr = now.strftime("Loaded at %H:%M:%S")
        self._statusBar.SetStatusText(objectFile.path, 0)
        self._statusBar.SetStatusText(lastLoadStr, 1)

        #update window title
        fileName = os.path.basename(objectFile.path)
        appName = wx.GetApp().GetAppName()
        self.SetTitle("%s - %s"% (fileName, appName))

    def setMessage(self, message):
        self.message.setMessage(message)

    def setNumberFormatter(self, formatter):
        self.totalCode.setNumberFormatter(formatter)
        self.totalMemory.setNumberFormatter(formatter)
        self.flashSymbolList.setNumberFormatter(formatter)
        self.ramSymbolList.setNumberFormatter(formatter)
        self.summary.setNumberFormatter(formatter)

    def setNumberFormatProperty(self, value):
        if value == "decimal":
            self.menuItem_decimal.Check(True)
        elif value == "hex":
            self.menuItem_hex.Check(True)

    def setTotalFlashSize(self, size):
        try:
            sizeNumber = unknownBaseStringToInt(size)
        except ValueError:
            sizeNumber = None

        self.totalCode.setLimit(sizeNumber)
        self.txt_codeSize.ChangeValue(size)

    def setTotalMemorySize(self, size):
        try:
            sizeNumber = unknownBaseStringToInt(size)
        except ValueError:
            sizeNumber = None

        self.totalMemory.setLimit(sizeNumber)
        self.txt_memorySize.ChangeValue(size)

    def setLastOpenedDirectory(self, dir):
        self._lastOpenedDirectory = dir

    def showColorKey(self, show):
        if show:
            self.colorKey.Show()
        else:
            self.colorKey.Hide()
        self.menuItem_showKey.Check(show)
        self.colorKey.GetParent().Layout()
