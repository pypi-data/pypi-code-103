import uuid
from datetime import datetime

import pytest

from monite.services.entities.schemas import (
    CreateEntityRequest,
    CreateEntityResponse,
    CreateTokenResponse,
    PaginationResponse,
)
from monite.services.mailboxes.schemas import MailboxResponse


@pytest.mark.asyncio
def test_entities_schemas():
    create_entity_request = CreateEntityRequest(
        name="Entity name", type="person", country_code="DE", internal_id="optional string"
    )

    mailbox = MailboxResponse(
        id=123,
        entity_id=uuid.uuid4(),
        status="active",
        related_object_type="payable",
        mailbox_name="helo",
        mailbox_full_address="hello@monite.com",
        belongs_to_mailbox_domain_id=345,
    )

    create_entity_response = CreateEntityResponse(
        id=uuid.uuid4(),
        name="Entity name",
        type="person",
        country_code="DE",
        internal_id="optional string",
        status="active",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        mailboxes=[mailbox],
    )

    pagination_response_scheme = PaginationResponse(data=[create_entity_response])
    create_token_response_scheme = CreateTokenResponse(token="some string", expiration_in=datetime.now())

    assert isinstance(create_entity_request.dict(), dict)
    assert isinstance(create_entity_response.dict(), dict)
    assert isinstance(pagination_response_scheme.dict(), dict)
    assert isinstance(create_token_response_scheme.dict(), dict)
