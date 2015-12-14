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
            textYPos = (rect.height-textHeight)/2

            if textHeight > rect.height:
                textYPos = 0-descent+extraLeading
            textXPos = (rect.width-textWidth)/2
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
        self._total = None
        self._numberFormatter = lambda x: "%d"% x
        self._limit = None

    def _generateText(self):
        if not self._total:
            return ""

        totalSizeFormatted = self._numberFormatter(self._total)
        if self._limit is None:
            return "%s%s bytes"% (self._label, totalSizeFormatted)
        else:
            percent = (float(self._total) * 100) / self._limit
            limitSizeFormatted = self._numberFormatter(self._limit)
            return "%s%s of %s bytes (%d%%)"% (self._label, totalSizeFormatted, limitSizeFormatted, percent)

    def _updateText(self):
        text = self._generateText()
        self.SetText(text)

    def _updateColors(self):
        if not self._total:
            return

        if self._total > self._limit and self._limit is not None:
            self.SetBarColors(dict((name, self._overflowColor) for name, _ in self._categories))
        else:
            self.SetBarColors(dict((name, color) for name, color in self._categories))

    def setNumberFormatter(self, formatter):
        self._numberFormatter = formatter
        self._updateText()
        self.Refresh()

    def setLimit(self, limit):
        self._limit = limit

        if self._total > self._limit or self._limit is None:
            self.SetRange(self._total if self._total else 1)
        else:
            self.SetRange(self._limit)

        self._updateColors()
        self._updateText()
        self.Refresh()

    def setCategoryValues(self, *values):
        if values is None:
            self._total = None
            self.SetValue(0)

        else:
            self._total = sum(values)
            if self._total > self._limit:
                self.SetRange(self._total)

            namedValues = dict((name, value) for (name, _), value in zip(self._categories, values))
            self.SetValues(namedValues)

        self._updateColors()
        self._updateText()
        self.Refresh()


class CodeTotalGraph(TotalGraph):
    _label = "Code size: "
    _categories = (
        ("text", CodeSymbol.color),
        ("roData", RoDataSymbol.color),
        ("initData", InitDataSymbol.color),
    )


class MemoryTotalGraph(TotalGraph):
    _label = "Memory used: "
    _categories = (
        ("initData", InitDataSymbol.color),
        ("uninitData", UninitDataSymbol.color),
    )