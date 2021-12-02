"""delete some attributes

Revision ID: 4398f463d243
Revises: 2910eaefa574
Create Date: 2021-09-20 11:56:40.187352

"""
from alembic import op


from sqlalchemy.orm.session import Session

import datetime

from sqlalchemy import MetaData
from flask_sqlalchemy import SQLAlchemy

# revision identifiers, used by Alembic.
revision = "4398f463d243"
down_revision = "2910eaefa574"
branch_labels = None
depends_on = None


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


class ProductType(sa.Model):
    __tablename__ = "product_types"
    type_id = sa.Column(sa.Integer(), primary_key=True)
    name = sa.Column(sa.Text(), nullable=False, unique=True, index=True)
    order = sa.Column(sa.Integer())
    indef_article = sa.Column(sa.Text())
    singular = sa.Column(sa.Text())
    plural = sa.Column(sa.Text())
    icon = sa.Column(sa.Text())


class Product(sa.Model):
    __tablename__ = "products"
    product_id = sa.Column(sa.Integer(), primary_key=True)
    type_id = sa.Column(sa.ForeignKey("product_types.type_id"), nullable=False)
    type_ = sa.relationship("ProductType", backref=sa.backref("products"))
    name = sa.Column(sa.Text(), nullable=False)
    contact = sa.Column(sa.Text())
    date_produced = sa.Column(sa.Date())
    produced_by = sa.Column(sa.Text())
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


class AttributeBase:
    attribute_id = sa.Column(sa.Integer(), primary_key=True)
    name = sa.Column(sa.Text(), nullable=False)

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.name!r}>"


class AttributeText(sa.Model, AttributeBase):
    __tablename__ = "attribute_text"
    product_id = sa.Column(
        sa.Integer(), sa.ForeignKey("products.product_id"), nullable=False
    )
    product = sa.relationship(
        "Product",
        backref=sa.backref("attributes_text", cascade="all, delete-orphan"),
    )
    value = sa.Column(sa.Text())


class AttributeDate(sa.Model, AttributeBase):
    __tablename__ = "attribute_date"
    product_id = sa.Column(
        sa.Integer(), sa.ForeignKey("products.product_id"), nullable=False
    )
    product = sa.relationship(
        "Product",
        backref=sa.backref("attributes_date", cascade="all, delete-orphan"),
    )
    value = sa.Column(sa.Date())


class AttributeDateTime(sa.Model, AttributeBase):
    __tablename__ = "attribute_date_time"
    product_id = sa.Column(
        sa.Integer(), sa.ForeignKey("products.product_id"), nullable=False
    )
    product = sa.relationship(
        "Product",
        backref=sa.backref(
            "attributes_date_time", cascade="all, delete-orphan"
        ),
    )
    value = sa.Column(sa.DateTime())


def upgrade():
    session = Session(bind=op.get_bind())

    columns_text = [
        "name",
        "posted_by",
        "updated_by",
        "note",
    ]
    columns_date = []
    columns_date_time = ["time_posted", "time_updated"]

    products = session.query(Product).all()
    for p in products:
        for c in columns_text:
            for a in session.query(AttributeText).filter_by(name=c):
                session.delete(a)
        for c in columns_date:
            for a in session.query(AttributeDate).filter_by(name=c):
                session.delete(a)
        for c in columns_date_time:
            for a in session.query(AttributeDateTime).filter_by(name=c):
                session.delete(a)
    session.commit()


def downgrade():
    pass
