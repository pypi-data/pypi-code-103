import pytest

from acondbs import ops

@pytest.fixture
def app(app_users):
    y = app_users

    with y.app_context():
        ops.create_log(level="DEBUG", message="A debug message!")
        ops.create_log(level="ERROR", message="An error message!")
        ops.commit()

    yield y
