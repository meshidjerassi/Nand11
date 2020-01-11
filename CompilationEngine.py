import LexicalElements as consts
from SymbolTable import SymbolTable
from VMWriter import VMWriter

OP_VM = {'+': "add", '-': "sub", '*': "Math.multiply", '/': "Math.divide", '&': "and", '|': "or", "<": "lt", ">": "gt",
         "=": "eq"}
UNI_VM = {'-': "neg", '~': "not"}
KIND_VM = {"static": "static", "field": "this", "arg": "argument", "var": "local"}


class CompilationEngine:
    labelC = 0  # todo: per subroutine???

    def __init__(self, tokenizer, output):
        """
        c'tor
        :param tokenizer: tokenizer object
        :param output: output file/stream
        """
        self.tokenizer = tokenizer
        self.vmWriter = VMWriter(output)
        self.symbols = SymbolTable()
        self.className = None

    def CompileClass(self):
        """
        this method is called for each file right after the c'tor. it calls all other methods, and compiles the class
        """
        self.tokenizer.advance()  # class
        self.tokenizer.advance()  # class name
        self.className = self.tokenizer.identifier()
        self.tokenizer.advance()  # {
        while self.tokenizer.hasMoreTokens():
            self.tokenizer.advance()
            if self.tokenizer.tokenType() == "keyword":
                if self.tokenizer.keyWord() in consts.CLASS_VARS:
                    self.CompileClassVarDec()
                elif self.tokenizer.keyWord() in consts.SUB_ROUTINES:
                    self.CompileSubroutine()

    def CompileClassVarDec(self):
        """
        compiles class variables decelerations
        """
        varKind = self.tokenizer.keyWord()
        self.tokenizer.advance()  # type
        varType = self._writeType()
        self.tokenizer.advance()  # varName
        varName = self.tokenizer.identifier()
        self.symbols.define(varName, varType, varKind)
        self.tokenizer.advance()  # , or ;
        while self.tokenizer.tokenType() == "symbol" and self.tokenizer.symbol() == ',':
            self.tokenizer.advance()  # varName
            varName = self.tokenizer.identifier()
            self.symbols.define(varName, varType, varKind)
            self.tokenizer.advance()  # , or ;

    def CompileSubroutine(self):
        """
        compiles subroutine declarations
        """
        subroutine = self.tokenizer.keyWord()
        self.tokenizer.advance()  # retType
        retType = self._writeType()
        self.tokenizer.advance()  # subRoutine name
        name = self.tokenizer.identifier()
        self.tokenizer.advance()  # (
        # todo: hi!
        self.symbols.startSubroutine()
        if subroutine == "method":
            self.symbols.define("this", self.className, "arg")
        self.CompileParameterList()
        self.tokenizer.advance()  # {
        self.tokenizer.advance()  # var / statement
        localN = 0
        while self.tokenizer.tokenType() == "keyword" and self.tokenizer.keyWord() == "var":
            localN += self.CompileVarDec()
        self.vmWriter.writeFunction(self.className + "." + name, localN)
        if subroutine == "method":
            self.vmWriter.writePush("argument", 0)
            self.vmWriter.writePop("pointer", 0)
        elif subroutine == "constructor":
            fields = self.symbols.varCount("field")
            self.vmWriter.writePush("constant", fields)
            self.vmWriter.writeCall("Memory.alloc", 1)
            self.vmWriter.writePop("pointer", 0)
        self.CompileStatements()

    def CompileVarDec(self):
        """
        compiles variable declarations
        """
        self.tokenizer.advance()  # type
        varType = self._writeType()
        self.tokenizer.advance()  # var name
        varName = self.tokenizer.identifier()
        self.symbols.define(varName, varType, "var")
        self.tokenizer.advance()  # , or ;
        counter = 1
        while self.tokenizer.symbol() == ',':
            counter += 1
            self.tokenizer.advance()  # varName
            varName = self.tokenizer.identifier()
            self.symbols.define(varName, varType, "var")
            self.tokenizer.advance()  # , or ;
        self.tokenizer.advance()
        return counter

    def _writeType(self):
        """
        helper method to compile type
        """
        if self.tokenizer.tokenType() == "keyword":
            return self.tokenizer.keyWord()
        else:
            return self.tokenizer.identifier()

    def CompileParameterList(self):
        """
        compiles parameter list
        """
        self.tokenizer.advance()  # type / statement
        if self.tokenizer.tokenType() == "identifier" or (
                self.tokenizer.tokenType() == "keyword" and self.tokenizer.keyWord() in consts.VAR_TYPES):
            paramType = self._writeType()
            self.tokenizer.advance()  # varName
            paramName = self.tokenizer.identifier()
            self.symbols.define(paramName, paramType, "arg")
            self.tokenizer.advance()  # , or statement
            while self.tokenizer.tokenType() == "symbol" and self.tokenizer.symbol() == ',':
                self.tokenizer.advance()  # type
                paramType = self.tokenizer.keyWord()
                self.tokenizer.advance()  # varName
                paramName = self.tokenizer.identifier()
                self.symbols.define(paramName, paramType, "arg")
                self.tokenizer.advance()  # , or statement

    def CompileStatements(self):
        """
        compiles statements
        """
        while self.tokenizer.tokenType() == "keyword" and self.tokenizer.keyWord() in consts.STATEMENTS:
            if self.tokenizer.keyWord() == "let":
                self.CompileLet()
            elif self.tokenizer.keyWord() == "do":
                self.CompileDo()
            elif self.tokenizer.keyWord() == "while":
                self.CompileWhile()
            elif self.tokenizer.keyWord() == "return":
                self.CompileReturn()
            elif self.tokenizer.keyWord() == "if":
                self.CompileIf()

    def CompileLet(self):
        """
        compiles let statement
        """
        self.tokenizer.advance()  # var name
        name = self.tokenizer.identifier()
        kind = self.symbols.kindOf(name)
        self.tokenizer.advance()  # [ or =
        if self.tokenizer.symbol() == '[':
            self.tokenizer.advance()  # exp
            self.CompileExpression()
            position = self.symbols.indexOf(name)
            self.vmWriter.writePush(KIND_VM[kind], position)
            self.vmWriter.writeArithmetic("add")
            self.tokenizer.advance()  # =
            self.tokenizer.advance()
            self.CompileExpression()
            self.vmWriter.writePop("temp", 0)
            self.vmWriter.writePop("pointer", 1)
            self.vmWriter.writePush("temp", 0)
            self.vmWriter.writePop("that", 0)
        else:
            self.tokenizer.advance()
            self.CompileExpression()
            position = self.symbols.indexOf(name)
            self.vmWriter.writePop(KIND_VM[kind], position)
        self.tokenizer.advance()

    def CompileIf(self):
        """
        compiles if statement
        """
        elseLabel = "L" + str(CompilationEngine.labelC)
        CompilationEngine.labelC += 1
        after = "L" + str(CompilationEngine.labelC)
        CompilationEngine.labelC += 1
        self.tokenizer.advance()  # (
        self.tokenizer.advance()  # exp
        self.CompileExpression()
        self.vmWriter.writeArithmetic("not")
        self.vmWriter.writeIf(elseLabel)
        self.tokenizer.advance()  # {
        self.tokenizer.advance()  # statements
        self.CompileStatements()
        self.vmWriter.writeGoto(after)
        self.vmWriter.writeLabel(elseLabel)
        self.tokenizer.advance()
        if self.tokenizer.tokenType() == "keyword" and self.tokenizer.keyWord() == "else":
            self.tokenizer.advance()  # {
            self.tokenizer.advance()  # statements
            self.CompileStatements()
            self.tokenizer.advance()
        self.vmWriter.writeLabel(after)

    def CompileWhile(self):
        """
        compiles while statement
        """
        loop = "L" + str(CompilationEngine.labelC)
        CompilationEngine.labelC += 1
        after = "L" + str(CompilationEngine.labelC)
        CompilationEngine.labelC += 1
        self.tokenizer.advance()  # (
        self.tokenizer.advance()  # exp
        self.vmWriter.writeLabel(loop)
        self.CompileExpression()
        self.vmWriter.writeArithmetic("not")
        self.vmWriter.writeIf(after)
        self.tokenizer.advance()  # {
        self.tokenizer.advance()  # statements
        self.CompileStatements()
        self.vmWriter.writeGoto(loop)
        self.vmWriter.writeLabel(after)
        self.tokenizer.advance()

    def CompileDo(self):
        """
        compiles do statement
        """
        self.tokenizer.advance()  # subroutine name / class name/var name
        self.CompileTerm()
        self.vmWriter.writePop("temp", 0)
        self.tokenizer.advance()

    def CompileReturn(self):
        """
        compiles return statement
        """
        self.tokenizer.advance()  # statement or ;
        if self.tokenizer.tokenType() != "symbol" or self.tokenizer.symbol() != ';':
            self.CompileExpression()
        else:
            self.vmWriter.writePush("constant", 0)
        self.vmWriter.writeReturn()
        self.tokenizer.advance()

    def _write_exp_and_statements(self):
        """
        helper method to write (expression){statements}
        """
        self.tokenizer.advance()  # (
        # self.output.write(WRITE_SYMBOL.format("("))
        self.tokenizer.advance()  # exp
        self.CompileExpression()
        # self.output.write(WRITE_SYMBOL.format(")"))
        self.tokenizer.advance()  # {
        # self.output.write(WRITE_SYMBOL.format("{"))
        self.tokenizer.advance()  # statements
        self.CompileStatements()
        # self.output.write(WRITE_SYMBOL.format("}"))
        self.tokenizer.advance()

    def CompileExpression(self):
        """
        compiles expression
        """
        self.CompileTerm()
        while self.tokenizer.tokenType() == "symbol" and self.tokenizer.symbol() in consts.OP:
            op = self.tokenizer.symbol()
            self.tokenizer.advance()  # term
            self.CompileTerm()
            if op in ("*", "/"):
                self.vmWriter.writeCall(OP_VM[op], 2)
            else:
                self.vmWriter.writeArithmetic(OP_VM[op])

    def CompileTerm(self):
        """
        compiles term
        """
        if self.tokenizer.tokenType() == "integerConstant":
            self.vmWriter.writePush("constant", self.tokenizer.intVal())
            self.tokenizer.advance()
        elif self.tokenizer.tokenType() == "stringConstant":
            stringLen = len(self.tokenizer.stringVal())
            self.vmWriter.writePush("constant", stringLen)
            self.vmWriter.writeCall("String.new", 1)
            for i in range(stringLen):
                char = ord(self.tokenizer.stringVal()[i])
                self.vmWriter.writePush("constant", char)
                self.vmWriter.writeCall("String.appendChar", 2)
            self.tokenizer.advance()
        elif self.tokenizer.tokenType() == "keyword":
            kw = self.tokenizer.keyWord()
            if kw == "this":
                self.vmWriter.writePush("pointer", 0)
            else:  # null, true, false
                self.vmWriter.writePush("constant", 0)
                if kw == "true":
                    self.vmWriter.writeArithmetic("not")
            self.tokenizer.advance()
        elif self.tokenizer.tokenType() == "symbol":
            if self.tokenizer.symbol() == '(':
                self.tokenizer.advance()
                self.CompileExpression()
                self.tokenizer.advance()  # next thing
            elif self.tokenizer.symbol() in ("-", "~"):
                op = self.tokenizer.symbol()
                self.tokenizer.advance()
                self.CompileTerm()
                self.vmWriter.writeArithmetic(UNI_VM[op])
        else:
            name = self.tokenizer.identifier()
            kind = self.symbols.kindOf(name)
            self.tokenizer.advance()  # ( [ . or next thing (if var name)

            if self.tokenizer.symbol() == '[':
                self.tokenizer.advance()
                self.CompileExpression()
                position = self.symbols.indexOf(name)
                self.vmWriter.writePush(KIND_VM[kind], position)
                self.vmWriter.writeArithmetic("add")
                self.vmWriter.writePop("pointer", 1)
                self.vmWriter.writePush("that", 0)
                self.tokenizer.advance()  # next thing
            else:
                fname = name
                fclass = self.className
                dot = False
                argsN = 0
                if self.tokenizer.symbol() == '.':
                    dot = True
                    self.tokenizer.advance()  # subroutine name
                    fname = self.tokenizer.identifier()
                    if kind != "NONE":
                        argsN += 1
                        fclass = self.symbols.typeOf(name)
                        position = self.symbols.indexOf(name)
                        self.vmWriter.writePush(KIND_VM[kind], position)
                    else:
                        fclass = name
                    self.tokenizer.advance()  # (
                if self.tokenizer.tokenType() == "symbol" and self.tokenizer.symbol() == "(":
                    if not dot:
                        argsN += 1
                        self.vmWriter.writePush("pointer", 0)
                    self.tokenizer.advance()  # exp or )
                    argsN += self.CompileExpressionList()
                    self.vmWriter.writeCall(fclass + "." + fname, argsN)
                    self.tokenizer.advance()  # next thing todo:?
                elif kind != "NONE":
                    position = self.symbols.indexOf(name)
                    self.vmWriter.writePush(KIND_VM[kind], position)
                else:
                    self.tokenizer.advance()  # next thing todo:?

    def CompileExpressionList(self):
        """
        compiles expression list
        """
        counter = 0
        if not (self.tokenizer.tokenType() == "symbol" and self.tokenizer.symbol() == ')'):
            counter += 1
            self.CompileExpression()
            while self.tokenizer.symbol() == ',':
                counter += 1
                self.tokenizer.advance()  # expression
                self.CompileExpression()
        return counter
