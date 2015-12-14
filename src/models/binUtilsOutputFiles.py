
import subprocess
import os.path
import errno

import symbolTypes


class ParseError(Exception): pass


class RawSymbolType:
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

    def __init__(self, code):
        self._code = code

    def __eq__(self, other):
        return self._code == other._code

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def code(self):
        return self._code.lower()

    @property
    def description(self):
        return self.symbolDescriptions.get(self._code.upper(), "unknown")

    @property
    def isGlobal(self):
        return self._code.isupper()


class Symbol(object):
    def __init__(self, size, rawType, name):
        self._size = size
        self._name = name
        self._rawType = rawType

    @property
    def size(self):
        return self._size

    @property
    def name(self):
        return self._name

    @property
    def rawType(self):
        return self._rawType

    @property
    def basicType(self):
        if self._rawType.code in "t":
            return symbolTypes.CodeSymbol

        elif self._rawType.code in "gd":
            return symbolTypes.InitDataSymbol

        elif self._rawType.code in "r":
            return symbolTypes.RoDataSymbol

        elif self._rawType.code in "bcs":
            return symbolTypes.UninitDataSymbol

        else:
            return None


class ExternalToolGeneratedFile(object):
    def __init__(self, toolPath, filePath):
        self._toolPath = os.path.abspath(toolPath)
        self._filePath = filePath

    def _buildArgs(self):
        return [self._toolPath, self._filePath]

    def _runExternalTool(self):
        if hasattr(subprocess, "STARTUPINFO"):
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        else:
            startupinfo = None

        try:
            process = subprocess.Popen(self._buildArgs(), stdout=subprocess.PIPE, startupinfo=startupinfo)
        except OSError as e:
            if e.errno == errno.ENOENT:
                raise ParseError("Input file '%s' not found."% self._fileath)
            elif e.errno == errno.ACCES:
                raise ParseError("External tool '%s' not found."% self._exePath)
            else:
                raise ParseError(e)

        return process.communicate()[0]


class SizeOutputFile(ExternalToolGeneratedFile):
    def __init__(self, *args, **kwargs):
        ExternalToolGeneratedFile.__init__(self, *args, **kwargs)

        fields = self._parseSizeOutput()
        self._textSize = fields[0]
        self._dataSize = fields[1]
        self._bssSize = fields[2]

    def __str__(self):
        return "text=%d data=%d bss=%s total=%d"% \
               (self._textSize, self._dataSize, self._bssSize, self.totalSize)

    def _parseSizeOutput(self):
        output = self._runExternalTool()

        lines = output.split("\n")
        if len(lines) < 2:
            raise ParseError("Failed running 'size' on '%s'"% self._filePath)

        try:
            text, data, bss, _ = lines[1].split(None, 3)
            fields = [int(field) for field in (text, data, bss)]
        except ValueError as e:
            raise ParseError("Failed running 'size' on '%s'"% self._filePath)

        return fields

    @property
    def textSize(self):
        return self._textSize

    @property
    def dataSize(self):
        return self._dataSize

    @property
    def bssSize(self):
        return self._bssSize

    @property
    def totalSize(self):
        return self._textSize + self._dataSize + self._bssSize


class NmOutputFile(ExternalToolGeneratedFile):
    def __init__(self, *args, **kwargs):
        ExternalToolGeneratedFile.__init__(self, *args, **kwargs)
        self._symbols = self._parseOutput()

    def _buildArgs(self):
        return [self._toolPath, "--size-sort", "--special-syms", self._filePath]

    def _parseOutput(self):
        output = self._runExternalTool()

        symbols = []
        for line in output.split("\n"):
            try:
                size, rawTypeCode, name = line.strip().split()
                size = int(size, 16)
            except ValueError:
                pass
            else:
                rawType = RawSymbolType(rawTypeCode)
                symbol = Symbol(size, rawType, name)
                symbols.append(symbol)
        return symbols

    def getSymbols(self):
        return self._symbols[:]

    def prettyPrintSymbolList(self):
        types = {}
        for sym in self._symbols:
            symType = sym.basicType
            if symType not in types:
                types[symType] = []
            types[symType].append(sym)

        output = []
        for type, syms in types.items():
            if type is None:
                continue

            typeTotalSize = sum([sym.size for sym in syms])
            output.append("%s: %d symbols, totalling %d bytes"% (type.name, len(syms), typeTotalSize))

        totalSize = sum([sym.size for sym in self._symbols])
        output.append("total %d symbols, total size %d bytes"% (len(self._symbols), totalSize))
        return "\n".join(output)
