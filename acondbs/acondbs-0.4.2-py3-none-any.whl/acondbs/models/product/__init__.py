"""declare ORM models for tables for products

"""

##__________________________________________________________________||
from .product_type import ProductType  # noqa: F401
from .product import Product  # noqa: F401
from .product_file_path import ProductFilePath  # noqa: F401
from .product_relation_type import ProductRelationType  # noqa: F401
from .product_relation import ProductRelation  # noqa: F401

from .attribute import (  # noqa: F401
    AttributeUnicodeText,
    AttributeBoolean,
    AttributeInteger,
    AttributeFloat,
    AttributeDate,
    AttributeDateTime,
    AttributeTime,
)

from .field import (  # noqa: F401
    FieldType,  # enum
    saEnumFieldType,  # SQLAlchemy Enum
    Field,
)


from .type_field_association import TypeFieldAssociation  # noqa: F401

##__________________________________________________________________||
