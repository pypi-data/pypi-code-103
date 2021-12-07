"""Generated implementation of restrictions."""

# WARNING DO NOT EDIT
# This code was generated from restrictions.mcn

from __future__ import annotations

import abc  # noqa: F401
import dataclasses  # noqa: F401
import datetime  # noqa: F401
import enum  # noqa: F401
import isodate  # noqa: F401
import json  # noqa: F401
import jsonschema  # noqa: F401
import logging  # noqa: F401
import typing  # noqa: F401
import uuid  # noqa: F401


@dataclasses.dataclass(frozen=True)
class AttributeKey:
    """Attribute name.
    
    Args:
        value (str): A data field.
    """
    
    value: str
    
    def __str__(self) -> str:
        """Return a str of the wrapped value."""
        return str(self.value)
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for AttributeKey data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "string"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> AttributeKey:
        """Validate and parse JSON data into an instance of AttributeKey.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of AttributeKey.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return AttributeKey(str(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing AttributeKey", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return str(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> AttributeKey:
        """Parse a JSON string such as a dictionary key."""
        return AttributeKey(str(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class AttributeDisplay:
    """Display details for an attribute value.
    
    Args:
        emoji (str): A data field.
        colour (str): A data field.
    """
    
    emoji: str
    colour: str
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for AttributeDisplay data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "emoji": {
                    "type": "string"
                },
                "colour": {
                    "type": "string"
                }
            },
            "required": [
                "emoji",
                "colour",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> AttributeDisplay:
        """Validate and parse JSON data into an instance of AttributeDisplay.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of AttributeDisplay.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return AttributeDisplay(
                emoji=str(data["emoji"]),
                colour=str(data["colour"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing AttributeDisplay",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "emoji": str(self.emoji),
            "colour": str(self.colour)
        }


@dataclasses.dataclass(frozen=True)
class AttributeChoice:
    """An attribute value.
    
    Args:
        value (str): A data field.
        display (typing.Optional[AttributeDisplay]): A data field.
    """
    
    value: str
    display: typing.Optional[AttributeDisplay]
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for AttributeChoice data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "value": {
                    "type": "string"
                },
                "display": {
                    "oneOf": [
                        {"type": "null"},
                        AttributeDisplay.json_schema(),
                    ]
                }
            },
            "required": [
                "value",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> AttributeChoice:
        """Validate and parse JSON data into an instance of AttributeChoice.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of AttributeChoice.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return AttributeChoice(
                value=str(data["value"]),
                display=(
                    lambda v: v and AttributeDisplay.from_json(v)
                )(
                    data.get("display", None)
                ),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing AttributeChoice",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "value": str(self.value),
            "display": (lambda v: v and v.to_json())(self.display)
        }


class AttributeTarget(enum.Enum):
    """Object types an attribute may be applied to."""
    Cluster = "cluster"
    """Cluster attribute."""
    Destination = "destination"
    """Destination attribute."""
    Entity = "entity"
    """Entity attribute."""
    Feature = "feature"
    """Feature attribute."""
    FeatureSet = "featureset"
    """FeatureSet attribute."""
    FeatureStore = "featurestore"
    """FeatureStore attribute."""
    Source = "source"
    """Source attribute."""
    Table = "table"
    """Table attribute."""
    
    @classmethod
    def json_schema(cls) -> dict:
        """JSON schema for 'AttributeTarget'.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "adt_type": {
                    "type": "string",
                    "enum": [
                        "cluster",
                        "destination",
                        "entity",
                        "feature",
                        "featureset",
                        "featurestore",
                        "source",
                        "table",
                    ]
                }
            },
            "required": [
                "adt_type",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> AttributeTarget:
        """Validate and parse JSON data into an instance of AttributeTarget.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of AttributeTarget.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return AttributeTarget(str(data['adt_type']))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing AttributeTarget", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            JSON data ready to be serialised.
        """
        return {'adt_type': self.value}
    
    @classmethod
    def from_json_key(cls, data: str) -> AttributeTarget:
        """Validate and parse a value from a JSON dictionary key.
        
        Args:
            data (str): JSON data to validate and parse.
        
        Returns:
            An instance of AttributeTarget.
        """
        return AttributeTarget(str(data))
    
    def to_json_key(self) -> str:
        """Serialised this instanse as a JSON string for use as a dictionary key.
        
        Returns:
            A JSON string ready to be used as a key.
        """
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class AttributeRestriction(abc.ABC):
    """Defines attributes, values, and the objects they can be applied to.
    
    Args:
        appliesTo (typing.List[AttributeTarget]): A data field.
        description (str): A data field.
        key (AttributeKey): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = ""
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    appliesTo: typing.List[AttributeTarget]
    description: str
    key: AttributeKey
    
    @classmethod
    def json_schema(cls) -> AttributeRestriction:
        """JSON schema for variant AttributeRestriction.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        adt_types = [klass.ADT_TYPE for klass in cls.__subclasses__()]
        return {
            "type": "object",
            "properties": {
                "adt_type": {
                    "type": "string",
                    "enum": adt_types
                }
            },
            "required": [
                "adt_type",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> AttributeRestriction:
        """Validate and parse JSON data into an instance of AttributeRestriction.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of AttributeRestriction.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            adt_type = data.get("adt_type", None)
            for klass in cls.__subclasses__():
                if klass.ADT_TYPE == adt_type:
                    return klass.from_json(data)
            raise ValueError("Unknown adt_type: '{ty}'".format(ty=adt_type))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing AttributeRestriction", exc_info=ex)
            raise
    
    @abc.abstractmethod
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        raise NotImplementedError


@dataclasses.dataclass(frozen=True)
class EnumAttribute(AttributeRestriction):
    """Enumeration attribute with fixed choices.
    
    Args:
        key (AttributeKey): A data field.
        description (str): A data field.
        choices (typing.List[AttributeChoice]): A data field.
        appliesTo (typing.List[AttributeTarget]): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "enumattribute"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    key: AttributeKey
    description: str
    choices: typing.List[AttributeChoice]
    appliesTo: typing.List[AttributeTarget]
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for EnumAttribute data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "adt_type": {
                    "type": "string",
                    "enum": [cls.ADT_TYPE]
                },
                "key": AttributeKey.json_schema(),
                "description": {
                    "type": "string"
                },
                "choices": {
                    "type": "array",
                    "item": AttributeChoice.json_schema()
                },
                "appliesTo": {
                    "type": "array",
                    "item": AttributeTarget.json_schema()
                }
            },
            "required": [
                "adt_type",
                "key",
                "description",
                "choices",
                "appliesTo",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> EnumAttribute:
        """Validate and parse JSON data into an instance of EnumAttribute.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of EnumAttribute.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return EnumAttribute(
                key=AttributeKey.from_json(data["key"]),
                description=str(data["description"]),
                choices=[AttributeChoice.from_json(v) for v in data["choices"]],
                appliesTo=[AttributeTarget.from_json(v) for v in data["appliesTo"]],
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing EnumAttribute",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "adt_type": self.ADT_TYPE,
            "key": self.key.to_json(),
            "description": str(self.description),
            "choices": [v.to_json() for v in self.choices],
            "appliesTo": [v.to_json() for v in self.appliesTo]
        }


@dataclasses.dataclass(frozen=True)
class FreeTextAttribute(AttributeRestriction):
    """Free text response attribute.
    
    Args:
        key (AttributeKey): A data field.
        description (str): A data field.
        appliesTo (typing.List[AttributeTarget]): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "freetextattribute"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    key: AttributeKey
    description: str
    appliesTo: typing.List[AttributeTarget]
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for FreeTextAttribute data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "adt_type": {
                    "type": "string",
                    "enum": [cls.ADT_TYPE]
                },
                "key": AttributeKey.json_schema(),
                "description": {
                    "type": "string"
                },
                "appliesTo": {
                    "type": "array",
                    "item": AttributeTarget.json_schema()
                }
            },
            "required": [
                "adt_type",
                "key",
                "description",
                "appliesTo",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> FreeTextAttribute:
        """Validate and parse JSON data into an instance of FreeTextAttribute.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of FreeTextAttribute.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return FreeTextAttribute(
                key=AttributeKey.from_json(data["key"]),
                description=str(data["description"]),
                appliesTo=[AttributeTarget.from_json(v) for v in data["appliesTo"]],
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing FreeTextAttribute",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "adt_type": self.ADT_TYPE,
            "key": self.key.to_json(),
            "description": str(self.description),
            "appliesTo": [v.to_json() for v in self.appliesTo]
        }


@dataclasses.dataclass(frozen=True)
class AllowedAttributesResponse:
    """Policy for attributes permitted by the server configuration.
    
    Args:
        allowedAttributes (typing.Optional[typing.List[AttributeRestriction]]): A data field.
    """
    
    allowedAttributes: typing.Optional[typing.List[AttributeRestriction]]
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for AllowedAttributesResponse data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "allowedAttributes": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "array", "item": AttributeRestriction.json_schema()},
                    ]
                }
            },
            "required": []
        }
    
    @classmethod
    def from_json(cls, data: dict) -> AllowedAttributesResponse:
        """Validate and parse JSON data into an instance of AllowedAttributesResponse.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of AllowedAttributesResponse.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return AllowedAttributesResponse(
                allowedAttributes=(
                    lambda v: v and [AttributeRestriction.from_json(v) for v in v]
                )(
                    data.get("allowedAttributes", None)
                ),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing AllowedAttributesResponse",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "allowedAttributes": (lambda v: v and [v.to_json() for v in v])(self.allowedAttributes)
        }


@dataclasses.dataclass(frozen=True)
class LabelRestriction:
    """Label restriction rule.
    
    Args:
        text (str): A data field.
        emoji (typing.Optional[str]): A data field.
        colour (typing.Optional[str]): A data field.
    """
    
    text: str
    emoji: typing.Optional[str]
    colour: typing.Optional[str]
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for LabelRestriction data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string"
                },
                "emoji": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string"},
                    ]
                },
                "colour": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string"},
                    ]
                }
            },
            "required": [
                "text",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> LabelRestriction:
        """Validate and parse JSON data into an instance of LabelRestriction.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of LabelRestriction.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return LabelRestriction(
                text=str(data["text"]),
                emoji=(lambda v: v and str(v))(data.get("emoji", None)),
                colour=(lambda v: v and str(v))(data.get("colour", None)),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing LabelRestriction",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "text": str(self.text),
            "emoji": (lambda v: v and str(v))(self.emoji),
            "colour": (lambda v: v and str(v))(self.colour)
        }


@dataclasses.dataclass(frozen=True)
class AllowedLabelsResponse:
    """Policy for labels permitted by the server configuration.
    
    Args:
        allowedLabels (typing.Optional[typing.List[LabelRestriction]]): A data field.
    """
    
    allowedLabels: typing.Optional[typing.List[LabelRestriction]]
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for AllowedLabelsResponse data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "allowedLabels": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "array", "item": LabelRestriction.json_schema()},
                    ]
                }
            },
            "required": []
        }
    
    @classmethod
    def from_json(cls, data: dict) -> AllowedLabelsResponse:
        """Validate and parse JSON data into an instance of AllowedLabelsResponse.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of AllowedLabelsResponse.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return AllowedLabelsResponse(
                allowedLabels=(
                    lambda v: v and [LabelRestriction.from_json(v) for v in v]
                )(
                    data.get("allowedLabels", None)
                ),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing AllowedLabelsResponse",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "allowedLabels": (lambda v: v and [v.to_json() for v in v])(self.allowedLabels)
        }
