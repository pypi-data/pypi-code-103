import os.path

from kigo.etl.runtime.registry import reader
from kigo.etl.file import FileReader
from kigo.etl.file import ReaderType


@reader
class TextReader(FileReader):

    __reader_type__ = ReaderType.TEXT

    def __init__(self, path):
        self.path = path

    def read(self):
        with open(self.path, "r") as f:
            check=100000
            for num, line in enumerate(f):
                if check == 0:
                    print(num)
                    check = 100000
                check -= 1
                yield num, line
