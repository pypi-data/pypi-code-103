import logging

from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Account
from .. import Operations
from ..validation import validate_request_data_for

logger = logging.getLogger(__name__)


class Register(APIView):
    """
    This APIView takes care of the registration of new users.
    It checks if the new user has entered all fields for registration.
    When a new user logs in, he is also directly logged in and receives a token.
    """

    @staticmethod
    def validate(request: Request) -> Response:
        """
        This method validates the data provided for the new user.
        It validates if the username, email and the password is set and they are not empty.

        :param request: The request which should be validated.
        :return: 400_BAD_REQUEST if the provided data is sparse or one of the values is empty.
                 201_CREATED otherwise.
        """
        return validate_request_data_for(Operations.REGISTER, request)

    def post(self, request: Request) -> Response:
        """
        This method handles the actual POST-request of the new user.
        First the data send is checked for mistakes, missing or empty values.
        Afterwards the User is created and logged in.

        :param request: The request of the new user containing all necessary information for an registration.
        :return: 400_BAD_REQUEST if the provided data is sparse or one of the values is empty or the user existing.
                 201_CREATE if the new user is created (Contains the token in the data-section).
        """
        valid: Response = self.validate(request)
        if valid.status_code != 201:
            return valid

        username: str = valid.data["username"]
        user: User = User.objects.filter(username=username).first()
        account: Account = Account.objects.create(user=user)
        login(request, account.user)
        return Response(status=valid.status_code, data={"token": Token.objects.create(user=account.user).__str__()})


class Login(APIView):
    """
    This APIView takes care of the login of a requesting users.
    It checks if the user has entered all fields for login.
    When a user logs in, he receives a token.
    """

    @staticmethod
    def validate(request: Request) -> Response:
        """
        This method validates the data provided for the requesting user.
        It validates if the username and the password is set and they are not empty.

        :param request: The data provided by the requesting user.
        :return: 400_BAD_REQUEST if the provided data is sparse or one of the values is empty.
                 200_OK otherwise.
        """
        return validate_request_data_for(Operations.LOGIN, request)

    def post(self, request):
        """
        This method handles the actual POST-request of the requesting user.
        First the data send is checked for mistakes, missing or empty values.
        Afterwards the User is authenticated and logged in.
        
        :param request: The request of the user containing all necessary information for an login.
        :return: 400_BAD_REQUEST if the provided data is sparse or one of the values is empty or wrong.
                 200_OK if the user is authenticated (Contains the token in the data-section).
        """
        valid: Response = self.validate(request)
        if valid.status_code != 200:
            return valid

        username: str = valid.data["username"]
        user: User = User.objects.filter(username=username).first()
        token, operation_was_create = Token.objects.get_or_create(user=user)

        if not operation_was_create:
            # refresh the token if there was a previous token detected
            token.delete()
            token = Token.objects.create(user=user)
        login(request, user)

        return Response(status=valid.status_code, data={"token": token.key.__str__()})


class Logout(APIView):
    """
    This APIView takes care of the logout of a requesting users.
    It checks if the user has entered all fields for logout.
    When a user logs out, his token will be destroyed.
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = (IsAuthenticated,)

    @staticmethod
    def post(request):
        """
        This method handles the actual POST-request of the requesting user.
        First the data send is checked for mistakes, missing or empty values.
        Afterwards the User is authenticated and logged out.

        :param request: The request of the user containing all necessary information for an logout.
        :return: 400_BAD_REQUEST if the provided data is sparse or one of the values is empty or wrong or the user is not logged in.
                 200_OK if the user is authenticated (will destroy the users token).
        """
        user: User = request.user
        token: Token = Token.objects.filter(user=user).first()
        if token:
            token.delete()
        logout(request)
        return Response(status=status.HTTP_200_OK)


class TokenValidation(APIView):
    """
    This view can be used to validate a token of an user.
    Therefore it can be used for the frontend to validate if the token has expired e.g. if the user has logged in
    on another device.

    """
    authentication_classes = [TokenAuthentication]
    permission_classes = (IsAuthenticated,)

    def get(self, request) -> Response:
        """
        This method is allways called if the token is valid.
        Otherwise the permission_classes will return 401 indication an invalid token.

        :param request: Unused
        :return: Status 200 Ok if the token is authorized.
        """
        return Response(status=status.HTTP_200_OK)
