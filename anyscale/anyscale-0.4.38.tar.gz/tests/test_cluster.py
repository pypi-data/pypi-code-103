from unittest.mock import Mock, patch

import click
import pytest

from anyscale.api import get_api_client
from anyscale.cluster import get_job_submission_client_cluster_info


@pytest.mark.parametrize(
    "mock_sessions_return_value",
    [
        Mock(results=[]),
        Mock(
            results=[Mock(host_name="mock_host_name", access_token="mock_access_token")]
        ),
    ],
)
@pytest.mark.parametrize("create_cluster_if_needed", [True, False])
def test_get_job_submission_client_cluster_info(
    mock_sessions_return_value: Mock, create_cluster_if_needed: bool
):
    mock_project_definition = Mock()
    mock_project_definition.root = "/some/directory"
    mock_load_project_or_throw = Mock(return_value=mock_project_definition)

    mock_get_project_id = Mock(return_value="mock_project_id")
    with patch.multiple(
        "anyscale.api", load_credentials=Mock(return_value="fake_credentials")
    ):
        mock_api_client = get_api_client()
    mock_api_client.get_user_info_api_v2_userinfo_get = Mock(
        return_value=Mock(result=Mock(id="mock_user_id"))
    )
    mock_api_client.list_sessions_api_v2_sessions_get = Mock(
        return_value=mock_sessions_return_value
    )

    class MockClientBuilder:
        def __init__(self, **kwargs):
            pass

        def _start_cluster_if_needed(self):
            return ("mock_project_id", "mock_cluster_name")

    with patch.multiple(
        "anyscale.cluster",
        load_project_or_throw=mock_load_project_or_throw,
        get_project_id=mock_get_project_id,
        ClientBuilder=MockClientBuilder,
    ):
        if len(mock_sessions_return_value.results) == 0:
            with pytest.raises(click.ClickException):
                get_job_submission_client_cluster_info(
                    "mock_cluster_name", create_cluster_if_needed
                )
        else:
            get_job_submission_client_cluster_info(
                "mock_cluster_name", create_cluster_if_needed
            )

    mock_api_client.list_sessions_api_v2_sessions_get.assert_called_once_with(
        project_id="mock_project_id", active_only=True, name="mock_cluster_name"
    )
