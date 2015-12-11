
import wx
from wx.lib.agw.pygauge import PyGauge
from controls import defaultColors

class StackedPyGaugeWithText(PyGauge):
    def __init__(self, barNames, *args, **kwargs):
        kwargs["style"] = kwargs.get("style", 0) | wx.FULL_REPAINT_ON_RESIZE
        PyGauge.__init__(self, *args, **kwargs)

        self._barNames = barNames
        self._barValues = [0] * len(barNames)
        self._barColors = [wx.BLACK] * len(barNames)
        self._text = ""

    def SetBarColors(self, colorDict):
        for name, color in colorDict.items():
            idx = self._barNames.index(name)
            self._barColors[idx] = color
        PyGauge.SetBarColor(self, self._barColors)

    def SetValues(self, valueDict):
        for name, value in valueDict.items():
            idx = self._barNames.index(name)
            self._barValues[idx] = value

        values = []
        total = 0
        for value in self._barValues:
            if value:
                total += value
                values.append(total)
            else:
                values.append(0)
        PyGauge.SetValue(self, values)

    def SetText(self, text):
        self._text = text

    def OnPaint(self, event):
        PyGauge.OnPaint(self, event)

        if self._text:
            dc = wx.BufferedPaintDC(self)
            dc.SetFont(wx.NORMAL_FONT)
            dc.SetTextForeground(wx.BLACK)
            rect = self.GetClientRect()
            (textWidth, textHeight, descent, extraLeading) = dc.GetFullTextExtent(self._text)
            textYPos = (rect.height-textHeight)/2

            if textHeight > rect.height:
                textYPos = 0-descent+extraLeading
            textXPos = (rect.width-textWidth)/2
            if textWidth>rect.width:
                textXPos = 0

            dc.DrawText(self._text, textXPos, textYPos)

class MemUsageGauge(StackedPyGaugeWithText):
    def __init__(self, *args, **kwargs):
        kwargs["style"] = kwargs.get("style", 0) | wx.SUNKEN_BORDER
        barNames = ["text", "roData", "initData"]
        StackedPyGaugeWithText.__init__(self, barNames, *args, **kwargs)

        self._colors = {
            "text": defaultColors["code"],
            "roData": defaultColors["roData"],
            "initData": defaultColors["initData"],
            }
        self._fullColor = defaultColors["flashFull"]

        self._values = {
            "text": 0,
            "roData": 0,
            "initData": 0,
            }
        self._capacity = 0

    def SetCapacity(self, capacity):
        self._capacity = capacity
        self.SetRange(capacity)
        self._updateBars()

    def SetSizes(self, code=0, readOnly=0, initialized=0):
        self._values["text"] = code
        self._values["roData"] = readOnly
        self._values["initData"] = initialized
        self._updateBars()

    def SetText(self, text):
        StackedPyGaugeWithText.SetText(self, text)
        self.Refresh()

    def _updateBars(self):
        totalSize = sum(self._values.values())
        if totalSize > self._capacity:
            self.SetBarColor(self._fullColor)
            self.SetValue(self._capacity)

        else:
            self.SetBarColors(self._colors)
            self.SetValues(self._values)
        self.Refresh()