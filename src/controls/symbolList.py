
import wx
import wx.lib.agw.ultimatelistctrl as ULC
import wx.lib.mixins.listctrl as listmix
from wx.lib.agw.pygauge import PyGauge

from graphs import StackedPyGaugeWithText
from controls import defaultColors
from guiHelpers import Event

class SymbolList(ULC.UltimateListCtrl, listmix.ListCtrlAutoWidthMixin, listmix.ColumnSorterMixin):
    symbolTypeNames = {
        "code":"Code",
        "initData":"Initialised data",
        "roData":"Read-only data",
        }

    COL_NAME = 0
    COL_TYPE = 1
    COL_SIZE = 2
    COL_GRAPH = 3

    def __init__(self, *args, **kwargs):
        kwargs["agwStyle"] = wx.LC_REPORT | wx.LC_VRULES | wx.LC_HRULES | wx.LC_SINGLE_SEL | ULC.ULC_NO_HIGHLIGHT | ULC.ULC_HAS_VARIABLE_ROW_HEIGHT
        ULC.UltimateListCtrl.__init__(self, *args, **kwargs)
        listmix.ListCtrlAutoWidthMixin.__init__(self)
        listmix.ColumnSorterMixin.__init__(self, 4)
        self.itemDataMap = {}

        self._numberFormatter = lambda x: "%d"% x

        self.InsertColumn(self.COL_NAME, "Symbol name", width=150)
        self.InsertColumn(self.COL_TYPE, "Type", width=100)
        self.InsertColumn(self.COL_SIZE, "Size", width=50)
        self.InsertColumn(self.COL_GRAPH, "")
        self.setResizeColumn(self.COL_GRAPH + 1)

        #hack: Make self redraw properly when on a tabbed notebook with certain wxPython versions.
        self.GetParent().Bind(
            wx.EVT_NOTEBOOK_PAGE_CHANGED,
            lambda e: wx.CallAfter(self.SendSizeEvent) and e.Skip()
            )
        #end hack

    def setNumberFormatter(self, formatter):
        self._numberFormatter = formatter

        for pos in range(self.GetItemCount()):
            obj = self.GetItemData(pos)
            sizeStr = self._numberFormatter(obj.size)
            self.SetStringItem(pos, self.COL_SIZE, sizeStr)

    def _addRow(self, symbol, largestSymbolSize, symbolType):
        pos = self.InsertStringItem(self.GetItemCount(), symbol.name)
        self.SetItemData(pos, symbol)
        self.itemDataMap[symbol] = (symbol.name.lower(), symbolType, symbol.size, symbol.size)

        typeStr = self.symbolTypeNames[symbolType]
        self.SetStringItem(pos, self.COL_TYPE, typeStr)

        sizeStr = self._numberFormatter(symbol.size)
        self.SetStringItem(pos, self.COL_SIZE, sizeStr)

        gauge = PyGauge(self, wx.ID_ANY, style=wx.GA_HORIZONTAL | wx.SUNKEN_BORDER, size=(-1, 20))
        gauge.SetRange(largestSymbolSize)
        gauge.SetBarColor(defaultColors[symbolType])
        gauge.SetValue(symbol.size)
        self.SetItemWindow(pos, col=self.COL_GRAPH, wnd=gauge, expand=True)

    def updateInfo(self, codeSymbols, initDataSymbols, roDataSymbols):
        previousSort = self.GetSortState()

        #workaround for bug in certain versions of UltimateListCtrl when calling DeleteAllItems()
        for item in self._mainWin._itemWithWindow[:]:
            if item.GetWindow():
                self._mainWin.DeleteItemWindow(item)
        #end of workaround

        self.itemDataMap = {}
        self.DeleteAllItems()

        if codeSymbols or initDataSymbols or roDataSymbols:
            largest = max([obj.size for obj in codeSymbols + initDataSymbols + roDataSymbols])
            for sym in codeSymbols:
                self._addRow(sym, largest, "code")
            for sym in initDataSymbols:
                self._addRow(sym, largest, "initData")
            for sym in roDataSymbols:
                self._addRow(sym, largest, "roData")

            if previousSort == (-1, 0): #Hasn't been sorted yet
                previousSort = (self.COL_SIZE, False)
            self.SortListItems(*previousSort)

    #Required by listmix.ColumnSorterMixin
    def GetListCtrl(self):
        return self

    #Required by listmix.ColumnSorterMixin
    def OnSortOrderChanged(self):
        self.Refresh()

    def GetSecondarySortValues(self, col, key1, key2):
        #If sorting by name or symbol type, secondary sort should always be by size, and descending
        if col == self.COL_NAME or col == self.COL_TYPE:
            value1 = self.itemDataMap[key1][2]
            value2 = self.itemDataMap[key2][2]

            _, dirn = self.GetSortState()
            if dirn:
                return (value2, value1)
            else:
                return (value1, value2)
        else:
            return listmix.ColumnSorterMixin.GetSecondarySortValues(self, col, key1, key2)

    #this version contains the fix for including/not-including the width of the scrollbar
    def _doResize(self):
        """ Resize the last column as appropriate.

            If the list's columns are too wide to fit within the window, we use
            a horizontal scrollbar.  Otherwise, we expand the right-most column
            to take up the remaining free space in the list.

            We remember the current size of the last column, before resizing,
            as the preferred minimum width if we haven't previously been given
            or calculated a minimum width.  This ensure that repeated calls to
            _doResize() don't cause the last column to size itself too large.
        """

        if not self:  # avoid a PyDeadObject error
            return

        if self.GetSize().height < 32:
            return  # avoid an endless update bug when the height is small.

        numCols = self.GetColumnCount()
        if numCols == 0: return # Nothing to resize.

        if(self._resizeColStyle == "LAST"):
            resizeCol = self.GetColumnCount()
        else:
            resizeCol = self._resizeCol

        resizeCol = max(1, resizeCol)

        if self._resizeColMinWidth == None:
            self._resizeColMinWidth = self.GetColumnWidth(resizeCol - 1)

        # We're showing the vertical scrollbar -> allow for scrollbar width
        # NOTE: on GTK, the scrollbar is included in the client size, but on
        # Windows it is not included
        listWidth = self.GetClientSize().width
        if wx.Platform != '__WXMSW__':
            if self.GetItemCount() > self.GetCountPerPage():
                scrollWidth = wx.SystemSettings_GetMetric(wx.SYS_VSCROLL_X)
                listWidth = listWidth - scrollWidth

        totColWidth = 0 # Width of all columns except last one.
        for col in range(numCols):
            if col != (resizeCol-1):
                totColWidth = totColWidth + self.GetColumnWidth(col)

        resizeColWidth = self.GetColumnWidth(resizeCol - 1)

        if totColWidth + self._resizeColMinWidth > listWidth:
            # We haven't got the width to show the last column at its minimum
            # width -> set it to its minimum width and allow the horizontal
            # scrollbar to show.
            self.SetColumnWidth(resizeCol-1, self._resizeColMinWidth)
            return

        # Resize the last column to take up the remaining available space.

        self.SetColumnWidth(resizeCol-1, listWidth - totColWidth)
