import uuid
from datetime import datetime

import pytest

from monite.services.roles.schemas import CreateRoleRequest, RoleResponse


@pytest.mark.asyncio
def test_create_role_request():
    scheme = CreateRoleRequest(name="role_name", permissions="{}")
    assert isinstance(scheme.dict(), dict)


@pytest.mark.asyncio
def test_role_response():
    scheme = RoleResponse(
        id=uuid.uuid4(),
        name="Role name",
        permissions=dict(),  # noqa
        status="active",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    assert isinstance(scheme.dict(), dict)
