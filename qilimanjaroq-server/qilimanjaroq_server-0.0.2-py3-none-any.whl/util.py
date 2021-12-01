from base64 import urlsafe_b64encode, urlsafe_b64decode
import json
from typing import Any


def base64url_encode(payload) -> str:
    if isinstance(payload, dict):
        payload = json.dumps(payload)
    if not isinstance(payload, bytes):
        payload = payload.encode('utf-8')
    return urlsafe_b64encode(payload).decode('utf-8')


def base64url_decode(encoded_data: str) -> Any:
    return json.loads(urlsafe_b64decode(encoded_data).decode('utf-8'))
