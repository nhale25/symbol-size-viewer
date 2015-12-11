
import wx
from controls import defaultColors

class ObjectFileSummary(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        self._numberFormatter = lambda x: "%d"% x

        self._dataValid = False
        self._values = {
            "code": 0,
            "roData": 0,
            "initData": 0,
            "initData2": 0,
            "uninitData": 0,
            "programTotal": 0,
            "ramTotal": 0,
            }

        self._initUi()

    def _initUi(self):
        centeredPanel = wx.Panel(self)
        grid = wx.FlexGridSizer(cols=3, hgap=5, vgap=10)
        self._grid = grid
        self._widgets = {
            "code": wx.StaticText(centeredPanel, label=""),
            "roData": wx.StaticText(centeredPanel, label=""),
            "initData": wx.StaticText(centeredPanel, label=""),
            "initData2": wx.StaticText(centeredPanel, label=""),
            "uninitData": wx.StaticText(centeredPanel, label=""),
            "programTotal": wx.StaticText(centeredPanel, label=""),
            "ramTotal": wx.StaticText(centeredPanel, label=""),
            }

        self._addRow(grid, centeredPanel, defaultColors["code"], "Code", self._widgets["code"])
        self._addRow(grid, centeredPanel, defaultColors["roData"], "Read-only data", self._widgets["roData"])
        self._addRow(grid, centeredPanel, defaultColors["initData"], "Initialised data", self._widgets["initData"])
        self._addRow(grid, centeredPanel, None, "Total", self._widgets["programTotal"])
        self._addRow(grid, centeredPanel, None, "", (0,0))
        self._addRow(grid, centeredPanel, defaultColors["initData"], "Initialised data", self._widgets["initData2"])
        self._addRow(grid, centeredPanel, defaultColors["uninitData"], "Uninitialised data", self._widgets["uninitData"])
        self._addRow(grid, centeredPanel, None, "Total", self._widgets["ramTotal"])

        centeredPanel.SetSizer(grid)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddStretchSpacer(1)
        sizer.Add(centeredPanel, 0, wx.ALIGN_CENTER)
        sizer.AddStretchSpacer(1)
        self.SetSizer(sizer)

    def _addRow(self, grid, parent, color, label, valueWidget):
        if color is not None:
            colorPanel = wx.Panel(parent, size=(14, 14), style=wx.SIMPLE_BORDER)
            colorPanel.SetBackgroundColour(color)
        else:
            colorPanel = (0, 0)

        grid.AddMany([
            (wx.StaticText(parent, label=label), 0, wx.ALIGN_RIGHT),
            (colorPanel, 0, wx.RIGHT, 20),
            (valueWidget, 0, wx.ALIGN_RIGHT),
            ])

    def _updateWidgets(self):
        for name, widget in self._widgets.items():
            if self._dataValid:
                newValue = self._numberFormatter(self._values[name])
            else:
                newValue = ""
            widget.SetLabel(newValue)
        self.Layout()

    def setNumberFormatter(self, formatter):
        self._numberFormatter = formatter
        self._updateWidgets()

    def updateInfo(self, sizeInfo, codeSymbols, roDataSymbols):
        if sizeInfo is None:
            self.clearInfo()
            return

        roDataSum = sum([sym.size for sym in roDataSymbols])

        self._values["code"] = sizeInfo.text - roDataSum
        self._values["roData"] = roDataSum
        self._values["initData"] = sizeInfo.data
        self._values["programTotal"] = sizeInfo.text + sizeInfo.data

        self._values["initData2"] = sizeInfo.data
        self._values["uninitData"] = sizeInfo.bss
        self._values["ramTotal"] = sizeInfo.data + sizeInfo.bss

        self._dataValid = True
        self._updateWidgets()

    def clearInfo(self):
        self._dataValid = False
        self._updateWidgets()
