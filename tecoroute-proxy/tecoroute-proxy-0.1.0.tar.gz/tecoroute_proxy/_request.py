import binascii
from asyncio import sleep
from base64 import b64decode, b64encode
from hashlib import sha1
from http.cookies import Morsel, SimpleCookie
from json import JSONDecodeError, dumps, loads
from logging import DEBUG, WARNING, getLogger
from random import choices
from string import ascii_lowercase, digits
from typing import Optional
from urllib.parse import urlencode
from xml.etree import ElementTree
from zlib import compress, decompress
from zlib import error as zlib_error

from aiohttp import (
    ClientConnectionError,
    ClientPayloadError,
    ClientResponse,
    ClientResponseError,
    ClientSession,
)
from aiohttp.web import HTTPServiceUnavailable, HTTPUnauthorized, Request, Response
from yarl import URL

AGENT_NAME = "tecoroute-proxy/1.0 (+https://github.com/czetech/tecoroute-proxy)"
ORIGIN = "https://route.tecomat.com"


class ProxyRequest:
    """TODO."""

    COOKIE_SESSION = __name__.split(".")[0]
    LOGIN_PATH = "/TR_LOGIN.XML"

    def __init__(self, request: Request, origin: str = ORIGIN):
        """TODO."""
        self._request = request
        self._origin = URL(origin).origin()
        self._fetch_no = 0
        logs = [(DEBUG, "Created")]

        # Create HTTP client with headers
        client_headers = request.headers.copy()
        for header_key in ("Cookie", "Content-Length"):
            client_headers.pop(header_key, None)
        client_headers["User-Agent"] = AGENT_NAME
        self._client = ClientSession(headers=client_headers)

        # Process request session
        # The value of `request_cookie` is a cookie from the user's browser that stores
        # the session between the user and the proxy server.
        # The value of `self._session['cookies']` are cookies that store the session
        # between the proxy server and TecoRoute.
        # The value of `client_cookies` are cookies passed to TecoRoute.
        self._session = {}
        try:
            request_cookie = self._request.cookies[ProxyRequest.COOKIE_SESSION]
            session = loads(decompress(b64decode(request_cookie)))
            assert isinstance(session, dict)
            assert "id" in session
            self._session.update(session)
            try:
                client_cookies = SimpleCookie()
                cookies = self._session["cookies"]
                for cookie in cookies:
                    client_cookies.load(cookie)
                self._client.cookie_jar.update_cookies(client_cookies)
            except KeyError:
                logs.append((WARNING, "Missing session cookies"))
            except TypeError:
                logs.append((WARNING, f"Invalid session cookies ({cookies})"))
            else:
                logs.append((DEBUG, "Session loaded"))
        except KeyError:
            logs.append((DEBUG, "Empty cookie"))
        except (binascii.Error, zlib_error, JSONDecodeError):
            logs.append((WARNING, f"Invalid cookie ({request_cookie})"))
        except AssertionError:
            logs.append((WARNING, f"Invalid session ({self._session})"))

        alphabet = ascii_lowercase + digits
        if not self._session:
            session_id = "".join(choices(alphabet, k=8))
            self._session["id"] = session_id
            logs.append((DEBUG, "New session initialized"))
        else:
            session_id = self._session["id"]
        request_id = "".join(choices(alphabet, k=8))
        self._id = f"{session_id}-{request_id}"

        self._logger = getLogger(f"{__name__}.{self._id}")
        for log in logs:
            self._logger.log(*log)

    async def __aenter__(self):
        """TODO."""
        return self

    async def __aexit__(self, _, __, ___):
        """TODO."""
        await self.close()

    @property
    def _route(self) -> Optional[str]:
        """Value of RoutePLC from cookies, which is the TecoRoute session identifier."""
        morsel = next(
            (morsel for morsel in self._client.cookie_jar if morsel.key == "RoutePLC"),
            Morsel(),
        )
        return morsel.value

    async def _fetch(
        self, method: str = "GET", path: str = "/", data: Optional[bytes] = None
    ) -> ClientResponse:
        """Perform a request to TecoRoute."""
        path = URL(path)
        await sleep(max(self._fetch_no - 2, 0))
        last = True if self._fetch_no == 5 else False
        self._logger.debug(
            f"TecoRoute request ({method} {path}) fetch {self._fetch_no}"
        )
        self._fetch_no += 1
        try:
            client_response = await self._client.request(
                method, self._origin.join(URL(path)), data=data, allow_redirects=False
            )
            self._logger.debug(f"TecoRoute response ({client_response.status})")
            if (
                client_response.status == 302
                and client_response.headers.get("Location") == ProxyRequest.LOGIN_PATH
            ):
                self._logger.debug("TecoRoute response redirected to login")
                if last:
                    raise RecursionError("can't create a RoutePLC session")
                return await self._login()
            else:
                return client_response
        except (ClientConnectionError, ClientPayloadError, ClientResponseError) as e:
            self._logger.warning(f"TecoRoute request failed ({e})")
            if last:
                raise RecursionError("TecoRoute can't be reached") from None
        return await self._fetch(method, path, data)

    async def _login(self) -> ClientResponse:
        """Login with saved credentials."""
        self._logger.debug(
            "RoutePLC " + (f"({self._route})" if self._route else "empty")
        )
        credentials = self._session["credentials"]
        secret = sha1(
            ((self._route or "") + credentials["password"]).encode()
        ).hexdigest()
        body = urlencode(
            {"USER": credentials["username"], "PASS": secret, "PLC": credentials["plc"]}
        )
        client_response = await self._fetch("POST", ProxyRequest.LOGIN_PATH, body)
        if (
            client_response.status == 200
            and client_response.method == "POST"
            and client_response.url == self._origin.join(URL(ProxyRequest.LOGIN_PATH))
        ):
            try:
                et = ElementTree.fromstring(await client_response.text())
                acer = et.find("ACER").attrib["VALUE"]
            except (ElementTree.ParseError, AttributeError, KeyError):
                self._logger.warning("Unknown TecoRoute login response")
            else:
                raise RecursionError(f"TecoRoute login failed [{acer}]")
        return client_response

    def _sync_cookies(self, response: Response) -> None:
        """Synchronize client cookies with session cookies and set response cookie."""
        self._session["cookies"] = []
        for morsel in self._client.cookie_jar:
            self._session["cookies"].append(morsel.output(header="").lstrip())
            # Convert the morsel object to the set_cookie arguments
            attrs = {
                k.replace("-", "_"): v or None
                for k, v in morsel.items()
                if k != "comment"
            }
            if attrs["domain"] == self._origin.host:
                attrs["domain"] = ""
            response.set_cookie(morsel.key, morsel.value, **attrs)
        cookie = b64encode(compress(dumps(self._session).encode())).decode()
        response.set_cookie(ProxyRequest.COOKIE_SESSION, cookie)

    async def _prepare_response(self, client_response) -> Response:
        """Create a server response from the client response."""
        headers = client_response.headers.copy()
        headers.pop("Set-Cookie", None)
        response = Response(
            body=await client_response.read(),
            status=client_response.status,
            headers=headers,
        )
        self._sync_cookies(response)
        return response

    def _response_unavailable(self, message: str) -> Response:
        if self._logger.isEnabledFor(10):
            id_ = self._logger.name.split(".")[-1]
            debug_info = f"\n\nLog ID: {id_}"
        response = HTTPServiceUnavailable(
            text=(
                "Sorry, service temporary unavailable, please try again later "
                f"({message}).{debug_info}"
            )
        )
        self._sync_cookies(response)
        return response

    async def login(self, username: str, password: str, plc: str) -> Response:
        """Clear session cookies, save credentials and login."""
        self._logger.debug("Login")
        self._client.cookie_jar.clear()
        credentials = {k: v for k, v in locals().items() if k != "self"}
        self._session["credentials"] = credentials
        try:
            return await self._prepare_response(await self._login())
        except RecursionError as e:
            return self._response_unavailable(e)

    async def response(self) -> Response:
        """TODO."""
        if not self._session.get("credentials"):
            response = HTTPUnauthorized(text="Unauthorized")
            self._sync_cookies(response)
            return response
        try:
            client_response = await self._fetch(
                self._request.method, self._request.rel_url, await self._request.read()
            )
            return await self._prepare_response(client_response)
        except RecursionError as e:
            return self._response_unavailable(e)

    async def close(self):
        """TODO."""
        await self._client.close()
