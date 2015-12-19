
import os.path
import watchdog.observers
from watchdog.events import FileSystemEventHandler


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
        self._watchedFilePath = None
        self._fsWatcher = None
        self._shouldWatch = False

    def _startWatching(self):
        if not self._fsWatcher and self._watchedFilePath:
            self._fsWatcher = watchdog.observers.Observer()
            self._fsWatcher.start()
            self._fsWatcher.unschedule_all()
            handler = FileWatcher.MyEventHandler(self._callback, self._watchedFilePath)
            self._fsWatcher.schedule(handler, os.path.dirname(self._watchedFilePath))

    def _stopWatching(self):
        if self._fsWatcher:
            self._fsWatcher.stop()
            self._fsWatcher.join()
            self._fsWatcher = None

    def setFileToWatch(self, path):
        if self._watchedFilePath == path:
            return

        self._stopWatching()
        self._watchedFilePath = path
        if self._shouldWatch:
            self._startWatching()

    def startWatching(self):
        self._shouldWatch = True
        self._startWatching()

    def stopWatching(self):
        self._shouldWatch = False
        self._stopWatching()
