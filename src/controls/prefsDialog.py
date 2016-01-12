
import wx
from wx.lib.sized_controls import SizedDialog
from guiHelpers import Event


class PrefsDialog(SizedDialog):
    def __init__(self, prefs):
        style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER
        SizedDialog.__init__(self, None, title="Preferences", style=style)

        panel = self.GetContentsPane()
        panel.SetSizerType("form")

        label = wx.StaticText(panel, label="Location of nm executable:")
        label.SetSizerProps(valign="center")
        self.txt_nmExeLoc = wx.TextCtrl(panel, size=(200, -1))

        label = wx.StaticText(panel, label="Location of size executable:")
        label.SetSizerProps(valign="center")
        self.txt_sizeExeLoc = wx.TextCtrl(panel, size=(200, -1))

        label = wx.StaticText(panel, label="Watch input file for changes:")
        label.SetSizerProps(valign="center")
        self.chk_autoUpdate = wx.CheckBox(panel)

        buttons = self.CreateSeparatedButtonSizer(wx.OK | wx.CANCEL)
        self.SetButtonSizer(buttons)

        #load initial values
        self.txt_nmExeLoc.SetValue(prefs["nmExeLocation"].getAsString())
        self.txt_sizeExeLoc.SetValue(prefs["sizeExeLocation"].getAsString())
        self.chk_autoUpdate.SetValue(prefs["watchFileForChanges"].get())

        self.Fit()

    def getPreferences(self):
        return {
            "nmExeLocation": self.txt_nmExeLoc.GetValue(),
            "sizeExeLocation": self.txt_sizeExeLoc.GetValue(),
            "watchFileForChanges": self.chk_autoUpdate.GetValue()
        }
