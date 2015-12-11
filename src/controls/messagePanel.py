
import wx

class MessagePanel(wx.Panel):
    def __init__(self, message, *args, **kwargs):
        kwargs["style"] = kwargs.get("style", 0) | wx.SIMPLE_BORDER
        wx.Panel.__init__(self, *args, **kwargs)
        self.text = wx.StaticText(self)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.text, 0, wx.ALL | wx.ALIGN_CENTER, 2)
        self.SetSizer(vbox)

        self.setMessage(message)

    def setMessage(self, message):
        if message is None:
            self.Hide()

        else:
            self.text.SetLabel(message)
            self.Show()
        self.GetParent().Layout()