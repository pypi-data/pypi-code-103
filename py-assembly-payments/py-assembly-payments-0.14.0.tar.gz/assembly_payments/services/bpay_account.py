from assembly_payments.services.base import BaseService
from assembly_payments.types import User, BPayAccount, BPayAccountRequest


class BPayAccountService(BaseService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.endpoint = "/bpay_accounts"

    def get(self, bpay_account_id):
        response = self._execute(
            BPayAccountService.GET, f"{self.endpoint}/{bpay_account_id}"
        )
        return BPayAccount(**response["bpay_accounts"])

    def get_user(self, bpay_account_id):
        response = self._execute(
            BPayAccountService.GET, f"{self.endpoint}/{bpay_account_id}/users"
        )
        return User(**response["users"])

    def create(self, **kwargs):
        data = BPayAccountRequest(**kwargs)
        response = self._execute(
            BPayAccountService.POST, self.endpoint, data=data.dict()
        )
        return BPayAccount(**response["bpay_accounts"])

    def delete(self, bpay_account_id):
        self._execute(BPayAccountService.DELETE, f"{self.endpoint}/{bpay_account_id}")
