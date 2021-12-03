# SPDX-FileCopyrightText: Mintlab B.V.
#
# SPDX-License-Identifier: EUPL-1.2

import codecs
import jose.exceptions
import json
import logging
import minty.cqrs
import requests.exceptions
import statsd
import time
from . import oidc
from collections import defaultdict
from functools import wraps
from minty import Base
from pyramid.httpexceptions import (
    HTTPForbidden,
    HTTPInternalServerError,
    HTTPUnauthorized,
)
from redis import StrictRedis
from typing import Dict, List, Sequence, cast
from uuid import UUID

SCOPE_PREFIX = "zs:"


class SessionRetrieverError(Exception):
    """Base for session retrieval related exceptions."""

    pass


class SessionNotFoundError(SessionRetrieverError, ValueError):
    """Session can't be found in Redis."""

    pass


class SessionDataNotFoundError(SessionRetrieverError, ValueError):
    """Session data can't be found in Redis."""

    pass


class SessionRetriever(Base):
    """HTTP session retriever.

    retrieves a session stored by the Perl application from the Redis store
    """

    __slots__ = ["redis", "decoder"]

    def __init__(self, redis: StrictRedis):
        """Initialize a HTTP session retriever.

        :param redis: Redis connection object to retrieve session data
        :type redis: StrictRedis
        """
        self.redis = redis

    def retrieve(self, session_id: str):
        """Retrieve a session from Redis.

        :param session_id: session id to retrieve
        :type session_id: str
        :raises SessionNotFoundError: if the session cannot be found
        :raises SessionDataNotFoundError: if the session is found, but contains
                                          no data
        :return: the session data
        :rtype: dict
        """
        now = time.time()

        timer = cast(statsd.Timer, self.statsd.get_timer("retrieve_session"))
        counter = cast(statsd.Counter, self.statsd.get_counter("retrieve"))

        with timer.time():
            expiration = self.redis.get(f"expires:{session_id}")

            if expiration is None:
                self.logger.info(f"Session '{session_id}' not found")
                counter.increment("redis.session_not_found.count")
                raise SessionNotFoundError(session_id)

            if float(expiration) < now:
                self.logger.info(f"Session '{session_id}' has expired")
                counter.increment("redis.session_not_found.count")
                raise SessionNotFoundError(session_id)

            session_data_raw = self.redis.get(f"json:session:{session_id}")

            if session_data_raw is None:
                self.logger.info(f"Session '{session_id}' not found")
                counter.increment("redis.session_not_found.count")
                raise SessionDataNotFoundError(session_id)

            session_data_decoded = codecs.decode(session_data_raw, "base64")
            session_data = json.loads(session_data_decoded)

            self.logger.debug(f"Session '{session_id}' retrieved")

            return session_data


def redis_from_config(config: dict) -> StrictRedis:
    """Create a Redis cleint from variables in the config parameter.

    :param config: config variables
    :type config: dict
    :return: configured redis client
    :rtype: StrictRedis
    """
    redis_conf = config["redis"]["session"]

    redis = StrictRedis(**redis_conf)
    return redis


def session_manager_factory(infra_factory):
    """Create a configured SessionRetriever class.

    :param infra_factory: infrastructure factory class
    :type infra_factory: InfrastructureFactory
    :return: configured SessionRetriever class to retrieve session information
        from session store
    :rtype: SessionRetriever
    """
    infra_factory.register_infrastructure(
        name="redis", infrastructure=redis_from_config
    )
    redis = infra_factory.get_infrastructure(
        context=None, infrastructure_name="redis"
    )
    return SessionRetriever(redis)


def get_logged_in_user(request, logger: logging.Logger) -> minty.cqrs.UserInfo:
    """ Get the logged in user from the given pyramid request object

    Args:
        request: the pyramid request object to get the user from
        logger: the logging.getLogger() instance to log to

    Returns:
        user_info: dict containing values from handle_session_data()
    """

    try:
        request.assert_platform_key()

        user_uuid = request.get_platform_user_uuid()
        permissions: Dict[str, bool] = defaultdict(
            lambda: True, pip_user=False
        )

        user_info = minty.cqrs.UserInfo(user_uuid, permissions)
        logger.info("Platform key used successfully")
        return user_info
    except (AttributeError, KeyError):
        pass

    if request.authorization:
        logger.debug("Verifying Authorization header (OAuth2)")
        user_info = handle_oauth2(request)
    else:
        logger.debug("Verifying session cookie")
        try:
            session_data = request.retrieve_session()
            user_info = handle_session_data(
                session_data=session_data, logger=logger
            )
        except (SessionRetrieverError, KeyError) as e:
            logger.info(f"Invalid session: '{e}'")
            raise HTTPUnauthorized(
                content_type="application/json",
                json_body={"error": "Unauthorized"},
            )

    return user_info


