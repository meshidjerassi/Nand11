class VMWriter:
    def __init__(self, output):
        self._output = output

    def writePush(self, seg, index):
        self._output.write("push {} {}\n".format(seg, index))

    def writePop(self, seg, index):
        self._output.write("pop {} {}\n".format(seg, index))

    def writeArithmetic(self, cmd):
        self._output.write(cmd+"\n")

    def writeLabel(self, label):
        self._output.write("label {}\n".format(label))

    def writeGoto(self, label):
        self._output.write("goto {}\n".format(label))

    def writeIf(self, label):
        self._output.write("if-goto {}\n".format(label))

    def writeCall(self, name, nArgs):
        self._output.write("call {} {}\n".format(name, nArgs))

    def writeFunction(self, name, nLocals):
        self._output.write("function {} {}\n".format(name, nLocals))

    def writeReturn(self):
        self._output.write("return")
