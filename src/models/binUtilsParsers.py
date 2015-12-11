
import subprocess
import os.path
import errno

class ParseError(Exception): pass

class SizeInfo(object):
    def __init__(self, text, data, bss):
        self.text = text
        self.data = data
        self.bss = bss

        self.total = text + data # but not BSS because it's all zeroes, so doesn't need to be stored.

    def __str__(self):
        return "text=%d data=%d bss=%s total=%d"% (self.text, self.data, self.bss, self.total)

class SymbolType:
    symbolDescriptions = {
        "A": "absolute",
        "B": "uninitialised data",
        "C": "uninitialised data (common)",
        "D": "initialised data",
        "G": "initialised data (small objects)",
        "I": "indirect reference",
        "N": "debugging",
        "R": "read-only data",
        "S": "uninitialised data (small objects)",
        "T": "text (code)",
        "U": "undefined",
        "V": "weak",
        "W": "weak",
        "-": "stabs",
        "?": "unknown",
        }

    symbols = {}

    def __init__(self, code):
        self.code = code
        self.description = self.symbolDescriptions.get(code.upper(), "unknown")
        self.isGlobal = code.isupper()

    def __eq__(self, other):
        return self.code == other.code

    def __ne__(self, other):
        return not self.__eq__(other)

class SymbolInfo(object):
    def __init__(self, size, type, name):
        self.size = size
        self.name = name
        self.type = type

    def __str__(self):
        typeDesc = CObjectType.getName(self.type)
        return "%s %d %s"% (self.name, self.size, typeDesc)

class BinUtilParser(object):
    def __init__(self, exePath=None):
        self._exePath = None

        if exePath:
            self.setExePath(exePath)

    def setExePath(self, path):
        self._exePath = os.path.abspath(path)

    def _runExecutable(self, args):
        if not self._exePath:
            raise ParseError("No executable set")

        if hasattr(subprocess, "STARTUPINFO"):
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        else:
            startupinfo = None
        try:
            process = subprocess.Popen([self._exePath] + args, stdout=subprocess.PIPE, startupinfo=startupinfo)
        except OSError as e:
            if e.errno == errno.ENOENT:
                raise ParseError("'%s' not found."% self._exePath)

        return process.communicate()[0]

    def parseOutput(self, filename):
        raise NotImplementedError

class SizeParser(BinUtilParser):
    def parseOutput(self, path):
        output = self._runExecutable([path])

        lines = output.split("\n")
        if len(lines) < 2:
            raise ParseError("Failed running 'size' on '%s'"% path)

        try:
            text, data, bss, _ = lines[1].split(None, 3)
            info = SizeInfo(int(text), int(data), int(bss))
        except ValueError:
            raise ParseError("Failed running 'size' on '%s'"% path)

        return info

class NmParser(BinUtilParser):
    def parseOutput(self, path):
        output = self._runExecutable(["--size-sort", "--special-syms", path])

        symbols = []
        for line in output.split("\n"):
            try:
                size, symbolType, name = line.strip().split()
                size = int(size, 16)
            except ValueError:
                pass
            else:
                symbolType = SymbolType(symbolType)
                symbol = SymbolInfo(size, symbolType, name)
                symbols.append(symbol)
        return symbols

    @staticmethod
    def prettyPrintSymbolList(symbols):
        types = {}
        for sym in symbols:
            symType = sym.type.code.lower()
            if symType not in types:
                types[symType] = []
            types[symType].append(sym)

        output = []
        for type, syms in types.items():
            typeTotalSize = sum([sym.size for sym in syms])
            output.append("%s: %d symbols, totalling %d bytes"% (type, len(syms), typeTotalSize))

        totalSize = sum([sym.size for sym in symbols])
        output.append("%d symbols, total size %d"% (len(symbols), totalSize))
        return "\n".join(output)

#class MapFileInfo(object):
    #pass

#class MapFileInfoParser(BinUtilParser):
    #def _parseArchiveIncludes(self, lines):
        #pass

    #def _parseDiscardedSections(self, lines):
        #pass

    #def _parseMemoryConfiguration(self, lines):
        #pass

    #def _parseCrossReferenceTable(self, lines):
        #pass

    #def parseOutput(self, path):
        #pass