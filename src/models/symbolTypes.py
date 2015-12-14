

class SymbolType(object):
    color = ""
    name = ""
    description = ""

class CodeSymbol(SymbolType):
    color = "#729fcf"
    name = "code"
    description = "Code"

class RoDataSymbol(SymbolType):
    color = "#cf72cd"
    name = "roData"
    description = "Read-only data"

class InitDataSymbol(SymbolType):
    color = "#72cf73"
    name = "initData"
    description = "Initialized data"

class UninitDataSymbol(SymbolType):
    color = "#cfa272"
    name = "uninitData"
    description = "Uninitialized data"
