import hashlib
import hmac
from urllib.parse import urljoin
from typing import Union
import requests
import pyjazzcash

class BaseClient(object):
    """
    Common class for sending request to server
    """
    version = "2.0"
    base_url = "https://sandbox.jazzcash.com.pk"
    hash_key = 'pp_SecureHash'
    integrity_salt, merchant_id, merchant_password = None, None, None

    def __init__(self, *, integrity_salt=None, merchant_id=None, merchant_password=None) -> None:
        self.address = "{0}/ApplicationAPI/API/{1}/".format(self.base_url, self.version)
        object.__setattr__(self, "integrity_salt", integrity_salt)
        object.__setattr__(self, "merchant_id", merchant_id)
        object.__setattr__(self, "merchant_password", merchant_password)
        self.integrity_salt = integrity_salt
        self.merchant_id = merchant_id
        self.merchant_password = merchant_password

    @classmethod
    def get_integrity_salt(cls):
        return cls.integrity_salt if cls.integrity_salt else pyjazzcash.integrity_salt

    @classmethod
    def get_merchant_id(cls):
        return cls.merchant_id if cls.merchant_id else pyjazzcash.merchant_id

    @classmethod
    def get_merchant_password(cls):
        return cls.merchant_password if cls.merchant_password else pyjazzcash.merchant_password

    @classmethod
    def get_request_data_hash(cls, data):
        """

        """
        # Alphabetical order of keys
        empty_removed = dict((k, v) for k, v in data.items() if v)

        # remove hash key
        if cls.hash_key in empty_removed:
            del empty_removed[cls.hash_key]
        # insert common attributes
        empty_removed["pp_MerchantID"] = cls.get_merchant_id()
        empty_removed["pp_Password"] = cls.get_merchant_password()
        values = list(v for k, v in sorted(empty_removed.items()))
        integrity_salt = cls.get_integrity_salt()
        values.insert(0, integrity_salt)
        plaintext = '&'.join(values)
        secure_hash = hmac.new(
            integrity_salt.encode('utf-8'), msg=plaintext.encode('utf-8'), digestmod=hashlib.sha256
        ).hexdigest().upper()
        return secure_hash

    def send_request(
            self, method: str, resource: str, **kwargs: dict
    ) -> Union[dict, list]:
        """
        Fetch `resource` from a Node
        Return response as Python object
        """
        url = urljoin(self.address, resource)
        kwargs['data'][self.hash_key] = self.get_request_data_hash(kwargs['data'])
        print(url)
        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()
