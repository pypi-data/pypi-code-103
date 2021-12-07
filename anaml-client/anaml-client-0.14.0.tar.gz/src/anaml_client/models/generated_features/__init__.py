"""Generated implementation of generated_features."""

# WARNING DO NOT EDIT
# This code was generated from generated-features.mcn

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


class FeatureData(enum.Enum):
    """Placeholder for map of feature data."""
    Json = "json"
    
    @classmethod
    def json_schema(cls) -> dict:
        """JSON schema for 'FeatureData'.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "adt_type": {
                    "type": "string",
                    "enum": [
                        "json",
                    ]
                }
            },
            "required": [
                "adt_type",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> FeatureData:
        """Validate and parse JSON data into an instance of FeatureData.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of FeatureData.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return FeatureData(str(data['adt_type']))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing FeatureData", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            JSON data ready to be serialised.
        """
        return {'adt_type': self.value}
    
    @classmethod
    def from_json_key(cls, data: str) -> FeatureData:
        """Validate and parse a value from a JSON dictionary key.
        
        Args:
            data (str): JSON data to validate and parse.
        
        Returns:
            An instance of FeatureData.
        """
        return FeatureData(str(data))
    
    def to_json_key(self) -> str:
        """Serialised this instanse as a JSON string for use as a dictionary key.
        
        Returns:
            A JSON string ready to be used as a key.
        """
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class GeneratedFeatures:
    """Features generated for a specific entity.
    
    Args:
        id (str): A data field.
        date (datetime.date): A data field.
        features (FeatureData): A data field.
    """
    
    id: str
    date: datetime.date
    features: FeatureData
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for GeneratedFeatures data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "id": {
                    "type": "string"
                },
                "date": {
                    "type": "string",
                    "format": "date"
                },
                "features": FeatureData.json_schema()
            },
            "required": [
                "id",
                "date",
                "features",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> GeneratedFeatures:
        """Validate and parse JSON data into an instance of GeneratedFeatures.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of GeneratedFeatures.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return GeneratedFeatures(
                id=str(data["id"]),
                date=datetime.date.fromisoformat(data["date"]),
                features=FeatureData.from_json(data["features"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing GeneratedFeatures",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "id": str(self.id),
            "date": self.date.isoformat(),
            "features": self.features.to_json()
        }
