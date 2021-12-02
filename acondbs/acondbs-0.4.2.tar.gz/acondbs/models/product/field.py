import enum

from ...db.sa import sa

from . import attribute


##__________________________________________________________________||
class FieldType(enum.Enum):
    # SQLAlchemy generic types: https://docs.sqlalchemy.org/en/14/core/type_basics.html#generic-types
    UnicodeText = 1
    Boolean = 2
    Integer = 3
    Float = 4
    Date = 5
    DateTime = 6
    Time = 7

    @property
    def attribute_class(self):
        return FIELDTYPE_ATTRIBUTECLASS_MAP[self]


FIELDTYPE_ATTRIBUTECLASS_MAP = {
    FieldType.UnicodeText: attribute.AttributeUnicodeText,
    FieldType.Boolean: attribute.AttributeBoolean,
    FieldType.Integer: attribute.AttributeInteger,
    FieldType.Float: attribute.AttributeFloat,
    FieldType.Date: attribute.AttributeDate,
    FieldType.DateTime: attribute.AttributeDateTime,
    FieldType.Time: attribute.AttributeTime,
}


saEnumFieldType = sa.Enum(FieldType)  # to be imported in another module


class Field(sa.Model):
    __tablename__ = "field"
    field_id = sa.Column(sa.Integer(), primary_key=True)
    name = sa.Column(sa.UnicodeText(), nullable=False)
    type_ = sa.Column(saEnumFieldType, nullable=False)

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.name!r} {self.type_name!r}>"

    @property
    def type_name(self):
        # used in __repr__()
        try:
            return self.type_.name
        except BaseException:
            return self.type_


##__________________________________________________________________||
