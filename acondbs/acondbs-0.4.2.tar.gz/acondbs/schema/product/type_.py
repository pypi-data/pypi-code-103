import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType

from ..connection import CountedConnection
from ...models import (
    Product as ProductModel,
    ProductType as ProductTypeModel,
    ProductFilePath as ProductFilePathModel,
    ProductRelation as ProductRelationModel,
    ProductRelationType as ProductRelationTypeModel,
    # FieldType as FieldTypeModel,  # enum
    saEnumFieldType,  # SQLAlchemy Enum
    Field as FieldModel,
    TypeFieldAssociation as TypeFieldAssociationModel,
    AttributeUnicodeText as AttributeUnicodeTextModel,
    AttributeBoolean as AttributeBooleanModel,
    AttributeInteger as AttributeIntegerModel,
    AttributeFloat as AttributeFloatModel,
    AttributeDate as AttributeDateModel,
    AttributeDateTime as AttributeDateTimeModel,
    AttributeTime as AttributeTimeModel,
)
from ..filter_ import PFilterableConnectionField


from graphene_sqlalchemy.enums import _convert_sa_to_graphene_enum


##__________________________________________________________________||
# FieldType is an enum. It is manually converted to a graphene enum
# here. An enum will be usually automatically converted. However, the
# automatic conversion causes an error if the automatic conversion
# of the same enum happens multiple times as described in
# https://github.com/graphql-python/graphene-sqlalchemy/issues/211.

# It is possible to use graphene.Enum.from_enum() as
# FieldType = graphene.Enum.from_enum(FieldTypeModel)

# However, instead, a private function _convert_sa_to_graphene_enum()
# is used here because this function desirably converts field names to
# the upper case, e.g., "UnicodeText" to "UNICODE_TEXT"
FieldType = _convert_sa_to_graphene_enum(saEnumFieldType)


##__________________________________________________________________||
class Product(SQLAlchemyObjectType):
    class Meta:
        model = ProductModel
        interfaces = (relay.Node,)
        connection_class = CountedConnection
        connection_field_factory = PFilterableConnectionField.factory


##__________________________________________________________________||
class ProductType(SQLAlchemyObjectType):
    """A product type"""

    class Meta:
        model = ProductTypeModel
        interfaces = (graphene.relay.Node,)
        connection_class = CountedConnection
        connection_field_factory = PFilterableConnectionField.factory


##__________________________________________________________________||
class ProductRelation(SQLAlchemyObjectType):
    """A relation from one product to another"""

    class Meta:
        model = ProductRelationModel
        interfaces = (graphene.relay.Node,)
        connection_class = CountedConnection
        connection_field_factory = PFilterableConnectionField.factory


##__________________________________________________________________||
class ProductRelationType(SQLAlchemyObjectType):
    """A type of relations between products"""

    class Meta:
        model = ProductRelationTypeModel
        interfaces = (graphene.relay.Node,)
        connection_class = CountedConnection
        connection_field_factory = PFilterableConnectionField.factory


##__________________________________________________________________||
class ProductFilePath(SQLAlchemyObjectType):
    class Meta:
        model = ProductFilePathModel
        interfaces = (relay.Node,)
        connection_class = CountedConnection
        connection_field_factory = PFilterableConnectionField.factory


##__________________________________________________________________||
class Field(SQLAlchemyObjectType):
    class Meta:
        model = FieldModel
        interfaces = (relay.Node,)
        connection_class = CountedConnection
        connection_field_factory = PFilterableConnectionField.factory
        exclude_fields = ("type_",)

    # Set "type_" manually to avoid an issue on enum as suggested in
    # https://github.com/graphql-python/graphene-sqlalchemy/pull/98#issuecomment-481497115
    # see also https://github.com/graphql-python/graphene-sqlalchemy/issues/211

    type_ = FieldType()


class TypeFieldAssociation(SQLAlchemyObjectType):
    class Meta:
        model = TypeFieldAssociationModel
        interfaces = (relay.Node,)
        connection_class = CountedConnection
        connection_field_factory = PFilterableConnectionField.factory


class AttributeUnicodeText(SQLAlchemyObjectType):
    """A unicode text attribute of a product"""

    class Meta:
        model = AttributeUnicodeTextModel
        interfaces = (relay.Node,)
        connection_class = CountedConnection
        connection_field_factory = PFilterableConnectionField.factory


class AttributeBoolean(SQLAlchemyObjectType):
    """A boolean attribute of a product"""

    class Meta:
        model = AttributeBooleanModel
        interfaces = (relay.Node,)
        connection_class = CountedConnection
        connection_field_factory = PFilterableConnectionField.factory


class AttributeInteger(SQLAlchemyObjectType):
    """An integer attribute of a product"""

    class Meta:
        model = AttributeIntegerModel
        interfaces = (relay.Node,)
        connection_class = CountedConnection
        connection_field_factory = PFilterableConnectionField.factory


class AttributeFloat(SQLAlchemyObjectType):
    """A float attribute of a product"""

    class Meta:
        model = AttributeFloatModel
        interfaces = (relay.Node,)
        connection_class = CountedConnection
        connection_field_factory = PFilterableConnectionField.factory


class AttributeDate(SQLAlchemyObjectType):
    """A date attribute of a product"""

    class Meta:
        model = AttributeDateModel
        interfaces = (relay.Node,)
        connection_class = CountedConnection
        connection_field_factory = PFilterableConnectionField.factory


class AttributeDateTime(SQLAlchemyObjectType):
    """A date time attribute of a product"""

    class Meta:
        model = AttributeDateTimeModel
        interfaces = (relay.Node,)
        connection_class = CountedConnection
        connection_field_factory = PFilterableConnectionField.factory


class AttributeTime(SQLAlchemyObjectType):
    """A time attribute of a product"""

    class Meta:
        model = AttributeTimeModel
        interfaces = (relay.Node,)
        connection_class = CountedConnection
        connection_field_factory = PFilterableConnectionField.factory


##__________________________________________________________________||
