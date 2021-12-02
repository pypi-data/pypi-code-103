import pytest

import datetime

from acondbs.db.sa import sa
from acondbs.models import (
    ProductType,
    FieldType,
    Field,
    TypeFieldAssociation,
    Product,
)


##__________________________________________________________________||
@pytest.fixture
def app(app_empty):

    y = app_empty

    # create fields
    field1 = Field(name="attr1", type_=FieldType.UnicodeText)
    field2 = Field(name="date_produced", type_=FieldType.Date)
    field3 = Field(name="time_posted", type_=FieldType.DateTime)
    fields = [field1, field2, field3]

    # create product types
    Map = ProductType(
        type_id=1,
        name="map",
        order=2,
        indef_article="a",
        singular="map",
        plural="maps",
        icon="mdi-map",
        fields=[TypeFieldAssociation(field=f) for f in fields],
    )
    Beam = ProductType(
        type_id=2,
        name="beam",
        order=1,
        indef_article="a",
        singular="beam",
        plural="beams",
        icon="mdi-spotlight-beam",
        fields=[TypeFieldAssociation(field=f) for f in fields],
    )

    # create products
    map1 = Product(product_id=1, name="map1", type_=Map)
    values = (
        "value1",
        datetime.date(2020, 2, 1),
        datetime.datetime(2020, 2, 1, 9, 10, 25),
    )
    for assoc, value in zip(Map.fields, values):
        assoc.field.type_.attribute_class(
            product=map1,
            type_field_association=assoc,
            field=assoc.field,
            value=value,
        )

    map2 = Product(product_id=2, name="map2", type_=Map)
    values = (
        "value2",
        datetime.date(2020, 2, 10),
        datetime.datetime(2020, 2, 10, 13, 20, 2),
    )
    for assoc, value in zip(Map.fields, values):
        assoc.field.type_.attribute_class(
            product=map2,
            type_field_association=assoc,
            field=assoc.field,
            value=value,
        )

    map3 = Product(product_id=3, name="map3", type_=Map)
    values = (
        "value3",
        datetime.date(2020, 3, 19),
        datetime.datetime(2020, 3, 20, 8, 45, 30),
    )
    for assoc, value in zip(Map.fields, values):
        assoc.field.type_.attribute_class(
            product=map3,
            type_field_association=assoc,
            field=assoc.field,
            value=value,
        )

    beam1 = Product(product_id=4, name="beam1", type_=Beam)
    values = (
        "value4",
        datetime.date(2020, 2, 5),
        datetime.datetime(2020, 2, 5, 12, 3, 48),
    )
    for assoc, value in zip(Map.fields, values):
        assoc.field.type_.attribute_class(
            product=beam1,
            type_field_association=assoc,
            field=assoc.field,
            value=value,
        )

    beam2 = Product(product_id=5, name="beam2", type_=Beam)
    values = (
        "value5",
        datetime.date(2020, 3, 4),
        datetime.datetime(2020, 3, 4, 19, 22, 5),
    )
    for assoc, value in zip(Map.fields, values):
        assoc.field.type_.attribute_class(
            product=beam2,
            type_field_association=assoc,
            field=assoc.field,
            value=value,
        )

    with y.app_context():
        sa.session.add(Map)
        sa.session.add(Beam)
        sa.session.commit()

    yield y


##__________________________________________________________________||
