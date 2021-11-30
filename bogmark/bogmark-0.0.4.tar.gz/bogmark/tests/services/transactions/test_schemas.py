import uuid
from datetime import datetime

import pytest

from monite.services.transactions.schemas import (
    CreateTransactionRequest,
    PaginationResponse,
    TransactionResponse,
)


@pytest.mark.asyncio
def test_create_transaction_request():
    scheme = CreateTransactionRequest(
        currency="EUR",
        amount=100000000000,
        description="some description",
        transaction_date=datetime.now(),
        transaction_date_utc=datetime.now(),
        internal_api_partner_transaction_id="some string",
        card_details_string="some string",
        entity_bank_id="bank ID",
        entity_account_id="account ID",
        counterpart_bank_id="counterpart bank ID",
        counterpart_account_id="counterpart account ID",
        was_created_by_user_name="Sergey",
        was_created_by_user_id="some external ID",
    )
    assert isinstance(scheme.dict(), dict)


@pytest.mark.asyncio
def test_transactions_pagination_response():
    transaction_response = TransactionResponse(
        id=uuid.uuid4(),
        status="active",
        currency="EUR",
        amount=100000000000,
        description="some description",
        transaction_date=datetime.now(),
        transaction_date_utc=datetime.now(),
        internal_api_partner_transaction_id="some string",
        card_details_string="some string",
        entity_bank_id="bank ID",
        entity_account_id="account ID",
        counterpart_bank_id="counterpart bank ID",
        counterpart_account_id="counterpart account ID",
        was_created_by_user_name="Sergey",
        was_created_by_user_id="some external ID",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    scheme = PaginationResponse(data=[transaction_response])

    assert isinstance(transaction_response.dict(), dict)
    assert isinstance(scheme.dict(), dict)
