import logging

from rest_framework import generics
from rest_framework.response import Response

from .contants import NotifyType, Status
from .serializers import QiwiKassaNotifySerializer

logger = logging.getLogger(__name__)


class QiwiKassaNotifyView(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        notify_type = request.data.get("type")
        if notify_type != NotifyType.PAYMENT:
            msg = (
                f"Qiwi Kassa notify with type={notify_type} cannot be processed. "
                "Just ignoring it."
            )
            logger.info(msg)
            return Response({"msg": msg})

        request_hmac = request.META.get("HTTP_SIGNATURE")
        serializer = QiwiKassaNotifySerializer(
            data=request.data,
            context={
                "hmac": request_hmac,
            },
        )
        if not serializer.is_valid():
            logger.info(
                f"Error with processing request.data={request.data} hmac={request_hmac}"
            )
            serializer.is_valid(raise_exception=True)

        status = serializer.validated_data["payment"]["status"]["value"]
        if status != Status.SUCCESS:
            msg = (
                f"Qiwi Kassa notify with status={status} cannot be processed. "
                "Just ignoring it."
            )
            logger.info(msg)
            return Response({"msg": msg})

        payment = serializer.validated_data["payment"]["bill_id"]
        payment.accept()

        return Response({"msg": "ok"})
