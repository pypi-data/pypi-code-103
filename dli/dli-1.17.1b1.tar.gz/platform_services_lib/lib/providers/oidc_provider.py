#
# Copyright (C) 2019 IHS Markit.
# All Rights Reserved
#

import logging
import dataclasses
import jwt.exceptions
from functools import wraps
from typing import Tuple, NewType, cast

from flask import Request, current_app
try:
    # these are only present for services, not for the SDK, and we do not wish to impose these in requirements.txt
    from injector import provider
    from flask_injector import request as request_scope
    from ..services.view_exceptions import (
        Unauthorized, Forbidden, UnprocessableEntity
    )

except ModuleNotFoundError:
    # set up an Identity decorator for @inject
    def provider(function):  # type: ignore
        def wrapper(*args, **kwargs):
            return function(*args, *kwargs)
        return wrapper

    def request_scope(function):  # type: ignore
        def wrapper(*args, **kwargs):
            return function(*args, *kwargs)

        return wrapper

    # dont need to patch exception, wont be used by SDK


from ..providers.base_provider import BaseModule


logger = logging.getLogger(__name__)


@dataclasses.dataclass
class Config:
    key: str
    audience: str
    algorithms: Tuple[str] = ('HS256',)
    cookie_name: str = 'oidc_id_token'
    auth_header_name: str = 'Authorization'
    bearer_prefix: str = 'Bearer '
    # TODO scott: After new pyjwt release, if the JWTs from Catalogue start failing because of these options then
    #  should they be set to False?
    verify_signature: bool = True
    verify_aud: bool = True
    verify_exp: bool = True

    aws_prefix: str = 'AWS'


JWT = NewType('JWT', dict)
JWTEncoded = NewType('JWTEncoded', str)


class OIDCDependencyProvider(BaseModule):
    config_class = Config

    @classmethod
    def _get_aws_jwt(cls, header_jwt):
        """
        Pulls the AWS Access key Id from a boto request.

        This is completely redundant if going via middleware (the apps/integration currently dont though)
        """
        if header_jwt.startswith('AWS4-HMAC-SHA256 '):
            _, _, data = header_jwt.partition(' ')
            for aws_credential in data.split(','):
                type_, _, cred_data = aws_credential.strip().partition('=')

                if type_ == 'Credential':
                    access_key_id, _, _ = cred_data.partition('/')
                    return access_key_id

        if header_jwt.startswith('AWS '):
            processed_header = header_jwt[len('AWS '):]
            access_key_id, _, _ = processed_header.strip().partition(':')
            return access_key_id

        logger.warning(
            'Malformed AWS Request',
            extra={
                'header': header_jwt
            }
        )

        raise UnprocessableEntity(
            'Malformed AWS Request.'
        )

    @request_scope
    @provider
    def user_info(self, jwt_encoded: JWTEncoded) -> JWT:
        """
        Verifies cookie and yields JWT

        ----

        I want to make clear we're doing a few things wrong with
        authentication.

        Retrieving the OIDC token is the job of the old application.
        Towards the end of the authentication flow a JWT cookie is set.

        The way the JWT cookie is set is completely wrong.

        Flask-OIDC (used in the old app) ignores the signature of the JWT
        issued by Hydra, then creates it's own SHA256 hash of of the header
        and payload, literally doing the following.

        >>> generated_signature = hmac.new(
        >>>     flask_secret_key,
        >>>     msg=header_and_payload,
        >>>     digestmod=hashlib.sha256
        >>> ).hexdigest()
        >>> assert generated_signature == signature
        """
        try:
            options = {
                "verify_signature": self.config.verify_signature,
                "verify_aud": self.config.verify_aud,
                "verify_exp": self.config.verify_exp,
            }
            payload = jwt.decode(
                jwt_encoded,
                self.config.key,
                audience=self.config.audience,
                algorithms=list(self.config.algorithms),
                options=options
            )
            pl = JWT(payload)
            return pl  # TODO refactor to call new class here
        except jwt.exceptions.InvalidSignatureError as e:
            # this is a configuration issue - check that JWT_SECRET_KEY/OIDC_SECRET_KEY is correct for/and correct env
            raise Unauthorized(
                'User not authenticated. Invalid Token: ' + str(e) + '.'
            )
        except jwt.exceptions.InvalidTokenError as e:
            raise Unauthorized(
                'User not authenticated. Invalid Token: ' + str(e) + '.'
            )
        except TypeError:
            logger.exception(
                f"JWT type error",
                extra={
                    'jwt_encoded': jwt_encoded,
                    'jwt_encoded type': type(jwt_encoded),
                    'config': self.config,
                },
            )
            raise

    @request_scope
    @provider
    def jwt(self, request: Request) -> JWTEncoded:

        cookie_jwt = request.cookies.get(self.config.cookie_name)
        header_jwt = request.headers.get(self.config.auth_header_name)

        # case: both
        if cookie_jwt and header_jwt:
            raise UnprocessableEntity(
                'User cannot be authenticated. '
                'Only one token should be '
                'provided either in the '
                'Authorization Header or in '
                'the Cookie.'
            )

        # case: neither
        if not cookie_jwt and not header_jwt:
            raise Unauthorized(
                'User not authenticated. Token '
                'has to be provided either '
                'in the Authorization Header .'
                # not mentioning cookie anymore here, as this is for QA/Catalogue only
                # we don't want external users knowing about it.
            )

        # case: either-or
        if cookie_jwt:
            return JWTEncoded(cookie_jwt)
        else:
            header_jwt = cast(str, header_jwt)

            if header_jwt.startswith(self.config.bearer_prefix):
                return JWTEncoded(header_jwt.split(' ')[-1])
            if header_jwt.startswith(self.config.aws_prefix):
                '''        
                    This is completely redundant if going via middleware (the apps/integration currently dont though).
                    boto makes direct requests here presently (s3proxy), so needs to be able to exchange directly.
                    
                    TODO will be to make everything travel via the middleware, at which point any AWS exchange should be 
                    removed (29/NOV/2021)
                '''
                return JWTEncoded(self._get_aws_jwt(header_jwt))
            else:
                raise UnprocessableEntity(
                    'User cannot be authenticated. '
                    'Authorization Header type not '
                    'provided.'
                )


def public(view):
    """
    Marks view as public. Ignores authentication errors.
    """
    @wraps(view)
    def wrapper(*args, **kwargs):
        try:
            current_app.injector.get(JWT)
        except (Unauthorized, Forbidden):
            pass

        return view(*args, **kwargs)

    return wrapper


def private(view):
    """
    Marks view as private. Attempts to get a token from
    the request. If it fails the OIDC provider will tell
    us why.
    """

    # This will modifier the swag from result to include security data
    if hasattr(view, 'specs_dict'):
        view.specs_dict['security'] = [{'bearer_auth': []}]

    @wraps(view)
    def wrapper(*args, **kwargs):
        # raises error if it fails. Caches user object
        current_app.injector.get(JWT)

        return view(*args, **kwargs)

    return wrapper
