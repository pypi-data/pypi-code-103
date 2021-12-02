import pytest

import datetime

from acondbs import ops


##__________________________________________________________________||
@pytest.fixture
def app(app_users):

    y = app_users

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
        ops.create_field(
            field_id=4,
            name="field_four",
            type_=ops.FieldType.UnicodeText,
        )
        ops.create_field(
            field_id=5,
            name="field_five",
            type_=ops.FieldType.UnicodeText,
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
            name="map1",
            attributes={3: datetime.date(2020, 2, 1)},
        )
        ops.create_product(
            type_id=1,
            name="map2",
            attributes={3: datetime.date(2020, 2, 10)},
        )
        ops.create_product(
            type_id=1,
            name="map3",
            attributes={3: datetime.date(2020, 3, 3)},
        )
        ops.commit()

    yield y


##__________________________________________________________________||
