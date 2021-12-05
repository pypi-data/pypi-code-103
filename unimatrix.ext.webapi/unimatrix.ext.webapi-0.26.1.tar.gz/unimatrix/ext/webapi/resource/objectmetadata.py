# pylint: skip-file
"""Declares :class:`ObjectMetadata`."""
import typing

import pydantic


class ObjectMetadata(pydantic.BaseModel):
    namespace: str = pydantic.Field("default",
        title="namespace",
        description=(
            "Namespace defines the space within which each name must be unique."
            " An empty namespace is equivalent to the \"default\" namespace, but "
            "\"default\" is the canonical representation. Not all objects are "
            "required to be scoped to a namespace - the value of this field for"
            " those objects will be empty. Cannot be updated."
        ),
        example="projects/12345"
    )

    name: str = pydantic.Field(None,
        title="Name",
        description=(
            "Name must be unique within a namespace. Is required when creating "
            "resources, although some resources may allow a client to request "
            "the generation of an appropriate name automatically. Name is "
            "primarily intended for creation idempotence and configuration "
            "definition. Cannot be updated. "
        ),
        example="foo"
    )

    labels: dict = pydantic.Field({},
        title="labels",
        description=(
            "Map of string keys and values that can be used to organize and "
            "categorize (scope and select) objects. May match selectors of "
            "services and external integrations."
        ),
        example={
            "unimatrixone.io/foo": "bar"
        }
    )

    annotations: dict = pydantic.Field({},
        title="annotations",
        description=(
            "Annotations is an unstructured key value map stored with a "
            "resource that may be set by external tools to store and retrieve "
            "arbitrary metadata. They are not queryable and should be "
            "preserved when modifying objects."
        ),
        example={
            "unimatrixone.io/foo": "bar"
        }
    )

    self_link: str = pydantic.Field(None,
        title="Self link",
        description="The URL representing this resource.",
        example="https://example.unimatrixapis.com/resource/1234",
        alias='selfLink'
    )

    class Config:
        allow_population_by_field_name = True
