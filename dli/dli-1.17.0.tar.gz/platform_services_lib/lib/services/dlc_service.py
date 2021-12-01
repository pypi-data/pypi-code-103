#
# Copyright (C) 2019 IHS Markit.
# All Rights Reserved
#
import logging
import operator
from typing import Optional, List, Dict
try:
    # these are only present for services, not for the SDK, and we do not wish to impose these in requirements.txt
    from pymemcache.client.hash import HashClient
    from injector import inject
except ModuleNotFoundError:
    # set up an Identity decorator for @inject
    def inject(function): # type: ignore
        def wrapper(*args, **kwargs):
            return function(*args, *kwargs)
        return wrapper

from ..adapters.filter_adapters import DLCFilterAdapter
from ..providers.memcache_provider import memcached_method
from ..providers.catalogue_provider import JWTDlcClient
from ..services.abstract_external_service import ExternalService

logger = logging.getLogger(__name__)


class DlcService(ExternalService):
    """
    Data Lake interface service, for interfacing
    with said interface.

    TODO Remove duplication of code between this and
    JWTDlcClient. The JWTDlcClient should ONLY be responsible
    for authentication and connection pooling. This class
    should be repsonsible for implementation of high level
    interfacing with the interface component.
    """
    @inject
    def __init__(
        self,
        dlc_session: JWTDlcClient,
        hash_client: 'HashClient',
    ):
        logger.debug('Init DlcService')
        self.dlc_session = dlc_session
        self.hash_client = hash_client

    @memcached_method(cache_getter=operator.attrgetter('hash_client'),)
    def get_dataset_for_shortcode(
        self, jwt: str, dataset_shortcode: str,
        organisation_short_code: Optional[str] = None,
    ) -> dict:
        # convert the dataset short code to org
        return self.dlc_session.get(
            f"/__api_v2/by_short_code/dataset/{dataset_shortcode}/",
            params={
                # WARNING! This endpoint as of 30-06-2021 is case sensitive. We have raised
                # ticket DL-7020 for the Catalogue team to make their filter case insensitive.
                'organisation_short_code': organisation_short_code
            },
            hooks=self._make_hook('No dataset for shortcode.')
        ).json()['data']

    @memcached_method(cache_getter=operator.attrgetter('hash_client'),)
    def get_datasets_in_organisation(
        self,
        jwt: str,
        organisation_short_code: str,
        location_type: str = 's3',
        shortcode_startswith: Optional[str] = None,
    ) -> List[dict]:
        """
        Only returns datasets the user can access (by checking the `location`
        field).

        :param jwt: SECURITY. Used to make caching specific to the user. Must be present.
        :param organisation_short_code:
        :param location_type:
        :param shortcode_startswith:
        :return:
        """

        """
        Only returns datasets the user can access (by checking the `location`
        field is not None).

        :param organisation_id:
        :param location_type:
        :param shortcode_startswith:
        :return:
        """

        filters = DLCFilterAdapter([
            # Use ilike to avoid case issues with Catalogue (vs hive style all lowercase).
            # The uniqueness constraint for creating an organisation short code in Catalogue is
            # to check for lowercase e.g. `ihsmarkit`
            # and they store in the database as mixed-case `IHSMarkit`
            # and then the search is against the case sensitive `IHSMarkit`.
            ('organisation_short_code', 'ilike', organisation_short_code),
            ('has_access', 'eq', 'True')
        ])

        if shortcode_startswith:
            filters.append(
                ('short_code', 'startswith', shortcode_startswith)
            )

        params = filters.to_params()
        # Crude substitute for pagination
        params['page_size'] = '5000'

        dataset_response = self.dlc_session.get(
            '/__api_v2/datasets/',
            params=params,
            hooks=self._make_hook('No datasets in organisation.')
        ).json()

        return [
            dataset for dataset in dataset_response['data']
            # Filter on location type (take the first key only and check that this matches the location_type (??))
            if 'location' in dataset['attributes'] and next(
                iter(
                    dataset['attributes']['location'].keys()
                ),
                ''
            ).lower() == location_type
        ]

    def get_dataset(self, dataset_id: str) -> Dict:
        # todo -- add JWT arg (to be able to cache) and cache
        """
        Security: you cannot cache this at the moment because the JWT
        is not a parameter on this function.
        :param dataset_id:
        :return:
        """
        url = f'/__api_v2/datasets/{dataset_id}/'
        logger.debug(
            f"get_dataset - dataset_id '{dataset_id}'",
            extra={'url': url, 'dataset_id': dataset_id}
        )
        response = self.dlc_session.get(
            url,
            hooks=self._make_hook(f'Dataset {dataset_id} not found')
        )
        return response.json()['data']

    def get_datafile(self, datafile_id: str) -> dict:
        # todo -- add JWT arg (to be able to cache) and cache
        logger.debug(f"get_datafile - datafile_id '{datafile_id}'")
        return self.dlc_session.get(
            f'/__api/datafiles/{datafile_id}/',
            hooks=self._make_hook('Datafile {datafile_id} not found')
        ).json()