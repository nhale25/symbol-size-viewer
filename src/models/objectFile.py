
from binUtilsOutputFiles import NmOutputFile, SizeOutputFile


class ObjectFile(object):
    def __init__(self, sizeToolLoc, nmToolLoc, objectFileLoc):
        self._path = objectFileLoc
        self._sizeOutputFile = SizeOutputFile(sizeToolLoc, objectFileLoc)
        self._nmOutputFile = NmOutputFile(nmToolLoc, objectFileLoc)

    @property
    def path(self):
        return self._path

    @property
    def textSize(self):
        return self._sizeOutputFile.textSize

    @property
    def dataSize(self):
        return self._sizeOutputFile.dataSize

    @property
    def bssSize(self):
        return self._sizeOutputFile.bssSize

    def getSymbols(self):
        return self._nmOutputFile.getSymbols()
