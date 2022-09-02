
from contextlib import contextmanager
import wx
from wx.lib.sized_controls import SizedDialog
from guiHelpers import Event


class PrefsDialog(SizedDialog):
    def __init__(self, prefs):
        style = wx.DEFAULT_DIALOG_STYLE
        SizedDialog.__init__(self, None, title="Preferences", style=style)

        panel = self.GetContentsPane()
        panel.SetSizerType("form")

        self.txt_nmExeLoc = self._addControl(panel,
            "Location of nm executable:",
            wx.TextCtrl, size=(200, -1))

        self.txt_sizeExeLoc = self._addControl(panel,
            "Location of size executable:",
            wx.TextCtrl, size=(200, -1))

        self.chk_autoUpdate = self._addControl(panel,
            "Watch input file for changes:",
            wx.CheckBox)

        self.chk_reopenLastFile = self._addControl(panel,
            "Reopen last file at startup:",
            wx.CheckBox)

        buttons = self.CreateSeparatedButtonSizer(wx.OK | wx.CANCEL)
        self.SetButtonSizer(buttons)

        #load initial values
        self.txt_nmExeLoc.SetValue(prefs["nmExeLocation"].getAsString())
        self.txt_sizeExeLoc.SetValue(prefs["sizeExeLocation"].getAsString())
        self.chk_autoUpdate.SetValue(prefs["watchFileForChanges"].get())
        self.chk_reopenLastFile.SetValue(prefs["reopenLastFile"].get())

        self.Fit()

    def _addControl(self, parent, caption, widgetType, *widgetArgs, **widgetKwargs):
        label = wx.StaticText(parent, label=caption)
        label.SetSizerProps(valign="center")

        widget = widgetType(parent, *widgetArgs, **widgetKwargs)
        widget.SetSizerProps(expand=True, valign="center")
        return widget

    def getPreferences(self):
        return {
            "nmExeLocation": self.txt_nmExeLoc.GetValue(),
            "sizeExeLocation": self.txt_sizeExeLoc.GetValue(),
            "watchFileForChanges": self.chk_autoUpdate.GetValue(),
            "reopenLastFile": self.chk_reopenLastFile.GetValue(),
        }
