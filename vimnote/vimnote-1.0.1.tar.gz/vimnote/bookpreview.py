from .preview import Preview
from typing import List
import os
import logging

class BookPreview(Preview):
    def __init__(self, pad):
        super().__init__(pad)
        self.content: List[str] = []

    def update(self, row: int, book_dir):
        super().update(row)
        self.content = map(lambda f: os.path.splitext(f)[0],
                sorted(
                    filter(lambda f: os.path.splitext(f)[1] == '.vmnt',
                        os.listdir(book_dir)),
                    key=lambda f: os.stat(os.path.join(book_dir, f)).st_mtime_ns, reverse=True)[:self.pad.getmaxyx()[0] - 1])

