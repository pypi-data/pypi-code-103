from django.http import HttpResponse, QueryDict
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.csrf import csrf_exempt

from .api import get_api
from .serializers import CoinPaymentsApproveSerializer


@method_decorator(csrf_exempt, "dispatch")
class CoinPaymentsNotifyView(generic.View):
    def post(self, request, *args, **kwargs):
        body = request.body
        encoding = request.encoding if request.encoding is not None else "utf-8"
        decoded_body = body.decode(encoding)
        expected_hmac = get_api().calculate_ipn_hmac(decoded_body)
        if request.META.get("HTTP_HMAC") != expected_hmac:
            return self.ipn_error("HMAC signatures do not match")

        data = QueryDict(decoded_body)
        serializer = CoinPaymentsApproveSerializer(data=data)
        if not serializer.is_valid():
            return self.ipn_error("Validation error")
        payment = serializer.validated_data["invoice"]
        payment.accept()
        return HttpResponse("IPN OK")

    def ipn_error(self, message):
        return HttpResponse(f"IPN Error: {message}")
