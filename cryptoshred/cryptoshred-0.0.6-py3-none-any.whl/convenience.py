from functools import partial
from typing import Any, List

from multiprocessing.pool import ThreadPool as Pool
import json
from json import JSONDecodeError
from cryptoshred.backends import KeyBackend

from cryptoshred.entities import CryptoContainer

import logging

log = logging.getLogger()


def find_and_decrypt(key_backend: KeyBackend, x: Any) -> Any:
    log.info("Entering find and decrypt")
    log.debug(f"Working on:{x}")

    if type(x) is dict:
        log.debug("Identified Dict")
        if "enc" not in x.keys():
            # Increases performance by about 1/3
            for key, value in x.items():
                x[key] = find_and_decrypt(key_backend, value)
            return x

        try:
            log.debug("Looking for crypto container")
            cc: CryptoContainer[str] = CryptoContainer(
                **x, key_backend=key_backend  # type:ignore
            )
            log.debug("Found")
            try:
                x = json.loads(cc.plain())
            except JSONDecodeError:
                x = cc.plain()
                log.debug(f"Plain value: {x}")
            return x
        except Exception as e:  # noqa: E722
            log.debug(f"Not a crypto container. Identification failed with: {e}")
            for key, value in x.items():
                x[key] = find_and_decrypt(key_backend, value)
            return x

    elif type(x) is list:
        log.debug("Identified List")
        for idx, a in enumerate(x):
            x[idx] = find_and_decrypt(key_backend, a)
        return x

    else:
        log.debug("Identified Leaf Node")
        return x


def find_and_decrypt_in_dict(input: List[Any], key_backend: KeyBackend) -> Any:
    """
    Used internally to parse through a valid json list and find crypto
    containers which will than be decrypted. This function still needs a lot of tuning
    for it to be as efficient as possible. Currently it works well on smallish datasets,
    but if you bring long lists, also bring time.

    Args:
        input (List[Any]): The json object do inspect
        key_backend (KeyBackend): The key backend
    """

    with Pool(10) as p:  # TODO: Currently limited by boto. Maybe This can be increased
        res = p.map(partial(find_and_decrypt, key_backend), input)

    return res
