from dataclasses import dataclass, field
import datetime
from typing import List, Dict


@dataclass(frozen=True)
class AttributeValuePair:
    """
    Represents an attribute consisting of a key and value. The "stringified" data type of the value can be determined
    using ``resolve_data_type()``. The "stringified" value can be determined using ``value_as_string()``. These are
    both important functions for interfacing with the PPRL encoder service.
    """
    name: str
    value: object

    def resolve_data_type(self):
        """
        Attempts to resolve the data type of the value held in this attribute-value pair.

        :return: Value data type expressed as a string for use with the encoder API
        """
        d_type = type(self.value)

        if d_type == str:
            if len(str(self.value)) <= 1:
                return "char"
            else:
                return "string"
        elif d_type == int:
            return "integer"
        elif d_type == float:
            return "float"
        elif d_type == datetime.date:
            return "date"
        elif d_type == datetime.datetime:
            return "datetime"

        raise ValueError(f"Cannot resolve data type {d_type} for value {self.value} on attribute {self.name}")

    def value_as_string(self):
        d_type = self.resolve_data_type()

        if d_type == "datetime":
            return self.value.strftime("%d.%m.%Y %H:%M:%S")
        elif d_type == "date":
            return self.value.strftime("%d.%m.%Y")
        else:
            return str(self.value)


@dataclass(frozen=True)
class AttributeSchema:
    """
    Represents a schema that can be applied to an attribute. Option values are converted to their string
    representations using ``str()`` on them before being sent off in a request.
    """
    attribute_name: str
    options: Dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class Entity:
    """
    Represents an entity that can be encoded using the PPRL encoder service.
    """
    identifier: str
    attributes: List[AttributeValuePair]


@dataclass(frozen=True)
class EncodedEntity:
    """
    Represents an encoded entity as a result of the PPRL encoder service.
    """
    identifier: str
    bit_vector: str


@dataclass(frozen=True)
class EncoderConfig:
    charset: str
    seed: str
    generation_function: str


@dataclass(frozen=True)
class EncoderRequest:
    """
    Represents a request to encode entities with the specified parameters.
    """
    config: EncoderConfig = field(default=EncoderConfig("UTF-8", "", "TRIGRAM_ATTRIBUTE_BLOOM_FILTER"))
    schema_list: List[AttributeSchema] = field(default_factory=list)
    entity_list: List[Entity] = field(default_factory=list)
