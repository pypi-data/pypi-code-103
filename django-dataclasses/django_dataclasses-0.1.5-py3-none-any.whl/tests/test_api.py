import pytest

import django_dataclasses


@pytest.mark.parametrize("method_name", ["get", "post", "put", "patch", "delete"])
def test_http_methods(mocker, method_name):
    mock_api_view = mocker.patch("django_dataclasses.api._api_view", autospec=True)
    http_method = getattr(django_dataclasses, method_name)
    view = object()
    http_method(view)

    assert mock_api_view.call_args_list == [mocker.call(view, method_name.upper())]
