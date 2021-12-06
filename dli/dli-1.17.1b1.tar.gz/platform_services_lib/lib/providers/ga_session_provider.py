#
# Copyright (C) 2019 IHS Markit.
# All Rights Reserved
#

import dataclasses
from urllib.parse import urljoin
from requests.adapters import DEFAULT_POOLSIZE
from requests import Session
try:
    # these are only present for services, not for the SDK, and we do not wish to impose these in requirements.txt
    from injector import provider, singleton as singleton_scope
except ModuleNotFoundError:
    # set up an Identity decorator for @inject
    def provider(function):  # type: ignore
        def wrapper(*args, **kwargs):
            return function(*args, *kwargs)
        return wrapper

    def singleton_scope(function):  # type: ignore
        def wrapper(*args, **kwargs):
            return function(*args, *kwargs)

        return wrapper

from urllib3 import Retry
import logging

from ..providers.base_provider import BaseModule
from ..adapters.session_adapters import BaseAdapter


@dataclasses.dataclass
class Config:
    api_root: str
    # Defaults taken from the requests library were 10, 10. Under performance
    # tests with 250 concurrent users and 30 pods, 10 was not enough.
    pool_connections: int = DEFAULT_POOLSIZE
    pool_maxsize: int = DEFAULT_POOLSIZE
    # With retries, the total delay of around 32 seconds before a request is
    # deemed "an unrecoverable error"
    # https://urllib3.readthedocs.io/en/latest/reference/
    # urllib3.util.html#urllib3.util.retry.Retry
    max_retries: int = 5


class GAClient(Session):

    logger = logging.getLogger(__name__)

    def __init__(self, config):
        super().__init__()
        self.config = config

        adapter = BaseAdapter(
            pool_connections=self.config.pool_connections,
            pool_maxsize=self.config.pool_maxsize,
            # https://urllib3.readthedocs.io/en/latest/reference/
            # urllib3.util.html#urllib3.util.retry.Retry
            max_retries=Retry(
                total=self.config.max_retries,
                status=self.config.max_retries,
                # List of expected errors
                # https://developers.google.com/analytics/devguides/
                # reporting/core/v4/errors
                status_forcelist=[500, 502, 503, 504],
                method_whitelist=Retry.DEFAULT_METHOD_WHITELIST,
                backoff_factor=1,
            ),
            pool_block=True,
        )

        self.logger.debug(
            f"GAClient session mount prefix '{self.config.api_root}'"
        )
        self.mount(self.config.api_root, adapter)

    def request(self, method, url, *args, **kwargs):
        url = urljoin(self.config.api_root, url)
        return super().request(method, url, *args, **kwargs)


class GADependencyProvider(BaseModule):
    config_class = Config

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.session = GAClient(self.config)

    @singleton_scope
    @provider
    def ga_client(self) -> GAClient:
        return self.session
