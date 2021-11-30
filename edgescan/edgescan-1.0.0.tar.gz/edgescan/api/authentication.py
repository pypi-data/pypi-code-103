from edgescan.errors import MissingCredentialsError

import os

DEFAULT_API_KEY = os.getenv('EDGESCAN_API_KEY')


def validate_api_key(key: str) -> str:
    if not key:
        raise MissingCredentialsError("An API key is required")
    return key
