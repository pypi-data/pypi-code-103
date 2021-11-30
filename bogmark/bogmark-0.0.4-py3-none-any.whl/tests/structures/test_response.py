from monite.structures.response import MoniteJSONResponse


def test_json_response():
    resp = MoniteJSONResponse(
        status_code=200,
        media_type="application/json",
        content={"1": 1},
    )
    assert resp.as_dict() == {"1": 1}

    resp = MoniteJSONResponse(
        status_code=200,
        media_type="application/pdf",
        content={"1": 1},
    )
    assert resp.as_dict() == {}
    assert resp.is_ok
