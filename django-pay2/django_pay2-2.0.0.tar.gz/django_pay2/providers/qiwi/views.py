from rest_framework import generics, status
from rest_framework.response import Response

from .serializers import QiwiNotifySerializer


class QiwiNotifyView(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        serializer = QiwiNotifySerializer(
            data=request.data,
            context={
                "hmac": request.META.get("HTTP_X_API_SIGNATURE_SHA256"),
            },
        )
        serializer.is_valid(raise_exception=True)
        serializer.validated_data["bill"]["bill_id"].accept()
        return Response(status=status.HTTP_204_NO_CONTENT)
