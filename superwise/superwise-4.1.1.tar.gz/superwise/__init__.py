""" root for supwrwise pacakge, set logger and load config"""
import json
import logging
import os
import pkgutil

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

vcr_log = logging.getLogger("vcr")
vcr_log.setLevel(logging.ERROR)

from superwise.config import Config
from superwise.controller.client import Client
from superwise.controller.task import TaskController
from superwise.controller.version import VersionController
from superwise.controller.role import RoleController
from superwise.controller.dataentity import DataEntityController
from superwise.controller.transaction import TransactionController
from superwise.controller.segment import SegmentController


class Superwise:
    """ Superwise class - main class for superwise package """

    def __init__(
        self,
        client_id=None,
        secret=None,
        _rest_client=None,
        email=None,
        password=None,
        _fegg_url=None,
        _superwise_host=None,
    ):
        """
        constructer for Superwise class

        :param client_id:
        :param secret:
        :param _rest_client: inject rest client if needed (allow mocking of rest api calls)
        """

        self.logger = logger
        if _superwise_host:
            Config.SUPERWISE_HOST = _superwise_host
        if _fegg_url:
            Config.FRONTEGG_URL = _fegg_url
        client_id = client_id or os.environ.get("SUPERWISE_CLIENT_ID")
        secret = secret or os.environ.get("SUPERWISE_SECRET")
        if email and password:
            self.logger.info("login using user and password")
        elif secret is None or client_id is None:
            raise Exception("secret or email/password are mendatory fields")
        api_host = Config.SUPERWISE_HOST
        if not _rest_client:
            _rest_client = Client(client_id, secret, api_host, email, password)
        self.tenant_id = _rest_client.tenant_id
        self.task = TaskController(_rest_client, self)
        self.version = VersionController(_rest_client, self)
        self.role = RoleController(_rest_client, self)
        self.data_entity = DataEntityController(_rest_client, self)
        self.transaction = TransactionController(_rest_client, self)
        self.segment = SegmentController(_rest_client, self)
