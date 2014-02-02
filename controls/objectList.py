
import wx
import wx.lib.agw.ultimatelistctrl as ULC
from memUsageGauge import MemUsageGauge
from guiHelpers import Event

class ObjectList(wx.Panel):
	def __init__(self, *args, **kwargs):
		wx.Panel.__init__(self, *args, **kwargs)
		self._numberFormatter = lambda x: "%d"% x
		
		self._listCtrl = ULC.UltimateListCtrl(self, wx.ID_ANY,
							agwStyle=wx.LC_REPORT | wx.LC_VRULES | wx.LC_HRULES | wx.LC_SINGLE_SEL | ULC.ULC_NO_HIGHLIGHT | ULC.ULC_HAS_VARIABLE_ROW_HEIGHT)
		self._listCtrl.InsertColumn(0, "Symbol name", width=200)
		self._listCtrl.InsertColumn(1, "Size", width=50)
		self._listCtrl.InsertColumn(2, "", width=200)
		
		sizer = wx.BoxSizer()
		sizer.Add(self._listCtrl, 1, wx.EXPAND)
		self.SetSizer(sizer)
	
	def setNumberFormatter(self, formatter):
		self._numberFormatter = formatter
		
		for pos in range(self._listCtrl.GetItemCount()):
			obj = self._listCtrl.GetItemData(pos)
			sizeStr = self._numberFormatter(obj.size)
			self._listCtrl.SetStringItem(pos, 1, sizeStr)
	
	def _addRow(self, symbol, largestSymbolSize, symbolType):
		pos = self._listCtrl.InsertStringItem(0, symbol.name)
		self._listCtrl.SetItemData(pos, symbol)
		
		sizeStr = self._numberFormatter(symbol.size)
		self._listCtrl.SetStringItem(pos, 1, sizeStr)
		
		gauge = MemUsageGauge(self._listCtrl, wx.ID_ANY, style=wx.GA_HORIZONTAL, size=(-1, 20))
		gauge.SetCapacity(largestSymbolSize)
		gauge.SetSizes(**{symbolType:symbol.size})
		self._listCtrl.SetItemWindow(pos, col=2, wnd=gauge, expand=True)
	
	def updateInfo(self, codeSymbols, initDataSymbols, roDataSymbols):
		for pos in range(self._listCtrl.GetItemCount()):
			self._listCtrl.DeleteItemWindow(pos, 2)
		self._listCtrl.DeleteAllItems()
		
		if codeSymbols is not None and initDataSymbols is not None and roDataSymbols is not None:
			largest = max([obj.size for obj in codeSymbols + initDataSymbols + roDataSymbols])
			for sym in codeSymbols:
				self._addRow(sym, largest, "code")
			for sym in initDataSymbols:
				self._addRow(sym, largest, "initialized")
			for sym in roDataSymbols:
				self._addRow(sym, largest, "readOnly")
			
			self._listCtrl.SortItems(lambda x, y: y.size - x.size)
