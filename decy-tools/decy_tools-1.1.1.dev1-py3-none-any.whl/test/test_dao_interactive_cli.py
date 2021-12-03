from app.dao.new_email_interactive_dao import NewEmailCli
from unittest.mock import patch, call


@patch("app.dao.new_email_interactive_dao.ApiClient")
def test_api_client(mock_api_client):
    cli = NewEmailCli()
    api_client = cli._api_client
    mock_api_client.assert_called_once()


@patch("app.dao.new_email_interactive_dao.PromptSession")
def test_session(mock_session):
    cli = NewEmailCli()
    session = cli._session
    mock_session.assert_called_once()


@patch("app.dao.new_email_interactive_dao.ApiClient._logger")
@patch("app.dao.new_email_interactive_dao.ApiClient")
def test_available_clients(mock_api_client, mock_logger):
    mock_logger.return_value = True
    cli = NewEmailCli(logger=mock_logger)
    clients = cli._available_clients
    mock_api_client.assert_has_calls([call(logger=mock_logger), call().make_api_call("post", "/get_available_clients")])


@patch("app.dao.new_email_interactive_dao.NewEmailCli._session")
def test_get_user_input(mock_session):
    cli = NewEmailCli()
    cli.get_user_input()
    mock_session.assert_has_calls(
        [
            call.prompt("Enter Last Name: ", bottom_toolbar="Awaiting Last Name"),
            call.prompt("Enter First Name: ", bottom_toolbar="Awaiting First Name"),
            call.prompt("Enter the account name: ", bottom_toolbar="Awaiting Account Name"),
        ]
    )


@patch("app.dao.new_email_interactive_dao.WordCompleter")
@patch("app.dao.new_email_interactive_dao.NewEmailCli._session")
@patch("app.dao.new_email_interactive_dao.NewEmailCli._available_clients")
def test_client(mock_avail_clients, mock_session, mock_word_completer):
    cli = NewEmailCli()
    client = cli._client
    mock_avail_clients.assert_has_calls([call.__iter__()])
    mock_session.assert_has_calls(
        [
            call.prompt(
                "Enter a client: ",
                completer=mock_word_completer(),
                bottom_toolbar="Start typing or press tab to see the available options. Use arrow keys, and press enter to select",
            )
        ]
    )
    mock_word_completer.assert_has_calls([call([])])


@patch("app.dao.new_email_interactive_dao.NewEmailCli._client")
@patch("app.dao.new_email_interactive_dao.NewEmailCli._available_clients")
def test_client_id(mock_avail_clients, mock_client):
    mock_client.return_value = "mock client"
    cli = NewEmailCli()
    client_id = cli._client_id
    mock_avail_clients.assert_has_calls([call.__getitem__(mock_client)])


@patch("app.dao.new_email_interactive_dao.ApiClient._logger")
@patch("app.dao.new_email_interactive_dao.dumps")
@patch("app.dao.new_email_interactive_dao.NewEmailCli._client_id")
@patch("app.dao.new_email_interactive_dao.ApiClient")
def test_available_domains(mock_api_client, mock_client_id, mock_dumps, mock_logger):
    mock_logger.return_value = True
    mock_client_id.return_value = "asdf"
    client = NewEmailCli(logger=mock_logger)
    domains = client._available_domains
    mock_api_client.assert_has_calls(
        [call(logger=mock_logger), call().make_api_call("post", "/get_available_domains", data=mock_dumps())]
    )
    mock_dumps.assert_has_calls([call({"client_id": mock_client_id}), call()])


@patch("app.dao.new_email_interactive_dao.WordCompleter")
@patch("app.dao.new_email_interactive_dao.NewEmailCli._available_domains")
@patch("app.dao.new_email_interactive_dao.NewEmailCli._session")
def test_domain(mock_session, mock_available_domains, mock_wordcompleter):
    client = NewEmailCli()
    domain = client._domain
    mock_session.assert_has_calls([call.prompt("Enter a domain: ", completer=mock_wordcompleter())])
    mock_wordcompleter.assert_has_calls([call(mock_available_domains), call()])


@patch("app.dao.new_email_interactive_dao.dumps")
@patch("app.dao.new_email_interactive_dao.NewEmailCli._client")
@patch("app.dao.new_email_interactive_dao.NewEmailCli._domain")
@patch("app.dao.new_email_interactive_dao.NewEmailCli._client_id")
def test_format_user_input(mock_client, mock_domain, mock_client_id, patch_dumps):
    client = NewEmailCli()
    client.format_user_input()
    patch_dumps.assert_has_calls(
        [
            call(
                {
                    "client": mock_client_id,
                    "fname": None,
                    "lname": None,
                    "username": None,
                    "domain": mock_domain,
                    "itg_client_id": mock_client,
                }
            )
        ]
    )


@patch("app.dao.new_email_interactive_dao.ApiClient._logger")
@patch("app.dao.new_email_interactive_dao.ApiClient")
@patch("app.dao.new_email_interactive_dao.NewEmailCli.format_user_input")
def test_new_email(mock_input, mock_api_client, mock_logger):
    mock_input.return_value = "asdf"
    client = NewEmailCli(logger=mock_logger)
    client.create_new_email()
    mock_api_client.assert_has_calls(
        [call(logger=mock_logger), call().make_api_call("post", "/new_mail_user", data="asdf")]
    )


@patch("app.dao.new_email_interactive_dao.NewEmailCli.create_new_email")
@patch("app.dao.new_email_interactive_dao.NewEmailCli.get_user_input")
def test_main(mock_input, mock_new_email):
    client = NewEmailCli()
    client.main()
    mock_input.assert_called_once()
    mock_new_email.assert_called_once()
