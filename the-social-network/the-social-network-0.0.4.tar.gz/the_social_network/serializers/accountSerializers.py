from rest_framework import serializers

from ..models import Account
from ..serializers.authenticationSerializers import UserPublicSerializer, UserOwnSerializer
from ..serializers.contentSerializers import StatementSerializer


class AccountSerializer(serializers.ModelSerializer):
    """
    This serializer serializes the accounts and their data.
    It can be used to serialize accounts.
    """
    user = UserPublicSerializer()

    class Meta:
        model = Account
        fields = ('user', 'image',)


class AccountPublicSerializer(serializers.ModelSerializer):
    """
    This serializer serializes the public data of accounts.
    It can be used to get all public data of the accounts.
    """
    # this is the parent account
    user = UserPublicSerializer()
    # these are the related (child) accounts
    related_to = serializers.ListField(source='get_related_to', child=AccountSerializer())
    # these are all statements of the account
    statements = serializers.ListField(source='get_statements', child=StatementSerializer())
    # check if the calling account knows the account as friend.
    is_friend = serializers.SerializerMethodField('_is_friend')
    # this field is to check if the one calls his own public data.
    self_request = serializers.SerializerMethodField('_self_request')

    def _self_request(self, obj: Account):
        return self.context["calling_account"].user.id == obj.user.id

    def _is_friend(self, obj: Account):
        """
        This intern method checks for the calling account if the requested account is a friend or not!

        :param obj: The requested account.
        :return: True if obj is a friend of the calling account.
        """
        account: Account = self.context["calling_account"]
        return obj in account.get_related_to()

    class Meta:
        model = Account
        fields = ('user', 'image', 'biography', 'related_to', 'statements', 'is_friend', 'self_request',)


class AccountTinySerializer(AccountPublicSerializer):
    """
    This serializer serializes the public data of accounts but it is shorter.
    It can be used to get all shortened public data of the accounts.
    """
    # this is the parent account
    user = UserPublicSerializer()

    class Meta:
        model = Account
        fields = ('user', 'image', 'related_to')


class AccountOwnSerializer(AccountPublicSerializer):
    """
    This serializer is for the representation of an own account.
    It shows more information to the user then the public serializer.
    Todo: Make statements use the StatementSerializer.
    """
    # this is the parent account, it overwrites the field of AccountPublicSerializer
    user = UserOwnSerializer()
    # to see how follows the own account
    related_by = serializers.ListField(source='get_related_by', child=AccountSerializer())

    class Meta:
        model = Account
        fields = ('user', 'image', 'biography', 'related_by', 'related_to', 'statements')
