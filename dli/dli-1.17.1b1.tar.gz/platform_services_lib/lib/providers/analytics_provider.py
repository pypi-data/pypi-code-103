import os
from typing import Optional

import requests
from injector import singleton as singleton_scope, provider
from requests import Session

from ..authentication.auth import _sam_app_flow
from ..context.environments import _Environment
from ..handlers.analytics_handler import AnalyticsHandler, AnalyticsSender
from ..providers.base_provider import BaseModule


class AnalyticsDependencyProvider(BaseModule):
    """
    This is currently used by the s3-proxy for analytics. If you want to use it for other services then you will need
    to override the `app_name` in the config dict.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        config = {
            'version': 'latest',
            'app_name': 's3proxy',
            'consumption_env': os.environ.get('CONSUMPTION_API_URL'),
            'strict': False,
        }

        catalogue_url = os.environ.get('CATALOGUE_API_URL')  # 'https://catalogue-qa.udpmarkit.net'
        environment = _Environment(catalogue_url)

        try:
            decoded_token = _sam_app_flow(
                environment,
                os.environ.get('DLI_ACCESS_KEY_ID'),
                os.environ.get('DLI_SECRET_ACCESS_KEY')
            )
        except Exception:
            decoded_token = None

        def new_session() -> Optional[requests.Session]:
            session = Session()
            session.headers.update({'Authorization': f"Bearer {decoded_token}"})
            return session

        def no_session() -> Optional[requests.Session]:
            return None

        # if DLI_ACCESS_KEY_ID and DLI_SECRET_ACCESS_KEY is
        # not valid we cannot retrieve a JWT from SAM.
        if decoded_token is not None:
            session_func = new_session
        else:
            session_func = no_session

        rest_analytics_sender = AnalyticsSender(config, session_func)
        self._analytics_handler = AnalyticsHandler(rest_analytics_sender)

    @singleton_scope
    @provider
    def analytics_handler(self) -> AnalyticsHandler:
        return self._analytics_handler
