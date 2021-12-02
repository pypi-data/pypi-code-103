import pytest

from acondbs.db.sa import sa
from acondbs.models import (
    ProductType,
    Product,
    ProductRelation,
    ProductRelationType,
)


##__________________________________________________________________||
@pytest.fixture
def app(app_empty):

    y = app_empty

    #                              +--------+
    #               --(child)-->   |        |
    #                    |         | child1 |
    #  +---------+  <-(parent)--   |        |
    #  |         |                 +--------+
    #  | parent1 |
    #  |         |                 +--------+
    #  +---------+  --(child)-->   |        |
    #                    |         | child2 |
    #               <-(parent)--   |        |
    #                              +--------+

    type_ = ProductType(name="robot")
    parent1 = Product(name="parent1", type_=type_)
    child1 = Product(name="child1", type_=type_)
    child2 = Product(name="child2", type_=type_)

    relation_type_parent = ProductRelationType(name="parent")
    relation_type_child = ProductRelationType(name="child")
    relation_type_parent.reverse = relation_type_child

    # parent1 --(child)--> child1
    relation_parent1_to_child1 = ProductRelation()
    relation_parent1_to_child1.type_ = relation_type_child
    relation_parent1_to_child1.self_ = parent1
    relation_parent1_to_child1.other = child1

    ## the reverse relation child1 --(parent)--> parent1 will be
    ## automatically set

    # parent1 --(child)--> child2
    relation_parent1_to_child2 = ProductRelation()
    relation_parent1_to_child2.type_ = relation_type_child
    relation_parent1_to_child2.self_ = parent1
    relation_parent1_to_child2.other = child2

    ## the reverse relation child2 --(parent)--> parent1 will be
    ## automatically set

    # commit
    with y.app_context():
        sa.session.add(parent1)
        sa.session.commit()
    yield y


##__________________________________________________________________||
