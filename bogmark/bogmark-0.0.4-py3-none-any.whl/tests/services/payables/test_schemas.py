from monite.services.payables.schemas import PayableResponseSchema


def test_payable_schema():
    scheme = PayableResponseSchema.validate(
        {
            "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "created_at": "2021-10-19T17:32:05.735Z",
            "updated_at": "2021-10-19T17:32:05.735Z",
            "entity_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "status": "active",
            "source_of_payable_data": "string",
            "currency": "EUR",
            "amount": 113,
            "description": "string",
            "due_date": None,
            "issued_at": None,
            "counterpart_bank_id": "string",
            "counterpart_account_id": "string",
            "counterpart_name": "string",
            "payable_origin": "upload",
            "was_created_by_external_user_name": "string",
            "was_created_by_external_user_id": "string",
            "file": {
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "created_at": "2021-10-19T17:32:05.735Z",
                "updated_at": "2021-10-19T17:32:05.735Z",
                "status": "active",
                "url": "string",
                "size": 2147483647,
                "mimetype": "string",
                "previews": [
                    {
                        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                        "created_at": "2021-10-19T17:32:05.735Z",
                        "updated_at": "2021-10-19T17:32:05.735Z",
                        "status": "active",
                        "url": "string",
                        "size": 2147483647,
                        "mimetype": "string",
                        "height": 2147483647,
                        "width": 2147483647,
                    }
                ],
            },
        }
    )

    assert isinstance(scheme.dict(), dict)
