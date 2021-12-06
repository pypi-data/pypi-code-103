# Copyright (c) 2010-2021 openpyxl_

from openpyxl_.xml.constants import CHART_NS

from openpyxl_.descriptors.serialisable import Serialisable
from openpyxl_.descriptors.excel import Relation


class ChartRelation(Serialisable):

    tagname = "chart"
    namespace = CHART_NS

    id = Relation()

    def __init__(self, id):
        self.id = id
