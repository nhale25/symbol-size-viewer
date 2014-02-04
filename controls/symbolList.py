
import wx
import wx.lib.agw.ultimatelistctrl as ULC
import wx.lib.mixins.listctrl as listmix

from memUsageGauge import MemUsageGauge
from guiHelpers import Event

class SymbolList(ULC.UltimateListCtrl, listmix.ListCtrlAutoWidthMixin, listmix.ColumnSorterMixin):
	symbolTypeNames = {
		"code":"Code",
		"initialized":"Initialised data",
		"readOnly":"Read-only data",
		}
	
	def __init__(self, *args, **kwargs):
		kwargs["agwStyle"] = wx.LC_REPORT | wx.LC_VRULES | wx.LC_HRULES | wx.LC_SINGLE_SEL | ULC.ULC_NO_HIGHLIGHT | ULC.ULC_HAS_VARIABLE_ROW_HEIGHT
		ULC.UltimateListCtrl.__init__(self, *args, **kwargs)
		listmix.ListCtrlAutoWidthMixin.__init__(self)
		listmix.ColumnSorterMixin.__init__(self, 4)
		self.itemDataMap = {}
		
		self._numberFormatter = lambda x: "%d"% x
		
		self.InsertColumn(0, "Symbol name", width=150)
		self.InsertColumn(1, "Type", width=100)
		self.InsertColumn(2, "Size", width=50)
		self.InsertColumn(3, "")
		self.setResizeColumn(4)
	
	def setNumberFormatter(self, formatter):
		self._numberFormatter = formatter
		
		for pos in range(self.GetItemCount()):
			obj = self.GetItemData(pos)
			sizeStr = self._numberFormatter(obj.size)
			self.SetStringItem(pos, 1, sizeStr)
	
	def _addRow(self, symbol, largestSymbolSize, symbolType):
		pos = self.InsertStringItem(0, symbol.name)
		self.SetItemData(pos, symbol)
		self.itemDataMap[symbol] = (symbol.name, symbolType, symbol.size, symbol.size)
		
		typeStr = self.symbolTypeNames[symbolType]
		self.SetStringItem(pos, 1, typeStr)
		
		sizeStr = self._numberFormatter(symbol.size)
		self.SetStringItem(pos, 2, sizeStr)
		
		gauge = MemUsageGauge(self, wx.ID_ANY, style=wx.GA_HORIZONTAL, size=(-1, 20))
		gauge.SetCapacity(largestSymbolSize)
		gauge.SetSizes(**{symbolType:symbol.size})
		self.SetItemWindow(pos, col=3, wnd=gauge, expand=True)
	
	def updateInfo(self, codeSymbols, initDataSymbols, roDataSymbols):
		#workaround for bug in certain versions of UltimateListCtrl when calling DeleteAllItems()
		for item in self._mainWin._itemWithWindow[:]:
			if item.GetWindow():
				self._mainWin.DeleteItemWindow(item)
		#end of workaround
		
		self.itemDataMap = {}
		self.DeleteAllItems()
		
		if codeSymbols is not None and initDataSymbols is not None and roDataSymbols is not None:
			largest = max([obj.size for obj in codeSymbols + initDataSymbols + roDataSymbols])
			for sym in codeSymbols:
				self._addRow(sym, largest, "code")
			for sym in initDataSymbols:
				self._addRow(sym, largest, "initialized")
			for sym in roDataSymbols:
				self._addRow(sym, largest, "readOnly")
			
			self.SortListItems(2, False)
			
	#Required by listmix.ColumnSorterMixin
	def GetListCtrl(self):
		return self
	
	#Required by listmix.ColumnSorterMixin
	def OnSortOrderChanged(self):
		self.Refresh()
	
	def GetSecondarySortValues(self, col, key1, key2):
		#If sorting by name or symbol type, secondary sort should always be by size, and descending
		if col == 0 or col == 1:
			value1 = self.itemDataMap[key1][2]
			value2 = self.itemDataMap[key2][2]
			
			_, dirn = self.GetSortState()
			if dirn:
				return (value2, value1)
			else:
				return (value1, value2)
		else:
			return listmix.ColumnSorterMixin.GetSecondarySortValues(self, col, key1, key2)
			
