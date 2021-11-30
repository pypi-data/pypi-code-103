import uuid
from datetime import datetime

import pytest

from monite.services.reconciliation.schemas import (
    PaginationResponse,
    ReconciliationRequest,
    ReconciliationResponse,
)


@pytest.mark.asyncio
def test_reconciliation_request():
    scheme = ReconciliationRequest(
        entity_id=uuid.uuid4(),
        payment_object_type="some string",
        payment_object_id=uuid.uuid4(),
        related_object_type="payable",
        related_object_id=uuid.uuid4(),
        was_created_by_user_name="Sergey",
        was_created_by_user_id="some external ID",
    )
    assert isinstance(scheme.dict(), dict)


@pytest.mark.asyncio
def test_reconciliation_pagination_response():
    response_scheme = ReconciliationResponse(
        id=uuid.uuid4(),
        oid=123,
        status="active",
        payment_object_type="some string",
        payment_object_id=uuid.uuid4(),
        related_object_type="payable",
        related_object_id=uuid.uuid4(),
        was_created_by_user_name="Sergey",
        was_created_by_user_id="some external ID",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    scheme = PaginationResponse(data=[response_scheme])

    assert isinstance(response_scheme.dict(), dict)
    assert isinstance(scheme.dict(), dict)
