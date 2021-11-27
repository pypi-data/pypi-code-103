import asyncio
import http.client
import json
from typing import Any, Callable, Iterable, Type, TypeVar

try:
    from django.core.exceptions import ValidationError as DjangoValidationError
    from django.core.exceptions import ObjectDoesNotExist
except ImportError:
    DjangoValidationError = None
    ObjectDoesNotExist = None

try:
    from rest_framework.exceptions import ValidationError as DRFValidationError
except ImportError:
    DRFValidationError = None

try:
    from pydantic import ValidationError as PydanticError
except ImportError:
    PydanticError = None

__all__ = [
    'version',
    'RichErr',
    'BadRequest',
    'Unauthorized',
    'PaymentRequired',
    'Forbidden',
    'NotFound',
    'MethodNotAllowed',
    'NotAcceptable',
    'ProxyAuthenticationRequired',
    'RequestTimeout',
    'Conflict',
    'Gone',
    'LengthRequired',
    'PreconditionFailed',
    'PayloadTooLarge',
    'UTITooLong',
    'UnsupportedMediaType',
    'RangeNotSatisfiable',
    'ExpectationFailed',
    'ImATeapot',
    'AuthenticationTimeout',
    'MisdirectedRequest',
    'UnprocessableEntity',
    'Locked',
    'FailedDependency',
    'TooEarly',
    'UpgradeRequired',
    'PreconditionRequired',
    'TooManyRequests',
    'RequestHeaderFieldsTooLarge',
    'RetryWith',
    'UnavailableForLegalReasons',
    'ClientClosedRequest',
    'InternalServerError',
    'MethodNotImplemented',
    'BadGateway',
    'ServiceUnavailable',
    'GatewayTimeout',
    'VersionNotSupported',
    'VariantAlsoNegotiates',
    'InsufficientStorage',
    'LoopDetected',
    'BandwidthLimitExceeded',
    'NotExtended',
    'NetworkAuthenticationRequired',
    'UnknownError',
    'WebServerIsDown',
    'ConnectionTimedOut',
    'OriginIsUnreachable',
    'TimeoutOccurred',
    'SSLHandshakeFailed',
    'InvalidSSLCertificate',
]

version = (0, 2, 3)

_T = TypeVar('_T', bound='RichErr')
_E = TypeVar('_E', bound=BaseException)


