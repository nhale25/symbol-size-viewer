
# -*- coding: utf-8 -*-

import wx
from models.symbolTypes import CodeSymbol, RoDataSymbol, InitDataSymbol, UninitDataSymbol


class SummaryPanel(wx.Panel):
    def __init__(self, numberFormatter, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

        self._numberFormatter = numberFormatter
        self._valueWidgets = {}
        self._values = {}

        self._gridSizer = wx.FlexGridSizer(cols=3, hgap=5, vgap=10)
        box = wx.StaticBox(self, label=self._title)
        boxSizer = wx.StaticBoxSizer(box)
        boxSizer.Add(self._gridSizer, 0, wx.ALL, 10)

        for symbolType in self._symbols:
            self._addRow(box, symbolType, symbolType.description, symbolType.color)
        self._addRow(box, "total", "Total", None)

        self.SetSizer(boxSizer)
        boxSizer.Fit(self)

    def _addRow(self, parent, widgetKey, name, color):
        if color is not None:
            colorPanel = wx.Panel(parent, size=(14, 14), style=wx.SIMPLE_BORDER)
            colorPanel.SetBackgroundColour(color)
        else:
            colorPanel = (0, 0)

        valueWidget = wx.StaticText(parent, label="")
        self._valueWidgets[widgetKey] = valueWidget

        self._gridSizer.AddMany([
            (wx.StaticText(parent, label=name), 0, wx.ALIGN_RIGHT),
            (colorPanel, 0, wx.RIGHT, 20),
            (valueWidget, 0, wx.ALIGN_RIGHT),
        ])

    def _updateWidgets(self):
        for key, widget in self._valueWidgets.items():
            value = self._values.get(key)
            valueStr = self._numberFormatter(value) if value is not None else u"–"
            widget.SetLabel(valueStr)
        self.Layout()
        self.GetSizer().Fit(self)

    def updateData(self, *args):
        total = 0
        for symbolType, value in zip(self._symbols, args):
            if value is not None:
                total += value
            self._values[symbolType] = value
        self._values["total"] = total

        self._updateWidgets()

    def setNumberFormatter(self, formatter):
        self._numberFormatter = formatter
        self._updateWidgets()


class FlashSummaryPanel(SummaryPanel):
    _title = "Flash usage"
    _symbols = (CodeSymbol, RoDataSymbol, InitDataSymbol)


class RamSummaryPanel(SummaryPanel):
    _title = "RAM usage"
    _symbols = (InitDataSymbol, UninitDataSymbol)


class ObjectFileSummary(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        self._numberFormatter = lambda x: "%d"% x

        self._initUi()

    def _initUi(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddStretchSpacer(2)

        self._flashUsage = FlashSummaryPanel(self._numberFormatter, self)
        sizer.Add(self._flashUsage, 0, wx.ALIGN_CENTER | wx.ALL, 20)

        sizer.AddStretchSpacer(1)

        self._ramUsage = RamSummaryPanel(self._numberFormatter, self)
        sizer.Add(self._ramUsage, 0, wx.ALIGN_CENTER | wx.ALL, 20)

        sizer.AddStretchSpacer(2)
        self.SetSizer(sizer)
        sizer.Fit(self)

    def setNumberFormatter(self, formatter):
        self._numberFormatter = formatter
        self._flashUsage.setNumberFormatter(formatter)
        self._ramUsage.setNumberFormatter(formatter)

    def updateInfo(self, textSize, roDataSize, dataSize, bssSize):
        codeSize = textSize - roDataSize

        self._flashUsage.updateData(codeSize, roDataSize, dataSize)
        self._ramUsage.updateData(dataSize, bssSize)

    def clearInfo(self):
        self._flashUsage.updateData(0, 0, 0)
        self._ramUsage.updateData(0, 0)
