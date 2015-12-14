
import wx
from models.symbolTypes import CodeSymbol, RoDataSymbol, InitDataSymbol, UninitDataSymbol

class ColorKey(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        hBox = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(hBox)

        for symbolType in (CodeSymbol, RoDataSymbol, InitDataSymbol, UninitDataSymbol):
            self._addColor(hBox, symbolType.description, symbolType.color)

    def _addColor(self, sizer, name, color):
        panel = wx.Panel(self, size=(14, 14), style=wx.SIMPLE_BORDER)
        panel.SetBackgroundColour(color)
        sizer.Add(panel, 0, wx.RIGHT, 5)

        text = wx.StaticText(self, label=name)
        sizer.Add(text, 0, wx.RIGHT, 15)