class RichErr(Exception):
    _conversions: list[tuple[Type[_E], list[Type[_E]], Type[_T] | Callable[[_E], _T]]] = []
    DEFAULT_CODE: int = 500
    DEFAULT_MESSAGE: str = 'Internal Server Error'
    ERRORS: dict[str, Type[_T]] = {}

    def __init__(self, message: str | bytes | None = None, code: int | None = None,
                 caused_by: _E | None = None, **extras):
        self.code: int = self.DEFAULT_CODE if code is None else code
        if isinstance(message, bytes):
            message = message.decode('utf-8')
        if message is not None:
            self.message: str = message
        elif self.code in http.client.responses:
            self.message: str = http.client.responses[self.code]
        else:
            self.message: str = self.DEFAULT_MESSAGE
        self.extras: dict = extras
        if caused_by is not None:
            self.cause = caused_by

    def __init_subclass__(cls):
        cls.ERRORS[cls.error_name()] = cls

    @classmethod
    def from_error(cls, err: _E, message: str | bytes | None = None,
                   code: int | None = None, name: str | bytes | None = None) -> _T:
        return cls._from_error(err, message, code, name, err)

    @classmethod
    def _from_error(cls, err: _E, message: str | bytes | None = None,
                    code: int | None = None, name: str | bytes | None = None, caused_by: _E | None = None) -> _T:
        exc = cls
        if isinstance(name, bytes):
            name = name.decode('utf-8')
        if name is not None:
            exc: Type[_T] = type(name, (RichErr,), {})  # noqa
        if message is None:
            message = str(err)
        if code is None:
            code = cls.DEFAULT_CODE
        return exc(message, code=code, caused_by=caused_by)

    @property
    def cause(self) -> _E | None:
        return self.__cause__

    @cause.setter
    def cause(self, err: _E | None) -> None:
        self.__cause__ = err

    @property
    def caused_by(self) -> dict | None:
        cause = self.__cause__
        if cause is None:
            return None
        if isinstance(cause, RichErr):
            return dict(cause)
        return dict(self._from_error(cause, name=type(cause).__name__))

    @classmethod
    def error_name(cls) -> str:
        cls_name = cls.__name__
        return cls_name.removesuffix('Exception')

    @classmethod
    def add_conversion(cls, exc_type: Type[_E], to: Type[_T] | Callable[[_E], _T]) -> None:
        mro = exc_type.mro()[:-1]
        idx = 0
        for i, (t, m, f) in enumerate(cls._conversions):
            if t in mro:
                idx = i
                break
            if exc_type in m:
                idx = i
        cls._conversions.insert(idx, (exc_type, mro, to))

    @classmethod
    def remove_conversion(cls, exc_type: Type[_E]) -> None:
        cls._conversions = [i for i in cls._conversions if i[0] is not exc_type]

    @classmethod
    def convert(cls, err: _E) -> _T:
        if isinstance(err, RichErr):
            return err
        for t, _, f in cls._conversions:
            if isinstance(err, t):
                if isinstance(f, type) and issubclass(f, RichErr):
                    return f.from_error(err)
                else:
                    return f(err)
        return InternalServerError.from_error(err)

    def __str__(self) -> str:
        return f'{self.error_name()}({self.code}): {self.message}'

    def __repr__(self) -> str:
        return f'{self.__class__.__qualname__}(message={self.message}, code={self.code}, caused_by={self.caused_by}, **{self.extras})'

    @property
    def __dict__(self) -> dict:
        return {
            'error': {
                'code': self.code,
                'exception': self.error_name(),
                'message': self.message,
                'caused_by': self.caused_by,
                **self.extras,
            }
        }

    def __iter__(self) -> Iterable[tuple[str, Any]]:
        yield from self.__dict__.items()

    def __hash__(self):
        return hash(self.json())

    def dict(self) -> dict:
        return self.__dict__

    def json(self, **kwargs) -> str:
        return json.dumps(dict(self), **kwargs)

    def __eq__(self, other) -> bool:
        return dict(self) == vars(other)


RichErr.ERRORS[RichErr.error_name()] = RichErr


class BadRequest(RichErr):
    DEFAULT_CODE = 400


class Unauthorized(RichErr):
    DEFAULT_CODE = 401


class PaymentRequired(RichErr):
    DEFAULT_CODE = 402


class Forbidden(RichErr):
    DEFAULT_CODE = 403


class NotFound(RichErr):
    DEFAULT_CODE = 404


class MethodNotAllowed(RichErr):
    DEFAULT_CODE = 405


class NotAcceptable(RichErr):
    DEFAULT_CODE = 406


class ProxyAuthenticationRequired(RichErr):
    DEFAULT_CODE = 407


class RequestTimeout(RichErr):
    DEFAULT_CODE = 408


class Conflict(RichErr):
    DEFAULT_CODE = 409


class Gone(RichErr):
    DEFAULT_CODE = 410


class LengthRequired(RichErr):
    DEFAULT_CODE = 411


class PreconditionFailed(RichErr):
    DEFAULT_CODE = 412


class PayloadTooLarge(RichErr):
    DEFAULT_CODE = 413


class UTITooLong(RichErr):
    DEFAULT_CODE = 414


class UnsupportedMediaType(RichErr):
    DEFAULT_CODE = 415


class RangeNotSatisfiable(RichErr):
    DEFAULT_CODE = 416


class ExpectationFailed(RichErr):
    DEFAULT_CODE = 417


class ImATeapot(RichErr):
    DEFAULT_CODE = 418


class AuthenticationTimeout(RichErr):
    DEFAULT_CODE = 419


class MisdirectedRequest(RichErr):
    DEFAULT_CODE = 421


class UnprocessableEntity(RichErr):
    DEFAULT_CODE = 422


class Locked(RichErr):
    DEFAULT_CODE = 423


