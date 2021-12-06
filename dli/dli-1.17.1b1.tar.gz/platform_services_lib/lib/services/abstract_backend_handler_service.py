import abc
from typing import List
from cachetools import TTLCache
import logging

try:
    # these are only present for services, not for the SDK, and we do not wish to impose these in requirements.txt
    from pymemcache import HashClient
except ModuleNotFoundError:
    pass

logger = logging.getLogger(__name__)


class AbstractBackendDatasetHandler:
    __metaclass__ = abc.ABCMeta

    def __init__(
            self,
            ttl_cache: TTLCache,
            hash_client: 'HashClient',
    ):
        """
        Constructor.

        :param ttl_cache: tbc
        :param hash_client: Used for caching responses from S3.
        """
        logger.debug('AbstractHandler constructor')
        self.hash_client = hash_client
        self.ttl_cache = ttl_cache

    @abc.abstractmethod
    def handle(self, dataset):
        """
        lists each item in the dataset from the backend storage subsystem in terms of a virtual file handle,
        eg. S3File/ServiceIO
        """
        pass

    @abc.abstractmethod
    def get_assumed_role_session(self, dataset):
        """ assumes any credentials needed by the handler to access the dataset on the backend storage subsystem """
        pass

    @abc.abstractmethod
    def list(self, accessible_datasets: List, organisation_shortcode: str, args, method_name: str):
        """
        listing of the dataset from the backend storage subsystem.
        We do not want to be prescriptive here over the return type, this could be
        - a list of s3 file paths
        - a dictionary of contents, prefixes
        - a list of s3 file paths and sizes

        """
        pass