import LexicalElements as consts

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
        self.output = output

    def CompileClass(self):
        """
        this method is called for each file right after the c'tor. it calls all other methods, and compiles the class
        """
        self.output.write(CLASS_OPEN)
        self.tokenizer.advance()  # class
        self.tokenizer.advance()  # class name
        self.output.write(WRITE_IDENTIFIER.format(self.tokenizer.identifier()))
        self.tokenizer.advance()  # {
        self.output.write(WRITE_SYMBOL.format("{"))
        while self.tokenizer.hasMoreTokens():
            self.tokenizer.advance()
            if self.tokenizer.tokenType() == "keyword":
                if self.tokenizer.keyWord() in consts.CLASS_VARS:
                    self.CompileClassVarDec()
                elif self.tokenizer.keyWord() in consts.SUB_ROUTINES:
                    self.CompileSubroutine()
        self.output.write(CLASS_END)

    def CompileClassVarDec(self):
        """
        compiles class variables decelerations
        """
        self.output.write(CLASS_VAR_DEC_OPEN.format(self.tokenizer.keyWord()))
        self.tokenizer.advance()  # type
        self._writeType()
        self.tokenizer.advance()  # varName
        self.output.write(WRITE_IDENTIFIER.format(self.tokenizer.identifier()))
        self.tokenizer.advance()  # , or ;
        while self.tokenizer.tokenType() == "symbol" and self.tokenizer.symbol() == ',':
            self.output.write(WRITE_SYMBOL.format(","))
            self.tokenizer.advance()  # varName
            self.output.write(WRITE_IDENTIFIER.format(self.tokenizer.identifier()))
            self.tokenizer.advance()  # , or ;
        self.output.write(WRITE_SYMBOL.format(";"))
        self.output.write(CLASS_VAR_DEC_END)

    def CompileSubroutine(self):
        """
        compiles subroutine declarations
        """
        self.output.write(SUBROUTINE_DEC_OPEN.format(self.tokenizer.keyWord()))
        self.tokenizer.advance()  # retType
        self._writeType()
        self.tokenizer.advance()  # subRoutine name
        self.output.write(WRITE_IDENTIFIER.format(self.tokenizer.identifier()))
        self.tokenizer.advance()  # (
        self.output.write(WRITE_SYMBOL.format("("))
        self.CompileParameterList()
        self.output.write(WRITE_SYMBOL.format(")"))
        self.output.write(SUBROUTINE_BODY_OPEN)
        self.tokenizer.advance()  # {
        self.output.write(WRITE_SYMBOL.format("{"))
        self.tokenizer.advance()  # var / statement
        while self.tokenizer.tokenType() == "keyword" and self.tokenizer.keyWord() == "var":
            self.CompileVarDec()
        self.CompileStatements()
        self.output.write(WRITE_SYMBOL.format("}"))
        self.output.write(SUBROUTINE_BODY_END)
        self.output.write(SUBROUTINE_DEC_END)

    def CompileVarDec(self):
        """
        compiles variable declarations
        """
        self.output.write(VAR_DEC_OPEN)
        self.output.write(WRITE_KEYWORD.format("var"))
        self.tokenizer.advance()  # type
        self._writeType()
        self.tokenizer.advance()  # var name
        self.output.write(WRITE_IDENTIFIER.format(self.tokenizer.identifier()))
        self.tokenizer.advance()  # , or ;
        while self.tokenizer.symbol() == ',':
            self.output.write(WRITE_SYMBOL.format(","))
            self.tokenizer.advance()  # varName
            self.output.write(WRITE_IDENTIFIER.format(self.tokenizer.identifier()))
            self.tokenizer.advance()  # , or ;
        self.output.write(WRITE_SYMBOL.format(";"))
        self.tokenizer.advance()
        self.output.write(VAR_DEC_END)

    def _writeType(self):
        """
        helper method to compile type
        """
        if self.tokenizer.tokenType() == "keyword":
            self.output.write(WRITE_KEYWORD.format(self.tokenizer.keyWord()))
        else:
            self.output.write(WRITE_IDENTIFIER.format(self.tokenizer.identifier()))

    def CompileParameterList(self):
        """
        compiles parameter list
        """
        self.output.write(PARAM_LIST_OPEN)
        self.tokenizer.advance()  # type / statement
        if self.tokenizer.tokenType() == "identifier" or (
                self.tokenizer.tokenType() == "keyword" and self.tokenizer.keyWord() in consts.VAR_TYPES):
            self._writeType()
            self.tokenizer.advance()  # varName
            self.output.write(WRITE_IDENTIFIER.format(self.tokenizer.identifier()))
            self.tokenizer.advance()  # , or statement
            while self.tokenizer.tokenType() == "symbol" and self.tokenizer.symbol() == ',':
                self.output.write(WRITE_SYMBOL.format(","))
                self.tokenizer.advance()  # type
                self.output.write(WRITE_KEYWORD.format(self.tokenizer.keyWord()))
                self.tokenizer.advance()  # varName
                self.output.write(WRITE_IDENTIFIER.format(self.tokenizer.identifier()))
                self.tokenizer.advance()  # , or statement
        self.output.write(PARAM_LIST_END)

    def CompileStatements(self):
        """
        compiles statements
        """
        self.output.write(STATEMENTS_OPEN)
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
        self.output.write(STATEMENTS_END)

    def CompileLet(self):
        """
        compiles let statement
        """
        self.output.write(A_STATEMENT_OPEN.format("let"))
        self.output.write(WRITE_KEYWORD.format("let"))
        self.tokenizer.advance()  # var name
        self.output.write(WRITE_IDENTIFIER.format(self.tokenizer.identifier()))
        self.tokenizer.advance()  # [ or =
        if self.tokenizer.symbol() == '[':
            self.output.write(WRITE_SYMBOL.format("["))
            self.tokenizer.advance()  # exp
            self.CompileExpression()
            self.output.write(WRITE_SYMBOL.format("]"))
            self.tokenizer.advance()  # =
        self.output.write(WRITE_SYMBOL.format("="))
        self.tokenizer.advance()
        self.CompileExpression()
        self.output.write(WRITE_SYMBOL.format(";"))
        self.tokenizer.advance()
        self.output.write(A_STATEMENT_END.format("let"))

    def CompileIf(self):
        """
        compiles if statement
        """
        self.output.write(A_STATEMENT_OPEN.format("if"))
        self.output.write(WRITE_KEYWORD.format("if"))
        self._write_exp_and_statements()
        if self.tokenizer.tokenType() == "keyword" and self.tokenizer.keyWord() == "else":
            self.output.write(WRITE_KEYWORD.format("else"))
            self.tokenizer.advance()  # {
            self.output.write(WRITE_SYMBOL.format("{"))
            self.tokenizer.advance()  # statements
            self.CompileStatements()
            self.output.write(WRITE_SYMBOL.format("}"))
            self.tokenizer.advance()
        self.output.write(A_STATEMENT_END.format("if"))

    def CompileWhile(self):
        """
        compiles while statement
        """
        self.output.write(A_STATEMENT_OPEN.format("while"))
        self.output.write(WRITE_KEYWORD.format("while"))
        self._write_exp_and_statements()
        self.output.write(A_STATEMENT_END.format("while"))

    def _write_exp_and_statements(self):
        """
        helper method to write (expression){statements}
        """
        self.tokenizer.advance()  # (
        self.output.write(WRITE_SYMBOL.format("("))
        self.tokenizer.advance()  # exp
        self.CompileExpression()
        self.output.write(WRITE_SYMBOL.format(")"))
        self.tokenizer.advance()  # {
        self.output.write(WRITE_SYMBOL.format("{"))
        self.tokenizer.advance()  # statements
        self.CompileStatements()
        self.output.write(WRITE_SYMBOL.format("}"))
        self.tokenizer.advance()

    def CompileDo(self):
        """
        compiles do statement
        """
        self.output.write(A_STATEMENT_OPEN.format("do"))
        self.output.write(WRITE_KEYWORD.format("do"))
        self.tokenizer.advance()  # subroutine name / class name/var name
        self.output.write(WRITE_IDENTIFIER.format(self.tokenizer.identifier()))
        self.tokenizer.advance()  # . or (
        self.output.write(WRITE_SYMBOL.format(self.tokenizer.symbol()))
        if self.tokenizer.symbol() == '.':
            self.tokenizer.advance()  # subroutine name
            self.output.write(WRITE_IDENTIFIER.format(self.tokenizer.identifier()))
            self.tokenizer.advance()  # (
            self.output.write(WRITE_SYMBOL.format('('))
        self.tokenizer.advance()  # exp or )
        self.CompileExpressionList()
        self.output.write(WRITE_SYMBOL.format(")"))
        self.tokenizer.advance()  # ;
        self.output.write(WRITE_SYMBOL.format(";"))
        self.tokenizer.advance()
        self.output.write(A_STATEMENT_END.format("do"))

    def CompileReturn(self):
        """
        compiles return statement
        """
        self.output.write(A_STATEMENT_OPEN.format("return"))
        self.output.write(WRITE_KEYWORD.format("return"))
        self.tokenizer.advance()  # statement or ;
        if self.tokenizer.tokenType() != "symbol" or self.tokenizer.symbol() != ';':
            self.CompileExpression()
        self.output.write(WRITE_SYMBOL.format(";"))
        self.tokenizer.advance()
        self.output.write(A_STATEMENT_END.format("return"))

    def CompileExpression(self):
        """
        compiles expression
        """
        self.output.write(EXP_OPEN)
        self.CompileTerm()
        while self.tokenizer.tokenType() == "symbol" and self.tokenizer.symbol() in consts.OP:
            self.output.write(WRITE_SYMBOL.format(self.tokenizer.symbol()))
            self.tokenizer.advance()  # term
            self.CompileTerm()
        self.output.write(EXP_END)

    def CompileTerm(self):
        """
        compiles term
        """
        self.output.write(TERM_OPEN)
        if self.tokenizer.tokenType() == "integerConstant":
            self.output.write(WRITE_INT.format(self.tokenizer.intVal()))
            self.tokenizer.advance()
        elif self.tokenizer.tokenType() == "stringConstant":
            self.output.write(WRITE_STRING.format(self.tokenizer.stringVal()))
            self.tokenizer.advance()
        elif self.tokenizer.tokenType() == "keyword":
            self.output.write(WRITE_KEYWORD.format(self.tokenizer.keyWord()))
            self.tokenizer.advance()
        elif self.tokenizer.tokenType() == "symbol":
            self.output.write(WRITE_SYMBOL.format(self.tokenizer.symbol()))
            if self.tokenizer.symbol() == '(':
                self.tokenizer.advance()
                self.CompileExpression()
                self.output.write(WRITE_SYMBOL.format(')'))
                self.tokenizer.advance()  # next thing
            elif self.tokenizer.symbol() in ("-", "~"):
                self.tokenizer.advance()
                self.CompileTerm()
        else:
            self.output.write(WRITE_IDENTIFIER.format(self.tokenizer.identifier()))
            self.tokenizer.advance()  # ( [ . or next thing (if var name)
            if self.tokenizer.tokenType() == "symbol" and self.tokenizer.symbol() in ("[", "(", "."):
                self.output.write(WRITE_SYMBOL.format(self.tokenizer.symbol()))
                if self.tokenizer.symbol() == '[':
                    self.tokenizer.advance()
                    self.CompileExpression()
                    self.output.write(WRITE_SYMBOL.format(']'))
                    self.tokenizer.advance()  # next thing
                elif self.tokenizer.symbol() == '(':
                    self.tokenizer.advance()  # exp or )
                    self.CompileExpressionList()
                    self.output.write(WRITE_SYMBOL.format(')'))
                    self.tokenizer.advance()  # next thing
                elif self.tokenizer.symbol() == '.':
                    self.tokenizer.advance()  # subroutine name
                    self.output.write(WRITE_IDENTIFIER.format(self.tokenizer.identifier()))
                    self.tokenizer.advance()  # (
                    self.output.write(WRITE_SYMBOL.format('('))
                    self.tokenizer.advance()  # exp or )
                    self.CompileExpressionList()
                    self.output.write(WRITE_SYMBOL.format(')'))
                    self.tokenizer.advance()  # next thing
        self.output.write(TERM_END)

    def CompileExpressionList(self):
        """
        compiles expression list
        """
        self.output.write(EXP_LIST_OPEN)
        if not (self.tokenizer.tokenType() == "symbol" and self.tokenizer.symbol() == ')'):
            self.CompileExpression()
            while self.tokenizer.symbol() == ',':
                self.output.write(WRITE_SYMBOL.format(','))
                self.tokenizer.advance()  # expression
                self.CompileExpression()
        self.output.write(EXP_LIST_END)
