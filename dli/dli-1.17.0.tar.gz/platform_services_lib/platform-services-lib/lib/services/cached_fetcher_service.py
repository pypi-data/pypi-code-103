import operator
from typing import List, Dict
from flask import current_app
try:
    # these are only present for services, not for the SDK, and we do not wish to impose these in requirements.txt
    from injector import inject
    from pymemcache import HashClient
except ModuleNotFoundError:
    # set up an Identity decorator for @inject
    def inject(function): # type: ignore
        def wrapper(*args, **kwargs):
            return function(*args, *kwargs)
        return wrapper
except:
    pass

import logging

from ..providers.oidc_provider import JWT
from ..services.abstract_backend_handler_service import AbstractBackendDatasetHandler
from ..services.view_exceptions import NotFound
from ..services.exceptions import ServiceException, InterfaceResourceUnavailable
from ..providers.memcache_provider import memcached_method
from ..services.dlc_service import DlcService
from ..services.identity_service import IdentityService

logger = logging.getLogger(__name__)


class CachedFetcherService:
    @inject
    def __init__(
        self,
        dlc_service: DlcService,
        identity_service: IdentityService,
        hash_client: 'HashClient'
    ):
        logger.debug('Init CachedFetcherService')
        self.dlc_service = dlc_service
        self.identity_service = identity_service
        self.hash_client = hash_client

    @memcached_method(cache_getter=operator.attrgetter('hash_client'), )
    def list_objects_in_dataset(self, organisation_shortcode: str, args, method_name: str,
                                handler: AbstractBackendDatasetHandler) -> Dict:
        jwt = current_app.injector.get(JWT)
        datasets: List[Dict] = self.dlc_get_accessible_datasets(
            jwt=jwt,
            organisation_shortcode=organisation_shortcode,
            key=args['Prefix']
        )
        return handler.list(datasets, organisation_shortcode, args, method_name)

    def dlc_get_accessible_datasets(
            self, jwt: str, organisation_shortcode: str, key: str = '',
    ) -> List[Dict]:
        """
        Only returns datasets the user can access (by checking visible
        organisations and the dataset's `location` field).

        Raises if no matching visible organisation for the user.

        SECURITY Do not cache the result of this function, there is too much logic here and
        not all of the parameters (such as `key`) should be in all of the caches.
        Instead each call this function makes is cached.

        :param jwt: SECURITY. Used to make caching specific to the user. Must be present.
        :param organisation_shortcode:
        :param key: If empty we need to list all the datasets.
        If partial with need to match the visible datasets starting with
        the short code.
        If full we need to list files inside dataset.
        If full with path we need to list files inside plus that path.
        :return: List of datasets the user can access.
        """

        # Raises if no matching visible organisation for the user.
        # self.get_organisation(
        #     jwt=jwt,  # Needed so that cache value is secured against the JWT.
        #     organisation_shortcode=organisation_shortcode,
        # )

        # Now get the dataset.

        # Some example keys
        # ''                          - Empty
        # 'data_s'                    - Possibly Incomplete
        # 'data_set1'                 - Complete dataset
        #                                 but search for other paths
        # 'data_set1/'                - Complete dataset
        # 'data_set1/path/to/file'    - Dataset with path

        # If empty we need to list all the datasets.
        # If partial with need to match the visible datasets starting with
        # the short code.
        # If full we need to list files inside dataset.
        # If full with path we need to list files inside plus that path.

        # Sanity check.
        if key and key.lower().startswith('s3:'):
            raise ServiceException(
                details='You have asked for a key that begins with `s3:`, which is an '
                        'absolute path. Please replace this with key that is a relative path. '
                        'The key should with the dataset short code '
                        'e.g. key=example-dataset-short-code   or  '
                        'key=example-dataset-short-code/as_of_date=2020-01-01 '
            )

        # noinspection PyBroadException
        try:
            func = self.dlc_service.get_datasets_in_organisation
            args = {
                "jwt": jwt,
                "organisation_short_code": organisation_shortcode,
            }

            if not key:
                # Empty key is the simplest case - we just get given /ORGANISATION
                return func(**args)

            dataset_shortcode, has_prefix_following, _ = key.partition('/')
            if not has_prefix_following:
                # We get given /ORGANISATION/DATASET
                return func(**args, shortcode_startswith=dataset_shortcode)
            else:
                # We get given /ORGANISATION/DATASET/...
                dataset = [self.dlc_service.get_dataset_for_shortcode(**args, dataset_shortcode=dataset_shortcode)]
                return dataset

        except InterfaceResourceUnavailable:
            # This means there's no match to return
            logger.debug(
                'No orgs found for short_code.',
                extra={'organisation_shortcode': organisation_shortcode}
            )
            return []
        except Exception:
            logger.exception('Unhandled exception in dlc_get_accessible_datasets')
            return []

    @memcached_method(cache_getter=operator.attrgetter('hash_client'), )
    def dlc_get_organisation(self, jwt: str, organisation_shortcode: str) -> dict:
        """
        Raises if:
        organisation_shortcode does not exist
        or the organisation is not visible to the user.

        :param jwt: SECURITY. Used to make caching specific to the user. Must be present.
        :param organisation_shortcode:
        :return: An organisation dict.
        """
        try:
            logger.debug(
                'get_organisation',
                extra={
                    'organisation_shortcode': organisation_shortcode,
                }
            )
            organisations = self.dlc_get_visible_organisations(jwt=jwt)

            for org in organisations['data']:
                if org['attributes']['short_code'].lower() == organisation_shortcode.lower():
                    return org

            logger.warning(
                'Attempt to get non-existing or non-visible org',
                extra={'organisation_shortcode': organisation_shortcode}
            )

            raise NotFound('Organisation not found')
        except Exception as e:
            logger.error(e)
            return {}

    @memcached_method(cache_getter=operator.attrgetter('hash_client'), )
    def dlc_get_visible_organisations(self, jwt: str) -> dict:
        """
        Get visible organisations.

        :param jwt: SECURITY. Used to make caching specific to the user. Must be present,
        otherwise a different user can see the organisations of this user. This happened in a
        red alert where an external QA user was able to see the internal organisation.
        :return: An organisation dict of only the organisations that are visible to this user's
        JWT.
        """
        try:
            return self.identity_service.get_visible_organisations()
        except Exception as e:
            logger.error(e)
            return {}

    @memcached_method(cache_getter=operator.attrgetter('hash_client'), )
    def dlc_me(self, jwt: str) -> dict:
        try:
            return self.identity_service.me()
        except Exception as e:
            logger.error(e)
            return {}
