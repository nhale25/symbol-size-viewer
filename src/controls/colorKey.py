
import wx
from controls import defaultColors

class ColorKey(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        hBox = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(hBox)

        self._addColor(hBox, "Code", defaultColors["code"])
        self._addColor(hBox, "Read-only data", defaultColors["roData"])
        self._addColor(hBox, "Initialized data", defaultColors["initData"])

    def _addColor(self, sizer, name, color):
        panel = wx.Panel(self, size=(14, 14), style=wx.SIMPLE_BORDER)
        panel.SetBackgroundColour(color)
        sizer.Add(panel, 0, wx.RIGHT, 5)

        text = wx.StaticText(self, label=name)
        sizer.Add(text, 0, wx.RIGHT, 15)
