
import os.path
import watchdog.observers
from watchdog.events import FileSystemEventHandler

from binUtilsParsers import NmParser, SizeParser
from guiHelpers import Event

class FileWatcher(object):
	class MyEventHandler(FileSystemEventHandler):
		def __init__(self, callback, path):
			self._callback = callback
			self._path = path
			self._absPath = os.path.abspath(path)
			
		def on_any_event(self, event):
			if event.src_path == self._absPath or \
				hasattr(event, "dest_path") and event.dest_path == self._absPath:
					self._callback(self._path, os.path.isfile(self._absPath))
						
	def __init__(self, callback):
		self._callback = callback
		self._fsWatcher = None
		self._path = None
	
	def startWatching(self):
		if not self._fsWatcher:
			self._fsWatcher = watchdog.observers.Observer()
			self._fsWatcher.start()
			self._tryStartWatchingFile()
	
	def stopWatching(self):
		if self._fsWatcher:
			self._fsWatcher.stop()
			self._fsWatcher.join()
			self._fsWatcher = None
	
	def setFileToWatch(self, path):
		if self._path == path:
			return

		self._path = path
		self._tryStartWatchingFile()
	
	def _tryStartWatchingFile(self):
		if self._fsWatcher:
			self._fsWatcher.unschedule_all()
			
			if self._path:
				handler = FileWatcher.MyEventHandler(self._callback, self._path)
				self._fsWatcher.schedule(handler, os.path.dirname(self._path))
			
class ObjectFileModel(object):
	def __init__(self, sizeExeLoc=None, nmExeLoc=None):
		self.fileChangedEvent = Event()
		self.path = None
		
		self._sizeParser = SizeParser(sizeExeLoc)
		self._nmParser = NmParser(nmExeLoc)
		self._fileWatcher = FileWatcher(self._fileWatcherCallback)
		
	def setSizeExeLocation(self, loc):
		self._sizeParser.setExePath(loc)
		
	def setNmExeLocation(self, loc):
		self._nmParser.setExePath(loc)
		
	def getSizeInfo(self):
		return self._sizeParser.parseOutput(self.path)
		
	def getSymbolInfo(self):
		return self._nmParser.parseOutput(self.path)
		
	def setFile(self, path):
		if self.path == path:
			return
		
		self.path = path
		self._fileWatcher.setFileToWatch(path)
		self.fileChangedEvent(self, os.path.isfile(path))
	
	def setWatchFileFileForChanges(self, watchForChanges):
		if watchForChanges:
			self._fileWatcher.startWatching()
		else:
			self._fileWatcher.stopWatching()
	
	def _fileWatcherCallback(self, path, stillExists):
		self.fileChangedEvent(self, stillExists)
