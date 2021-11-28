"""Declares :class:`APIMetadata`."""
from typing import Dict

from pydantic import BaseModel
from pydantic import Field

from .apiendpoint import APIEndpoint


class APIMetadata(BaseModel):
    version: str = Field(...,
        example="v2",
        title="API version",
        description="The version of the API metadata."
    )

    capabilities: list = Field([],
        example=["capability1", "capability2"],
        title="Capabilities",
        description="The capabilities of the API server."
    )

    catalog: Dict[str, APIEndpoint] = Field(...,
        title="Endpoint URLs",
        description="Maps symbolic names to endpoint URLs.",
        example={
            'foo.bar': "https://api.example.com/foo/{bar}/"
        }
    )

    client: dict
