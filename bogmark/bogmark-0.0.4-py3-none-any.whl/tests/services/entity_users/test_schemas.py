import uuid
from datetime import datetime

import pytest

from monite.services.entity_users.schemas import (
    CreateEntityUserRequest,
    EntityUserResponse,
)


@pytest.mark.asyncio
def test_create_entity_user_request():
    scheme = CreateEntityUserRequest(
        role_id=uuid.uuid4(),
        login="some login",
        first_name="Sergey",
        last_name="S",
        title="Entity Name",
    )

    assert isinstance(scheme.dict(), dict)


@pytest.mark.asyncio
def test_entity_user_response():
    scheme = EntityUserResponse(
        id=uuid.uuid4(),
        role_id=uuid.uuid4(),
        login="some login",
        first_name="Sergey",
        last_name="S",
        api_user_id=uuid.uuid4(),
        status="active",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    assert isinstance(scheme.dict(), dict)
