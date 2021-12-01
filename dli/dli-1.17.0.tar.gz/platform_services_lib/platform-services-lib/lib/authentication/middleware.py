import base64
import logging
import os
from typing import Optional, NewType, Tuple, Dict, Any
from flask import request
from requests.models import CaseInsensitiveDict, Response

from ..authentication.auth import _pre_request_get_token, Unauthorized
from ..context.environments import _Environment
from ..providers.oidc_provider import JWTEncoded

logger = logging.getLogger(__name__)

########################################################################################################################
# The middleware relies on the application to inject a header in order to stay generic.
#
# Examples of how to bind the functions are shown in the 'Identity' (I) functions below, which do nothing.
# Albeit, any field of the original headers could be modified with the extracted JWT before sending to upstream.

# use to set injection of header modifier function
# defined by the type :: str, Dict -> Dict
HEADER_MODIFIER = NewType('HEADER_MODIFIER', str)
RESPONSE_MODIFIER = NewType('REQUEST_MODIFIER', str)


def identity_header_function(jwt: Optional[str], headers: Dict) -> Dict:
    # Add this to your flask app to bind this function, or provide your own
    #
    #     app.injector.binder.bind(
    #         HEADER_MODIFIER,
    #         to=lambda: identity_header_function,
    #         scope=request,
    #     )

    return headers


def identity_response_function(resp: Response) -> Tuple[Any, int, CaseInsensitiveDict]:
    # Add this to your flask app to bind this function, or provide your own
    #
    #     app.injector.binder.bind(
    #         RESPONSE_MODIFIER,
    #         to=lambda: identity_response_function,
    #         scope=request,
    #     )

    return resp.raw, resp.status_code, resp.headers


########################################################################################################################
# A flask middleware to be applied to the flask app - this resolves any possible latency or memory requirement
# caused by running as a separate server on the same pod
#
# This should be used as follows on creation of the flask app as follows:
#
#     app = Flask(__name__)
#     app.register_blueprint([views,...])
#
#     app.injector = Injector()
#     app.wsgi_app = ModifyHeaderMiddleware(app.wsgi_app)
#     app.wsgi_app.injector = app.injector
#

