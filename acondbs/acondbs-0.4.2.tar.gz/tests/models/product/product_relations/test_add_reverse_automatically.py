import pytest

from itertools import permutations

from acondbs.db.sa import sa
from acondbs.models import (
    ProductType,
    Product,
    ProductRelation,
    ProductRelationType,
)

##__________________________________________________________________||
params = list(permutations([1, 2, 3]))
# i.e., [(1, 2, 3), (1, 3, 2), (2, 1, 3), (2, 3, 1), (3, 1, 2), (3, 2, 1)]

ids = ["-".join(["{}".format(e) for e in p]) for p in params]
# i.e., ['1-2-3', '1-3-2', '2-1-3', '2-3-1', '3-1-2', '3-2-1']


@pytest.mark.parametrize("perm", params, ids=ids)
def test_permutations(app_empty, perm):

    app = app_empty

    #
    # +---------+                 +--------+
    # |         |  --(child)-->   |        |
    # | parent1 |       |         | child1 |
    # |         |  <-(parent)--   |        |
    # +---------+                 +--------+
    #

    type_ = ProductType(name="robot")
    parent1 = Product(name="parent1", type_=type_)
    child1 = Product(name="child1", type_=type_)

    relation_type_parent = ProductRelationType(name="parent")
    relation_type_child = ProductRelationType(name="child")
    relation_type_parent.reverse = relation_type_child
    relation_type_child.reverse = relation_type_parent

    relation_parent1_to_child1 = ProductRelation()

    # set 'type_', 'self_', 'other' in different orders
    # each triggers an event in which a reverse is automatically set
    for p in perm:
        if p == 1:
            relation_parent1_to_child1.type_ = relation_type_child
        elif p == 2:
            relation_parent1_to_child1.self_ = parent1
        elif p == 3:
            relation_parent1_to_child1.other = child1

    with app.app_context():
        sa.session.add(parent1)
        sa.session.commit()

    with app.app_context():
        parent1 = Product.query.filter_by(name="parent1").first()
        child1 = Product.query.filter_by(name="child1").first()

        assert 1 == len(parent1.relations)
        assert 1 == len(child1.relations)

        assert "child" == parent1.relations[0].type_.name
        assert "parent" == child1.relations[0].type_.name

        assert child1 is parent1.relations[0].other

        assert parent1 is child1.relations[0].other

        assert parent1.relations[0] is child1.relations[0].reverse
        assert parent1.relations[0].reverse is child1.relations[0]


##__________________________________________________________________||
@pytest.mark.parametrize("perm", params, ids=ids)
def test_self_reverse_type(app_empty, perm):

    app = app_empty

    #
    # +----------+                 +----------+
    # |          |  --(sibling)--> |          |
    # | sibling1 |       |         | sibling2 |
    # |          |  <-(sibling)--  |          |
    # +----------+                 +----------+
    #

    type_ = ProductType(name="robot")
    sibling1 = Product(name="sibling1", type_=type_)
    sibling2 = Product(name="sibling2", type_=type_)

    relation_type_sibling = ProductRelationType(name="sibling")
    relation_type_sibling.reverse = relation_type_sibling

    relation_sibling1_to_sibling2 = ProductRelation()

    # set 'type_', 'self_', 'other' in different orders
    # each triggers an event in which a reverse is automatically set
    for p in perm:
        if p == 1:
            relation_sibling1_to_sibling2.type_ = relation_type_sibling
        elif p == 2:
            relation_sibling1_to_sibling2.self_ = sibling1
        elif p == 3:
            relation_sibling1_to_sibling2.other = sibling2

    with app.app_context():
        sa.session.add(sibling1)
        sa.session.commit()

    with app.app_context():
        sibling1 = Product.query.filter_by(name="sibling1").first()
        sibling2 = Product.query.filter_by(name="sibling2").first()

        assert 1 == len(sibling1.relations)
        assert 1 == len(sibling2.relations)

        assert "sibling" == sibling1.relations[0].type_.name
        assert "sibling" == sibling2.relations[0].type_.name

        assert sibling1.relations[0].type_ is sibling2.relations[0].type_

        assert sibling2 is sibling1.relations[0].other

        assert sibling1 is sibling2.relations[0].other

        assert sibling1.relations[0] is sibling2.relations[0].reverse
        assert sibling1.relations[0].reverse is sibling2.relations[0]


