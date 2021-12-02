import pytest

from acondbs import ops


##__________________________________________________________________||
@pytest.fixture
def app(app_users):

    y = app_users

    # map1 -> beam1
    #            |
    #            +---> beam2
    #
    # map2
    # map3

    with y.app_context():
        ops.create_product_relation_type(
            type_={"type_id": 1, "name": "parent"},
            reverse={"type_id": 2, "name": "child"},
        )

        ops.create_product_type(type_id=1, name="map")
        ops.create_product_type(type_id=2, name="beam")

        ops.commit()

    with y.app_context():
        ops.create_product(
            product_id=1,
            type_id=1,
            name="map1",
        )
        ops.create_product(
            product_id=2,
            type_id=1,
            name="map2",
        )
        ops.create_product(
            product_id=3,
            type_id=1,
            name="map3",
        )
        ops.create_product(
            product_id=4,
            type_id=2,
            name="beam1",
        )
        ops.create_product(
            product_id=5,
            type_id=2,
            name="beam2",
        )
        ops.commit()

    with y.app_context():
        ops.create_product_relation(
            relation_id=2,
            type_id=1,
            self_product_id=4,
            other_product_id=1,
        )
        ops.create_product_relation(
            relation_id=4,
            type_id=1,
            self_product_id=5,
            other_product_id=4,
        )
        ops.commit()

    yield y


##__________________________________________________________________||
