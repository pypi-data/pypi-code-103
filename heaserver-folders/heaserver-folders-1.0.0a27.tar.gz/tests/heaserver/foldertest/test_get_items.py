from .foldertestcase import ItemGetTestCase
from heaserver.service.testcase.mixin import GetAllMixin


class TestGetItems(ItemGetTestCase, GetAllMixin):
    pass
