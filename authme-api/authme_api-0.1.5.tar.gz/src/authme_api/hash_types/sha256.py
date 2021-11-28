from authme_api.hash_types import *
from hashlib import sha256


class SHA256(HashType):
    def __init__(self, _hash: str, salt: str):
        self.hash_name = "SHA"
        super().__init__(_hash, salt)

    @staticmethod
    def hash_func(password: str, salt: str) -> PasswordHash:
        _hash = sha256(
            sha256(password.encode()).hexdigest().encode() + salt.encode()
        ).hexdigest()
        return PasswordHash(_hash, salt)

    @staticmethod
    def process_hash_str(str_hash: str):
        spl = str_hash.split("$")
        return SHA256(spl[3], spl[2])
