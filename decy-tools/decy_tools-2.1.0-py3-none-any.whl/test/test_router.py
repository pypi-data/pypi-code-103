from app.router.router import Router
from unittest.mock import patch, call


@patch("app.router.router.get_logger")
@patch("app.router.router.NewEmailCli")
def test_new_email_interactive(mock_cli, mock_logger):
    router = Router("asdf", "asdf")
    router.new_email_interactive()
    mock_cli.assert_has_calls([call(logger=mock_logger()), call().main()])


@patch("app.router.router.Router.new_email_interactive")
def test_switcher(mock_method):
    mock_method.return_value = "asdf"
    router = Router("asdf", "asdf")
    assert router._switcher == {"new-email-interactive": mock_method}


@patch("app.router.router.Router._switcher")
def test_run_workflow(mock_switcher):
    router = Router("asdf", "asdf")
    router.run_workflow()
    mock_switcher.assert_has_calls([call.get("asdf"), call.get()()])
