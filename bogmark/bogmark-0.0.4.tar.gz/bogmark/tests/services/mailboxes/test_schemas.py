import uuid

import pytest

from monite.services.mailboxes.schemas import (
    DomainRequest,
    DomainResponse,
    DomainUpdateRequest,
)


@pytest.mark.asyncio
def test_mailbox_domain_request():
    scheme = DomainRequest(domain="monite.com", provider="mailgun")
    assert isinstance(scheme.dict(), dict)


@pytest.mark.asyncio
def test_mailbox_domain_update_request():
    scheme = DomainUpdateRequest(status="active")
    assert isinstance(scheme.dict(), dict)


@pytest.mark.asyncio
def test_mailbox_domain_response():
    scheme = DomainResponse(
        id=123,
        api_user_id=uuid.uuid4(),
        domain="monite.com",
        status="active",
        provider="mailgun",
        dns_records={"some": {"records": "here"}},
    )
    assert isinstance(scheme.dict(), dict)
