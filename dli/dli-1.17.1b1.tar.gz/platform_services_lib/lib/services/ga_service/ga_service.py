#
# Copyright (C) 2019 IHS Markit.
# All Rights Reserved
#
import dataclasses
from urllib import parse
from os import environ
import requests
import logging
from flask import current_app
try:
    # these are only present for services, not for the SDK, and we do not wish to impose these in requirements.txt
    from injector import inject
except ModuleNotFoundError:
    # set up an Identity decorator for @inject
    def inject(function): # type: ignore
        def wrapper(*args, **kwargs):
            return function(*args, *kwargs)
        return wrapper
except:
    pass

from ..analytics_service.model import AnalyticsEvent
from ...providers.oidc_provider import JWT
from ...providers.ga_session_provider import GAClient
from ...services.cached_fetcher_service import CachedFetcherService


@dataclasses.dataclass
class Config:
    tracking_id: str = environ.get('GA_TID', '')
    ga_request_timeout: float = float(environ.get('GA_REQUEST_TIMEOUT', '60'))


class GoogleAnalyticsService:
    logger = logging.getLogger(__name__)

    __params_mapping = {
        'user_id': 'cd1',
        'organisation_id': 'cd2',
        'package_id': 'cd3',
        'dataset_id': 'cd4',
        'dictionary_id': 'cd5',
        'datafile_id': 'cd6',
        'name': 'cd7',
        'dataset_name': 'cd8',
        # This was done for the problem with PowerBi masking the first field. Do not remove.
        'user_id_again': 'cd9',
    }

    __ga_version_field = 'v'
    __ga_tracking_id_field = 'tid'
    __ga_type_field = 't'

    ga_unhandled_exception_message = \
        'Problem with sending analytics to Google. ' \
        'The user should be unaffected but developers should ' \
        'check we do not have a Google Analytics problem that ' \
        'is not related to the connection pool e.g. network ' \
        'connectivity.'

    @inject
    def __init__(
            self,
            ga_client: GAClient,
            config: Config,
            identity_service: CachedFetcherService,
    ):
        self._ga_client = ga_client
        self._config = config
        self.__identity_service = identity_service
        if not self._config.tracking_id:
            raise ValueError('GA Tracking ID has to be defined.')
        self._static_params = (
            (self.__ga_version_field, 1),
            (self.__ga_tracking_id_field, self._config.tracking_id),
            (self.__ga_type_field, 'event')
        )
        if not self._config.ga_request_timeout:
            raise ValueError('GA request timeout has to be defined.')

    def send_message(self, body):
        """
        :param body: url encoded payload to send to Google Analytics.
        :return: request
        """
        try:
            self._ga_client.post(
                '',
                data=body,
                timeout=self._config.ga_request_timeout
            )
        except ConnectionResetError:
            # https://stackoverflow.com/questions/20568216/python-handling-socket-error-errno-104-connection-reset-by-peer
            self.logger.warning('GA ConnectionResetError')
        except requests.exceptions.ConnectionError:
            self.logger.warning('GA ConnectionError connection aborted')
        except ConnectionAbortedError:
            self.logger.warning('GA ConnectionAbortedError')
        except Exception:
            # Log the exception, we should not raise analytics exceptions
            # back to the user, instead log them as exceptions for developers
            # to deal with.
            self.logger.exception(self.ga_unhandled_exception_message)

    def create_message_body(self, action_info: AnalyticsEvent):
        # Lookup action_info.user_id (which is an email address in Catalogue to get
        # the user_id so that we do not leak user email addresses.
        # Use the sub in the key so that it is a result for this
        # specific user.

        jwt = current_app.injector.get(JWT)

        me = self.__identity_service.dlc_me(jwt=jwt)
        try:
            user_id = me['datalake']['user_id']
        except Exception as e:
            self.logger.warning(f"For some reason we couldn't get the user id for the JWT : {me}")
            user_id = 'missing'

        from dataclasses import replace
        action_info = replace(action_info, user_id=user_id)

        payload = self._prepare_static_params_based_on(action_info)

        if action_info.user_id:
            payload.update({
                self.__params_mapping.get('user_id', 'missing'): action_info.user_id,
                self.__params_mapping.get('user_id_again', 'missing'): action_info.user_id,
            })

        if action_info.organisation_id:
            payload.update({
                self.__params_mapping.get('organisation_id', 'missing'):
                    action_info.organisation_id
            })

        if action_info.properties:
            payload.update(self._map_properties(action_info.properties))

        self.logger.debug(
            'AnalyticsEvent mapped from user email address to user ID',
            extra={'payload': payload}
        )

        return parse.urlencode(self._static_params + tuple(payload.items()))

    @staticmethod
    def _prepare_static_params_based_on(action_info):
        payload = {
            'an': action_info.application_name,
            'av': action_info.application_version,
            'cid': action_info.user_id,
            'ec': action_info.entity,
            'ea': action_info.action,
            'ev': action_info.result
        }

        return {k: v for k, v in payload.items() if v}

    def _map_properties(self, properties: dict):
        mapped_properties = {}
        for key in self.__params_mapping.keys():
            if properties.get(key, None) is not None:
                mapped_properties.update(
                    {self.__params_mapping[key]: properties[key]}
                )

        return mapped_properties
