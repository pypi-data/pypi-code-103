#
# Copyright (C) 2019 IHS Markit.
# All Rights Reserved
#
import dataclasses
import logging

from injector import provider, singleton as singleton_scope
from requests import Session
from urllib3 import Retry

from ..providers.base_provider import BaseModule
from ..adapters.session_adapters import DlcAdapter


@dataclasses.dataclass
class Config:
    api_root: str
    # Defaults taken from the requests library were 10, 10. Under performance
    # tests with 250 concurrent users and 30 pods, 10 was not enough.
    pool_connections: int = 20
    pool_maxsize: int = 20
    max_retries: int = 10


class JWTDlcClient(Session):

    logger = logging.getLogger(__name__)

    def __init__(self, config):
        super().__init__()
        self.config = config

        adapter = DlcAdapter(
            pool_connections=self.config.pool_connections,
            pool_maxsize=self.config.pool_maxsize,
            # https://urllib3.readthedocs.io/en/latest/reference/
            # urllib3.util.html#urllib3.util.retry.Retry
            max_retries=Retry(
                total=self.config.max_retries,
                status=self.config.max_retries,
                status_forcelist=[500, 502, 504],
                method_whitelist=Retry.DEFAULT_METHOD_WHITELIST,
                backoff_factor=1,
            ),
            pool_block=True,
        )

        self.logger.info(
            f"JWTDlcClient session mount prefix '{self.config.api_root}'"
        )
        self.mount(self.config.api_root, adapter)

    def request(self, method, url, *args, **kwargs):
        # url = urljoin(self.config.api_root, url) # this isnt going to work for a local case
        url = "".join([self.config.api_root, url])

        self.logger.debug(
            f'JWTDlcClient request using connection pool {url}',
            extra={'url': url}
        )

        return super().request(method, url, *args, **kwargs)


class JWTDependencyProvider(BaseModule):
    config_class = Config

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.session = JWTDlcClient(config=self.config)

    @singleton_scope
    @provider
    def auth_client(self) -> JWTDlcClient:
        return self.session

