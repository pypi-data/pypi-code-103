import pytest

from monite.structures.context import get_current_request_id, set_current_request_id


def test_rid_context_var():
    rid = get_current_request_id()
    assert rid == "default_request_id"

    with pytest.raises(TypeError):
        set_current_request_id(1)
    set_current_request_id("666")

    rid = get_current_request_id()
    assert rid == "666"
