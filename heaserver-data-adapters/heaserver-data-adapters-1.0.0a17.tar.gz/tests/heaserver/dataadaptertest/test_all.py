from .dataadaptertestcase import DataAdapterTestCase
from heaserver.service.testcase.mixin import GetOneMixin, GetAllMixin, PostMixin, PutMixin, DeleteMixin


class TestGetComponent(DataAdapterTestCase, GetOneMixin):
    pass


class TestGetAllComponents(DataAdapterTestCase, GetAllMixin):
    pass


class TestPostComponent(DataAdapterTestCase, PostMixin):
    pass


class TestPutComponent(DataAdapterTestCase, PutMixin):
    pass


class TestDeleteComponent(DataAdapterTestCase, DeleteMixin):
    pass
