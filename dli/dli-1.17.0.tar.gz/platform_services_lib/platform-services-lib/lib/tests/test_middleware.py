import base64
import datetime
import json
from typing import Optional
from unittest import mock
from unittest.mock import MagicMock, call
import jwt
import pytest
import requests
from flask import Response, request, Blueprint

from ..authentication.middleware import HEADER_MODIFIER, RESPONSE_MODIFIER, ServiceMiddleware
from ..authentication import auth
from ..providers.oidc_provider import public
from ..tests.common import disconnected_client, mock_middleware_server
_ = disconnected_client  # stop import being marked as unused (fixture is used everywhere below)


class TestMiddleware:

    def test_wsgi_middleware_calls_expected_route(self, disconnected_client):
        jw = jwt.encode(payload={"some": "payload"}, key="secret", algorithm="HS256")

        response = disconnected_client.get("/", headers={"Authorization": f"Bearer {jw}"})
        assert response.status_code == 200
        assert response.data == b'HELLO, WORLD'

        response2: Response = disconnected_client.get("/direct_test", headers={"Authorization": f"Bearer {jw}"})
        assert response2.status_code == 403
        assert response2.data == b'BE GONE, DRAGON'

    def test_wsgi_middleware_calls_injected_header_modifier(self, disconnected_client):
        # check that once we attach them, they are called

        jw = jwt.encode(payload={"some": "payload"}, key="secret", algorithm="HS256")
        header_modifier = MagicMock()
        header_modifier.side_effect = lambda jwt, env: env
        disconnected_client.application.injector.binder.bind(
            HEADER_MODIFIER,
            to=lambda: header_modifier,
            scope=request,
        )
        disconnected_client.get("/", headers={"Authorization": f"Bearer {jw}", "Another-Header": "findme"})
        header_modifier.assert_called()
        # argument list should be position[0] = jwt, position[1] = original headers (+ http/wsgi)
        header_modifier.assert_has_calls([
           call(jw, mock.ANY)
        ])
        # lets inspect those headers, make sure we have the one we passed
        recovered_headers_from_call_argument = header_modifier.call_args_list[0].args[1]
        assert "HTTP_ANOTHER_HEADER" in recovered_headers_from_call_argument
        # and that we popped the ones we didnt want already in middleware
        assert "HTTP_AUTHORIZATION" not in recovered_headers_from_call_argument
        assert "HTTP_HOST" not in recovered_headers_from_call_argument

    def test_wsgi_middleware_calls_injected_response_modifier(self, disconnected_client):
        # check that once we attach them, they are called

        jw = jwt.encode(payload={"some": "payload"}, key="secret", algorithm="HS256")
        ground_zero = disconnected_client.get("/", headers={"Authorization": f"Bearer {jw}"})

        response_modifier = MagicMock()
        response_modifier.side_effect = lambda response: ("goodbye world", 403, {})
        disconnected_client.application.injector.binder.bind(
            RESPONSE_MODIFIER,
            to=lambda: response_modifier,
        )
        result = disconnected_client.get("/", headers={"Authorization": f"Bearer {jw}"})

        class ResponseAny():
            def __eq__(self, other):
                return type(other) == requests.models.Response

        response_modifier.assert_called()
        response_modifier.assert_has_calls([
            call(ResponseAny())
        ])

        # check our responsemodifier has overwritten the response vis-a-vis calling without
        assert result.data == b"goodbye world"
        assert result.status_code == 403
        assert ground_zero.status_code != result.status_code

    def test_wsgi_middleware_injectors_called_before_and_after_route(self):
        # timing - we can check that within the route, the headers have been added/changed prior to route
        jw = jwt.encode(payload={"some": "payload"}, key="secret", algorithm="HS256")
        header_mod_called = None
        view_called = None
        response_mod_called = None

        def timing_header(jwt, env):
            nonlocal header_mod_called
            header_mod_called = datetime.datetime.now()
            return env

        def timing_response(response):
            nonlocal response_mod_called
            # assert we've not changed the response yet
            response_mod_called = datetime.datetime.now()
            return "goodbye world", 403, {}

        def timing_app():
            views = Blueprint('middleware', __name__)
            HTTP_METHODS = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH']

            @views.route(
                '/',
                methods=HTTP_METHODS
            )
            def test_route(optional_path: Optional[str] = None):
                nonlocal view_called
                view_called = datetime.datetime.now()

                resp = MagicMock()
                resp.status_code = 200
                resp.headers = {}
                resp.content = "HELLO, WORLD"
                return resp.content, resp.status_code, resp.headers.items()

            timing_app = mock_middleware_server(views)
            with timing_app.test_client() as client:
                return client

        disconnected_client = timing_app()

        header_modifier = MagicMock()
        header_modifier.side_effect = timing_header
        disconnected_client.application.injector.binder.bind(
            HEADER_MODIFIER,
            to=lambda: header_modifier,
            scope=request,
        )
        response_modifier = MagicMock()
        response_modifier.side_effect = timing_response
        disconnected_client.application.injector.binder.bind(
            RESPONSE_MODIFIER,
            to=lambda: response_modifier,
        )

        disconnected_client.get("/", headers={"Authorization": f"Bearer {jw}"})
        assert header_mod_called < view_called < response_mod_called

    def test_wsgi_modifies_headers_correctly_before_route(self, disconnected_client):
        # correctness - that the headers required are changed

        # here we will devise any incoming auth header should be intercepted and resolved by the time
        # we are in the view (be already transformed to custom auth header format)

        # example - our real endpoint only takes Authorisation: Bearer <TOKEN>, but our middleware we enter User:Pass
        #   we want to transform the Authorisation header into that form by exchanging the User:Pass -> Token prior
        #   to it arriving in the route which sends it onto the endpoint

        jw = jwt.encode(payload={"some": "payload"}, key="secret", algorithm="HS256")
        intercepted_headers = None

        # underscores are flipped to dashes in the wsgi container, HTTP_ prefix is dropped.
        # so additional headers may not use "_"
        # i.e. HTTP_X_SOURCE = X-Source
        additional_headers = {
            "X-Additional-Header1": "tag",
            "X-Source": "middleware",
            "X-Source-User": "<JWT>",
            "Cache-Control": "no-cache",
            "Connection": 'keep-alive',
            "Content-Type": "application/json"
        }

        def mod_header(jwt, env):
            new_headers = env.copy()

            # some kind of exchange has already taken place to get us a JWT from our creds in the params
            # so we place that into the bearer

            dd = {"HTTP_AUTHORIZATION": f"Bearer {jwt}"}

            # must be prefixed HTTP_ else won't end up in the middleware headers provided to the route
            # this way we also preserve the dash "-" which would otherwise be converted to underscore "_"
            # use 'HACK' of : dict([x for x in request.headers]) to read these back out without werkzeug throwing a fit
            for k, v in additional_headers.items():
                if v == "<JWT>":
                    dd["HTTP_"+k] = jwt
                else:
                    dd["HTTP_" + k] = v

            new_headers.update(dd)

            return new_headers

        def inspect_header_app():
            views = Blueprint('middleware', __name__)
            HTTP_METHODS = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH']

            @views.route(
                '/',
                methods=HTTP_METHODS
            )
            def test_route(optional_path: Optional[str] = None):

                # inspect the headers here to check they are already transformed as we would need to
                # make a request from here to an EP.
                nonlocal intercepted_headers
                intercepted_headers = request.headers

                def session():
                    return requests.Session()

                resp = MagicMock()
                resp.status_code = 200
                resp.headers = {}
                resp.content = "HELLO, WORLD"

                session()

                return resp.content, resp.status_code, resp.headers.items()

            inspect_app = mock_middleware_server(views)
            with inspect_app.test_client() as client:
                return client

        # basic auth is going to go down this exchange to get the JWT passed to our header modifier func
        auth._sam_app_flow = MagicMock()
        auth._sam_app_flow.return_value = jw

        # pat auth is going to go down this exchange to get the JWT passed to our header modifier func
        auth._sam_pat_flow = MagicMock()
        auth._sam_pat_flow.return_value = jw

        # jwt auth is going to return the JWT (the Identity function) so requires no mock
        _ = None

        disconnected_client = inspect_header_app()
        disconnected_client.application.injector.binder.bind(
            HEADER_MODIFIER,
            to=lambda: mod_header,
            scope=request,
        )

        # the LDAP/Presto case for PAT or APP cases
        user_pass = base64.urlsafe_b64encode(b"<app_user>:<app_pasw>").decode("ascii")
        disconnected_client.get("/", headers={"Authorization": f"Basic {user_pass}"})
        assert intercepted_headers["Authorization"] == f"Bearer {jw}"

        # the SDK case for Presto, passing JWT, ends up as the Identity function
        disconnected_client.get("/", headers={"Authorization": f"Bearer {jw}"})
        assert intercepted_headers["Authorization"] == f"Bearer {jw}"

        # the PAT or APP case, passing delimited user/pass secrets in the signature via Spark/Boto/tools (S3Proxy)
        sig = ("Credential=<app_user>\\<app_pasw>/<date>/<region>/<aws_service>/aws4_request, "
               "SignedHeaders=amz-sdk-invocation-id;amz-sdk-retry;content-type;host;user-agent;x-amz-content-sha256;x-amz-date, "
               "Signature=<calc_signature>")
        disconnected_client.get("/", headers={"Authorization": f"AWS4-HMAC-SHA256 {sig}"})
        assert intercepted_headers["Authorization"] == f"Bearer {jw}"

        # the SDK case for S3Proxy, passing JWT in the signature via boto (S3Proxy)
        sig2 = (f"Credential={jw}/<date>/<region>/<aws_service>/aws4_request, "
               "SignedHeaders=amz-sdk-invocation-id;amz-sdk-retry;content-type;host;user-agent;x-amz-content-sha256;x-amz-date, "
               "Signature=<calc_signature>")
        disconnected_client.get("/", headers={"Authorization": f"AWS4-HMAC-SHA256 {sig2}"})
        assert intercepted_headers["Authorization"] == f"Bearer {jw}"

        # we also add some additional headers, that we wanted to pass along to the service for each request.
        # lets check those were added in mod_header (again, recall they are not going to be prefixed HTTP_ inside
        # of the wsgi container), i.e. "HTTP_something" in fn: mod_header == "something" in flask view

        dict_of_modded_headers = dict([x for x in intercepted_headers])
        for k, v in additional_headers.items():
            assert k in dict_of_modded_headers
            assert dict_of_modded_headers[k] == (v if not v == "<JWT>" else jw)

    @pytest.mark.xfail
    def test_all_headers_data_sent_to_proxied_service(self, disconnected_client):
        # TBC - there isnt really a test for this, since its the app's responsibility in the view to decide
        # this is just to notate how to use those pesky headers that we hacked

        '''
            headers = dict([x for x in request.headers])  # headers back to dict to allow header[X] use in view
            resp = getattr(requests, request.method.lower())(upstream_service, headers=headers, data=request.data)
        '''

    def test_wsgi_modifies_response_correctly_after_route(self, disconnected_client):
        # correctness - that the content/headers are modified how we want

        # here we will devise any outgoing response should be intercepted and
        # transformed before sending to client. Lets imagine our service gives a json response with
        # `follow` urls in the json for the client to make the consequent request.

        # We need to modify those `follow` urls to redirect the consequent request via the middleware rather than
        # directly back towards the service (which may not be visible to them, nor permit their auth).

        # The client should then receive this modified response instead.
        jw = jwt.encode(payload={"some": "payload"}, key="secret", algorithm="HS256")

        def mod_response(response):
            content = response.content
            a = json.loads(content)
            a["nextUri"] = a["nextUri"].replace("my-service", "my-middleware")
            a["inspectUri"] = a["inspectUri"].replace("my-service", "my-middleware")
            return json.dumps(a), response.status_code, response.headers.items()

        def response_from_app():
            views = Blueprint('middleware', __name__)
            HTTP_METHODS = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH']

            @views.route(
                '/',
                methods=HTTP_METHODS
            )
            def test_route(optional_path: Optional[str] = None):

                resp = MagicMock()
                resp.status_code = 200
                resp.headers = {}

                json_body = {
                    "nextUri" : "http://my-service/1234",
                    "inspectUri": "http://my-service/inspect/1234?slug=vi54nvg65"
                }

                resp.content = json.dumps(json_body)

                return resp.content, resp.status_code, resp.headers.items()

            mock_response_app = mock_middleware_server(views)
            with mock_response_app.test_client() as client:
                return client

        # skip auth (patch before app)
        ServiceMiddleware._resolve = MagicMock()
        ServiceMiddleware._resolve.return_value = jw

        disconnected_client = response_from_app()
        disconnected_client.application.injector.binder.bind(
            RESPONSE_MODIFIER,
            to=lambda: mod_response,
            scope=request,
        )

        resp = disconnected_client.get("/", headers={"Authorization": f"Basic anything"})
        _json = json.loads(resp.data)
        assert _json["nextUri"] == "http://my-middleware/1234"
        assert _json["inspectUri"] == "http://my-middleware/inspect/1234?slug=vi54nvg65"

    @pytest.mark.xfail # TODO
    def test_wsgi_respond_from_bad_reply_from_proxied_service(self, disconnected_client):
        # correctness - that say a 403/500 from the service is sent back through correctly
        pass

    @pytest.mark.xfail # TODO
    def test_public_route_allowed(self, disconnected_client):
        # correctness - any public routes will be trapped behind auth of the middleware, unless handled
        def public_app():
            views = Blueprint('middleware', __name__)
            HTTP_METHODS = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH']

            @views.route(
                '/',
                methods=HTTP_METHODS
            )
            @public
            def test_route(optional_path: Optional[str] = None):

                resp = MagicMock()
                resp.status_code = 200
                resp.headers = {}

                json_body = {
                    "nextUri" : "http://my-service/1234",
                    "inspectUri": "http://my-service/inspect/1234?slug=vi54nvg65"
                }

                resp.content = json.dumps(json_body)

                return resp.content, resp.status_code, resp.headers.items()

            mock_response_app = mock_middleware_server(views)
            with mock_response_app.test_client() as client:
                return client

        disconnected_client = public_app()
        resp = disconnected_client.get("/")
        assert resp.status_code == 200