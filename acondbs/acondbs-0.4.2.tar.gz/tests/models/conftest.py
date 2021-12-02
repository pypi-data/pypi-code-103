import pytest

from acondbs import create_app
from acondbs.db.ops import define_tables


##__________________________________________________________________||
@pytest.fixture
def app_empty():
    database_uri = "sqlite:///:memory:"
    y = create_app(SQLALCHEMY_DATABASE_URI=database_uri)
    with y.app_context():
        define_tables()
    yield y


##__________________________________________________________________||
