"""Declares :class:`PKCSObject`."""
from ..algorithms import RSAPKCS1v15SHA256
from ..algorithms import RSAPKCS1v15SHA384
from ..algorithms import RSAPKCS1v15SHA512
from ..algorithms import RSAOAEPSHA256


class PKCSObject:
    capabilities = [
        RSAPKCS1v15SHA256,
        RSAPKCS1v15SHA384,
        RSAPKCS1v15SHA512,
        RSAOAEPSHA256
    ]
