import logging
import os
import uuid
import jwt
import requests
from urllib.parse import urljoin
from typing import Optional

from ..context.environments import _Environment
from ..context.urls import sam_urls, sam_api_urls, identity_urls
from ..providers.oidc_provider import JWTEncoded
from ..services.view_exceptions import Unauthorized

logger = logging.getLogger(__name__)


def _sam_app_flow(environment: _Environment, user_id: str, user_secret: str, origin=None) -> Optional[str]:

    if user_id is None:
        logger.warning("SAM App User ID is not set")

    if user_secret is None:
        logger.warning("SAM App User Secret is not set")

    if environment.sam is None:
        logger.warning("SAM Endpoint is not set")

    if environment.catalogue is None:
        logger.warning("Catalogue Endpoint is not set")

    catalogue_url = urljoin(environment.catalogue, identity_urls.identity_token)
    sam_url = urljoin(environment.sam, sam_urls.sam_token)

    # exchange the client credentials with SAM for an access token
    sam_payload = {
        'client_id': user_id,
        'client_secret': user_secret,
        'grant_type': 'client_credentials'
    }

    logger.info("Exchanging details with SAM")
    resp = external_session().post(sam_url, data=sam_payload)
    if resp.status_code != 200:
        raise Unauthorized('Could not retrieve jwt access token with client credentials')

    # exchange the acquired token with catalogue
    sam_token = resp.json()['access_token']
    dl_payload = {
        'client_id': user_id,
        'subject_token': sam_token
    }

    if origin:
        # this allows influencing JWT lifetime (1hr -> 8hr)
        dl_payload["origin"] = origin

    logger.info("Exchanging SAM token with Catalogue")
    resp = external_session().post(catalogue_url, data=dl_payload)
    if resp.status_code != 200:
        raise Unauthorized('Could not retrieve jwt access token with client credentials')

    return resp.json()['access_token']


def external_session():
    return requests.Session()


def _sam_pat_flow(environment: _Environment, user_id: str, user_secret: str) -> Optional[str]:

    if user_id is None:
        logger.warning("SAM PAT User ID is not set")

    if user_secret is None:
        logger.warning("SAM PAT User Secret is not set")

    if environment.sam is None:
        logger.warning("SAM Endpoint is not set")

    if environment.catalogue is None:
        logger.warning("Catalogue Endpoint is not set")

    catalogue_url = urljoin(environment.catalogue, identity_urls.identity_token)  # TODO would this be a new endpoint?
    sam_api_url = urljoin(environment.sam_api, sam_api_urls.sam_pat_token)

    sam_payload = {
        'username': user_id,
        'password': user_secret,
        'grant_type': 'password',

        # n.b. it makes no sense for us to have these per application, may as well be private once on Catalogue
        'client_id': os.environ["SAM_CLIENT_ID_FOR_PAT_EXCHANGE"],  # this must be for the one registered under 'Services' in PAT
        'client_secret': os.environ["SAM_CLIENT_SECRET_FOR_PAT_EXCHANGE"],  # this must be  for the one registered under 'Services' in PAT
    }
    sam_auth_header = {"apikey": os.environ["SAM_CLIENT_SECRET_FOR_PAT_EXCHANGE"]}

    logger.info("Exchanging details with SAM")
    resp = external_session().post(sam_api_url, data=sam_payload, headers=sam_auth_header)
    if resp.status_code != 200:
        raise Unauthorized('Could not retrieve jwt access token with client credentials')

    # exchange the acquired token with catalogue
    sam_token = resp.json()['access_token']
    dl_payload = {
        'client_id': "???", # TODO how would catalogue know its registered?
        'subject_token': sam_token
    }

    logger.info("Exchanging SAM token with Catalogue")
    resp = external_session().post(catalogue_url, data=dl_payload)
    if resp.status_code != 200:
        raise Unauthorized('Could not retrieve jwt access token with client credentials')

    jwt = resp.json()['access_token']
    return jwt


def decode_token(key):

    __pyjwt_algorithms = [
        # `HS256` is the value returned by the JWT from prod, but pyjwt seems
        # to complain about the signature.
        'HS256',
        'HS512', 'ES256', 'ES384', 'ES512', 'RS256', 'RS384',
        'RS512', 'PS256', 'PS384', 'PS512',
    ]

    return jwt.decode(
        jwt=key,
        algorithms=__pyjwt_algorithms,
        options={
            "verify_signature": False,
            "verify_aud": False,
            "verify_exp": False
        }
    )


def _pre_request_get_token(environment: _Environment, user_id: str, user_secret: str, hint: Optional[str]) -> JWTEncoded:

    _PAT = "PAT"
    _JWT = "JWT"
    _APP = "APP"

    if user_id is None or user_secret is None:
        raise Unauthorized()

    if not hint or hint == _PAT:
        # we think its a PAT or want to check it matches a UUID (which indicates it is)
        try:
            # is this a uuid as only PATs are UUIDs? - if it is it can be parse to UUID type
            uuid.UUID(user_id)
            return JWTEncoded(_sam_pat_flow(environment, user_id, user_secret))
        except (ValueError, TypeError) as e:
            logging.debug(f"{e} - doesn't look like a PAT {user_id}")
            if hint == _PAT:
                raise e

    if not hint or hint == _JWT:
        # we think its already a JWT or want to check its valid
        try:
            # is this a JWT? - if it is it can be decoded
            decode_token(user_id)
            return JWTEncoded(user_id)  # the JWT
        except jwt.DecodeError as e:
            logging.debug(f"{e} - doesn't look like a JWT {user_id}")
            if hint == _JWT:
                raise e

    if not hint or hint == _APP:
        # this seems to be an APP user, since its not a UUID or JWT
        try:
            return JWTEncoded(_sam_app_flow(environment, user_id, user_secret))
        except Exception as e:
            logging.debug(f"{e} - doesn't look like an APP {user_id}")
            if hint == _APP:
                raise e

    raise Unauthorized()
