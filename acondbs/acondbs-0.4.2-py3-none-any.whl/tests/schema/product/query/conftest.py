import datetime

import pytest

from acondbs import ops


##__________________________________________________________________||
@pytest.fixture
def app(app_users):

    y = app_users

    # Relation types:
    #   parent <-> child
    #   plaintiff <-> defendant

    # Products and Relations:
    #   map1 -> beam1
    #     |        |
    #     +--------+---> beam2
    #
    #   map2
    #   map3

    with y.app_context():
        ops.create_product_relation_type(
            type_={
                "type_id": 1,
                "name": "parent",
                "indef_article": "a",
                "singular": "parent",
                "plural": "parents",
            },
            reverse={
                "type_id": 2,
                "name": "child",
                "indef_article": "a",
                "singular": "child",
                "plural": "children",
            },
        )
        ops.create_product_relation_type(
            type_={
                "type_id": 3,
                "name": "plaintiff",
                "indef_article": "a",
                "singular": "plaintiff",
                "plural": "plaintiffs",
            },
            reverse={
                "type_id": 4,
                "name": "defendant",
                "indef_article": "a",
                "singular": "defendant",
                "plural": "defendants",
            },
        )
        ops.commit()

    with y.app_context():
        ops.create_field(
            field_id=1,
            name="contact",
            type_=ops.FieldType.UnicodeText,
        )
        ops.create_field(
            field_id=2,
            name="produced_by",
            type_=ops.FieldType.UnicodeText,
        )
        ops.create_field(
            field_id=3,
            name="date_produced",
            type_=ops.FieldType.Date,
        )
        ops.commit()

    with y.app_context():
        ops.create_product_type(
            type_id=1,
            name="map",
            order=2,
            indef_article="a",
            singular="map",
            plural="maps",
            icon="mdi-map",
            field_ids=[1, 2, 3],
        )
        ops.create_product_type(
            type_id=2,
            name="beam",
            order=1,
            indef_article="a",
            singular="beam",
            plural="beams",
            icon="mdi-spotlight-beam",
            field_ids=[1, 2, 3],
        )
        ops.commit()

    with y.app_context():
        ops.create_product(
            type_id=1,
            product_id=1,
            name="map1",
            attributes={3: datetime.date(2020, 2, 1)},
            paths=["site2:/another/way/map1"],
        )
        ops.create_product(
            type_id=1,
            product_id=2,
            name="map2",
            attributes={3: datetime.date(2020, 2, 10)},
            paths=["site1:/path/to/map2"],
        )
        ops.create_product(
            type_id=1,
            product_id=3,
            name="map3",
            attributes={3: datetime.date(2020, 3, 19)},
            paths=["site1:/path/to/map3", "site2:/another/way/map3"],
        )
        ops.create_product(
            type_id=2,
            product_id=4,
            name="beam1",
            attributes={3: datetime.date(2020, 2, 5)},
            paths=["site1:/path/to/beam1", "site2:/another/way/beam1"],
        )
        ops.create_product(
            type_id=2,
            product_id=5,
            name="beam2",
            attributes={3: datetime.date(2020, 3, 4)},
            paths=["site1:/path/to/beam2"],
        )
        ops.commit()

    with y.app_context():
        ops.create_product_file_path(
            product_id=1,
            path="site1:/path/to/map1",
            note="sample comment",
        )
        ops.commit()

    with y.app_context():
        ops.create_product_relation(
            type_id=1,
            self_product_id=4,
            other_product_id=1,
        )
        ops.create_product_relation(
            type_id=1,
            self_product_id=5,
            other_product_id=1,
        )
        ops.create_product_relation(
            type_id=1,
            self_product_id=5,
            other_product_id=4,
        )
        ops.commit()

    yield y

##__________________________________________________________________||
