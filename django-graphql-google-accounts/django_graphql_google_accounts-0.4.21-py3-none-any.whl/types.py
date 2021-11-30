import graphene
from django.contrib.auth import get_user_model
from graphene_django import DjangoObjectType

from accounts.models import RefreshTokens


class UserType(DjangoObjectType):
    nickname = graphene.String(name='nickname')

    class Meta:
        model = get_user_model()
        exclude = ('password',)


class RefreshTokenType(DjangoObjectType):
    class Meta:
        model = RefreshTokens
