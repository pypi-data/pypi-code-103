import pytest

from acondbs.db.sa import sa
from acondbs.models import ProductRelationType


##__________________________________________________________________||
@pytest.fixture
def app(app_empty):

    y = app_empty

    #
    #  +--------+                +-------+
    #  |        | --(reverse)->  |       |
    #  | parent |                | child |
    #  |        | <-(reverse)--  |       |
    #  +--------+                +-------+
    #

    #
    #  +------- -+
    #  |         | --(reverse)-+
    #  | sibling |             |
    #  |         | <-----------+
    #  +------ --+
    #

    parent = ProductRelationType(name="parent")
    child = ProductRelationType(name="child")
    parent.reverse = child
    assert child.reverse == parent

    sibling = ProductRelationType(name="sibling")
    sibling.reverse = sibling

    # commit
    with y.app_context():
        sa.session.add(parent)
        sa.session.add(sibling)
        sa.session.commit()
    yield y


##__________________________________________________________________||
def test_reverse(app):

    with app.app_context():
        parent = ProductRelationType.query.filter_by(name="parent").one()
        child = ProductRelationType.query.filter_by(name="child").one()

        assert child is parent.reverse
        assert parent is child.reverse


def test_self_reverse(app):

    with app.app_context():
        sibling = ProductRelationType.query.filter_by(name="sibling").one()
        assert sibling is sibling.reverse


def test_cascade(app):

    # delete parent
    with app.app_context():
        parent = ProductRelationType.query.filter_by(name="parent").one()
        sa.session.delete(parent)
        sa.session.commit()

    # assert
    with app.app_context():
        parent = ProductRelationType.query.filter_by(
            name="parent"
        ).one_or_none()
        child = ProductRelationType.query.filter_by(name="child").one_or_none()

        assert parent is None
        assert child is None


##__________________________________________________________________||
