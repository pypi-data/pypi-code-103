# Create your views here.
import logging

from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Account, Hashtag
from ..serializers.accountSerializers import AccountSerializer
from ..serializers.contentSerializers import HashtagSerializer

logger = logging.getLogger(__name__)

class Search(APIView):
    """
    This view is for searching hashtags and accounts.
    The search requires an user registration.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = (IsAuthenticated,)

    @staticmethod
    def get(request: Request, *args, **kwargs) -> Response:
        """
        This method searches for matching hashtags and account for a given search query.
        Then the results are returned in an corresponding composed dict.

        :param request: The request send by the user.
        :param args: Not used.
        :param kwargs: Additional arguments which provides the search parameter q.
        :return: Composed dict of results in the Response with status code 200, otherwise if no query q is given it will
        return an empty Response with status code 400.
        The results can also be filtered for single categories. Those categories are: account and hashtag.
        """
        query: str = request.query_params.get('q', None)
        limit: int = 5
        if not query:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        result_filter: str = request.query_params.get('filter', None)

        result: dict = {}
        
        if result_filter == "account" or not result_filter:
            accounts: Account = Account.objects.filter(user__username__contains=query)[:limit]
            result["accounts"] = AccountSerializer(instance=accounts, many=True).data

        if result_filter == "hashtag" or not result_filter:
            hashtags: Hashtag = Hashtag.objects.filter(tag__contains=query)[:limit]
            result["hashtags"] = HashtagSerializer(instance=hashtags, many=True).data
        
        if result:
            return Response(data=result, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)