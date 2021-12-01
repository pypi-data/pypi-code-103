import base64
import os
import uuid
from unittest.mock import MagicMock, patch
import pytest
import jwt

from requests import Response

from ..context.environments import _Environment
from ..authentication.middleware import ServiceMiddleware
from ..authentication.auth import _sam_app_flow, _sam_pat_flow, _pre_request_get_token, decode_token, Unauthorized
from ..authentication import auth

from lib.tests.common import disconnected_client
_ = disconnected_client  # stop import being marked as unused (fixture is used everywhere below)


class TestAuth:

    def test_no_auth(self, disconnected_client):
        a = disconnected_client.get("/test")
        assert a.status_code == 401
        assert a.data.decode() == 'No Authorization header provided'

    def test_unrecognized_auth(self, disconnected_client):
        with pytest.raises(Unauthorized):
            disconnected_client.get("/test", headers={"Authorization": "Random XXXXX"})

    def test_unrecognized_jwt_decode(self, disconnected_client):
        with pytest.raises(jwt.DecodeError):
            disconnected_client.get("/test", headers={"Authorization": "Bearer JWT"})

    def test_recognized_jwt_hits_backend(self, disconnected_client):
        jw = jwt.encode(payload={"some": "payload"}, key="secret", algorithm="HS256")
        resp = disconnected_client.get("/test", headers={"Authorization": f"Bearer {jw}"})
        assert resp.status_code == 200
        assert resp.data.decode() == "HELLO, WORLD"

    def test_resolver_is_called(self, disconnected_client):
        with patch.object(ServiceMiddleware, '_resolve', return_value=MagicMock()) as mock_method:
            jw = jwt.encode(payload={"some": "payload"}, key="secret", algorithm="HS256")
            disconnected_client.get("/test", headers={"Authorization": f"Bearer {jw}"})
            mock_method.assert_called()

    def test_resolver_calls_correct_method_for_auth_type(self, disconnected_client):

        # make all the caller methods magicmocks
        jw = jwt.encode(payload={"<jwt_user>": "payload"}, key="secret", algorithm="HS256")

        with patch.object(ServiceMiddleware, '_type_bearer', return_value=(jw, "NOP", "JWT")) as _bearer,\
             patch.object(ServiceMiddleware, '_type_ldap', return_value=("app_user", "app_pasw", None)) as _ldap,\
             patch.object(ServiceMiddleware, '_type_s3_rest', return_value=("app_user", "app_pass", None)) as _rest,\
             patch.object(ServiceMiddleware, '_type_v4_signature', return_value=("app_user", "app_pass", None)) as _sig,\
             patch.object(ServiceMiddleware, '_credentials_to_token', return_value=MagicMock()
        ):

            disconnected_client.get("/test", headers={"Authorization": f"Bearer {jw}"})
            # check only this one was called
            assert _bearer.call_count == 1
            assert _ldap.call_count == 0
            assert _sig.call_count == 0
            assert _rest.call_count == 0
            # check we called it how we expected
            _bearer.assert_called_with("\\", jw)
            _bearer.reset_mock()

            ldap = base64.urlsafe_b64encode(b"<app_user>:<app_pasw>")
            disconnected_client.get("/test", headers={"Authorization": f"Basic {ldap}"})
            # check only this one was called
            assert _bearer.call_count == 0
            assert _ldap.call_count == 1
            assert _sig.call_count == 0
            assert _rest.call_count == 0
            _ldap.assert_called_with("\\", str(ldap))
            _ldap.reset_mock()

            # https://docs.aws.amazon.com/AmazonS3/latest/userguide/RESTAuthentication.html
            rest ="<app_user\\app_pasw>:<signature>"
            disconnected_client.get("/test", headers={"Authorization": f"AWS {rest}"})
            _rest.assert_called_with("\\", rest)

            # https://docs.aws.amazon.com/general/latest/gr/sigv4-signed-request-examples.html
            sig = ("Credential=<app_user\\app_pasw>/<date>/<region>/<aws_service>/aws4_request, "
                "SignedHeaders=amz-sdk-invocation-id;amz-sdk-retry;content-type;host;user-agent;x-amz-content-sha256;x-amz-date, "
                "Signature=<calc_signature>")
            disconnected_client.get("/test", headers={"Authorization": f"AWS4-HMAC-SHA256 {sig}"})
            _sig.assert_called_with("\\", sig)

    def test_split_jwt_credentials(self):
        colon_case_present = ServiceMiddleware._split_to_jwt_or_credentials(auth_credential_delimiter=":", field_aws_access_key_id="user:password")
        assert colon_case_present == ("user", "password", None)

        backslash_case_present = ServiceMiddleware._split_to_jwt_or_credentials(auth_credential_delimiter="\\", field_aws_access_key_id="user\\password")
        assert backslash_case_present == ("user", "password", None)

        JWT = "jwt005"
        divider_missing = ServiceMiddleware._split_to_jwt_or_credentials(auth_credential_delimiter="\\", field_aws_access_key_id=JWT)
        assert divider_missing == (JWT, "NOP", "JWT")

        # we have confirmed the relevant divider cannot be present in: the user+header auth (CC - [A-Za-z0-9], or PAT - [UUID])
        # we have confirmed the relevant divider "\\" is not/cannot be present in the SAM PAT password (thus the choice)
        divider_in_password = ServiceMiddleware._split_to_jwt_or_credentials(auth_credential_delimiter="\\", field_aws_access_key_id="user\\pass\\w\\ord")
        assert divider_in_password == ("user", "pass\\w\\ord", None)

    def test_type_ldap(self):
        ldap = base64.urlsafe_b64encode(b"<app_user>:<app_pasw>")
        creds = ServiceMiddleware._type_ldap("\\", ldap)
        assert creds == ("<app_user>", "<app_pasw>", None)

    def test_type_bearer(self):
        jw = jwt.encode(payload={"some": "payload"}, key="secret", algorithm="HS256")
        creds = ServiceMiddleware._type_bearer("\\", jw)
        assert creds == (jw, "NOP", "JWT")

    def test_type_s3_rest(self):
        rest ="<app_user>\\<app_pasw>:<signature>"
        creds = ServiceMiddleware._type_s3_rest("\\", rest)
        assert creds == ("<app_user>", "<app_pasw>", None)

    def test_type_v4_signature(self):
        sig = ("Credential=<app_user>\\<app_pasw>/<date>/<region>/<aws_service>/aws4_request, "
               "SignedHeaders=amz-sdk-invocation-id;amz-sdk-retry;content-type;host;user-agent;x-amz-content-sha256;x-amz-date, "
               "Signature=<calc_signature>")
        creds = ServiceMiddleware._type_v4_signature("\\", sig)
        assert creds == ("<app_user>", "<app_pasw>", None)

    def test_sam_app_flow(self):
        # we aren't going overboard with testing on this method, since it will move to catalogue
        env = _Environment("https://catalogue-dev.udpmarkit.net")
        auth.external_session = MagicMock()

        sam_response = Response()
        sam_response._content = b'{"access_token": "<JWT>", "id_token": "<JWT2>"}'
        sam_response.headers.update({})
        sam_response.status_code = 200

        catalogue_response = Response()
        catalogue_response._content = b'{"access_token": "<JWT3>"}'
        catalogue_response.headers.update({})
        catalogue_response.status_code = 200

        auth.external_session.return_value.post.side_effect = [
            sam_response, catalogue_response
        ]
        jwt = _sam_app_flow(env, "user", "pasw")
        assert jwt == "<JWT3>"

    def test_sam_pat_flow(self):
        # we aren't going overboard with testing on this method, since it will move to catalogue
        env = _Environment("https://catalogue-dev.udpmarkit.net")

        auth.external_session = MagicMock()

        sam_response = Response()
        sam_response._content = b'{"access_token": "<JWT>", "id_token": "<JWT2>"}'
        sam_response.headers.update({})
        sam_response.status_code = 200

        catalogue_response = Response()
        catalogue_response._content = b'{"access_token": "<JWT3>"}'
        catalogue_response.headers.update({})
        catalogue_response.status_code = 200

        auth.external_session.return_value.post.side_effect = [
            sam_response, catalogue_response
        ]
        os.environ["SAM_CLIENT_ID_FOR_PAT_EXCHANGE"] = "PAT_ID"
        os.environ["SAM_CLIENT_SECRET_FOR_PAT_EXCHANGE"] = "PAT_SECRET"

        jwt = _sam_pat_flow(env, "user", "pasw")
        assert jwt == "<JWT3>"

    def test_decode_token(self):
        good_jwt = jwt.encode(payload={"some": "payload"}, key="secret", algorithm="HS256")
        assert decode_token(good_jwt) == {"some": "payload"}

        bad_jwt = "not_a_jwt"
        with pytest.raises(Exception) as execinfo:
            decode_token(bad_jwt)

    def test_pre_exchange_jwt_flow(self):
        env = _Environment("https://catalogue-dev.udpmarkit.net")

        with patch.object(auth, '_sam_pat_flow', return_value=MagicMock()) as patflow:
            with patch.object(auth, '_sam_app_flow', return_value=MagicMock()) as appflow:
                with patch.object(auth, 'decode_token', return_value=MagicMock()) as decodetoken:
                    # note - this test is precedence ordered, do not change order
                    # (must match same order flow as _pre_request_get_token): PAT->JWT->APP

                    # hinted PAT case, and provided PAT
                    r = _pre_request_get_token(env, str(uuid.uuid4()), "<pass>", "PAT")
                    patflow.assert_called()

                    # hinted PAT case, and not provided PAT
                    with pytest.raises(ValueError) as execinfo:
                        _pre_request_get_token(env, "APP_USER", "<pass>", "PAT")

                    # hinted JWT case and provided JWT
                    jw = jwt.encode(payload={"some": "payload"}, key="secret", algorithm="HS256")
                    _pre_request_get_token(env, str(jw), "<pass>", "JWT")
                    decodetoken.assert_called()

                # hinted JWT case and not provided JWT
                with pytest.raises(jwt.DecodeError) as execinfo:
                    _pre_request_get_token(env, str(uuid.uuid4()), "<pass>", "JWT")

                # hinted APP case, and provided APP
                _pre_request_get_token(env, "APP_USER", "<pass>", "APP")
                appflow.assert_called()

            # hinted APP case, and not provided APP
            # we now need to patch requests post to be a 403, as its actually gonna go to the EP
            resp = MagicMock()
            resp.post.return_value = MagicMock()
            resp.post.return_value.status_code = 403
            with patch.object(auth, 'external_session', return_value=resp) as response:
                with pytest.raises(Unauthorized) as execinfo:
                    _pre_request_get_token(env, str(uuid.uuid4()), "<pass>", "APP")

    def test_pre_exchange_jwt_flow_unhinted(self):
        env = _Environment("https://catalogue-dev.udpmarkit.net")
        auth._sam_pat_flow = MagicMock()
        auth._sam_app_flow = MagicMock()
        auth._decode_token = decode_token
        auth.sam_app_flow = _sam_app_flow
        auth.decode_token = MagicMock()

        # not provided username/pass
        with pytest.raises(Unauthorized) as execinfo:
            _pre_request_get_token(env, None, None, None)

        # unhinted PAT case, and provided PAT
        _pre_request_get_token(env, str(uuid.uuid4()), "<pass>", None)
        auth._sam_pat_flow.assert_called()
        auth._sam_pat_flow.reset_mock()

        # unhinted JWT case, and provided JWT
        jw = jwt.encode(payload={"some": "payload"}, key="secret", algorithm="HS256")
        _pre_request_get_token(env, str(jw), "<pass>", None)
        auth.decode_token.assert_called()
        auth.decode_token.reset_mock()

        # unhinted APP case, and provided APP
        auth.decode_token = auth._decode_token
        _pre_request_get_token(env, "APP_USER", "<pass>", None)
        auth._sam_app_flow.assert_called()
        auth._sam_app_flow.reset_mock()

        # unhinted case, and not valid
        auth._sam_app_flow = auth.sam_app_flow
        with pytest.raises(Unauthorized) as execinfo:
            _pre_request_get_token(env, "<user>", "<pass>", None)