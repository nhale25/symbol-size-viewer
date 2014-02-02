
import wx
from guiHelpers import Event

class PrefsDialog(wx.Dialog):
	def __init__(self, prefs, *args, **kwds):
		kwds["title"] = "Preferences"
		wx.Dialog.__init__(self, None, *args, **kwds)
		
		self.txt_nmExeLoc = wx.TextCtrl(self, size=(200, -1))
		self.txt_sizeExeLoc = wx.TextCtrl(self, size=(200, -1))
		self.txt_flashSize = wx.TextCtrl(self)
		self.chk_autoUpdate = wx.CheckBox(self)
		
		gridSizer = wx.FlexGridSizer(cols=2, hgap=20, vgap=10)
		gridSizer.AddGrowableCol(1, 1)
		gridSizer.AddMany([
			wx.StaticText(self, label="Location of nm.exe:"), (self.txt_nmExeLoc, 1, wx.EXPAND),
			wx.StaticText(self, label="Location of size.exe:"), (self.txt_sizeExeLoc, 1, wx.EXPAND),
			wx.StaticText(self, label="Size of Flash area:"), (self.txt_flashSize, 1, wx.EXPAND),
			wx.StaticText(self, label="Automatically reload input file if it changes:"), (self.chk_autoUpdate, 1, wx.EXPAND),
			])
		
		buttons = self.CreateSeparatedButtonSizer(wx.OK | wx.CANCEL)
		
		vSizer = wx.BoxSizer(wx.VERTICAL)
		vSizer.Add(gridSizer, 1, wx.EXPAND | wx.ALL, 20)
		vSizer.Add(buttons, 0, wx.EXPAND | wx.ALIGN_RIGHT | wx.ALL, 10)
		self.SetSizerAndFit(vSizer)
		
		#load initial values
		self.txt_nmExeLoc.SetValue(prefs["nmExeLocation"].getAsString())
		self.txt_sizeExeLoc.SetValue(prefs["sizeExeLocation"].getAsString())
		self.txt_flashSize.SetValue(prefs["totalFlashSize"].getAsString())
		self.chk_autoUpdate.SetValue(prefs["watchFileForChanges"].get())
	
	def getPreferences(self):
		return {
				"nmExeLocation": self.txt_nmExeLoc.GetValue(),
				"sizeExeLocation": self.txt_sizeExeLoc.GetValue(),
				"totalFlashSize": self.txt_flashSize.GetValue(),
				"watchFileForChanges": self.chk_autoUpdate.GetValue()
				}
