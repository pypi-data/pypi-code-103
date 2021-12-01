from .foldertestcase import ItemGetTestCase
from heaserver.service.testcase.mixin import GetOneMixin


class TestGetItem(ItemGetTestCase, GetOneMixin):
    pass
