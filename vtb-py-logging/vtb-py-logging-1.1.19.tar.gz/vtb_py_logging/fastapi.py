import functools
import urllib
import typing
import logbook
import time
from vtb_py_logging.log_extra import log_extra, get_extra
from vtb_py_logging.request_id import RequestId
from vtb_py_logging.utils import get_request_client_ip, env_get_bool
from starlette.types import ASGIApp, Scope, Receive, Send
from starlette.responses import JSONResponse as _JSONResponse, Response
from starlette.requests import Request
from starlette.background import BackgroundTask
from fastapi.routing import APIRoute
from multipart.multipart import parse_options_header
from fastapi.exceptions import RequestValidationError


def get_request_id_middleware(prefix, progname=""):
    return functools.partial(RequestIdMiddleware, prefix=prefix, progname=progname)


class RequestIdMiddleware:
    def __init__(self, app: ASGIApp, prefix="", progname="") -> None:
        self.app = app
        self.prefix = prefix
        self.default_extra = {}
        if progname:
            self.default_extra["progname"] = progname

    @staticmethod
    def get_request_id_header(headers):
        for name, value in headers:
            if name.lower() == b"x-request-id":
                try:
                    return value.decode("ascii")
                except UnicodeDecodeError as e:
                    logbook.warning("Failed to decode x-request-id header '{}': {}", value, e)
                    return ""

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = self.get_request_id_header(scope["headers"]) or RequestId.make(prefix=self.prefix)

        with log_extra(request_id=request_id, **self.default_extra):
            await self.app(scope, receive, send)


class JSONResponseRequestId(_JSONResponse):
    def __init__(self, content: typing.Any = None, status_code: int = 200,
                 headers: dict = None, media_type: str = None, background: BackgroundTask = None):
        super().__init__(content, status_code, headers, media_type, background)
        self.content = content

    def render(self, content: typing.Any) -> bytes:
        if isinstance(content, dict):
            if "request_id" not in content:
                extra = get_extra()
                content["request_id"] = extra.get("request_id")
        return super().render(content)


class LoggingConfig:
    def __init__(self, log_request, log_request_body, log_response, log_response_body,
                 log_error):
        self.log_request = env_get_bool("LOG_REQUEST", log_request)
        self.log_request_body = env_get_bool("LOG_REQUEST_BODY", log_request_body)

        self.log_response = env_get_bool("LOG_RESPONSE", log_response)
        self.log_response_body = env_get_bool("LOG_RESPONSE", log_response_body)
        self.log_error = env_get_bool("LOG_WHEN_ERROR", log_error)

    @classmethod
    def all(cls):
        return cls(True, True, True, True, True)

    @classmethod
    def nothing(cls):
        return cls(False, False, False, False, True)

    @classmethod
    def without_body(cls):
        return cls(True, False, True, False, True)

    @classmethod
    def response_only(cls):
        return cls(False, False, True, False, True)


class RequestLogInfo:
    FIELDS = ("ip", "who", "method", "path", "query_str", "request_type",
              "duration", "status_code")
    PRETTY_REPR = None

    def __init__(self, request: Request):
        self._request = request
        self._scope = request.scope
        self.status_code = ""
        self.duration = "="
        self.request_type = ""
        self.request_body = ""
        self.response_body_text = "-"
        self.response_body_data = "-"
        self.success = True

    def set_response(self, response: typing.Union[str, Response], status_code=None):
        self.status_code = status_code if status_code else response.status_code
        self.success = 200 <= self.status_code < 300
        if isinstance(response, str):
            self.response_body_data = self.response_body_text = response
            return

        if isinstance(response, JSONResponseRequestId):
            size = len(response.body)
            if size > self.PRETTY_REPR.maxstring * 10:
                self.response_body_data = self.response_body_text = self.PRETTY_REPR.repr(response.content)
            else:
                self.response_body_text = response.body.decode("utf-8")
                self.response_body_data = response.content

            return

        return f"<{type(response)}>"

    def get_response_template(self, config: LoggingConfig):
        template = "RSPN: {data[ip]}|{data[who]}"
        if not config.log_request:
            template += "|{data[method]}|{data[path]}|{data[query_str]}"
        template += "|{data[duration]}ms|{data[status_code]}"
        return template

    @property
    def path(self):
        return self._scope["path"]

    @property
    def method(self):
        return self._scope["method"]

    @functools.cached_property
    def query_str(self):
        query_str = self._scope["query_string"]
        query_str = urllib.parse.unquote(query_str.decode("utf-8"))
        return query_str

    @functools.cached_property
    def ip(self):
        return get_request_client_ip(self._request.headers) or self._scope.get("client", ("", ""))[0]

    @functools.cached_property
    def extra(self):
        return get_extra()

    @functools.cached_property
    def who(self):
        return self.extra.get("who", "<unknown>")

    def get_data(self):
        return {field: getattr(self, field) for field in self.FIELDS}

    def log_response(self, config):
        if config.log_error and not self.success:
            template = self.get_response_template(config)
            logbook.warning(template, data=self.get_data())
            logbook.warning("RSBD: {response_body_text}",
                            response_body_text=self.response_body_text,
                            extra={"response_body_data": self.response_body_data})
        elif config.log_response:
            template = self.get_response_template(config)
            logbook.info(template, data=self.get_data())
            if config.log_response_body:
                logbook.info("RSBD: {response_body_text}",
                             response_body_text=self.response_body_text,
                             extra={"response_body_data": self.response_body_data})

    async def extract_request_body(self):
        content_type_header = self._request.headers.get("Content-Type")
        content_type, options = parse_options_header(content_type_header)
        if content_type in (b"multipart/form-data", b"application/x-www-form-urlencoded"):
            form = await self._request.form()
            self.request_type = "f"
            self.request_body = ";".join(f"{name}:{value}" for name, value in form.items())
            return

        if content_type == b"application/json":
            self.request_type = "j"
            self.request_body = (await self._request.body()).decode("utf-8", "replace")
            return

        self.request_body = (await self._request.body()).replace(b"\n", b"").decode("utf-8", "replace")
        self.request_type = "b"


class LoggingRoute(APIRoute):
    API_EXCEPTION = None
    VALIDATION_ERROR = None
    RequestLogInfoClass = RequestLogInfo
    config: LoggingConfig = LoggingConfig.without_body()

    def get_route_handler(self) -> typing.Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            started_at = time.time()
            request_log = self.RequestLogInfoClass(request)

            if self.config.log_request:
                logbook.info("RQST: {method}|{path}|{query_str}",
                             method=request_log.method, path=request_log.path,
                             query_str=request_log.query_str)
            if self.config.log_request_body:
                await request_log.extract_request_body()
                if request_log.request_body:
                    logbook.info("RQBD: ({request_type}): {request_body}",
                                 request_type=request_log.request_type, request_body=request_log.request_body)
            try:
                response = await original_route_handler(request)
                request_log.set_response(response)
            except self.API_EXCEPTION as e:
                response = await e.get_json_response()
                request_log.set_response(response)
            except RequestValidationError as e:
                response = self.VALIDATION_ERROR(description=e.errors())
                response = await response.get_json_response()
                request_log.set_response(response, 422)
                return response
            except Exception as e:
                logbook.warning("Failed process request:", exc_info=True)
                request_log.set_response("<FAILED>", 500)
                raise
            finally:
                request_log.duration = int((time.time() - started_at) * 1000)
                request_log.log_response(self.config)

            return response

        return custom_route_handler
