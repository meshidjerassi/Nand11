"""
Our program parses a Jack file, breaks it down into it's 5 components and
creates an XML file according to the tokenized types
"""

import glob
import os
import JackTokenizer as jt
import CompilationEngine as ce
from sys import argv


def main(path):
    """
    Creates tokenizer and compilation engine objects and calls compile class on each.
    :param path: file path
    :return: void
    """
    directory = []
    if os.path.isdir(path):
        directory = glob.iglob(os.path.join(path, "*.jack"))
    else:
        directory.append(path)
    for file in directory:
        with open(file, 'r') as f:
            tokenizer = jt.JackTokenizer(f)
            with open(file[:-4] + "xml", 'w') as output:
                cEngine = ce.CompilationEngine(tokenizer, output)
                cEngine.CompileClass()


if __name__ == "__main__":
    main(argv[1])
