# Copyright (c) 2010-2021 openpyxl_

from openpyxl_.descriptors import (
    Bool,
    String,
    Typed
)
from openpyxl_.descriptors.serialisable import Serialisable
from openpyxl_.styles import Color


class ChartsheetProperties(Serialisable):
    tagname = "sheetPr"

    published = Bool(allow_none=True)
    codeName = String(allow_none=True)
    tabColor = Typed(expected_type=Color, allow_none=True)

    __elements__ = ('tabColor',)

    def __init__(self,
                 published=None,
                 codeName=None,
                 tabColor=None,
                 ):
        self.published = published
        self.codeName = codeName
        self.tabColor = tabColor
