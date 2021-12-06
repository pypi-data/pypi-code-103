# Copyright (c) 2010-2021 openpyxl_


from openpyxl_.descriptors.serialisable import Serialisable
from openpyxl_.descriptors import (
    Sequence,
    Alias
)


class AuthorList(Serialisable):

    tagname = "authors"

    author = Sequence(expected_type=str)
    authors = Alias("author")

    def __init__(self,
                 author=(),
                ):
        self.author = author
