import os.path

def getRelativePath(relativeTo, path):
    return os.path.abspath(os.path.join(os.path.dirname(relativeTo), path))

class Event(object):
    def __init__(self):
        self._fns = []

    def addHandler(self, fn):
        if fn not in self._fns:
            self._fns.append(fn)

    def removeHandler(self, fn):
        if fn in self._fns:
            self._fns.remove(fn)

    def __call__(self, *args, **kwargs):
        for fn in self._fns:
            fn(*args, **kwargs)

#class Observable:
     #def __init__(self, initialValue=None):
         #self.data = initialValue
         #self.callbacks = {}

     #def addCallback(self, func):
         #self.callbacks[func] = 1

     #def delCallback(self, func):
         #del self.callback[func]

     #def _docallbacks(self):
         #for func in self.callbacks:
             #func(self.data)

     #def set(self, data):
         #self.data = data
         #self._docallbacks()

     #def get(self):
         #return self.data

     #def unset(self):
         #self.data = None