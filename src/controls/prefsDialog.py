
import os

import wx
from wx.lib.sized_controls import SizedDialog


class PrefsDialog(SizedDialog):
    def __init__(self, prefs):
        style = wx.DEFAULT_DIALOG_STYLE | wx.CLOSE_BOX | wx.RESIZE_BORDER
        SizedDialog.__init__(self, None, title="Preferences", style=style)

        panel = self.GetContentsPane()
        panel.SetSizerType("grid", {"rows":4, "cols":3})

        label = wx.StaticText(panel, label="Location of nm executable:")
        label.SetSizerProps(valign="center")
        self.txt_nmExeLoc = wx.TextCtrl(panel, size=(200, -1))
        self.txt_nmExeLoc.SetSizerProps(expand=True, valign="center")
        self.btn_nmExeLoc = wx.Button(panel, id=wx.ID_OPEN)
        self.btn_nmExeLoc.Bind(wx.EVT_BUTTON, self._onOpenNmExe)

        label = wx.StaticText(panel, label="Location of size executable:")
        label.SetSizerProps(valign="center")
        self.txt_sizeExeLoc = wx.TextCtrl(panel, size=(200, -1))
        self.txt_sizeExeLoc.SetSizerProps(expand=True, valign="center")
        self.btn_sizeExeLoc = wx.Button(panel, id=wx.ID_OPEN)
        self.btn_sizeExeLoc.Bind(wx.EVT_BUTTON, self._onOpenSizeExe)

        label = wx.StaticText(panel, label="Watch input file for changes:")
        label.SetSizerProps(valign="center")
        self.chk_autoUpdate = wx.CheckBox(panel)
        self.chk_autoUpdate.SetSizerProps(expand=True, valign="center")
        blank = wx.StaticText(panel, label="") #for spacing

        label = wx.StaticText(panel, label="Reopen last file at startup:")
        label.SetSizerProps(valign="center")
        self.chk_reopenLastFile = wx.CheckBox(panel)
        self.chk_reopenLastFile.SetSizerProps(expand=True, valign="center")
        blank = wx.StaticText(panel, label="") #for spacing

        buttons = self.CreateSeparatedButtonSizer(wx.OK | wx.CANCEL)
        self.SetButtonSizer(buttons)

        #load initial values
        self.txt_nmExeLoc.SetValue(prefs["nmExeLocation"].getAsString())
        self.txt_sizeExeLoc.SetValue(prefs["sizeExeLocation"].getAsString())
        self.chk_autoUpdate.SetValue(prefs["watchFileForChanges"].get())
        self.chk_reopenLastFile.SetValue(prefs["reopenLastFile"].get())

        self.Fit()
    
    def _onOpenNmExe(self, event):
        currentLoc = self.txt_nmExeLoc.GetValue()
        currentDir, currentFile = os.path.split(currentLoc)
        openFileDialog = wx.FileDialog(self, "Select 'nm' executable", currentDir, currentFile,
                                       style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if openFileDialog.ShowModal() == wx.ID_OK:
            path = openFileDialog.GetPath()
            self.txt_nmExeLoc.SetValue(path)
    
    def _onOpenSizeExe(self, event):
        currentLoc = self.txt_sizeExeLoc.GetValue()
        currentDir, currentFile = os.path.split(currentLoc)
        openFileDialog = wx.FileDialog(self, "Select 'size' executable", currentDir, currentFile,
                                       style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if openFileDialog.ShowModal() == wx.ID_OK:
            path = openFileDialog.GetPath()
            self.txt_sizeExeLoc.SetValue(path)

    def getPreferences(self):
        return {
            "nmExeLocation": self.txt_nmExeLoc.GetValue(),
            "sizeExeLocation": self.txt_sizeExeLoc.GetValue(),
            "watchFileForChanges": self.chk_autoUpdate.GetValue(),
            "reopenLastFile": self.chk_reopenLastFile.GetValue(),
        }
