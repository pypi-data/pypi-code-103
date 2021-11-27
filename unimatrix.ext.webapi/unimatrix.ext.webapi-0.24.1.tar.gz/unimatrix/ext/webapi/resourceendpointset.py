# pylint: skip-file
"""Declares :class:`ResourceEndpointSet`."""
import copy
import functools
import inspect
import re
import types
import typing
from collections import OrderedDict

import ioc
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from fastapi.security import HTTPBearer
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel
from unimatrix.conf import settings

from .auth import IHTTPAuthenticationService
from .exceptions import BearerAuthenticationRequired
from .exceptions import TrustIssues
from .resourceschema import ResourceSchema


ACTION_METHODS = {
    'apply'     : 'PATCH',
    'create'    : 'POST',
    'destroy'   : 'DELETE',
    'index'     : 'GET',
    'purge'     : 'DELETE',
    'replace'   : 'PUT',
    'retrieve'  : 'GET',
    'update'    : 'POST',
}

DETAIL_ACTIONS = {'retrieve', 'update', 'replace', 'destroy', 'apply'}


def get_return_type(handler):
    rettype = typing.get_type_hints(handler).get('return')
    if rettype and not issubclass(rettype, BaseModel): # pragma: no cover
        rettype = None
    return rettype


class ResourceEndpointSetMetaclass(type):

    def __new__(cls, name, bases, attrs):
        super_new = super().__new__
        if name in ('ResourceEndpointSet', 'PublicResourceEndpointSet'):
            return super_new(cls, name, bases, attrs)
        new_class = super_new(cls, name, bases, attrs)
        hints = typing.get_type_hints(new_class)

        # Convert the path_parameter attribute to an inspect.Parameter
        # instance. This is later used for constructing the appropriate
        # signature. If there is no annotation, assume that it is a string.
        new_class.path_parameter = inspect.Parameter(
            'path_parameter',
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=hints.get('path_parameter') or str,
            default=new_class.path_parameter
        )

        return new_class