class FailedDependency(RichErr):
    DEFAULT_CODE = 424


class TooEarly(RichErr):
    DEFAULT_CODE = 425


class UpgradeRequired(RichErr):
    DEFAULT_CODE = 426


class PreconditionRequired(RichErr):
    DEFAULT_CODE = 428


class TooManyRequests(RichErr):
    DEFAULT_CODE = 429


class RequestHeaderFieldsTooLarge(RichErr):
    DEFAULT_CODE = 431


class RetryWith(RichErr):
    DEFAULT_CODE = 449


class UnavailableForLegalReasons(RichErr):
    DEFAULT_CODE = 451


class ClientClosedRequest(RichErr):
    DEFAULT_CODE = 499


class InternalServerError(RichErr):
    DEFAULT_CODE = 500


class MethodNotImplemented(RichErr):
    DEFAULT_CODE = 501


class BadGateway(RichErr):
    DEFAULT_CODE = 502


class ServiceUnavailable(RichErr):
    DEFAULT_CODE = 503


class GatewayTimeout(RichErr):
    DEFAULT_CODE = 504


class VersionNotSupported(RichErr):
    DEFAULT_CODE = 505


class VariantAlsoNegotiates(RichErr):
    DEFAULT_CODE = 506


class InsufficientStorage(RichErr):
    DEFAULT_CODE = 507


class LoopDetected(RichErr):
    DEFAULT_CODE = 508


class BandwidthLimitExceeded(RichErr):
    DEFAULT_CODE = 509


class NotExtended(RichErr):
    DEFAULT_CODE = 510


class NetworkAuthenticationRequired(RichErr):
    DEFAULT_CODE = 511


class UnknownError(RichErr):
    DEFAULT_CODE = 520


class WebServerIsDown(RichErr):
    DEFAULT_CODE = 521


class ConnectionTimedOut(RichErr):
    DEFAULT_CODE = 522


class OriginIsUnreachable(RichErr):
    DEFAULT_CODE = 523


class TimeoutOccurred(RichErr):
    DEFAULT_CODE = 524


class SSLHandshakeFailed(RichErr):
    DEFAULT_CODE = 525


class InvalidSSLCertificate(RichErr):
    DEFAULT_CODE = 526


RichErr.add_conversion(asyncio.CancelledError, InternalServerError)
RichErr.add_conversion(asyncio.TimeoutError, GatewayTimeout)
RichErr.add_conversion(ValueError, BadRequest)
RichErr.add_conversion(TypeError, BadRequest)
RichErr.add_conversion(AssertionError, BadRequest)
RichErr.add_conversion(IndexError, NotFound)
RichErr.add_conversion(KeyError, NotFound)
RichErr.add_conversion(http.client.HTTPException, InternalServerError)

if DRFValidationError is not None:
    def _convert(err: DRFValidationError) -> _T:
        detail = err.detail
        field = ''
        if isinstance(detail, list):
            detail = next(iter(detail), err.default_detail)
        elif isinstance(detail, dict):
            detail = next(iter(detail.items()), (None, err.default_detail))
            field = f'{detail[0]}: '
            detail = detail[1][0]

        return NotAcceptable.from_error(err, f'{field}{detail!s}')


    RichErr.add_conversion(DRFValidationError, _convert)

if DjangoValidationError is not None:
    def _convert(err: DjangoValidationError) -> _T:
        message = list(err)
        if not message:
            message = str(err.message)
        elif isinstance(message[0], str):
            message = message[0]
        elif isinstance(message[0], tuple):
            for e in message[0][1]:
                return _convert(e)
            message = str(err)
        return NotAcceptable.from_error(err, message)


    RichErr.add_conversion(DjangoValidationError, _convert)
    RichErr.add_conversion(ObjectDoesNotExist, NotFound)

if PydanticError is not None:
    def _convert(err: PydanticError):
        error = err.errors()[0]
        loc = ' -> '.join(str(e) for e in error['loc'])
        message = f'"{loc}": {error["msg"]}'
        return BadRequest.from_error(err, message=message, name='ValidationError')


    RichErr.add_conversion(PydanticError, _convert)
