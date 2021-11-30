import uuid

import pytest

from monite.services.api_users.schemas import (
    AuthSchema,
    AuthSchemaResponse,
    TokenSchemaResponse,
)


@pytest.mark.asyncio
def test_api_users_schemas():
    auth_schema = AuthSchema(user_id=uuid.uuid4(), secret="some secret text")
    token_schema = TokenSchemaResponse(token="token string", type="type string")
    scheme = AuthSchemaResponse(data=token_schema)

    assert isinstance(auth_schema.dict(), dict)
    assert isinstance(token_schema.dict(), dict)
    assert isinstance(scheme.dict(), dict)
