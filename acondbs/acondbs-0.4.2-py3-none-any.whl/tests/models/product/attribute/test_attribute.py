import datetime
from sqlalchemy.orm import aliased

import sqlparse

import pytest

from acondbs.db.sa import sa

from acondbs.models import (
    Product,
    ProductType,
    FieldType,
    Field,
    TypeFieldAssociation,
    AttributeUnicodeText,
    AttributeBoolean,
    AttributeInteger,
    AttributeFloat,
    AttributeDate,
    AttributeDateTime,
    AttributeTime,
)


##__________________________________________________________________||
params = [
    pytest.param(
        FieldType.UnicodeText,
        AttributeUnicodeText,
        "value1 値１",
        id="UnicodeText",
    ),
    pytest.param(FieldType.Boolean, AttributeBoolean, True, id="Boolean"),
    pytest.param(FieldType.Integer, AttributeInteger, -512442, id="Integer"),
    pytest.param(FieldType.Float, AttributeFloat, 3.14592613, id="Float"),
    pytest.param(
        FieldType.Date, AttributeDate, datetime.date(2020, 2, 1), id="Date"
    ),
    pytest.param(
        FieldType.DateTime,
        AttributeDateTime,
        datetime.datetime(2020, 2, 1, 9, 10, 25),
        id="DateTime",
    ),
    pytest.param(
        FieldType.Time, AttributeTime, datetime.time(9, 10, 25), id="Time"
    ),
]


@pytest.mark.parametrize("field_type, AttributeClass, value", params)
def test_repr(app_empty, field_type, AttributeClass, value):
    app = app_empty  # noqa: F841

    attr1 = AttributeClass(value=value)
    repr(attr1)

    field1 = Field(name="attr1", type_=field_type)
    assoc1 = TypeFieldAssociation(field=field1)
    attr1.type_field_association = assoc1
    attr1.field = field1
    repr(attr1)


@pytest.mark.parametrize("field_type, AttributeClass, value", params)
def test_obj(app_empty, field_type, AttributeClass, value):
    app = app_empty  # noqa: F841
    field = Field(name="field1", type_=field_type)
    assoc = TypeFieldAssociation(field=field)
    attr = AttributeClass(
        type_field_association=assoc, field=field, value=value
    )  # noqa: F841


@pytest.mark.parametrize("field_type, AttributeClass, value", params)
def test_commit(app_empty, field_type, AttributeClass, value):
    app = app_empty
    with app.app_context():
        field = Field(name="field1", type_=field_type)
        assoc = TypeFieldAssociation(field=field)
        product_type = ProductType(name="map")
        product_type.fields = [assoc]
        sa.session.add(product_type)
        sa.session.commit()

    with app.app_context():
        product_type = ProductType.query.filter_by(name="map").one()
        assoc = product_type.fields[0]
        field = assoc.field
        product = Product(name="product1", type_=product_type)
        attr = AttributeClass(
            product=product,
            type_field_association=assoc,
            field=field,
            value=value,
        )
        sa.session.add(attr)
        sa.session.commit()

    with app.app_context():
        attr = AttributeClass.query.one()
        assert attr.__class__ is AttributeClass
        assert attr.type_field_association.field.name == "field1"
        assert attr.type_field_association.field.type_ is field_type
        assert attr.field.name == "field1"
        assert attr.field.type_ is field_type
        assert attr.value == value
        assert getattr(attr.product, AttributeClass.backref_column) == [attr]
        assert getattr(attr.field, AttributeClass.backref_column) == [attr]


##__________________________________________________________________||
def test_filter(app):

    with app.app_context():
        expected = Product.query.filter_by(product_id=1).one()
        print(expected.attributes_unicode_text[0].type_field_association)
        query = (
            Product.query.join(AttributeUnicodeText)
            .join(TypeFieldAssociation)
            .join(Field)
            .filter(
                Field.name == "attr1", AttributeUnicodeText.value == "value1"
            )
        )
        # print(sqlparse.format(str(query), reindent=True))
        actual = query.one()
        assert actual is expected

        # another way
        query = (
            Product.query.join(AttributeUnicodeText)
            .filter_by(value="value1")
            .join(TypeFieldAssociation)
            .join(Field)
            .filter_by(name="attr1")
        )
        # print(sqlparse.format(str(query), reindent=True))
        actual = query.one()
        assert actual is expected


def test_order(app):

    with app.app_context():
        map1 = Product.query.filter_by(product_id=1).one()
        map2 = Product.query.filter_by(product_id=2).one()
        map3 = Product.query.filter_by(product_id=3).one()

        expected = [map3, map2, map1]

        query = (
            Product.query.join(ProductType)
            .filter_by(name="map")
            .join(AttributeDate)
            .join(TypeFieldAssociation)
            .join(Field)
            .filter_by(name="date_produced")
            .order_by(AttributeDate.value.desc())
        )

        # print(sqlparse.format(str(query), reindent=True))

        actual = query.all()

        assert actual == expected


