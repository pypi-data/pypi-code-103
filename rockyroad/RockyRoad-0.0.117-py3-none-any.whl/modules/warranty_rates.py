from .module_imports import *


@headers({"Ocp-Apim-Subscription-Key": key})
class Rates(Consumer):
    """Inteface to Warranties Rates resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url
        super().__init__(base_url=Resource._base_url, *args, **kw)

    @returns.json
    @get("warranties/rates")
    def list(
        self,
        uid: Query(type=str) = None,
        dealer_account: Query(type=str) = None,  # remove after no longer in use
        daaler_account_uid: Query(type=str) = None,  # remove after no longer in use
        dealer_branch_uid: Query(type=str) = None,
    ):
        """This call will return detailed waranty rate information for the specified criteria."""

    @returns.json
    @delete("warranties/rates")
    def delete(self, uid: Query(type=str)):
        """This call will delete the warranty rates for the specified uid."""

    @returns.json
    @json
    @post("warranties/rates")
    def insert(self, warrantyRates: Body):
        """This call will create warranty rates with the specified parameters."""

    @returns.json
    @json
    @patch("warranties/rates")
    def update(self, warrantyRates: Body):
        """This call will update the warranty rates with the specified parameters."""