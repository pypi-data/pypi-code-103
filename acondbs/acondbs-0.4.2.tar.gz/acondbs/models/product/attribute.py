from sqlalchemy.orm import declared_attr
from sqlalchemy.orm import declarative_mixin

from ...db.sa import sa


##__________________________________________________________________||
@declarative_mixin
class AttributeBase:
    iid = sa.Column(sa.Integer(), primary_key=True)

    @declared_attr
    def product_id(self):
        return sa.Column(
            sa.Integer(),
            sa.ForeignKey("products.product_id"),
            nullable=False,
        )

    @declared_attr
    def product(self):
        return sa.relationship(
            "Product",
            backref=sa.backref(
                self.backref_column,
                cascade="all, delete-orphan",
            ),
        )

    @declared_attr
    def type_field_association_iid(self):
        return sa.Column(
            sa.Integer(),
            sa.ForeignKey("type_field_association.iid"),
            nullable=False,
        )

    @declared_attr
    def type_field_association(self):
        return sa.relationship(
            "TypeFieldAssociation",
            backref=sa.backref(
                self.backref_column,  # TODO: need to change
                cascade="all, delete-orphan",
            ),
        )

    @declared_attr
    def field_id(self):
        return sa.Column(
            sa.Integer(),
            sa.ForeignKey("field.field_id"),
            nullable=False,
        )
        # TODO: remove, replace with type_field_association_iid

    @declared_attr
    def field(self):
        return sa.relationship(
            "Field",
            backref=sa.backref(
                self.backref_column,
                cascade="all, delete-orphan",
            ),
        )
        # TODO: remove, replace with type_field_association

    def __repr__(self):
        return (
            f"<{self.__class__.__name__} {self.field_name!r}: {self.value!r}>"
        )

    @property
    def field_name(self):
        try:
            return self.field.name
        except BaseException:
            return self.field


##__________________________________________________________________||
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


##__________________________________________________________________||
