"""Declares :class:`APIEndpoint`."""
from pydantic import BaseModel
from pydantic import Field


class APIEndpoint(BaseModel):
    url: str = Field(...,
        title="Endpoint URL",
        description="The endpoint absolute URL with interpolatable variables.",
        example="https://api.example.com/foo/{bar}/"
    )
