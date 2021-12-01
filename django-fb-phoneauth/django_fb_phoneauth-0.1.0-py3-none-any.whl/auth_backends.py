import logging
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
import firebase_admin
from firebase_admin.auth import (
    verify_id_token,
    get_user,
)

logger = logging.getLogger(__name__)

fireBaseApp = firebase_admin.initialize_app()

User = get_user_model()
PHONENUMBER_FIELD = getattr(settings, 'FB_PHONENUMBER_FIELD', 'phone_number')


class FbPhoneAuthBackend(ModelBackend):
    """
    Custom auth backend that uses an phone number and token got from firebase
    For this to work, the User model must have an 'phone_number' field
    """

    def _authenticate(self, request, phone_number=None, token=None, *args, **kwargs):

        logger.debug(
            (F'Phone authenticate :{phone_number}')
        )
        if phone_number is None:
            if 'username' not in kwargs or kwargs['username'] is None:
                return None
            clean_phone_number = kwargs['username']
        else:
            clean_phone_number = phone_number

        # Check if we're dealing with an international formatted number
        if '+' not in clean_phone_number:
            logger.debug(
                (F'A non international number {clean_phone_number}')
            )
            return None

        decoded_token = verify_id_token(
            token, app=fireBaseApp, check_revoked=True)

        uid = decoded_token['uid']

        user = get_user(uid, app=fireBaseApp)
        user_phone_number = user.phone_number  # NOTE: This is FireBase user Obj

        if phone_number != user_phone_number:
            logger.warning(
                (f'phone_number ({phone_number}) from client does not match with'
                 f' phone_number ({user_phone_number}) from firebase user obj')
            )
            return None

        filter_kwargs = {PHONENUMBER_FIELD: phone_number}
        matching_users = User.objects.filter(**filter_kwargs)

        if len(matching_users) > 1:
            # This is the problem scenario where we have multiple users
            logger.error(
                (f'Multiple users with the given phone_number ({phone_number})')
            )
            raise User.MultipleObjectsReturned(
                "There are multiple users with the given phone number")
        elif len(matching_users) < 1:
            logger.info(
                (f'Create a new user with the given phone_number ({phone_number})')
            )
            db_user = User.objects.create(**filter_kwargs)
        else:
            db_user = matching_users[0]

        if self.user_can_authenticate(db_user):
            return db_user
        else:
            logger.warning(
                (f'Inactive user with the phone_number ({phone_number}) is trying to login')
            )
        return None

    def authenticate(self, *args, **kwargs):
        return self._authenticate(*args, **kwargs)
