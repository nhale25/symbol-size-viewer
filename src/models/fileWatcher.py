
import os.path
import watchdog.observers
from watchdog.events import FileSystemEventHandler

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