import re
import LexicalElements as le

NEW_LINE = '\n'
COMMENT = "//"
MULTI_LINE_COMMENT_START = "/*"
MULTI_LINE_COMMENT_END = "*/"


class JackTokenizer:
    """
    Handle one or multiple VM files, parses then and splits them into lines to send to the codeWriter obj
    """

    def __init__(self, f):
        """
        constructor, creates an array of parsed lines from the given path
        :param f: opened file
        """
        self.index = -1
        self.__tokenized = []
        file = self.__readFile(f)
        while self.__commentHandler(file, COMMENT, NEW_LINE):
            file = self.__commentHandler(file, COMMENT, NEW_LINE)
        file = file.replace(NEW_LINE, " ")
        while self.__commentHandler(file, MULTI_LINE_COMMENT_START, MULTI_LINE_COMMENT_END):
            file = self.__commentHandler(file, MULTI_LINE_COMMENT_START, MULTI_LINE_COMMENT_END)
        self.__regexMaster(file)

    def __readFile(self, file):
        line = file.readline()
        string = line
        while line:
            line = file.readline()
            string += line + " " + NEW_LINE
        return string

    def __commentHandler(self, file, start, end):
        ind = file.find(start)
        if ind == -1:
            return ""
        else:
            temp = file[:ind]
            file = file[ind:]
            ind = file.find(end)
            file = temp + file[ind + len(end):]
        return file

    def __regexMaster(self, file):
        reg = le.regex_builder()
        pattern = re.compile(reg)
        while file:
            m = re.match(pattern, file)
            if m is not None:
                for i in range(1, 6):
                    if m.group() == m.group(i):
                        self.__tokenized.append((m.group(), le.GROUP_DICT[i]))
                file = file[m.span()[1]:]
            else:
                file = file[1:]

    def hasMoreTokens(self):
        return self.index < len(self.__tokenized)-1

    def advance(self):
        self.index += 1

    def tokenType(self):
        return self.__tokenized[self.index][1]

    def keyWord(self):
        if self.__tokenized[self.index][1] == le.GROUP_DICT[2]:
            return self.__tokenized[self.index][0]

    def symbol(self):
        if self.__tokenized[self.index][1] == le.GROUP_DICT[3]:
            ret = self.__tokenized[self.index][0]
            if ret in le.HTML_TRANSLATOR:
                return le.HTML_TRANSLATOR[ret]
            return ret

    def identifier(self):
        if self.__tokenized[self.index][1] == le.GROUP_DICT[4]:
            return self.__tokenized[self.index][0]

    def intVal(self):
        if self.__tokenized[self.index][1] == le.GROUP_DICT[5]:
            return self.__tokenized[self.index][0]

    def stringVal(self):
        if self.__tokenized[self.index][1] == le.GROUP_DICT[1]:
            string = self.__tokenized[self.index][0]
            return string[1:-1]
