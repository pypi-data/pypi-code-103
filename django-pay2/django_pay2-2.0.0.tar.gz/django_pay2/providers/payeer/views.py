import logging

from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.csrf import csrf_exempt

from .exceptions import AlreadyPaid, PayeerValidationError
from .functions import get_payeer_api

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class NotifyView(generic.View):
    def post(self, request, *args, **kwargs):
        api = get_payeer_api()
        try:
            result = api.notify(request.POST)
        except PayeerValidationError as exc:
            logger.info(
                f"Payeer validation error for payment {exc.order_id}: {exc.msg}"
            )
            return HttpResponse(f"{exc.order_id}|error")
        except AlreadyPaid as exc:
            return HttpResponse(f"{exc.order_id}|success")

        result.payment.accept()
        logger.info(f"Successfully payeer paid {result.payment.id}")
        return HttpResponse(f"{result.raw_order_id}|success")
