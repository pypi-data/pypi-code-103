import os
import base64
from typing import Any, Union
from uuid import UUID, uuid4, uuid5
from dotenv import load_dotenv

from .logger.core import logger
from .validator.core import Validator


class Fur:
    def __init__(self) -> None:
        load_dotenv()

        self.secret = UUID(self.__get_env("FUR_VALIDATION_SECRET"))

    def __get_env(self, key, default=None) -> Union[str, None]:
        Validator.validate_str(key)

        if default is not None:
            Validator.validate_str(default)

        value = os.getenv(key)
        if not value:
            return default
        return value

    def __generate_seed(self) -> bytes:
        seed = uuid4().__str__().encode("ascii")

        return seed

    def __generate_name(self) -> str:
        seed = self.__generate_seed()
        name = base64.b64encode(seed).decode("ascii")

        return name

    def __generate_key(self, name=None) -> str:
        if not name:
            name = self.__generate_name()

        key = uuid5(namespace=self.secret, name=name).__str__()

        return key

    def generate_keyring(self) -> dict[str, Any]:
        name = self.__generate_name()
        key = self.__generate_key(name)

        keyring: dict[str, Any] = {"header": name, "key": key}

        return keyring
