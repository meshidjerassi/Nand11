import LexicalElements as consts
from SymbolTable import SymbolTable
from VMWriter import VMWriter

FUNC_TYPE = {"function": 0, "method": 1, "constructor": 0}
OP_VM = {'+': "add", '-': "sub", '*': "Math.multiply", '/': "Math.divide", '&': "and", '|': "or"}
UNI_VM = {'-': "neg", '~': "not"}

WRITE_KEYWORD = "<keyword> {} </keyword>\n"
WRITE_SYMBOL = "<symbol> {} </symbol>\n"
WRITE_IDENTIFIER = "<identifier> {} </identifier>\n"
WRITE_INT = "<integerConstant> {} </integerConstant>\n"
WRITE_STRING = "<stringConstant> {} </stringConstant>\n"

CLASS_OPEN = "<class>\n" + WRITE_KEYWORD.format("class")
CLASS_END = WRITE_SYMBOL.format("}") + "</class>\n"
CLASS_VAR_DEC_OPEN = "<classVarDec>\n" + WRITE_KEYWORD
CLASS_VAR_DEC_END = "</classVarDec>\n"
SUBROUTINE_DEC_OPEN = "<subroutineDec>\n" + WRITE_KEYWORD
SUBROUTINE_DEC_END = "</subroutineDec>\n"
PARAM_LIST_OPEN = "<parameterList>\n"
PARAM_LIST_END = "</parameterList>\n"
SUBROUTINE_BODY_OPEN = "<subroutineBody>\n"
SUBROUTINE_BODY_END = "</subroutineBody>\n"
VAR_DEC_OPEN = "<varDec>\n"
VAR_DEC_END = "</varDec>\n"
STATEMENTS_OPEN = "<statements>\n"
STATEMENTS_END = "</statements>\n"
A_STATEMENT_OPEN = "<{}Statement>\n"
A_STATEMENT_END = "</{}Statement>\n"
EXP_OPEN = "<expression>\n"
EXP_END = "</expression>\n"
TERM_OPEN = "<term>\n"
TERM_END = "</term>\n"
EXP_LIST_OPEN = "<expressionList>\n"
EXP_LIST_END = "</expressionList>\n"


class CompilationEngine:

    def __init__(self, tokenizer, output):
        """
        c'tor
        :param tokenizer: tokenizer object
        :param output: output file/stream
        """
        self.tokenizer = tokenizer
        self.vm = VMWriter(output)
        self._symbolTable = SymbolTable()
        self.className = None
        self.isVoid = None

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
        # self.output.write(CLASS_VAR_DEC_OPEN.format(self.tokenizer.keyWord()))
        self.tokenizer.advance()  # type
        varType = self._writeType()

        self.tokenizer.advance()  # varName
        varName = self.tokenizer.identifier
#todo
        self.tokenizer.advance()  # , or ;
        while self.tokenizer.tokenType() == "symbol" and self.tokenizer.symbol() == ',':
            # self.output.write(WRITE_SYMBOL.format(","))
            self.tokenizer.advance()  # varName
            # self.output.write(WRITE_IDENTIFIER.format(self.tokenizer.identifier()))
            self.tokenizer.advance()  # , or ;
        # self.output.write(WRITE_SYMBOL.format(";"))
        # self.output.write(CLASS_VAR_DEC_END)

    def CompileSubroutine(self):
        """
        compiles subroutine declarations
        """
        addToArgNum = FUNC_TYPE[self.tokenizer.keyWord()]
        self.tokenizer.advance()  # retType
        self.isVoid = (self.tokenizer.tokenType() == "keyword" and self.tokenizer.keyWord() == "void")
        self.tokenizer.advance()  # subRoutine name
        funcName = self.className + "." + self.tokenizer.identifier()
        self.tokenizer.advance()  # (
        argN = self.CompileParameterList()
        self.vm.writeFunction(funcName, argN + addToArgNum)
        self.tokenizer.advance()  # {
        self.tokenizer.advance()  # var / statement
        while self.tokenizer.tokenType() == "keyword" and self.tokenizer.keyWord() == "var":
            self.CompileVarDec()
        self.CompileStatements()

    def CompileVarDec(self):  # todo comments to Meshi - added the var declarations to symbol table
        """
        compiles variable declarations
        """
        self.tokenizer.advance()  # type
        var_type = self._writeType()

        self.tokenizer.advance()  # varName
        var_name = self.tokenizer.identifier
        self._symbolTable.define(var_name, var_type, consts.SUBROUTINE_KINDS[1])  # Add var to symbol table

        self.tokenizer.advance()  # , or ;
        while self.tokenizer.symbol() == ',':
            var_name = self.tokenizer.advance()  # varName
            self._symbolTable.define(var_name, var_type, consts.SUBROUTINE_KINDS[1])  # Add var to symbol table
            self.tokenizer.advance()  # , or ;
        self.tokenizer.advance()

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
        counter = 0
        if self.tokenizer.tokenType() == "identifier" or (
                self.tokenizer.tokenType() == "keyword" and self.tokenizer.keyWord() in consts.VAR_TYPES):
            counter += 1
            argType = self._writeType()
            self.tokenizer.advance()  # varName
            argName = self.tokenizer.identifier()
            self._symbolTable.define(argName, argType, consts.SUBROUTINE_KINDS[0])
            self.tokenizer.advance()  # , or statement
            while self.tokenizer.tokenType() == "symbol" and self.tokenizer.symbol() == ',':
                counter += 1
                self.tokenizer.advance()  # type
                argType = self._writeType()
                self.tokenizer.advance()  # varName
                argName = self.tokenizer.identifier()
                self._symbolTable.define(argName, argType, consts.SUBROUTINE_KINDS[0])
                self.tokenizer.advance()  # , or statement
        return counter

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