##__________________________________________________________________||
@pytest.mark.xfail(reason="events won't be triggered by foreign keys")
def test_id(app_empty):

    # This test doesn't pass because the "set" events to the
    # relationships won't be triggered when the foreign keys are set.

    # It might be possible to pass this test with before_flush().
    # Useful links about before_flush():
    # https://docs.sqlalchemy.org/en/14/orm/session_events.html#persistence-events
    # https://stackoverflow.com/questions/36731020/sqlalchemy-orm-event-hook-for-attribute-persisted

    app = app_empty

    #
    # +---------+                 +--------+
    # |         |  --(child)-->   |        |
    # | parent1 |       |         | child1 |
    # |         |  <-(parent)--   |        |
    # +---------+                 +--------+
    #

    type_ = ProductType(name="robot")
    parent1 = Product(product_id=1, name="parent1", type_=type_)
    child1 = Product(product_id=2, name="child1", type_=type_)

    relation_type_parent = ProductRelationType(type_id=1, name="parent")
    relation_type_child = ProductRelationType(type_id=2, name="child")
    relation_type_parent.reverse = relation_type_child

    relation_parent1_to_child1 = ProductRelation(
        type_id=2, self_product_id=1, other_product_id=2
    )

    with app.app_context():
        sa.session.add(parent1)
        sa.session.add(child1)
        sa.session.add(relation_type_parent)
        sa.session.add(relation_parent1_to_child1)
        sa.session.flush()
        sa.session.commit()

    with app.app_context():
        parent1 = Product.query.filter_by(name="parent1").first()
        child1 = Product.query.filter_by(name="child1").first()

        assert 1 == len(parent1.relations)
        assert 1 == len(child1.relations)

        assert "child" == parent1.relations[0].type_.name
        assert "parent" == child1.relations[0].type_.name

        assert child1 is parent1.relations[0].other

        assert parent1 is child1.relations[0].other

        assert parent1.relations[0] is child1.relations[0].reverse
        assert parent1.relations[0].reverse is child1.relations[0]


##__________________________________________________________________||
def test_attach_to_self(app_empty):

    app = app_empty

    #
    # +---------+                 +--------+
    # |         |  --(child)-->   |        |
    # | parent1 |       |         | child1 |
    # |         |  <-(parent)--   |        |
    # +---------+                 +--------+
    #

    type_ = ProductType(name="robot")
    parent1 = Product(product_id=1, name="parent1", type_=type_)
    child1 = Product(product_id=2, name="child1", type_=type_)

    relation_type_parent = ProductRelationType(type_id=1, name="parent")
    relation_type_child = ProductRelationType(type_id=2, name="child")
    relation_type_parent.reverse = relation_type_child

    relation_parent1_to_child1 = ProductRelation(
        type_=relation_type_child, other=child1
    )

    parent1.relations = [relation_parent1_to_child1]

    with app.app_context():
        sa.session.add(parent1)
        sa.session.add(child1)
        sa.session.add(relation_type_parent)
        sa.session.add(relation_parent1_to_child1)
        sa.session.flush()
        sa.session.commit()

    with app.app_context():
        parent1 = Product.query.filter_by(name="parent1").first()
        child1 = Product.query.filter_by(name="child1").first()

        assert 1 == len(parent1.relations)
        assert 1 == len(child1.relations)

        assert "child" == parent1.relations[0].type_.name
        assert "parent" == child1.relations[0].type_.name

        assert child1 is parent1.relations[0].other

        assert parent1 is child1.relations[0].other

        assert parent1.relations[0] is child1.relations[0].reverse
        assert parent1.relations[0].reverse is child1.relations[0]


##__________________________________________________________________||
