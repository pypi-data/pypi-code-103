# Copyright (c) 2010-2021 openpyxl_

from openpyxl_.descriptors.serialisable import Serialisable
from openpyxl_.descriptors.excel import Relation


class Related(Serialisable):

    id = Relation()


    def __init__(self, id=None):
        self.id = id


    def to_tree(self, tagname, idx=None):
        return super(Related, self).to_tree(tagname)