def check_user_permission(
    permissions: Sequence[str], user_info: minty.cqrs.UserInfo
) -> bool:
    """Returns whether the user has any of the given permissions.

    Args:
        permissions: List containing permissions in string format
        user_info: the result from handle_session_data() to check against

    Returns:
        perm: the string permission we first positively validated against
    """

    # User permissions will be set on login, based on a table of roles
    # and access rights.
    #
    # This generally means someone with "admin" rights will also have
    # the other permissions set.

    for permission in permissions:
        try:
            if user_info.permissions[permission]:
                return True
        except KeyError:
            pass

    return False


def protected_route(permission="gebruiker", *args):
    """Check session and inject `minty.cqrs.UserInfo` in wrapped view .

    zaaksysteem_session cookie is checked for validity and `minty.cqrs.UserInfo` is
    injected in the view.

    :param view: view function
    :type view: pyramid view
    :raises HTTPUnauthorized: session not valid or non-existant
    :return: view with `minty.cqrs.UserInfo` injected
    :rtype: wrapped view
    """
    permission_list: List[str] = [permission, *args]

    def protected_view_wrapper(view):
        @wraps(view)
        def view_wrapper(request):
            logger = logging.getLogger(view.__name__)

            user_info = get_logged_in_user(request, logger)
            perm = check_user_permission(permission_list, user_info)

            if not perm:
                raise HTTPForbidden(
                    json={
                        "error": "You do not have permission to access this."
                    }
                )

            return view(request=request, user_info=user_info)

        return view_wrapper

    return protected_view_wrapper


def handle_session_data(session_data: dict, logger) -> minty.cqrs.UserInfo:
    """Handle session data for different types of users.

    Current users: zaaksyteem user & pip_user

    :param session_data: session
    :type session_data: dict
    :param logger: logger
    :type logger: Logger
    :raises HTTPUnauthorized: if user is not Authorized
    :return: user_info object
    :rtype: minty.cqrs.UserInfo
    """
    try:
        user_info_raw = session_data.get("__user", "{}")
        if user_info_raw != "{}":
            user_info_decoded = json.loads(user_info_raw)
            user_info = minty.cqrs.UserInfo(
                user_uuid=user_info_decoded["subject_uuid"],
                permissions=user_info_decoded["permissions"],
            )
            return user_info

        user_info_pip = session_data.get("pip", {})
        if user_info_pip != {}:
            user_info = minty.cqrs.UserInfo(
                user_uuid=user_info_pip["user_uuid"],
                permissions={"pip_user": True},
            )
            return user_info
    except (TypeError, KeyError) as e:
        logger.info(f"Unauthorized: error in session data: '{e}'")

    raise HTTPUnauthorized(
        content_type="application/json", json_body={"error": "Unauthorized"}
    )


def handle_oauth2(request) -> minty.cqrs.UserInfo:
    logger = logging.getLogger(__name__)

    config = request.configuration

    required_configuration = {"oidc_client_id", "oidc_endpoint_config"}
    if not required_configuration.issubset(config.keys()):
        logger.info("Authorization header found, but OIDC is not configured")
        raise HTTPUnauthorized(
            content_type="application/json",
            json_body={"error": "Unauthorized"},
        )

    authorization = request.authorization
    access_token = authorization.params

    try:
        redis = request.infrastructure_factory.get_infrastructure(
            context=None, infrastructure_name="redis"
        )

        token_info = oidc.parse_token(
            access_token=access_token,
            oidc_client_id=config["oidc_client_id"],
            oidc_endpoint_config=config["oidc_endpoint_config"],
            instance_uuid=config["instance_uuid"],
            cache=redis,
        )
    except requests.exceptions.HTTPError as e:
        raise HTTPInternalServerError(
            content_type="application/json",
            json_body={"error": "Internal server error"},
        ) from e
    except jose.exceptions.JOSEError as e:
        logger.info(f"Error parsing OAuth2 token: {e}", exc_info=True)
        raise HTTPUnauthorized(
            content_type="application/json",
            json_body={"error": "Unauthorized"},
        ) from e

    return minty.cqrs.UserInfo(
        user_uuid=UUID(token_info["user_uuid"]),
        permissions={
            scope[len(SCOPE_PREFIX) :]: True
            for scope in token_info["scope"]
            if scope.startswith(SCOPE_PREFIX)
        },
    )
