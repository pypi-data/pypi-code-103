"""copy attributes

Revision ID: 35e6ddccd22a
Revises: 1583f2de9f39
Create Date: 2021-09-23 20:35:53.480108

"""
from alembic import op

from sqlalchemy.orm.session import Session

from sqlalchemy import MetaData
from flask_sqlalchemy import SQLAlchemy

# revision identifiers, used by Alembic.
revision = "35e6ddccd22a"
down_revision = "1583f2de9f39"
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

#
import enum  # noqa: E402
import datetime  # noqa: E402

from sqlalchemy.orm import declared_attr  # noqa: E402
from sqlalchemy.orm import declarative_mixin  # noqa: E402


class ProductType(sa.Model):
    __tablename__ = "product_types"
    type_id = sa.Column(sa.Integer(), primary_key=True)
    name = sa.Column(sa.Text(), nullable=False, unique=True, index=True)
    order = sa.Column(sa.Integer())
    indef_article = sa.Column(sa.Text())
    singular = sa.Column(sa.Text())
    plural = sa.Column(sa.Text())
    icon = sa.Column(sa.Text())

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.name!r}>"


class Product(sa.Model):
    # TODO: rename the class name to be more generic, e.g., "Entry"
    # TODO: use singular for the table name
    __tablename__ = "products"
    product_id = sa.Column(sa.Integer(), primary_key=True)
    type_id = sa.Column(sa.ForeignKey("product_types.type_id"), nullable=False)
    type_ = sa.relationship("ProductType", backref=sa.backref("products"))
    name = sa.Column(sa.Text(), nullable=False)
    contact = sa.Column(sa.Text())  # TODO: move to attribute model
    date_produced = sa.Column(sa.Date())  # TODO: move to attribute model
    produced_by = sa.Column(sa.Text())  # TODO: move to attribute model
    time_posted = sa.Column(
        sa.DateTime(), default=lambda: datetime.datetime.now()
    )
    posted_by = sa.Column(sa.Text())
    posting_git_hub_user_id = sa.Column(sa.ForeignKey("github_users.user_id"))
    posting_git_hub_user = sa.relationship(
        "GitHubUser",
        foreign_keys=[posting_git_hub_user_id],
        backref=sa.backref("posted_products", cascade="all"),
    )
    time_updated = sa.Column(sa.DateTime())
    updated_by = sa.Column(sa.Text())
    updating_git_hub_user_id = sa.Column(sa.ForeignKey("github_users.user_id"))
    updating_git_hub_user = sa.relationship(
        "GitHubUser",
        foreign_keys=[updating_git_hub_user_id],
        backref=sa.backref("updated_products", cascade="all"),
    )
    note = sa.Column(sa.Text())
    __table_args__ = (
        sa.UniqueConstraint("type_id", "name", name="_type_id_name"),
    )

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.name!r}>"


class GitHubUser(sa.Model):
    __tablename__ = "github_users"
    user_id = sa.Column(sa.Integer(), primary_key=True)
    git_hub_id = sa.Column(sa.Text(), unique=True, nullable=False)
    login = sa.Column(sa.Text(), unique=True, nullable=False)
    name = sa.Column(sa.Text())
    avatar_url = sa.Column(sa.Text())
    url = sa.Column(sa.Text())

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.login!r}>"


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
        type_name = self.type_.name if self.type_ else self.type_
        return f"<{self.__class__.__name__} {self.name!r} {type_name!r}>"


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
        type_name = self.type_.name if self.type_ else self.type_
        field_name = self.field.name if self.field else self.field
        return f"<{self.__class__.__name__} {type_name!r} {field_name!r}>"


@declarative_mixin
class AttributeBase:
    attribute_id = sa.Column(sa.Integer(), primary_key=True)
    name = sa.Column(sa.Text())  # TODO: Remove

    @declared_attr
    def product_id(self):
        return sa.Column(sa.Integer(), sa.ForeignKey("products.product_id"), nullable=False)  # fmt: skip

    @declared_attr
    def product(self):
        return sa.relationship(
            "Product",
            backref=sa.backref(self.backref_column, cascade="all, delete-orphan"),  # fmt: skip
        )

    @declared_attr
    def field_id(self):
        return sa.Column(sa.Integer(), sa.ForeignKey("field.field_id"), nullable=True)  # fmt: skip
        # TODO: Make nullable False

    @declared_attr
    def field(self):
        return sa.relationship(
            "Field",
            backref=sa.backref(self.backref_column, cascade="all, delete-orphan"),  # fmt: skip
        )

    def __repr__(self):
        field_name = self.field.name if self.field else self.field
        return f"<{self.__class__.__name__} {field_name!r}: {self.value!r}>"


class AttributeUnicodeText(AttributeBase, sa.Model):
    __tablename__ = "attribute_unicode_text"
    backref_column = "attributes_unicode_text"
    value = sa.Column(sa.UnicodeText())


class AttributeBoolean(AttributeBase, sa.Model):
    __tablename__ = "attribute_boolean"
    backref_column = "attributes_boolean"
    value = sa.Column(sa.Boolean())


class AttributeInteger(AttributeBase, sa.Model):
    __tablename__ = "attribute_integer"
    backref_column = "attributes_integer"
    value = sa.Column(sa.Integer())


class AttributeFloat(AttributeBase, sa.Model):
    __tablename__ = "attribute_float"
    backref_column = "attributes_float"
    value = sa.Column(sa.Float())


class AttributeDate(AttributeBase, sa.Model):
    __tablename__ = "attribute_date"
    backref_column = "attributes_date"
    value = sa.Column(sa.Date())


class AttributeDateTime(AttributeBase, sa.Model):
    __tablename__ = "attribute_date_time"
    backref_column = "attributes_date_time"
    value = sa.Column(sa.DateTime())


class AttributeTime(AttributeBase, sa.Model):
    __tablename__ = "attribute_time"
    backref_column = "attributes_time"
    value = sa.Column(sa.Time())


def upgrade():
    session = Session(bind=op.get_bind())

    AttributeClasses = [AttributeUnicodeText, AttributeDate, AttributeDateTime]

    for product in session.query(Product):
        field_dict = {f.field.name: f.field for f in product.type_.fields}
        for AttributeClass in AttributeClasses:
            attrs = getattr(product, AttributeClass.backref_column)
            for attr in attrs:
                attr.field = field_dict[attr.name]
    session.commit()


def downgrade():
    pass
