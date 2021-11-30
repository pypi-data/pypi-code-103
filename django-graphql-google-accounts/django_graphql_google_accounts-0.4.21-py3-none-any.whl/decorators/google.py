import random
import string
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth import get_user_model, authenticate, login
from django.db.utils import IntegrityError

from accounts.auth.google import GoogleProviderToken
from accounts.auth.token import JSONWebToken
from accounts.erros import NotFoundIDToken
from accounts.models import RefreshTokens

CONFIG = settings.ACCOUNTS_SETTINGS.get('google', {})


class GoogleProviderCallback(GoogleProviderToken, JSONWebToken):

    def __init__(self, function):
        super(GoogleProviderCallback, self).__init__()
        self.func = function

    def __call__(self, request, *args, **kwargs):
        self.request = request

        query_string = self.save()
        redirect_url = f"{CONFIG.get('front_redirect_uri', '/')}?{query_string}"

        kwargs.update({'redirect_url': redirect_url})
        dispatch = self.func(request, *args, **kwargs)
        return dispatch

    @staticmethod
    def save_refresh_token(token: str):
        RefreshTokens.objects.update_or_create(
            refresh_token=token,
            defaults={'refresh_token': token}
        )

    @staticmethod
    def save_user(profiles: dict) -> dict:
        defaults = {
            'uid': profiles.get('sub', ''),  # google user id
            'nickname': profiles.get('name', ''),
            'locale': profiles.get('locale', ''),
            'picture': profiles.get('picture', ''),
        }
        try:
            obj, _ = get_user_model().objects.update_or_create(
                email=profiles.get('email', ''),
                defaults=defaults
            )
        except IntegrityError:
            rand_string = ''.join(random.choices(list(string.hexdigits), k=8))
            defaults['nickname'] = f"{profiles.get('name', '')}_{rand_string}"
            obj, _ = get_user_model().objects.update_or_create(
                email=profiles.get('email', ''),
                defaults=defaults
            )
        defaults.update({'id': obj.id})
        return defaults

    def save(self) -> str:
        tokens = self.get_token()
        id_token = tokens.get('id_token', '')
        if not id_token:
            raise NotFoundIDToken

        profiles = self.extra_data(id_token)
        defaults: dict = self.save_user(profiles)

        uid = profiles.get('sub', '')
        access_token = self._access_token(id=defaults.get('id', 0), uid=uid)
        refresh_token = self._refresh_token()
        self.save_refresh_token(refresh_token)
        user = authenticate(uid=uid)
        login(self.request, user)

        return urlencode({
            **defaults,
            'email': profiles.get('email', ''),
            'accessToken': access_token,
            'refreshToken': refresh_token,
        })
