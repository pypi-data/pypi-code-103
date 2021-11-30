import uuid
from datetime import datetime

import pytest

from monite.services.api_user_settings.schemas import (
    ApiUserResponseSchema,
    CreateSettings,
)

GOOD_PAYLOAD = {
    "entity_users": {"userpics": {"previews": [{"width": 200, "height": 200}], "min_width": 200, "min_height": 200}}
}


@pytest.mark.asyncio
def test_api_user_settings_schemas():
    create = CreateSettings(**GOOD_PAYLOAD)
    resp = ApiUserResponseSchema(
        **{
            "settings": GOOD_PAYLOAD,
            "updated_at": datetime.now(),
            "created_at": datetime.now(),
            "name": "lala",
            "status": "active",
            "id": uuid.uuid4(),
        }
    )

    assert isinstance(create.dict(), dict)
    assert isinstance(resp.dict(), dict)
