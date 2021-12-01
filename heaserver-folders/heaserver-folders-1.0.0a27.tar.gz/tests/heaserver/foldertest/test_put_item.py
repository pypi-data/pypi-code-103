from .foldertestcase import ItemGetTestCase
from heaserver.service.testcase.mixin import PutMixin


class TestPutItem(ItemGetTestCase, PutMixin):
    pass
