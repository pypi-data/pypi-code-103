import logging
from typing import OrderedDict

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

logger = logging.getLogger(__name__)


class UserDefaultSerializer(serializers.ModelSerializer):
    """
    This is the default serializer to get users and validate their data.
    """

    username = serializers.CharField()

    def validate(self, data: OrderedDict):
        """
        This method validates the provided data to check if there is an user existing.

        :param data: Data describing the user.
        :return: The validated data.
        """
        username: str = data.get("username", None)
        password: str = data.get("password", None)

        if not username:
            raise serializers.ValidationError("This username is missing", code='blank')

        if not password:
            raise serializers.ValidationError("This password is missing", code='blank')

        user: User = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError({"user": "There is no user like this"}, code='invalid')

        return data

    class Meta:
        model = User
        fields = ['username', 'password']


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    This serializer is used for user registration and their validation.
    A user should have a unique valid and non-empty username, email and password.
    """

    username = serializers.CharField(
        required=True,
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            RegexValidator(r'^[0-9a-zA-Z_]*$', 'Only aA-zZ, 0-9, _ are allowed.')
        ]
    )
    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(queryset=User.objects.all())
        ]
    )

    def create(self, validated_data):
        """
        This method creates a new user by the validated data.

        :param validated_data: The validated data providing all information to create an user.
        :return: The created user.
        """
        user: User = User.objects.create_user(**validated_data)
        return user

    class Meta:
        model = User
        fields = ['username', 'email', 'password']


class UserPublicSerializer(serializers.ModelSerializer):
    """
    This serializer is for the public representation of the user.
    It only shows the username.
    """

    class Meta:
        model = User
        fields = ('id', 'username',)


class UserOwnSerializer(serializers.ModelSerializer):
    """
    This serializer is for the own representation of the user.
    """

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'date_joined',)
