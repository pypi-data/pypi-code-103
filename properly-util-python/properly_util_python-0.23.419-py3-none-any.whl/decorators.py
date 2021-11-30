import functools

from flask import request
from flask.wrappers import Response

from properly_util_python.dynamo_helper import EnvironmentControlledDynamoHelper
from properly_util_python.properly_logging import ProperLogger

from properly_util_python.user_auth import UserAuthHelper


def authorized(role, return_keys: list = []):
    def outer(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            logger = ProperLogger("AuthDecorator")
            logger.debug("Authorizing request", {"request": request})

            user_auth_helper = UserAuthHelper(EnvironmentControlledDynamoHelper())
            event_object = request.environ.get("event")
            user_auth = user_auth_helper.get_user_auth_context_from_event(event_object)

            if user_auth is None:
                logger.error("NoContext", "no context")
                return Response(response="{'error': 'no context'}", status=403, mimetype="application/json")

            sub = user_auth.get("auth_id")
            provider = user_auth.get("provider")
            logger.add_common_tags({"sub": sub, "provider": provider})

            # find the user
            properly_user = user_auth_helper.get_properly_user_from_user_verified_email(
                email=user_auth["auth_email"]
            )

            if properly_user is None:
                logger.error("UserNotFound", "user not found")
                return Response(response="{'error': 'user not found'}", status=403, mimetype="application/json")

            properly_user_id_caller = properly_user.get("id")
            logger.add_common_tags({"user_id": properly_user_id_caller})

            # verify the user record matches the Cognito information received
            is_user_identity_correct = user_auth_helper.check_user_identity(properly_user, sub, provider)
            if not is_user_identity_correct:
                logger.error("MismatchedIdentity", "identity received doesn't match user record")
                return Response(
                    response="{'error': 'identity received doesn't match user record'}",
                    status=403,
                    mimetype="application/json",
                )

            # verify the user has the right roles for the operation
            is_in_role_flag = user_auth_helper.check_user_in_role(properly_user, role)

            if not is_in_role_flag:
                logger.error("MissingRole", "missing role")
                return Response(response="{'error': 'missing role'}", status=403, mimetype="application/json")

            logger.debug("Authorization succeeded")

            if "user_id" in return_keys:
                return func(*args, user_id=properly_user_id_caller, **kwargs)

            return func(*args, **kwargs)

        return inner

    return outer
