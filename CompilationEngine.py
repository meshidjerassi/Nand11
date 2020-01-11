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
        var_name = self.tokenizer.identifier
        kind_to_push = self._symbolTable.kindOf(var_name)  # check type of var
        if kind_to_push == consts.SUBROUTINE_KINDS[1]:
            kind_to_push = "local"
        index = self._symbolTable.indexOf(var_name)
        self.tokenizer.advance()  # [ or =
        if self.tokenizer.symbol() == '[':
            self.tokenizer.advance()  # exp
            self.CompileExpression()
            self.tokenizer.advance()  # =
        self.tokenizer.advance()
        self.CompileExpression()
        self.tokenizer.advance()
        # todo why should we pop local 0?????
        self.vm.writePush(kind_to_push, index)  # seg  + index

    def CompileIf(self):
        """
        compiles if statement
        """
        # self.output.write(A_STATEMENT_OPEN.format("if"))
        # self.output.write(WRITE_KEYWORD.format("if"))
        self._write_exp_and_statements()
        if self.tokenizer.tokenType() == "keyword" and self.tokenizer.keyWord() == "else":
            # self.output.write(WRITE_KEYWORD.format("else"))
            self.tokenizer.advance()  # {
            # self.output.write(WRITE_SYMBOL.format("{"))
            self.tokenizer.advance()  # statements
            self.CompileStatements()
            # self.output.write(WRITE_SYMBOL.format("}"))
            self.tokenizer.advance()
        # self.output.write(A_STATEMENT_END.format("if"))

    def CompileWhile(self):
        """
        compiles while statement
        """
        # self.output.write(A_STATEMENT_OPEN.format("while"))
        # self.output.write(WRITE_KEYWORD.format("while"))
        # self._write_exp_and_statements()
        # self.output.write(A_STATEMENT_END.format("while"))

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

    def CompileDo(self):
        """
        compiles do statement
        """
        self.tokenizer.advance()  # subroutine name / class name/var name
        name = self.tokenizer.identifier()

        self.tokenizer.advance()  # . or (
        if self.tokenizer.symbol() == '.':
            self.tokenizer.advance()  # subroutine name
            name += "." + self.tokenizer.identifier()
            self.tokenizer.advance()  # (
        self.tokenizer.advance()  # exp or )
        argN = self.CompileExpressionList()
        self.tokenizer.advance()  # ;
        self.tokenizer.advance()
        self.vm.writeCall(name, argN)
        if self.isVoid:
            self.vm.writePop("temp", 0)

    def CompileReturn(self):
        """
        compiles return statement
        """
        self.tokenizer.advance()  # statement or ;
        if self.tokenizer.tokenType() != "symbol" or self.tokenizer.symbol() != ';':
            self.CompileExpression()
        if self.isVoid:
            self.vm.writePush("constant", 0)
        self.vm.writeReturn()
        self.tokenizer.advance()

    def CompileExpression(self):
        """
        compiles expression
        """
        self.CompileTerm()
        while self.tokenizer.tokenType() == "symbol" and self.tokenizer.symbol() in consts.OP:
            op = OP_VM[self.tokenizer.symbol()]
            simpleOp = self.tokenizer.symbol() not in ("*", "/")
            self.tokenizer.advance()  # term
            self.CompileTerm()
            if simpleOp:
                self.vm.writeArithmetic(op)
            else:
                self.vm.writeCall(op, 2)

    def CompileTerm(self):
        """
        compiles term
        """
        if self.tokenizer.tokenType() == "integerConstant":
            self.vm.writePush("constant", self.tokenizer.intVal())
            self.tokenizer.advance()
        elif self.tokenizer.tokenType() == "stringConstant":
            # self.output.write(WRITE_STRING.format(self.tokenizer.stringVal()))
            self.tokenizer.advance()
        elif self.tokenizer.tokenType() == "keyword":
            # self.output.write(WRITE_KEYWORD.format(self.tokenizer.keyWord()))
            self.tokenizer.advance()
        elif self.tokenizer.tokenType() == "symbol":
            if self.tokenizer.symbol() == '(':
                self.tokenizer.advance()
                self.CompileExpression()
                self.tokenizer.advance()  # next thing
            elif self.tokenizer.symbol() in ("-", "~"):
                op = UNI_VM[self.tokenizer.symbol()]
                self.tokenizer.advance()
                self.CompileTerm()
                self.vm.writeArithmetic(op)

        else:
            func_name = self.tokenizer.identifier()
            self.tokenizer.advance()
            if self.tokenizer.symbol() == '.':
                func_name += self.tokenizer.symbol()
                self.tokenizer.advance()
                func_name += self.tokenizer.identifier()
            argN = self.CompileParameterList()
            self.vm.writeCall(func_name, argN)
            self.tokenizer.advance()  # ( [ . or next thing (if var name)
            if self.tokenizer.tokenType() == "symbol" and self.tokenizer.symbol() in ("[", "(", "."):
                # self.output.write(WRITE_SYMBOL.format(self.tokenizer.symbol()))
                if self.tokenizer.symbol() == '[':
                    self.tokenizer.advance()
                    self.CompileExpression()
                    # self.output.write(WRITE_SYMBOL.format(']'))
                    self.tokenizer.advance()  # next thing
                elif self.tokenizer.symbol() == '(':
                    self.tokenizer.advance()  # exp or )
                    self.CompileExpressionList()
                    # self.output.write(WRITE_SYMBOL.format(')'))
                    self.tokenizer.advance()  # next thing
                elif self.tokenizer.symbol() == '.':
                    self.tokenizer.advance()  # subroutine name
                    # self.output.write(WRITE_IDENTIFIER.format(self.tokenizer.identifier()))
                    self.tokenizer.advance()  # (
                    # self.output.write(WRITE_SYMBOL.format('('))
                    self.tokenizer.advance()  # exp or )
                    self.CompileExpressionList()
                    # self.output.write(WRITE_SYMBOL.format(')'))
                    self.tokenizer.advance()  # next thing
        # self.output.write(TERM_END)

    def CompileExpressionList(self):
        """
        compiles expression list
        """
        counter = 0
        if not (self.tokenizer.tokenType() == "symbol" and self.tokenizer.symbol() == ')'):
            self.CompileExpression()
            counter += 1
            while self.tokenizer.symbol() == ',':
                counter += 1
                self.tokenizer.advance()  # expression
                self.CompileExpression()
        return counter
