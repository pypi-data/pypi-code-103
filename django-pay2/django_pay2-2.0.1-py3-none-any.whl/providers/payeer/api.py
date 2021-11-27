import decimal
import hashlib

import requests

from django_pay2.models import Payment
from django_pay2.payment_methods import PaymentRedirect

from .exceptions import AlreadyPaid, PayeerError, PayeerValidationError


class PayeerApi:
    url = "https://payeer.com/ajax/api/api.php"

    def __init__(
        self,
        account: str,
        api_id: str,
        api_password: str,
        secret_key: str,
        shop_id: str,
    ):
        self.account = account
        self.api_id = (api_id,)
        self.api_password = api_password
        self.secret_key = secret_key
        self.shop_id = shop_id

    def create_payment(
        self, order_id: str, amount: decimal.Decimal, currency: str, desc: str
    ) -> str:
        response = requests.post(
            self.url,
            {
                "account": self.account,
                "apiId": self.api_id,
                "apiPass": self.api_password,
                "action": "invoiceCreate",
                "m_shop": self.shop_id,
                "m_orderid": order_id,
                "m_amount": float(amount),
                "m_curr": currency,
                "m_desc": desc,
            },
        )
        response.raise_for_status()
        response_data = response.json()
        if not response_data["success"]:
            raise PayeerError(response_data["errors"])
        return PaymentRedirect(response_data["url"])

    def notify(self, data):
        try:
            request = PayeerNotifyRequest(data)
        except (ValueError, TypeError, decimal.ConversionSyntax):
            raise PayeerValidationError("Invalid data format")
        try:
            payment = Payment.objects.get(id=request.order_id)
        except Payment.DoesNotExist:
            raise PayeerValidationError("Payment does not exist", request.order_id)
        if payment.status != Payment.StatusType.PENDING:
            raise AlreadyPaid(request.order_id)
        if payment.amount != request.amount:
            raise PayeerValidationError("Amounts are not equal", request.order_id)
        if request.sign != self._calculate_sign(request):
            raise PayeerValidationError("Incorrect sign", request.order_id)
        return PayeerNotifyResult(payment, request.status, request.order_id)

    def _calculate_sign(self, notify_request: "PayeerNotifyRequest"):
        hash_list = [
            notify_request.operation_id,
            notify_request.operation_ps,
            notify_request.operation_date,
            notify_request.operation_pay_date,
            notify_request.shop,
            notify_request.order_id,
            notify_request.amount,
            notify_request.currency,
            notify_request.desc,
            notify_request.status,
            self.secret_key,
        ]
        hash_list = [str(s) for s in hash_list]
        return hashlib.sha256(":".join(hash_list).encode("utf-8")).hexdigest().upper()


class PayeerNotifyRequest:
    def __init__(self, raw_data: dict):
        self.operation_id = raw_data.get("m_operation_id")
        self.operation_ps = raw_data.get("m_operation_ps")
        self.operation_date = raw_data.get("m_operation_date")
        self.operation_pay_date = raw_data.get("m_operation_pay_date")
        self.shop = raw_data.get("m_shop")
        self.order_id = raw_data.get("m_orderid")
        self.amount = decimal.Decimal(raw_data.get("m_amount"))
        self.currency = raw_data.get("m_curr")
        self.desc = raw_data.get("m_desc")
        self.status = raw_data.get("m_status")
        self.sign = raw_data.get("m_sign")


class PayeerNotifyResult:
    def __init__(self, payment, status, raw_order_id):
        self.payment = payment
        self.status = status
        self.raw_order_id = raw_order_id
