from datetime import datetime

import pytest

from monite.services.entity_user_tokens.schemas import CreateTokenResponse


@pytest.mark.asyncio
def test_create_token_response():
    scheme = CreateTokenResponse(token="some string", expiration_in=datetime.now())

    assert isinstance(scheme.dict(), dict)
