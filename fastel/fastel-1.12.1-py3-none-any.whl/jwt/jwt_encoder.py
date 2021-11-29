import random
from typing import Any, Type

from .decode_static import prod_cert, stg_cert
from .jwt_payload import JWTPayloadBuilder
from .kms_encode import kms_encode as encode


class JWTEncoder:
    payload_builder_class: Type[JWTPayloadBuilder]
    stage: str = "stg"

    def __init__(self, client: Any) -> None:
        self.client = client

    def encode(self, user: Any) -> str:
        keys = stg_cert if self.stage == "stg" else prod_cert
        key = random.choice(keys["keys"])["kid"]
        builder = self.payload_builder_class(client=self.client, data=user)
        payload = builder.get_payload()
        encoded = encode(payload, key=key, headers={"kid": key})
        return encoded
