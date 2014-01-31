
from ConfigParser import ConfigParser
from guiHelpers import Event
import os
import os.path
import errno

class PrefsModel:
	def __init__(self, fileName=None):
		self.nmExeLocation = ""
		self.sizeExeLocation = ""
		self.numberFormat = "decimal"
		self.totalFlashSizeStr = ""
		self.lastOpenedDirectory = ""
		self.watchFileForChanges = True
		
		self.prefsChangedEvent = Event()
		
		if fileName is not None:
			self.loadFromFile(fileName)
	
	@property
	def totalFlashSize(self):
		if self.totalFlashSizeStr.lower().startswith("0x"):
			base = 16
		else:
			base = 10
			
		try:
			return int(self.totalFlashSizeStr, base)
		except ValueError:
			return 0
	
	def loadFromFile(self, fileName):
		try:
			config = ConfigParser()
			with open(fileName) as f:
				config.readfp(f)
			
			self.nmExeLocation = config.get("DEFAULT", "nmExeLocation")
			self.sizeExeLocation = config.get("DEFAULT", "sizeExeLocation")
			self.numberFormat = config.get("DEFAULT", "numberFormat")
			self.totalFlashSizeStr = config.get("DEFAULT", "totalFlashSizeStr")
			self.lastOpenedDirectory = config.get("DEFAULT", "lastOpenedDirectory")
			self.watchFileForChanges = config.getboolean("DEFAULT", "watchFileForChanges")
			self.prefsChangedEvent(self)
			
		except Exception as e:
			print e
	
	def saveToFile(self, fileName):
		config = ConfigParser()
		config.set("DEFAULT", "nmExeLocation", self.nmExeLocation)
		config.set("DEFAULT", "sizeExeLocation", self.sizeExeLocation)
		config.set("DEFAULT", "numberFormat", self.numberFormat)
		config.set("DEFAULT", "totalFlashSizeStr", self.totalFlashSizeStr)
		config.set("DEFAULT", "lastOpenedDirectory", self.lastOpenedDirectory)
		config.set("DEFAULT", "watchFileForChanges", self.watchFileForChanges)
		
		try:
			os.makedirs(os.path.dirname(fileName))
		except OSError as e:
			if e.errno != errno.EEXIST:
				raise
		
		with open(fileName, "w") as f:
			config.write(f)
