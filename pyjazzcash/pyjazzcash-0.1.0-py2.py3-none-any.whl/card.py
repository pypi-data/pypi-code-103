from pyjazzcash.base_client import BaseClient


class Card(BaseClient):
    """

    """
    @classmethod
    def check3dsEnrollment(self):
        """

        """
        data = {
            "pp_IsRegisteredCustomer": "No",
            "pp_CustomerID": "test",
            "pp_CustomerEmail": "test@test.com",
            "pp_CustomerMobile": "03222852628",
            "pp_TxnType": "AUTH",
            "pp_TxnRefNo": "T202111131520121",
            "pp_Amount": "111",
            "pp_TxnCurrency": "PKR",
            "pp_TxnDateTime": "20211113152106",
            "pp_TxnExpiryDateTime": "20211114152106",
            "pp_BillReference": "billRef",
            "pp_Description": "Description of transaction",
            "pp_CustomerCardNumber": "5123456789012346",
            "pp_CustomerCardExpiry": "1222",
            "pp_CustomerCardCvv": "123",
        }
        return self().send_request('POST', 'Purchase/Check3DsEnrollment', data=data)
