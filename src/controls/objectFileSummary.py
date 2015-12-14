
import wx
from models.symbolTypes import CodeSymbol, RoDataSymbol, InitDataSymbol, UninitDataSymbol

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

        self._addRow(grid, centeredPanel, CodeSymbol.color, "Code", self._widgets["code"])
        self._addRow(grid, centeredPanel, RoDataSymbol.color, "Read-only data", self._widgets["roData"])
        self._addRow(grid, centeredPanel, InitDataSymbol.color, "Initialised data", self._widgets["initData"])
        self._addRow(grid, centeredPanel, None, "Total", self._widgets["programTotal"])
        self._addRow(grid, centeredPanel, None, "", (0,0))
        self._addRow(grid, centeredPanel, InitDataSymbol.color, "Initialised data", self._widgets["initData2"])
        self._addRow(grid, centeredPanel, UninitDataSymbol.color, "Uninitialised data", self._widgets["uninitData"])
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

    def updateInfo(self, textSize, roDataSize, dataSize, bssSize):
        codeSize = textSize - roDataSize

        self._values["code"] = codeSize
        self._values["roData"] = roDataSize
        self._values["initData"] = dataSize
        self._values["programTotal"] = textSize + dataSize

        self._values["initData2"] = dataSize
        self._values["uninitData"] = bssSize
        self._values["ramTotal"] = dataSize + bssSize

        self._dataValid = True
        self._updateWidgets()

    def clearInfo(self):
        self._dataValid = False
        self._updateWidgets()
