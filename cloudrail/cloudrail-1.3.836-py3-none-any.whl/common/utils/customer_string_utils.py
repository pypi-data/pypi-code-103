from cloudrail.knowledge.utils.hash_utils import to_hashcode


class CustomerStringUtils:
    salt: str = None

    @classmethod
    def set_hashcode_salt(cls, salt):
        cls.salt = salt

    @classmethod
    def unset_hashcode_salt(cls):
        cls.salt = None

    @classmethod
    def to_hashcode(cls, value) -> str:
        if not cls.salt:
            raise Exception(f'cannot run to_hashcode on {value} before init salt')
        return to_hashcode(value, cls.salt)
