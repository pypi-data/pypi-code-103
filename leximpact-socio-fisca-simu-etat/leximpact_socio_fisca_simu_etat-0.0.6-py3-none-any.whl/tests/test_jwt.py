import time
import unittest

from fastapi.exceptions import HTTPException
from jose import JWTError, jwt

from leximpact_socio_fisca_simu_etat.config import Configuration
from leximpact_socio_fisca_simu_etat_api.security import check_token

config = Configuration()
api_limit = int(config.get("API_MAX_CALL_PER_MINUTE_PER_USER"))
JWT_SECRET_KEY = "secret_for_test"

# {'user':
#   {'sub': 'ae211368-6dec-4286-842c-c788580ab1f8', 'email_verified': True,
#    'roles': ['offline_access', 'default-roles-leximpact', 'uma_authorization'],
#    'name': 'xxx', 'last_name': 'xxx', 'preferred_username': 'xxxx', 'given_name': 'xxx',
#    'locale': 'fr', 'family_name': 'Raviart', 'email': 'xxx@xxxx.com', 'provider': 'leximpact'},
#  'iat': 1631183582, 'exp': 1633775582}


class TestJWT(unittest.TestCase):
    def test_check_token_valid(self):
        claims = {
            "user": {"email": "lex@leximpact"},
            "iat": time.time(),
            "exp": time.time() + 500,
        }
        token = jwt.encode(claims, JWT_SECRET_KEY, algorithm="HS256")
        res = check_token(token, JWT_SECRET_KEY)
        self.assertEqual(res, claims["user"]["email"])

    def test_check_many_calls(self):
        claims = {
            "user": {"email": "test_check_many_calls@leximpact"},
            "iat": int(time.time()),
            "exp": int(time.time()) + 500,
        }
        token = jwt.encode(claims, JWT_SECRET_KEY, algorithm="HS256")
        for _ in range(api_limit):
            res = check_token(token, JWT_SECRET_KEY)
        self.assertEqual(res, claims["user"]["email"])

    def test_check_error_token_without_mail(self):
        claims = {"user": {"toto": "titi"}, "iat": time.time(), "exp": time.time()}
        token = jwt.encode(claims, JWT_SECRET_KEY, algorithm="HS256")
        with self.assertRaises((JWTError, HTTPException)):
            check_token(token, JWT_SECRET_KEY)

    def test_check_error_token_invalid_secret(self):
        claims = {"user": {"email": "lex@leximpact"}}
        token = jwt.encode(claims, "invalidTokenSecret", algorithm="HS256")
        with self.assertRaises((JWTError, HTTPException)):
            check_token(token, JWT_SECRET_KEY)

    def test_check_error_token_malformed(self):
        token = "invalidtoken"
        with self.assertRaises((JWTError, HTTPException)):
            check_token(token, JWT_SECRET_KEY)

    def test_check_error_token_expired(self):
        claims = {
            "user": {"email": "lex@leximpact"},
            "iat": time.time(),
            "exp": time.time() - 500,
        }
        token = jwt.encode(claims, JWT_SECRET_KEY, algorithm="HS256")
        with self.assertRaises((JWTError, HTTPException)):
            check_token(token, JWT_SECRET_KEY)

    def test_check_error_token_in_future(self):
        claims = {
            "user": {"email": "lex@leximpact"},
            "iat": time.time() + 500,
            "exp": time.time() + 1500,
        }
        token = jwt.encode(claims, JWT_SECRET_KEY, algorithm="HS256")
        with self.assertRaises((JWTError, HTTPException)):
            check_token(token, JWT_SECRET_KEY)

    def test_check_error_too_many_calls(self):
        claims = {
            "user": {"email": "test_check_error_too_many_calls@leximpact.dev"},
            "iat": int(time.time()),
            "exp": int(time.time()) + 5000,
        }
        token = jwt.encode(claims, JWT_SECRET_KEY, algorithm="HS256")
        for _ in range(api_limit):
            _ = check_token(token, JWT_SECRET_KEY)
        with self.assertRaises((HTTPException)):
            check_token(token, JWT_SECRET_KEY)
