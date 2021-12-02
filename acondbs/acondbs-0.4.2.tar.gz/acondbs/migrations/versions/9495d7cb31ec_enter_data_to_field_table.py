"""enter data to field table

Revision ID: 9495d7cb31ec
Revises: 097c6676314c
Create Date: 2021-09-22 19:09:48.564031

"""
from alembic import op

from sqlalchemy.orm.session import Session

import datetime

from sqlalchemy import MetaData
from flask_sqlalchemy import SQLAlchemy

import enum


# revision identifiers, used by Alembic.
revision = '9495d7cb31ec'
down_revision = '097c6676314c'
branch_labels = None
depends_on = None

#
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    # "ck": "ck_%(table_name)s_%(constraint_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
metadata = MetaData(naming_convention=convention)

sa = SQLAlchemy(metadata=metadata)


class ProductType(sa.Model):
    __tablename__ = "product_types"
    type_id = sa.Column(sa.Integer(), primary_key=True)
    name = sa.Column(sa.Text(), nullable=False, unique=True, index=True)
    order = sa.Column(sa.Integer())
    indef_article = sa.Column(sa.Text())
    singular = sa.Column(sa.Text())
    plural = sa.Column(sa.Text())
    icon = sa.Column(sa.Text())


class FieldType(enum.Enum):
    # SQLAlchemy generic types: https://docs.sqlalchemy.org/en/14/core/type_basics.html#generic-types
    UnicodeText = 1
    Boolean = 2
    Integer = 3
    Float = 4
    Date = 5
    DateTime = 6
    Time = 7


class Field(sa.Model):
    __tablename__ = "field"
    field_id = sa.Column(sa.Integer(), primary_key=True)
    name = sa.Column(sa.UnicodeText(), nullable=False)
    type_ = sa.Column(sa.Enum(FieldType), nullable=False)

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.name!r}>"


class TypeFieldAssociation(sa.Model):
    __tablename__ = "type_field_association"
    type_id = sa.Column(
        #
        sa.Integer(),
        sa.ForeignKey("product_types.type_id"),
        primary_key=True,
    )
    field_id = sa.Column(
        #
        sa.Integer(),
        sa.ForeignKey("field.field_id"),
        primary_key=True,
    )
    type_ = sa.relationship(
        "ProductType",
        backref=sa.backref("fields", cascade="all, delete-orphan"),
    )
    field = sa.relationship(
        "Field",
        backref=sa.backref("entry_types", cascade="all, delete-orphan"),
    )

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.type_.name!r} {self.field.name!r}>"


#


def upgrade():
    session = Session(bind=op.get_bind())

    product_types = session.query(ProductType).all()
    if not product_types:
        return

    fields = [
        Field(name="contact", type_=FieldType.UnicodeText),
        Field(name="produced_by", type_=FieldType.UnicodeText),
        Field(name="date_produced", type_=FieldType.Date)
    ]

    with session.no_autoflush:
        for product_type in product_types:
            product_type.fields = [TypeFieldAssociation(field=f) for f in fields]
    session.commit()

def downgrade():
    pass
