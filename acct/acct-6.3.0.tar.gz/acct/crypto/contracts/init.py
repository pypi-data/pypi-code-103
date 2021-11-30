from typing import Tuple


def sig_generate_key(hub):
    ...


def sig_encrypt(hub, data, key) -> Tuple[str, str]:
    """
    Returns the encrypted data and the encryption key
    """


def sig_decrypt(hub, data, key):
    ...
