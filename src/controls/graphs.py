import wx
from wx.lib.agw.pygauge import PyGauge

from models.symbolTypes import CodeSymbol, RoDataSymbol, InitDataSymbol, UninitDataSymbol

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
            textYPos = (rect.height-textHeight)//2

            if textHeight > rect.height:
                textYPos = 0-descent+extraLeading
            textXPos = (rect.width-textWidth)//2
            if textWidth>rect.width:
                textXPos = 0

            dc.DrawText(self._text, textXPos, textYPos)


class TotalGraph(StackedPyGaugeWithText):
    _label = ""
    _categories = ()
    _overflowColor = "#cc0000"

    def __init__(self, *args, **kwargs):
        kwargs["style"] = kwargs.get("style", 0) | wx.SUNKEN_BORDER
        barNames = [category[0] for category in self._categories]
        StackedPyGaugeWithText.__init__(self, barNames, *args, **kwargs)

        self.SetBarColors(dict((name, color) for name, color in self._categories))
        self._numberFormatter = lambda x: "%d"% x
        self._limit = None
        self._values = []

    def _getText(self):
        if not self._values:
            return ""

        total = sum(self._values)
        totalSizeFormatted = self._numberFormatter(total)
        if not self._limit:
            return "%s%s bytes"% (self._label, totalSizeFormatted)
        else:
            percent = (float(total) * 100) / self._limit
            limitSizeFormatted = self._numberFormatter(self._limit)
            return "%s%s of %s bytes (%d%%)"% (self._label, totalSizeFormatted, limitSizeFormatted, percent)

    def setNumberFormatter(self, formatter):
        self._numberFormatter = formatter
        self.SetText(self._getText())
        self.Refresh()

    def setLimit(self, limit):
        self._limit = limit
        self._redraw()
    
    def setCategoryValues(self, *values):
        self._values = values
        self._redraw()
    
    def _redraw(self):
        total = sum(self._values)

        # maybe about to reduce the range, so ensure the value will always be
        # less than the new range. Value will be updated again afterwards.
        self.SetValue(0)

        if not self._values:
            self.SetRange(1)

        elif self._limit and total > self._limit:
            self.SetRange(total)
            self.SetValue(total)
            self.SetBarColors(dict((name, self._overflowColor) for name, _ in self._categories))
        
        else:
            self.SetRange(self._limit if self._limit else total)
            namedValues = dict((name, value) for (name, _), value in zip(self._categories, self._values))
            self.SetValues(namedValues)
            self.SetBarColors(dict((name, color) for name, color in self._categories))

        self.SetText(self._getText())
        self.Refresh()


class CodeTotalGraph(TotalGraph):
    _label = "Flash used: "
    _categories = (
        ("text", CodeSymbol.color),
        ("roData", RoDataSymbol.color),
        ("initData", InitDataSymbol.color),
    )


class MemoryTotalGraph(TotalGraph):
    _label = "RAM used: "
    _categories = (
        ("initData", InitDataSymbol.color),
        ("uninitData", UninitDataSymbol.color),
    )