##__________________________________________________________________||
def test_order_nested(app_empty):
    app = app_empty

    field_attr1 = Field(name="attr1", type_=FieldType.UnicodeText)
    field_attr2 = Field(name="attr2", type_=FieldType.UnicodeText)
    Map = ProductType(type_id=1, name="map")
    assoc1 = TypeFieldAssociation(field=field_attr1)
    assoc2 = TypeFieldAssociation(field=field_attr2)
    Map.fields = [assoc1, assoc2]

    map1 = Product(product_id=1, name="map1", type_=Map)
    map2 = Product(product_id=2, name="map2", type_=Map)
    map3 = Product(product_id=3, name="map3", type_=Map)
    map4 = Product(product_id=4, name="map4", type_=Map)
    map5 = Product(product_id=5, name="map5", type_=Map)

    AttributeUnicodeText(
        product=map1,
        type_field_association=assoc1,
        field=field_attr1,
        value="1",
    )
    AttributeUnicodeText(
        product=map2,
        type_field_association=assoc1,
        field=field_attr1,
        value="2",
    )
    AttributeUnicodeText(
        product=map3,
        type_field_association=assoc1,
        field=field_attr1,
        value="1",
    )
    AttributeUnicodeText(
        product=map4,
        type_field_association=assoc1,
        field=field_attr1,
        value="2",
    )
    AttributeUnicodeText(
        product=map5,
        type_field_association=assoc1,
        field=field_attr1,
        value="1",
    )

    AttributeUnicodeText(
        product=map1,
        type_field_association=assoc2,
        field=field_attr2,
        value="b",
    )
    AttributeUnicodeText(
        product=map2,
        type_field_association=assoc2,
        field=field_attr2,
        value="a",
    )
    AttributeUnicodeText(
        product=map3,
        type_field_association=assoc2,
        field=field_attr2,
        value="c",
    )
    AttributeUnicodeText(
        product=map4,
        type_field_association=assoc2,
        field=field_attr2,
        value="b",
    )
    AttributeUnicodeText(
        product=map5,
        type_field_association=assoc2,
        field=field_attr2,
        value="a",
    )

    with app.app_context():
        sa.session.add(Map)
        sa.session.commit()

    with app.app_context():

        map1 = Product.query.filter_by(product_id=1).one()
        map2 = Product.query.filter_by(product_id=2).one()
        map3 = Product.query.filter_by(product_id=3).one()
        map4 = Product.query.filter_by(product_id=4).one()
        map5 = Product.query.filter_by(product_id=5).one()

        expected = [map2, map4, map5, map1, map3]

        # ORM Alias: https://docs.sqlalchemy.org/en/14/tutorial/data_select.html#orm-entity-aliases
        # refer to the same table multiple times
        AliasedAttributeUnicodeText1 = aliased(AttributeUnicodeText)
        AliasedAttributeUnicodeText2 = aliased(AttributeUnicodeText)

        AliasedTypeFieldAssociation1 = aliased(TypeFieldAssociation)
        AliasedTypeFieldAssociation2 = aliased(TypeFieldAssociation)

        AliasedField1 = aliased(Field)
        AliasedField2 = aliased(Field)

        # sort descending order of attr1 then ascending order of attr2
        query = (
            Product.query.join(ProductType)
            .filter_by(name="map")
            .join(AliasedAttributeUnicodeText1)
            .join(AliasedTypeFieldAssociation1)
            .join(AliasedField1)
            .filter_by(name="attr1")
            .order_by(AliasedAttributeUnicodeText1.value.desc())
            .join(
                AliasedAttributeUnicodeText2, Product.attributes_unicode_text
            )
            .join(AliasedTypeFieldAssociation2)
            .join(AliasedField2)
            .filter_by(name="attr2")
            .order_by(AliasedAttributeUnicodeText2.value)
        )

        # print(sqlparse.format(str(query), reindent=True))

        actual = query.all()

        assert actual == expected


##__________________________________________________________________||
def test_delte_orphan_product(app_empty):
    app = app_empty

    with app.app_context():
        field1 = Field(name="field1", type_=FieldType.UnicodeText)
        assoc1 = TypeFieldAssociation(field=field1)
        type1 = ProductType(type_id=1, name="type1", fields=[assoc1])

        product1 = Product(name="product1", type_=type1)
        field1_attribute_class = field1.type_.attribute_class
        attr1 = field1_attribute_class(
            product=product1,
            type_field_association=assoc1,
            field=field1,
            value="value1",
        )

        sa.session.add(product1)
        sa.session.commit()

        product1_id = product1.product_id
        attr1_id = attr1.iid

    with app.app_context():
        product1 = Product.query.filter_by(product_id=product1_id).one()
        sa.session.delete(product1)
        sa.session.commit()

    with app.app_context():
        product1 = Product.query.filter_by(
            product_id=product1_id
        ).one_or_none()
        attr1 = field1_attribute_class.query.filter_by(
            iid=attr1_id
        ).one_or_none()
        assert product1 is None
        assert attr1 is None


def test_delte_orphan_type_field_association_and_field(app_empty):
    app = app_empty

    with app.app_context():
        field1 = Field(name="field1", type_=FieldType.UnicodeText)
        assoc1 = TypeFieldAssociation(field=field1)
        type1 = ProductType(type_id=1, name="type1", fields=[assoc1])

        product1 = Product(name="product1", type_=type1)
        field1_attribute_class = field1.type_.attribute_class
        attr1 = field1_attribute_class(
            product=product1,
            type_field_association=assoc1,
            field=field1,
            value="value1",
        )

        sa.session.add(product1)
        sa.session.commit()

        field1_id = field1.field_id
        assoc1_id = assoc1.iid
        product1_id = product1.product_id
        attr1_id = attr1.iid

    with app.app_context():
        assoc1 = TypeFieldAssociation.query.filter_by(iid=assoc1_id).one()
        field1 = Field.query.filter_by(field_id=field1_id).one()
        sa.session.delete(assoc1)
        sa.session.delete(field1)
        sa.session.commit()

    with app.app_context():
        product1 = Product.query.filter_by(product_id=product1_id).one()
        attr1 = field1_attribute_class.query.filter_by(
            iid=attr1_id
        ).one_or_none()
        assert attr1 is None


##__________________________________________________________________||