class ServiceMiddleware(object):
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app
        self.env = _Environment(os.environ["CATALOGUE_API_URL"])


    def __call__(self, environ: Dict, start_response):
        # before request to route, add some variables to the environ according to the app
        if not environ.get("HTTP_AUTHORIZATION"):
            start_response('401 Unauthorized', [('Content-Type', 'text/html')])
            return ["No Authorization header provided".encode()]

        jwt = ServiceMiddleware._resolve(self.env, "HTTP_AUTHORIZATION", environ)

        # lets remove this to make clear that we later set it
        environ.pop('HTTP_AUTHORIZATION', None)

        # this will interfere with the request
        environ.pop('HTTP_HOST', None)

        # this will likely set HTTP_AUTHORIZATION and any other headers it wants (prepended HTTP_)
        header_modifier_fn = self.injector.get(HEADER_MODIFIER)

        if header_modifier_fn:
            # application itself is requesting a header modification be run before sending to its routes
            environ = header_modifier_fn(jwt, environ)

        response_status = None
        response_headers = None

        def custom_start_response(status, environ=[]):
            nonlocal response_status
            nonlocal response_headers
            response_headers = environ
            response_status = status
            # after response from route, intercept the response (applicable only on plain out)
            # route_response = start_response(status, environ)
            # return route_response

        # go to the route with pre-adjusted environ, and response callback
        app_iter = self.wsgi_app(environ, custom_start_response)

        try:
            response_modifier = self.injector.get(RESPONSE_MODIFIER)
            if response_modifier:

                # recover the response as we still want to do some adjustment
                response_content_reread = b"".join(app_iter)
                dummy_response = Response()
                dummy_response._content = response_content_reread
                dummy_response.headers.update(response_headers)
                dummy_response.status_code = response_status

                # application itself is requesting a header modification be run before sending to its routes
                content, content_status, content_headers = response_modifier(dummy_response)
                start_response(str(content_status), list(dict(content_headers).items()))
                return [content]
            else:
                # if not modification needed, dont re-read, just return it* (this is an future)
                # based on the fact that you may still be writing/streaming the response in chunk
                # see https://stackoverflow.com/questions/16774952/wsgi-whats-the-purpose-of-start-response-function
                start_response(response_status, environ)
                return app_iter
        except Exception as e:
            start_response(str(e), [('Content-Type', 'text/html')])
            return [f"{str(e)}".encode()]

    @staticmethod
    def _resolve(env, auth_header="Authorization", use_environ=None) -> JWTEncoded:

        # Authorization schemes seen in the Authorization HTTP header
        bearer_prefix = "Bearer"
        ldap_basic_prefix = "Basic"
        aws_v4_signed_prefix = "AWS4-HMAC-SHA256"
        aws_s3_rest_prefix = "AWS"

        # Delimiter character which divides username and password in single field scenarios
        # Non-presence of the delimiter indicates that it can only be a JWT flow
        auth_credential_delimiter = "\\"

        user = None       # extracted username or JWT (if extracted)
        password = None   # extract password or "NOP" (if extracted)
        hint = None       # type of credential        (if can be inferred)

        if use_environ is None and request.authorization is not None:
            # for BI tools - username/password style forms
            # we know for a fact its a Credential: (App user/pass) or (PAT user/pass) or (JWT/nop), but not which
            if not use_environ:
                user = request.authorization.username
                password = request.authorization.password
            else:
                # shouldn't be receiving a middleware request with wsgi environ, this will raise Unauthorized later
                pass

        elif use_environ is not None or request.headers[auth_header] is not None:
            # we know this is either:
            # AMS4-HMAC-SHA256 <JWT>/... <User>:<Password>/.../.../  (v4 signing, used by AWS SDK [Spark/Boto etc])
            # AWS <JWT>/... <User>:<Password>/.../...                (s3 rest, used by AWS S3 over REST to spec. [CURL])
            # Bearer <JWT>                                           (Bearer, used by Datalake [S3-Proxy, Catalogue])
            # Basic <User>:<Password>                                (LDAP/Basic, [Presto])
            #
            # but we're not yet sure which, nor which Credential inhabits them.
            # check the prefix of the header

            # choose whether to look at the wsgi headers or use Flask request headers to get the Auth field
            if use_environ is None:
                auth = request.headers[auth_header]
            else:
                auth = use_environ[auth_header]

            # split the Authorization field into its parts
            space_idx = auth.find(" ")
            if space_idx != -1:
                auth_type_key = auth[0:space_idx].lower()
                auth_type_value = auth[space_idx+1:]
                extract_fn = None

                if auth_type_key == bearer_prefix.lower():
                    extract_fn = ServiceMiddleware._type_bearer
                elif auth_type_key == ldap_basic_prefix.lower():
                    extract_fn = ServiceMiddleware._type_ldap
                elif auth_type_key == aws_s3_rest_prefix.lower():
                    extract_fn = ServiceMiddleware._type_s3_rest
                elif auth_type_key == aws_v4_signed_prefix.lower():
                    extract_fn = ServiceMiddleware._type_v4_signature

                if extract_fn:
                    user, password, hint = extract_fn(auth_credential_delimiter, auth_type_value)
                else:
                    # doesn't look like a recognized auth scheme that we deal with
                    logger.warning(f"We cannot extract credentials for this type of authorization key {auth_type_key}")
            else:
                # doesn't look like an auth scheme
                pass

        if user is None:
            raise Unauthorized()

        return ServiceMiddleware._credentials_to_token(env, user, password, hint)

    @staticmethod
    def _credentials_to_token(env, user, password, hint):
        # we have this static method to make testing super easy to override
        return _pre_request_get_token(env, user, password, hint)

    @staticmethod
    def _split_to_jwt_or_credentials(
            auth_credential_delimiter, field_aws_access_key_id
    ) -> Tuple[str, str, Optional[str]]:
        if auth_credential_delimiter not in field_aws_access_key_id:
            # this MUST be a JWT, since there is no split character
            return field_aws_access_key_id, "NOP", "JWT"
        else:
            # we need to split into the respective values, split by the first we see
            # we still do not know which of the credential types it is however
            user, pasw = field_aws_access_key_id.split(auth_credential_delimiter, 1)
            return user, pasw, None

    @staticmethod
    def _type_ldap(auth_credential_delimiter, auth_type_value) -> Tuple[str, str, Optional[str]]:
        ldap_separator = ":"

        # only presto uses this, we know it is of the form (Basic <User>:<Password>) so we can split it
        # may be any one of the 3 credential types
        # we still do not know which of the credential types it is
        unencoded = base64.urlsafe_b64decode(auth_type_value).decode("ascii")
        user, pasw = unencoded.split(ldap_separator, 1)
        return user, pasw, None

    @staticmethod
    def _type_bearer(auth_credential_delimiter, auth_type_value) -> Tuple[str, str, Optional[str]]:
        # only datalake apps use bearer tokens, thus its a token of the form (Bearer <JWT>)
        # may only be JWT
        return auth_type_value, "NOP", "JWT"

    @staticmethod
    def _type_s3_rest(auth_credential_delimiter, auth_type_value) -> Tuple[str, str, Optional[str]]:
        aws_s3_rest_separator = ":"

        # only S3 REST, may be any one of the 3 credential types
        field_aws_access_key_id, _, _ = auth_type_value.strip().partition(aws_s3_rest_separator)
        return ServiceMiddleware._split_to_jwt_or_credentials(auth_credential_delimiter, field_aws_access_key_id)

    @staticmethod
    def _type_v4_signature(auth_credential_delimiter, auth_type_value) -> Tuple[str, str, Optional[str]]:
        aws_v4_fields_separator = ","
        aws_v4_field_components_separator = "="
        aws_v4_credential_field = "Credential"
        aws_v4_credential_field_values_separator = "/"

        # only AWS V4 Signed use by s3proxy only, may be any one of the 3 credential types
        fields = auth_type_value.split(aws_v4_fields_separator)
        for field in fields:
            field_name, _, field_value = field.strip().partition(aws_v4_field_components_separator)

            if field_name == aws_v4_credential_field:
                field_aws_access_key_id, _, _ = field_value.partition(aws_v4_credential_field_values_separator)
                return ServiceMiddleware._split_to_jwt_or_credentials(auth_credential_delimiter, field_aws_access_key_id)

        # if Credential field is not in there, we need to return None, to hit Unauthorized
        return None, None, None