# Copyright (c) 2010-2021 openpyxl_

from openpyxl_.descriptors.serialisable import Serialisable
from openpyxl_.descriptors.excel import Relation


class Drawing(Serialisable):

    tagname = "drawing"

    id = Relation()

    def __init__(self, id=None):
        self.id = id
