from dataclasses import dataclass


@dataclass
class PasswordHash:
    hash: str
    salt: str


class HashType:
    @staticmethod
    def process_hash_str(str_hash: str):
        spl = str_hash.split("$")
        return HashType(spl[2], spl[3])

    def hash_password(self, password) -> str:
        return self.get_hash_str(_hash=self.hash_func(password, self._hash.salt).hash)

    @staticmethod
    def hash_func(password: str, salt: str) -> PasswordHash:
        return PasswordHash(password, salt)

    def __init__(self, _hash: str, salt: str):
        self._hash = PasswordHash(hash=_hash, salt=salt)
        self.hash_str = self.get_hash_str()

    def is_equal(self, password: str) -> bool:
        return self.hash_password(password) == self.hash_str

    def change_password(self, new_password: str):
        self._hash = self.hash_func(new_password, self._hash.salt)
        self.hash_str = self.get_hash_str()

    def get_hash_str(self, hash_name=None, _hash=None, salt=None) -> str:
        return f"${self.hash_name if hash_name is None else hash_name}${self._hash.salt if salt is None else salt}${self._hash.hash if _hash is None else _hash}"
