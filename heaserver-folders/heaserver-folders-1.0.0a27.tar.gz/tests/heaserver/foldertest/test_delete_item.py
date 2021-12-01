from .foldertestcase import ItemGetTestCase
from heaserver.service.testcase.mixin import DeleteMixin


class TestDeleteChild(ItemGetTestCase, DeleteMixin):
    pass
