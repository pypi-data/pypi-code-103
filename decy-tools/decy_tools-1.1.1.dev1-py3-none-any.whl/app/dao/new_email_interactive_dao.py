from app.api.api_client import ApiClient
from app.utils.logger.logging_utils import get_logger
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit import PromptSession
from functools import cached_property
from json import dumps


class NewEmailCli:
    def __init__(self, logger=None):
        self._logger = logger or get_logger()
        self._first_name = None
        self._last_name = None
        self._acc_name = None

    @cached_property
    def _api_client(self):
        return ApiClient(logger=self._logger)

    @cached_property
    def _session(self):
        return PromptSession()

    @cached_property
    def _available_clients(self):
        return self._api_client.make_api_call("post", "/get_available_clients")

    def get_user_input(self):
        self._last_name = self._session.prompt("Enter Last Name: ", bottom_toolbar="Awaiting Last Name")
        self._first_name = self._session.prompt("Enter First Name: ", bottom_toolbar="Awaiting First Name")
        self._acc_name = self._session.prompt("Enter the account name: ", bottom_toolbar="Awaiting Account Name")

    @cached_property
    def _client(self):
        client_list = [client for client in self._available_clients]
        return self._session.prompt(
            "Enter a client: ",
            completer=WordCompleter(client_list),
            bottom_toolbar=str(
                "Start typing or press tab to see the "
                "available options. Use arrow keys, and "
                "press enter to select"
            ),
        )

    @cached_property
    def _client_id(self):
        return self._available_clients[self._client]

    @cached_property
    def _available_domains(self):
        return self._api_client.make_api_call(
            "post", "/get_available_domains", data=dumps({"client_id": self._client_id})
        )

    @cached_property
    def _domain(self):
        return self._session.prompt("Enter a domain: ", completer=WordCompleter(self._available_domains))

    def format_user_input(self):
        data = {
            "client": self._client,
            "fname": self._first_name,
            "lname": self._last_name,
            "username": self._acc_name,
            "domain": self._domain,
            "itg_client_id": self._client_id,
        }
        return dumps(data)

    def create_new_email(self):
        self._api_client.make_api_call("post", "/new_mail_user", data=self.format_user_input())

    def main(self):
        self.get_user_input()
        return self.create_new_email()
