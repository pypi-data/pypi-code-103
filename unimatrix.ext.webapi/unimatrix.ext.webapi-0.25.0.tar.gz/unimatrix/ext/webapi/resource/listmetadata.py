# pylint: skip-file
"""Declares :class:`ListMetadata`."""
import typing

import pydantic


class ListMetadata(pydantic.BaseModel):
    length: int = pydantic.Field(None,
        title="Length",
        description=(
            "The length of the collection i.e. the total number "
            "of items."
        ),
        example=1000,
        alias='totalItems'
    )

    next_url: str = pydantic.Field(None,
        title="Next URL",
        description=(
            "The URL where the next subset of resource may be "
            "retrieved, based on the **offset** and **limit** "
            "parameters. This attribute is absent if the is no "
            "next subset i.e. **offset** and **limit** exceed "
            "the size of the collection. This attribute may be "
            "null for servers that do not implement it."
        ),
        example="https://example.unimatrixapis.com/resource?offset=100&limit=100",
        alias='nextUrl'
    )

    prev_url: str = pydantic.Field(None,
        title="Previous URL",
        description=(
            "The URL where the previous subset of resource may be "
            "retrieved, based on the **offset** and **limit** "
            "parameters. This attribute is absent if the is no "
            "previous subset i.e. **offset** is `0`. This attribute may be "
            "null for servers that do not implement it."
        ),
        example="https://example.unimatrixapis.com/resource?offset=0&limit=100",
        alias='prevUrl'
    )
