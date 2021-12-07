# Create your views here.
import logging
from io import BytesIO

from PIL import Image
from django.contrib.auth.models import User
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models import Q
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Account, Statement
from ..serializers.accountSerializers import AccountPublicSerializer, AccountOwnSerializer
from ..serializers.contentSerializers import ReactionSerializer, StatementSerializer

logger = logging.getLogger(__name__)


class PublicAccounts(APIView):
    """
    This view is used to represent the accounts.
    It can be used to get public information about accounts from the perspective of the calling account.
    To get this information the calling account must use its token.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = (IsAuthenticated,)

    def get(self, request: Request, *args, **kwargs):
        """
        This method is used to get all public information regarding a specific account.
        :param request: Not used.
        :param args: Not used.
        :param kwargs: Should have the id of the requested account (see view.py)
        :return:
        """
        calling_account: Account = Account.objects.filter(user=request.user).first()
        account: Account = Account.objects.filter(user=int(kwargs.get("id")))
        serializer: AccountPublicSerializer = AccountPublicSerializer(instance=account,
                                                                      many=True,
                                                                      context={"calling_account": calling_account})
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class AllPublicAccounts(APIView):
    """
    This view is for showing all public accounts.
    It requires the user token to see which account is calling the overview.
    The calling account is then removed from the result.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = (IsAuthenticated,)

    def get(self, request: Request):
        """
        This method gets all available public accounts.
        Furthermore the calling account is excluded from the result.
        :param request: Used to get the calling account.
        :return:
        """
        calling_account: Account = Account.objects.filter(user=request.user).first()
        accounts: Account = Account.objects.filter(~Q(user=request.user))
        serializer: AccountPublicSerializer = AccountPublicSerializer(instance=accounts,
                                                                      many=True,
                                                                      context={"calling_account": calling_account})
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class OwnAccount(APIView):
    """
    This view is used to represent the private account of an user.
    To access the information one have to use its token.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = (IsAuthenticated,)

    def get(self, request: Request):
        """
        This method is used to get the own account data.
        :param request: To access the user from its token.
        :return: Data regarding the own account.
        """
        account: Account = Account.objects.filter(user=request.user)
        serializer: AccountOwnSerializer = AccountOwnSerializer(instance=account, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class OwnAccountFollow(APIView):
    """
    This view is for adding a follow relation from the calling account to the targeted one.
    To access this view the requesting account has to use its token.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = (IsAuthenticated,)

    def post(self, request: Request, *args, **kwargs):
        own_account: Account = Account.objects.filter(user=request.user).first()
        foreign_account: Account = Account.objects.filter(user=kwargs.get("id")).first()
        if not foreign_account:
            return Response(status=status.HTTP_409_CONFLICT)
        created: bool = own_account.add_relationship(foreign_account)
        if created:
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_409_CONFLICT)


class OwnAccountUnfollow(APIView):
    """
    This view is for deleting a follow relation from the calling account to the targeted one.
    To access this view the requesting account has to use its token.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = (IsAuthenticated,)

    def post(self, request: Request, *args, **kwargs):
        own_account: Account = Account.objects.filter(user=request.user).first()
        foreign_account: Account = Account.objects.filter(user=kwargs.get("id")).first()
        if not foreign_account:
            return Response(status=status.HTTP_409_CONFLICT)
        deleted: bool = own_account.remove_relationship(foreign_account)
        if deleted:
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_409_CONFLICT)


class OwnAccountUpdate(APIView):
    """
    This view is for updating the account data.
    It will update an image.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = (IsAuthenticated,)

    @staticmethod
    def put(request: Request):
        """
        This method updates the image as well as the biography.
        :param request: The request send by the user.
        :return: A response with an 200 status.
        """
        user: User = request.user
        account: Account = Account.objects.filter(user=user).first()

        if "biography" in request.data.keys():
            biography: str = request.data["biography"]
            account.update_biography(biography)
        if "file" in request.FILES.keys():
            file: InMemoryUploadedFile = request.FILES["file"]
            file.name = "{name}.{extension}".format(name="account{user}{secret}".format(user=user, secret=hash(user)),
                                                    extension="jpeg")
            # compress image
            image: Image = Image.open(file)
            image = image.convert('RGB')
            io_stream = BytesIO()
            image.save(io_stream, format="JPEG", quality=50, optimize=True)
            compressed_image: InMemoryUploadedFile = InMemoryUploadedFile(file=io_stream,
                                                                          field_name=None,
                                                                          name=file.name,
                                                                          content_type="image/jpeg",
                                                                          size=io_stream.tell(),
                                                                          charset=None)
            # update with compressed image
            account.update_image(compressed_image)
        return Response(status=status.HTTP_200_OK)


class AddStatement(APIView):
    """
    This view serves to add statements for an specific user.
    The user must be authenticated.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = (IsAuthenticated,)

    @staticmethod
    def post(request: Request):
        """
        This method handles the post of an new statement.
        :param request: The request to be handled, containing the input.
        :return: Response with an 200 OK if everything is okay. 400 if there is no statement input.
        If there is an reaction then this will return 200 and the serialized reaction.
        This is necessary, because the frontend must only add this element to the overview of reaction and needs the
        analysis regarding the mentions and tags by the backend.
        todo: Make it possible for single statement

        """
        account: Account = Account.objects.filter(user=request.user).first()
        statement: str = request.data.get("input", None)
        if not statement:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        statement: Statement = account.add_statement(statement)
        # if there is an reaction given then is must be added to the parent element.
        reaction: dict = request.data.get("reaction", None)
        if reaction:
            parent: Statement = Statement.objects.get(id=reaction.get("to"))
            vote: int = 1 if reaction.get("relation") == "support" else 2
            reaction, _ = parent.add_reaction(reaction_statement=statement, vote=vote)
            serializer: ReactionSerializer = ReactionSerializer(instance=reaction, many=False)
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        serializer: StatementSerializer = StatementSerializer(instance=statement, many=False)
        return Response(status=status.HTTP_200_OK, data=serializer.data)
