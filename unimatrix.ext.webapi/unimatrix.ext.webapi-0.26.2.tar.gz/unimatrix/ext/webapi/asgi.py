# pylint: disable=line-too-long
"""Declares :class:`Application`."""
import asyncio
import logging
import os
import random
import time
import typing

import fastapi
import unimatrix.runtime
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from fastapi.responses import JSONResponse
from ioc.exc import UnsatisfiedDependency
from starlette.middleware.trustedhost import TrustedHostMiddleware
from unimatrix.conf import settings
from unimatrix.ext import crypto
from unimatrix.ext import jose
from unimatrix.ext.model.exc import CanonicalException
from unimatrix.ext.model.exc import FeatureNotSupported
from uvicorn.config import LOGGING_CONFIG

from . import urlconf
from .exceptions import TryAgain
from .exceptions import UpstreamServiceNotAvailable
from .exceptions import UpstreamConnectionFailure
from .healthcheck import live as liveness_handler
from .healthcheck import ready as readyness_handler
from .metadata import APIMetadataService
from .models import APIMetadata


class Application(fastapi.FastAPI):
    """Provides the ASGI interface to handle requests."""
    cors_max_age: int = 600
    logger: logging.Logger = logging.getLogger('uvicorn')

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('openid_providers',
            getattr(settings, 'OPENID_PROVIDERS', {})
        )
        kwargs.setdefault('redoc_url', getattr(settings, 'REDOC_URL', '/docs'))
        kwargs.setdefault('docs_url', getattr(settings, 'DOCS_URL', '/ui'))
        kwargs.setdefault('openapi_url',
            getattr(settings, 'OPENAPI_URL', '/openapi.json')
        )
        kwargs.setdefault('root_path', os.getenv('HTTP_MOUNT_PATH'))

        # Configure the default exception handlers for the errors specified by
        # the Unimatrix Framework.
        exception_handlers = kwargs.setdefault('exception_handlers', {})
        exception_handlers.update({
            asyncio.TimeoutError: self.canonical_exception,
            CanonicalException: self.canonical_exception,
            ConnectionError: self.canonical_exception,
            TimeoutError: self.canonical_exception,
            UnsatisfiedDependency: self.canonical_exception
        })

        # Remove the additional variables that we added to prevent them from
        # being passed to the fastapi.FastAPI.
        allowed_hosts = kwargs.pop('allowed_hosts', None)
        self.audience = kwargs.pop('audience', None)
        self.issuer = kwargs.pop('issuer', None)
        self.urlconf = kwargs.pop('urlconf', settings.HTTP_URLCONF)

        # Check if debug endpoints are enabled
        enable_debug_endpoints = kwargs.pop('enable_debug_endpoints', False)

        super().__init__(*args, **kwargs)
        # Not so elegant
        LOGGING_CONFIG['disable_existing_loggers'] = True
        LOGGING_CONFIG['loggers']['uvicorn']['level'] = settings.LOG_LEVEL
        logging.config.dictConfig(LOGGING_CONFIG)

        # Add standard health-check routes. The initial use case here was
        # Kubernetes.
        self.add_api_route(
            '/.well-known/health/live',
            liveness_handler,
            name='live',
            status_code=204,
            tags=['Health'],
            methods=['GET'],
            response_description = "The service is live.",
            responses={
                '503': {'description': "The service is not live."},
            }
        )
        self.add_api_route(
            '/.well-known/health/ready',
            readyness_handler,
            name='ready',
            tags=['Health'],
            methods=['GET'],
            status_code=204,
            response_description = "The service is ready.",
            responses={
                '503': {'description': "The service is not ready."},
            }
        )

        # Ensure that the Unimatrix startup and teardown functions are invoked
        # when spawning a new ASGI application.

        @self.on_event('startup')
        async def on_startup(): # pylint: disable=unused-variable
            await unimatrix.runtime.on('boot') # pragma: no cover
            self.logger.info("Unimatrix bootstrap complete.")

            if enable_debug_endpoints:
                self.logger.warning("Mounting debug endpoints.")

            # If there is an URL configuration file and it exists, add the routes
            # from it to the application.
            if self.urlconf is not None:
                if not os.path.exists(self.urlconf):
                    self.logger.warning(
                        "URL configuration file does not exist: %s", self.urlconf
                    )
                else:
                    urlconf.fromfile(self, self.urlconf)


        @self.on_event('shutdown')
        async def on_shutdown(): # pylint: disable=unused-variable
            await unimatrix.runtime.on('shutdown') # pragma: no cover

        @self.middleware('http')
        async def set_cache_headers(request: Request, call_next):
            response = await call_next(request)
            if not response.headers.get('Cache-Control'):
                response.headers['Cache-Control'] = "no-cache, no-store, must-revalidate"
                response.headers['Pragma'] = "no-cache"
                response.headers['Expires'] = "0"
            return response

        # Add mandatory middleware to the application.
        self.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=(
                allowed_hosts or getattr(settings, 'HTTP_ALLOWED_HOSTS', [])
            )
        )

        # Enable CORS based on the environment variables and/or settings
        # module.
        self.enable_cors(
            allow_origins=settings.HTTP_CORS_ALLOW_ORIGINS,
            allow_credentials=settings.HTTP_CORS_ALLOW_CREDENTIALS,
            allow_methods=settings.HTTP_CORS_ALLOW_METHODS,
            allow_headers=settings.HTTP_CORS_ALLOW_HEADERS,
            expose_headers=settings.HTTP_CORS_EXPOSE_HEADERS,
            max_age=settings.HTTP_CORS_TTL
        )

        # Add debug handlers if the debug endpoints are enabled.
        if enable_debug_endpoints:
            debug = fastapi.APIRouter()

            @debug.get('/sleep') # pragma: no cover
            async def sleep(seconds: float = None):
                await asyncio.sleep(seconds or random.randint(0, 5) / 10) # nosec

            @debug.post('/token', response_class=PlainTextResponse)
            async def create_bearer_token(
                request: Request,
                dto: dict,
                alg: typing.Literal[
                    'RSAPKCS1v15SHA256',
                    'RSAPKCS1v15SHA384',
                    'RSAPKCS1v15SHA512',
                    'SECP256K1SHA256',
                    'SECP256R1SHA256',
                ] = None,
                keyid: str = None
            ) -> str:
                """Create a JWT with the claims provided in the request body.
                For development purposes only.
                """
                signer = crypto.get_signer()
                if keyid and alg:
                    signer = crypto.get_signer(
                        getattr(crypto, alg),
                        keyid=keyid
                    )
                now = int(time.time())
                dto = {
                    'iss': f'{request.url.scheme}://{request.url.netloc}',
                    'aud': f'{request.url.scheme}://{request.url.netloc}',
                    'sub': f'{request.url.scheme}://{request.url.netloc}',
                    'iat': now,
                    'exp': now + 3600,
                    **(dto or {})
                }
                jwt = await jose.jwt(dto, signer=signer)
                return bytes.decode(bytes(jwt))

            self.include_router(debug, prefix='/debug', tags=['Debug'])

        @self.get('/.well-known/self', tags=['Metadata'], response_model=APIMetadata)
        async def metadata(request: Request):
            svc = APIMetadataService()
            return APIMetadata(**await svc.get(self, request))

    async def canonical_exception(self, request, exception):
        """Handles a canonical exception to a standard error message format."""
        if isinstance(exception, ConnectionRefusedError):
            kwargs = {}
            return await self.canonical_exception(
                request,
                UpstreamServiceNotAvailable(**kwargs),
            )
        elif isinstance(
            exception,
            (BrokenPipeError, ConnectionResetError, ConnectionAbortedError)
        ):
            kwargs = {}
            return await self.canonical_exception(
                request,
                UpstreamConnectionFailure(**kwargs),
            )
        elif isinstance(exception, UnsatisfiedDependency):
            return await self.canonical_exception(
                request, FeatureNotSupported()
            )
        elif isinstance(exception, (asyncio.TimeoutError, TimeoutError)):
            #count = int(request.headers.get('X-Retry') or 0)
            return await self.canonical_exception(
                request, TryAgain(30)
            )
        elif isinstance(exception, CanonicalException):
            if exception.http_status_code >= 500:
                exception.log(self.logger.exception)
            response = JSONResponse(
                status_code=exception.http_status_code,
                content=exception.as_dict()
            )
            response.headers['X-Canonical-Exception'] = type(exception).__name__
            return response
        else:
            raise NotImplementedError

    def enable_cors(self,
        allow_origins: list = None,
        allow_credentials: bool = False,
        allow_methods: list = None,
        allow_headers: list = None,
        expose_headers: list = None,
        max_age: int = None
    ):
        """Enables and configures Cross-Origin Resource Sharing (CORS)."""
        self.add_middleware(
            CORSMiddleware,
            allow_origins=allow_origins or [],
            allow_credentials=allow_credentials,
            allow_methods=allow_methods or [],
            allow_headers=allow_headers or [],
            expose_headers=expose_headers or [],
            max_age=max_age or self.cors_max_age
        )

    def get_audience(self, request: Request) -> str:
        """Return the issuer used for JWS access tokens."""
        return self.audience or f'{request.url.scheme}://{request.url.netloc}'

    def get_issuer(self, request: Request) -> str:
        """Return the issuer used for JWS access tokens."""
        return self.issuer or f'{request.url.scheme}://{request.url.netloc}'
