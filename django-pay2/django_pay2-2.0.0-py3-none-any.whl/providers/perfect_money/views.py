from rest_framework import parsers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import PerfectMoneyNotifySerializer


class PerfectMoneyNotifyView(APIView):
    parser_classes = (parsers.FormParser,)

    def post(self, request, *args, **kwargs):
        serializer = PerfectMoneyNotifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment = serializer.validated_data["payment_id"]
        payment.accept()
        return Response(status=status.HTTP_204_NO_CONTENT)
