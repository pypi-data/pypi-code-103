# Copyright (c) 2010-2021 openpyxl_

from openpyxl_.descriptors.serialisable import Serialisable
from openpyxl_.descriptors import (
    Sequence
)
from openpyxl_.descriptors.excel import (
    Relation,
)

class ExternalReference(Serialisable):

    tagname = "externalReference"

    id = Relation()

    def __init__(self, id):
        self.id = id
