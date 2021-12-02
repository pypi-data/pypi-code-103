from sqlalchemy import exc

import pytest

from acondbs.db.sa import sa
from acondbs.models import ProductType, FieldType, Field, TypeFieldAssociation


##__________________________________________________________________||
def test_column(app_empty):
    app = app_empty

    with app.app_context():
        field1 = Field(name="field1", type_=FieldType.UnicodeText)
        type1 = ProductType(name="type1")
        model = TypeFieldAssociation(
            order=123,
            type_=type1,
            field=field1,
        )
        sa.session.add(model)
        sa.session.commit()
        iid = model.iid

    with app.app_context():
        model = TypeFieldAssociation.query.filter_by(iid=iid).one()
        assert model.iid == iid
        assert model.order == 123


def test_repr(app_empty):
    app = app_empty  # noqa: F841

    model = TypeFieldAssociation()
    repr(model)

    field1 = Field(name="field1", type_=FieldType.UnicodeText)
    type1 = ProductType(name="type1")

    model.type_ = type1
    model.field = field1
    repr(model)


##__________________________________________________________________||
def test_relationship(app):
    with app.app_context():
        field1 = Field.query.filter_by(name="field1").one()
        field2 = Field.query.filter_by(name="field2").one()
        type1 = ProductType.query.filter_by(name="type1").one()
        assoc1 = TypeFieldAssociation.query.filter_by(iid=1).one()
        assoc2 = TypeFieldAssociation.query.filter_by(iid=2).one()
        assert type1.fields == [assoc1, assoc2]
        assert field1.entry_types == [assoc1]
        assert field2.entry_types == [assoc2]
        assert assoc1.type_ is type1
        assert assoc1.field is field1
        assert assoc2.type_ is type1
        assert assoc2.field is field2


##__________________________________________________________________||
def test_unique_constraint(app_empty):
    # A type cannot have multiple same field.
    app = app_empty
    with app.app_context():
        field1 = Field(name="field1", type_=FieldType.UnicodeText)
        assoc1 = TypeFieldAssociation(field=field1)
        assoc2 = TypeFieldAssociation(field=field1)
        type1 = ProductType(name="type1", fields=[assoc1, assoc2])
        sa.session.add(type1)
        with pytest.raises(exc.IntegrityError):
            sa.session.commit()


##__________________________________________________________________||
def test_cascade_deleting_type(app):
    """test delete a type

    When a type is deleted, its associations should be automatically
    deleted while the fields themselves should still exist.

    """

    with app.app_context():
        type1 = ProductType.query.filter_by(name="type1").one()
        sa.session.delete(type1)
        sa.session.commit()

    with app.app_context():
        assert ProductType.query.filter_by(name="type1").one_or_none() is None
        assert Field.query.filter_by(name="field1").one()
        assert Field.query.filter_by(name="field2").one()
        associations = TypeFieldAssociation.query.all()
        assert not associations  # emtpy


def test_cascade_updating_type(app):
    with app.app_context():
        type1 = ProductType.query.filter_by(name="type1").one()

        type1.fields = [f for f in type1.fields if f.field.name == "field2"]
        # remove field1

        sa.session.commit()

    with app.app_context():
        field1 = Field.query.filter_by(name="field1").one()
        field2 = Field.query.filter_by(name="field2").one()
        type1 = ProductType.query.filter_by(name="type1").one()
        association2 = TypeFieldAssociation.query.filter_by(type_=type1, field=field2).one()  # fmt: skip
        assert type1.fields == [association2]
        assert field1.entry_types == []
        assert field2.entry_types == [association2]
        assert association2.type_ is type1
        assert association2.field is field2
        assert type1.fields == [association2]
        assert TypeFieldAssociation.query.all() == [association2]
        # association1 is deleted from the DB


##__________________________________________________________________||
def test_nullable_deleting_field(app):
    """test delete a field

    A field cannot be deleted if it is associated

    """

    with app.app_context():
        field1 = Field.query.filter_by(name="field1").one()
        sa.session.delete(field1)
        with pytest.raises(exc.IntegrityError):
            sa.session.commit()

    with app.app_context():
        field1 = Field.query.filter_by(name="field1").one()
        assert field1.entry_types


##__________________________________________________________________||
