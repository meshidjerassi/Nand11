import LexicalElements as le

class SymbolTable:
    def __init__(self):
        self._classVar = {}
        self._subroutineVar = {}
        self._fieldCount = 0
        self._staticCount = 0
        self._varCount = 0
        self._argCount = 0

    def startSubroutine(self):
        self._subroutineVar = {}
        self.varCount = 0
        self._argCount = 0

# STATIC FIELD ARG VAR
    def define(self, name, type, kind):
        if kind in le.CLASS_KINDS:
            if kind == le.CLASS_KINDS[0]:
                num = self._staticCount
                self._staticCount += 1
            else:
                num = self._fieldCount
                self._fieldCount += 1
            self._classVar[name] = (type, kind, num)
        else:
            if kind == le.SUBROUTINE_KINDS[0]:
                num = self._argCount
                self._argCount += 1
            else:
                num = self._varCount
                self._varCount += 1
            self._subroutineVar[name] = (type, kind, num)

    def varCount(self, kind):
        if kind == le.CLASS_KINDS[0]:
            return self._staticCount
        if kind == le.CLASS_KINDS[1]:
            return self._fieldCount
        if kind == le.SUBROUTINE_KINDS[0]:
            return self._argCount
        if kind == le.SUBROUTINE_KINDS[1]:
            return self._varCount
        print("error var count")
        #todo delete after testing

    def kindOf(self, name):
        if name in self._subroutineVar:
            return self._subroutineVar[name][1]
        elif name in self._classVar:
            return self._classVar[name][1]
        return "NONE"

    def typeOf(self, name):
        if name in self._subroutineVar:
            return self._subroutineVar[name][0]
        elif name in self._classVar:
            return self._classVar[name][0]

    def indexOf(self, name):
        if name in self._subroutineVar:
            return self._subroutineVar[name][2]
        elif name in self._classVar:
            return self._classVar[name][2]