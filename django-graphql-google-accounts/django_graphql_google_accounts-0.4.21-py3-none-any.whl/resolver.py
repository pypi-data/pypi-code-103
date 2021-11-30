import graphene
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from graphene import Field, Int

from accounts.auth.token import JSONWebToken
from accounts.decorators.define import login_required
from accounts.models import RefreshTokens
from accounts.types import UserType

EXPIRE_DAYS = settings.ACCOUNTS_SETTINGS.get('refresh_token_expire', 30)


class UserQuery:
    user = Field(UserType, id=Int())

    @staticmethod
    @login_required
    def resolve_user(root, info, id: str):
        return get_user_model().objects.get(pk=id)


class RefreshTokenMutation(graphene.Mutation, JSONWebToken):
    class Arguments:
        token = graphene.String(required=True)

    ok = graphene.Boolean()
    access_token = graphene.String()
    refresh_token = graphene.String()
    refresh_time = graphene.DateTime()

    @classmethod
    def mutate(cls, root, info, token):
        delta = timezone.timedelta(days=EXPIRE_DAYS)
        expire = timezone.now() + delta
        obj = RefreshTokens.objects.filter(
            refresh_token=token,
            created_at__lt=expire,
        )
        if obj:
            obj.delete()
            _token = cls._refresh_token()
            claim = cls.get_info_token(info)
            access_token = cls._access_token(
                id=claim.get('id', 0),
                uid=claim.get('uid', '')
            )
            RefreshTokens.objects.create(refresh_token=_token)
            return RefreshTokenMutation(
                ok=True,
                access_token=access_token,
                refresh_token=_token,
                refresh_time=timezone.now()
            )
        return RefreshTokenMutation(
            ok=False,
            access_token='',
            refresh_token=''
        )
