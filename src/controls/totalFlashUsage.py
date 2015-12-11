
import wx
from memUsageGauge import MemUsageGauge
from guiHelpers import Event

class TotalFlashUsage(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        self._numberFormatter = lambda x: "%d"% x
        self._totalFlashSize = 0
        self._dataLoaded = False
        self._totalSize = 0

        self.gauge = MemUsageGauge(self, wx.ID_ANY, style=wx.GA_HORIZONTAL)
        sizer = wx.BoxSizer()
        sizer.Add(self.gauge, 1, wx.EXPAND)
        self.SetSizer(sizer)

    def setNumberFormatter(self, formatter):
        self._numberFormatter = formatter

    def setTotalFlashSize(self, size):
        self._totalFlashSize = size
        if size == 0:
            self.Hide()
            self.GetParent().Layout()

        else:
            self.Show()
            self.GetParent().Layout()
            self.gauge.SetCapacity(size)
            self._updateBarText()

    def updateInfo(self, sizeInfo, roDataSize):
        if sizeInfo is None:
            self.gauge.SetSizes(0, 0, 0)
            self._dataLoaded = False

        else:
            code = sizeInfo.text - roDataSize
            self.gauge.SetSizes(code, roDataSize, sizeInfo.data)
            self._dataLoaded = True
            self._totalSize = roDataSize + code + sizeInfo.data

        self._updateBarText()

    def _updateBarText(self):
        if not self._dataLoaded or self._totalFlashSize == 0:
            self.gauge.SetText("")

        else:
            totalSize = self._totalSize
            percent = (float(totalSize) * 100) / self.gauge._capacity
            totalSizeFormatted = self._numberFormatter(totalSize)
            flashSizeFormatted = self._numberFormatter(self._totalFlashSize)
            self.gauge.SetText("Using %s of %s bytes (%d%%)"% (totalSizeFormatted, flashSizeFormatted, percent))
