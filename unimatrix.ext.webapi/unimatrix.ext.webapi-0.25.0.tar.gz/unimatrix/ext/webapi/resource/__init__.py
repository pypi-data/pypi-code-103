# pylint: skip-file
import copy
import inspect
import typing

import pydantic

from .baseresource import BaseResource
from .listmetadata import ListMetadata
from .objectmetadata import ObjectMetadata


COMMON_ATTRS={
    'api_version': pydantic.Field(...,
        title="Version",
        description=(
            "APIVersion defines the versioned schema of this representation"
            " of an object. Servers should convert recognized schemas to "
            "the latest internal value, and may reject unrecognized values."
        ),
        example="books/v1",
        alias='apiVersion'
    ),
    'kind': pydantic.Field(...,
        title="Kind",
        description=(
            "Kind is a string value representing the REST resource this"
            " object represents. Servers may infer this from the "
            "endpoint the client submits requests to. Cannot be "
            "updated. In CamelCase. "
        )
    )
}


OBJECT_ATTRS = {
    **copy.deepcopy(COMMON_ATTRS),
    'metadata': pydantic.Field(
        title="Metadata",
        description="Standard object metadata."
    ),
    'spec': pydantic.Field(
        title="Specification"
    )
}


LIST_ATTRS = {
    **copy.deepcopy(COMMON_ATTRS),
    'metadata': pydantic.Field(
        title="Metadata",
        description="Standard list metadata."
    ),
}


def _get_model_fields(cls):
    return {
        attname: value for attname, value
            in dict.items(dict(cls.__dict__))
            if not inspect.isfunction(value)
            and not str.startswith(attname, '__')
    }

def _get_object_attrs(spec_class, kind):
    return {
        **copy.deepcopy(OBJECT_ATTRS),
        '__annotations__': {
            'api_version': str,
            'kind': typing.Literal[kind],
            'metadata': ObjectMetadata,
            'spec': spec_class
        }
    }


def _spec_factory(cls):
    return type(
        f'{cls.__name__}Spec',
        (pydantic.BaseModel,),
        {
            **_get_model_fields(cls),
            '__annotations__': cls.__dict__.get('__annotations__') or {}
        }
    )


def _list_factory(cls, version, kind):
    return type(f'{kind}List', (pydantic.BaseModel,), {
        **copy.deepcopy(LIST_ATTRS),
        '_version': version,
        '_kind': f'{kind}List',
        'items': pydantic.Field(...,
            title="items",
            description=f"Items in the list of {kind}s"
        ),
        '__annotations__': {
            'api_version': str,
            'kind': typing.Literal[f'{kind}List'],
            'metadata': ListMetadata,
            'items': typing.List[cls]
        }
    })


def resource(version, with_list=False):
    """Create a :class:`pydantic.BaseModel` implementation with
    default properties and methods.
    """
    def decorator_factory(cls):
        resource_class = type(
            cls.__name__,
            (BaseResource, pydantic.BaseModel),
            {
                '_version': version,
                **_get_object_attrs(_spec_factory(cls), cls.__name__)
            }
        )
        if with_list:
            resource_class.List = _list_factory(
                resource_class, version, cls.__name__
            )
        return resource_class

    return decorator_factory
