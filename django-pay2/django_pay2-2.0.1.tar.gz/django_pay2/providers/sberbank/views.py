import logging

from django.http import HttpResponse
from django.views.generic import View

from .constants import SberbankCallbackOperation, SberbankCallbackStatus
from .serializers import SberbankCallbackSerializer

logger = logging.getLogger(__file__)


class CallbackView(View):
    def get(self, request):
        serializer = SberbankCallbackSerializer(data=request.GET.dict())
        if not serializer.is_valid():
            logger.info(
                f"Validation error for sberbank callback. "
                f"Data: {serializer.initial_data}. "
                f"Errors: {serializer.errors}"
            )
            return HttpResponse(status=400)

        payment = serializer.validated_data["order_num"]

        operation = serializer.validated_data["operation"]
        if operation != SberbankCallbackOperation.approved:
            logger.info(
                f'Got callback for payment "{payment.id}": operation {operation}'
            )
            return HttpResponse(status=200)

        status = serializer.validated_data["status"]
        if status != SberbankCallbackStatus.success:
            logger.info(
                f'Got callback for payment "{payment.id}": '
                f"operation {operation} finished with error"
            )
            return HttpResponse(status=200)

        payment.accept()
        logger.info(f'Got callback for payment "{payment.id}": accepted.')
        return HttpResponse(status=200)
