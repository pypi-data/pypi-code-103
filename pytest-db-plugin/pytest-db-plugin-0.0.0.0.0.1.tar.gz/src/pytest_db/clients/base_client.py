from abc import ABC, abstractmethod
import pytest
import subprocess
from ..logger import logger
from ..utils import exec_and_capture_output


class FailedUpload(Exception):
    pass


class DbClient(ABC):
    def __init__(self, config, *, raise_upon_failure=False):
        """
        DB Client that collects the data from each test and then uploads it.

        Args:
            config (dict)

        Kwargs:
            raise_upon_failure (bool)
        """
        self._config = config
        self._logger = logger
        self._data = []
        self._raise_upon_failure = raise_upon_failure

    def _get_config_sources(self):
        data = {}

        data.update(self._config.get("additional-data", {}).get("consts", {}))

        python_commands = self._config.get("additional-data", {}).get("python", {})
        data.update(
            {
                key: exec_and_capture_output(command)
                for key, command in python_commands.items()
            }
        )

        bash_commands = self._config.get("additional-data", {}).get("bash", {})
        data.update(
            {
                key: subprocess.check_output(
                    command, shell=True, stderr=subprocess.STDOUT
                ).decode()
                for key, command in bash_commands.items()
            }
        )

        return data

    def collect(self, report):
        # longreprtext is only not-None if the test has failed
        sources = {
            "text": report.longreprtext or report.capstdout,
        }

        sources.update(self._get_config_sources())

        filtered = {k: v for k, v in sources.items() if v}
        self._data = filtered

    @abstractmethod
    def _upload(self):
        pass

    def upload(self):
        try:
            self._upload()
        except FailedUpload as e:
            if self._raise_upon_failure:
                raise
            self._logger.warning("upload to db failed")

    @pytest.hookimpl(tryfirst=True, hookwrapper=True)
    def pytest_runtest_makereport(self, item, call):
        outcome = yield
        report = outcome.get_result()

        if report.when == "call":
            self.collect(report)
            self.upload()


class UrlClient(DbClient):
    """
    Uploads each document to a DB using a url (can also be a DB hosted on
    localhost)
    """

    def __init__(self, config, url, *, raise_upon_failure=False):
        """
        DB Client that collects the data from each test and then uploads it.

        Args:
            config (dict)
            url (str)

        Kwargs:
            raise_upon_failure (bool)
        """
        super().__init__(config, raise_upon_failure=raise_upon_failure)
        self._url = url

    @abstractmethod
    def connect(self):
        pass

    def upload(self):
        self.connect()
        super().upload()