class ResourceEndpointSet(metaclass=ResourceEndpointSetMetaclass):
    """Groups a set of endpoints that allow reading, mutating and
    destroying a specific resource.
    """

    #: The list of valid action names.
    valid_actions: list = [
        'create', 'retrieve', 'update', 'destroy', 'index', 'apply', 'replace',
        'purge'
    ]

    #: The current request that is being handled. This attribute is ``None``
    #: when initializing :class:`ResourceEndpointSet` and is set when the ASGI
    #: interface function is invoked.
    request: Request = None

    #: The schema class used to serialize and deserialize the resource.
    resource_schema: ResourceSchema = None

    #: The name of the resource identifier as a path path_parameter.
    path_parameter: str = 'resource_id'

    #: Set this to ``True`` if the path parameter may have
    #: slashes.
    path_allows_slashes: bool = False

    #: A list of :class:`ResourceEndpointSet` implementations representing
    #: subresources. Subresources always operate on a single object.
    subresources: list = []

    #: Indicates if a request must be authenticated using the ``Authorization``
    #: header.
    require_authentication: bool = True

    #: The list of audiences of which a bearer token must specify at least one
    #: (through the ``aud`` claim).
    accepted_audiences: set = []

    #: The permission scope that an authenticated request must have.
    required_scope: set = []

    #: The list of bearer token issuers that are trusted by this endpoint.
    #: This is also the return value of the default implementation of
    #: :meth:`get_trusted_issuers`.
    trusted_issuers: set = []

    #: Specifies the internal name of the resource that may be used to
    #: reverse its endpoints e.g. if :attr:`resource_name` is `foo`,
    #: then the `retrieve` method becomes reversible by the name
    #: `foo.retrieve`. If :attr:`resource_name` is not defined, then the
    #: class name is used.
    resource_name: str = None

    #: Specifies a human-readable name to group the endpoint set under.
    group_name: str = None

    #: The policy used to determine wether a key is trusted or not.
    trust_policy = None

    #: Indicate if the application default secret key is trusted by this
    #: endpoint.
    trust_local: bool = False

    #: Indicates if the resource is a singleton and detail-specific
    #: behavior must be forced.
    singleton: bool = False

    def __init__(self, action, *args, **kwargs):
        self.action = action

    @classmethod
    def add_to_router(cls,
        router: APIRouter,
        base_path: str,
        parent: 'ResourceEndpointSet' = None,
        url_params: list = None,
        base_name: str = None,
        group_name: str = None,
        path_parameters: list = None
    ) -> None:
        """Add the :class:`ResourceEndpointSet` to a router instance at the given
        `base_path`.
        """
        path_parameters = path_parameters or []
        if not cls.singleton:
            path_parameters.append(cls.path_parameter)
        url_params = []
        base_name = str.lower(
            base_name
            or cls.resource_name
            or re.sub('(Ctrl|EndpointSet)', '', cls.__name__)
        )
        if parent is not None:
            base_name = f'{base_name}.' + str.lower(
                cls.resource_name
                or re.sub('(Ctrl|EndpointSet)', '', cls.__name__)
            )

        group_name = group_name or cls.group_name
        if parent:
            url_params.insert(0, parent.path_parameter.default)
        if not str.startswith(base_path, '/'): # pragma: no cover
            raise ValueError("The `base_path` must begin with a slash (/).")

        # Iterate over methods that are marked as actions.
        for attname, obj in list(cls.__dict__.items()):
            if not hasattr(obj, 'action'):
                continue
            if obj.action.name == 'action': # pragma: no cover
                raise ValueError('Can not use `action` as a function name.')

            path = base_path
            if obj.action.detail:
                path = f'{base_path}/{{{cls.path_parameter.default}}}'
                if cls.path_allows_slashes:
                    path = f'{base_path}/{{{cls.path_parameter.default}:path}}'
                path = re.sub('^[/]+', '/', path) # TODO: hack

                # Check if the path parameter name is not the same as the
                # parent class
                if parent and parent.path_parameter.default\
                == cls.path_parameter.default: # pragma: no cover
                    raise ValueError(
                        "Parent path parameter name must be different from "
                        "the child."
                    )

            tags = []
            if group_name: # pragma: no cover
                tags.append(group_name)
            path = f'{path}/{obj.action.path}'
            name = f'{base_name}.{str.lower(obj.action.name)}'
            router.add_api_route(
                path,
                cls._create_annotated_handler(
                    cls, obj.action.name, obj, parent=parent,
                    detail=obj.action.detail,
                    path_parameters=path_parameters,
                    logger=router.logger
                ),
                name=name,
                summary=name,
                tags=tags,
                methods=obj.action.methods,
                response_model=getattr(
                    obj,
                    'response_model',
                    get_return_type(obj)),
                response_model_exclude_defaults=True,
                response_model_exclude_none=True,
            )

        has_detail_methods = False
        has_collection_methods = False or cls.singleton
        for action in cls.valid_actions:
            # Create a fake signature to trick FastAPI in registering the
            # correct path parameters, authentication schemes, etc.
            handler = getattr(cls, action, None)
            path = base_path
            if handler is None: # pragma: no cover
                continue

            # Add the path parameter for actions that operate on a specific
            # resource.
            is_detail = (action in DETAIL_ACTIONS)
            if is_detail and not cls.singleton:
                has_detail_methods = True
                path = f'{base_path}/{{{cls.path_parameter.default}}}'
                if cls.path_allows_slashes:
                    path = f'{base_path}/{{{cls.path_parameter.default}:path}}'
                path = re.sub('^[/]+', '/', path) # TODO: hack

                # Check if the path parameter name is not the same as the
                # parent class
                if parent and parent.path_parameter.default\
                == cls.path_parameter.default: # pragma: no cover
                    raise ValueError(
                        "Parent path parameter name must be different from "
                        "the child."
                    )
            else:
                has_collection_methods = True

            name = f'{base_name}.{action}'
            summary = name
            tags = []
            if group_name: # pragma: no cover
                tags.append(group_name)
            router.add_api_route(
                path,
                cls._create_annotated_handler(
                    cls, action, handler,
                    parent=parent,
                    detail=is_detail,
                    path_parameters=path_parameters,
                    logger=router.logger
                ),
                name=name,
                summary=summary,
                tags=tags,
                methods=[ ACTION_METHODS[action] ],
                response_model=getattr(
                    handler,
                    'response_model',
                    get_return_type(handler)),
                response_model_exclude_defaults=True,
                response_model_exclude_none=True,
            )

        # Iterate over subresources and add them add detail endpoints.
        for subresource_class in cls.subresources:
            subresource_class.add_to_router(
                router, f'{base_path}/{{{cls.path_parameter.default}}}/{subresource_class.resource_name}', # pylint: disable=line-too-long
                parent=cls,
                url_params=url_params,
                group_name=group_name,
                base_name=base_name,
                path_parameters=copy.deepcopy(path_parameters)
            )

        # Create the OPTIONS methods. Basically, we need to figure out what
        # the URL parameters are i.e. on subresources there are multiple URL
        # parameters.
        #
        #async def options(request: Request, *args, **kwargs):
        #    view = cls('options')
        #    view.request = request
        #    return await view.dispatch(*args, **kwargs)

        #sig = inspect.signature(options)
        #ann = OrderedDict()
        #ann['request'] = inspect.Parameter(
        #    'request',
        #    inspect.Parameter.POSITIONAL_OR_KEYWORD,
        #    annotation=Request
        #)
        #for name in url_params:
        #    ann[name] = inspect.Parameter(
        #        name,
        #        inspect.Parameter.POSITIONAL_OR_KEYWORD
        #    )
        #options.__signature__ = sig.replace(
        #    parameters=list(ann.values())
        #)
        #options.__annotations__ = ann
        #if has_collection_methods:
        #    router.add_api_route(base_path, options, methods=['OPTIONS'])

        #if has_detail_methods:
        #    ann[cls.path_parameter] = inspect.Parameter(
        #        cls.path_parameter,
        #        inspect.Parameter.POSITIONAL_OR_KEYWORD
        #    )
        #    options.__signature__ = sig.replace(
        #        parameters=list(ann.values())
        #    )
        #    options.__annotations__ = ann
        #    router.add_api_route(f'{base_path}/{{{cls.path_parameter}}}', options, methods=['OPTIONS'])


    @staticmethod
    def _update_signature(action, handler, protected=False, detail=False, path_parameters=None, singleton=False): # pylint: disable=line-too-long
        # Create an ordered dictionary containing the handlers' signature
        # parameters and add in the following order:
        #
        # 1. The request object
        #
        # This will cause FastAPI to inject the correct dependencies and
        # update the OpenAPI specification properly.
        signature = inspect.signature(handler)
        annotations = OrderedDict()
        annotations['request'] = inspect.Parameter(
            'request',
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=Request
        )

        if detail and path_parameters:
            for param in path_parameters:
                annotations[param.default] = inspect.Parameter(
                    param.default,
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=param.annotation
                )

        # Update the annotations dictionary with the remaining parameters
        # and create a new call signature. Do that before the other arguments
        # to prevent argument order errors. Remove the 'self' parameter since
        # it confuses FastAPI. Handle variable arguments after any inserted
        # arguments.
        for varname, param in list(signature.parameters.items()):
            if param.kind == inspect.Parameter.VAR_POSITIONAL: # pragma: no cover
                break
            annotations[varname] = param

        # Add the bearer token as a keyword parameter for protected endpoints.
        if protected:
            annotations['_bearer'] = inspect.Parameter(
                '_bearer',
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                default=Depends(HTTPBearer(auto_error=False)),
            )

        # Remove the self parameter (causes incorrect rendering of the UI)
        # and add the variable positional and keyword arguments, if any. This
        # should not happen because request handlers do no accept these kind
        # of arguments, but the error raised by the inspect module if the
        # order is incorrect is quite cryptic.
        for varname, param in list(signature.parameters.items()): # pragma: no cover
            if param.kind != inspect.Parameter.VAR_POSITIONAL\
            and param.kind != inspect.Parameter.VAR_KEYWORD:
                continue
            annotations[varname] = param

        # Update the signature to hold the new annotations. Remove the self
        # parameter to not confuse FastAPI
        annotations.pop('self', None)
        annotations.pop('args', None)
        annotations.pop('kwargs', None)
        signature = signature.replace(
            parameters=list(annotations.values())
        )

        return signature, annotations

    @staticmethod # pylint: disable=line-too-long
    def _create_annotated_handler(view_class, action, handler, parent, detail, path_parameters, logger=None):
        @functools.wraps(handler)
        async def request_handler(
            request: Request,
            *args, **kwargs
        ):
            """Wrapper function that ensures that the proper dependencies
            are injected when handling an incoming HTTP request.
            """
            view = view_class(action)
            view.request = request
            view.logger = logger
            return await view.dispatch(*args, **kwargs)

        request_handler.__signature__, request_handler.__annotations__ = (
            view_class._update_signature(action, handler,
                protected=view_class.require_authentication,
                detail=detail,
                path_parameters=path_parameters,
                singleton=view_class.singleton
            )
        )
        return request_handler

    def get_audience(self) -> set:
        """Return the audience for this endpoint that is used to verify
        the ``aud`` claim of bearer tokens. The default implementation returns
        an empty list.
        """
        audiences = self.accepted_audiences\
            + [f"https://{self.request.url.netloc}", "self"]\
            + list(settings.OAUTH2_AUDIENCES)
        return list(sorted(set(audiences)))

    def get_scope(self) -> set:
        """Return the scope that is required for authenticated requests."""
        return self.required_scope

    def get_trusted_issuers(self) -> set:
        """Return the list of trusted issuers as compared against the ``iss``
        claim.
        """
        return list(self.trusted_issuers)\
            + list(settings.OAUTH2_TRUSTED_STS)\
            + [f"https://{self.request.url.netloc}", "self"]

    async def dispatch(self, *args, **kwargs) -> dict:
        """Dispatch the incoming HTTP request to the appropriate request
        handler.
        """
        if self.require_authentication:
            await self.authenticate(kwargs.pop('_bearer', None))
        handler = getattr(self, self.action)

        assert callable(handler), handler #nosec
        return await handler(*args, **kwargs)


    @ioc.inject('authentication', 'HTTPAuthenticationService')
    async def authenticate(self,
        dto: HTTPAuthorizationCredentials,
        authentication: IHTTPAuthenticationService
    ):
        """Authenticates the request using the bearer token provided in the
        request.

        Pass the request instance and the bearer to all authenticators and
        return the result of the first succesful attempt. If no authenticator
        could resolve a principal and subject, raise an exception if the
        resource requires authentication.
        """
        self.principal = None
        if dto is not None:
            if not self.trust_policy\
            and self.require_authentication\
            and not self.trust_local:
                raise TrustIssues
            self.principal = await authentication.resolve(
                str.encode(dto.credentials),
                audience=self.get_audience(),
                issuers=self.get_trusted_issuers(),
                scope=self.get_scope(),
                policy=self.trust_policy
            )
        if self.principal is None and self.require_authentication:
            raise BearerAuthenticationRequired


class PublicResourceEndpointSet(ResourceEndpointSet):
    """A :class:`ResourceEndpointSet` implementation that is public i.e.
    no authentication or authorization is performed.
    """
    require_authentication = False
