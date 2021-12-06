#
# Copyright (C) 2020 IHS Markit.
# All Rights Reserved
#
import os
from urllib.parse import urlparse, ParseResult


class _Environment:

    _catalogue_environment_name_map = {
        'catalogue.datalake.ihsmarkit.com': 'prod',
        'catalogue-testprod.datalake.ihsmarkit.com': 'testprod',
        'catalogue-uat.datalake.ihsmarkit.com': 'uat',
        'catalogue-uatus.datalake.ihsmarkit.com': 'uatus',
        'client-uat.datalake.ihsmarkit.com': 'uat2',
        'catalogue-dev.udpmarkit.net': 'dev',
        'catalogue-qa.udpmarkit.net': 'qa',
        'catalogue-qa2.udpmarkit.net': 'qa2',
        'catalogue-qa3.udpmarkit.net': 'qa3',
    }

    _catalogue_accounts_environment_map = {
        'catalogue.datalake.ihsmarkit.com': 'catalogue.datalake.ihsmarkit.com',
        'catalogue-testprod.datalake.ihsmarkit.com': 'catalogue-testprod.datalake.ihsmarkit.com',
        'catalogue-uat.datalake.ihsmarkit.com': 'catalogue-uat.datalake.ihsmarkit.com',
        'catalogue-uatus.datalake.ihsmarkit.com': 'catalogue-uatus.datalake.ihsmarkit.com',
        'client-uat.datalake.ihsmarkit.com': 'client-uat.datalake.ihsmarkit.com',
        'catalogue-dev.udpmarkit.net': 'catalogue-dev.udpmarkit.net',
        'catalogue-qa.udpmarkit.net': 'catalogue-qa.udpmarkit.net',
        'catalogue-qa2.udpmarkit.net': 'catalogue-qa2.udpmarkit.net',
        'catalogue-qa3.udpmarkit.net': 'catalogue-qa3.udpmarkit.net',
    }

    _catalogue_consumption_environment_map = {
        'catalogue.datalake.ihsmarkit.com': 'consumption.datalake.ihsmarkit.com',
        'catalogue-testprod.datalake.ihsmarkit.com': 'consumption-testprod.datalake.ihsmarkit.com',
        'catalogue-uat.datalake.ihsmarkit.com': 'consumption-uat.datalake.ihsmarkit.com',
        'catalogue-uatus.datalake.ihsmarkit.com': 'consumption-uatus.datalake.ihsmarkit.com',
        'client-uat.datalake.ihsmarkit.com': 'consumption-uat2.datalake.ihsmarkit.com',
        'catalogue-dev.udpmarkit.net': 'consumption-dev.udpmarkit.net',
        'catalogue-qa.udpmarkit.net': 'consumption-qa.udpmarkit.net',
        'catalogue-qa2.udpmarkit.net': 'consumption-qa2.udpmarkit.net',
        'catalogue-qa3.udpmarkit.net': 'consumption-qa3.udpmarkit.net',
    }

    _catalogue_sam_api_environment_map = {
        'catalogue.datalake.ihsmarkit.com': 'sam-api.ihsmarkit.com',
        'catalogue-testprod.datalake.ihsmarkit.com': 'sam-api.ihsmarkit.com',
        'catalogue-uat.datalake.ihsmarkit.com': 'sam-api.ihsmarkit.com',
        'catalogue-uatus.datalake.ihsmarkit.com': 'sam-api.ihsmarkit.com',
        'client-uat.datalake.ihsmarkit.com': 'sam-api.ihsmarkit.com',
        'catalogue-qa.udpmarkit.net': 'sam-api.samexternal.net',
        'catalogue-qa2.udpmarkit.net': 'sam-api.samexternal.net',
        'catalogue-qa3.udpmarkit.net': 'sam-api.samexternal.net',
        'catalogue-dev.udpmarkit.net': 'sam-api.samexternal.net',
    }

    _catalogue_sam_environment_map = {
        'catalogue.datalake.ihsmarkit.com': 'sam.ihsmarkit.com',
        'catalogue-testprod.datalake.ihsmarkit.com': 'sam.ihsmarkit.com',
        'catalogue-uat.datalake.ihsmarkit.com': 'sam.ihsmarkit.com',
        'catalogue-uatus.datalake.ihsmarkit.com': 'sam.ihsmarkit.com',
        'client-uat.datalake.ihsmarkit.com': 'sam.ihsmarkit.com',
        'catalogue-qa.udpmarkit.net': 'sam.samexternal.net',
        'catalogue-qa2.udpmarkit.net': 'sam.samexternal.net',
        'catalogue-qa3.udpmarkit.net': 'sam.samexternal.net',
        'catalogue-dev.udpmarkit.net': 'sam.samexternal.net',
    }

    _s3_proxy_environment_map = {
        'catalogue.datalake.ihsmarkit.com': 's3.datalake.ihsmarkit.com',
        'catalogue-testprod.datalake.ihsmarkit.com': 's3-testprod.datalake.ihsmarkit.com',
        'catalogue-uat.datalake.ihsmarkit.com': 's3-uat.datalake.ihsmarkit.com',
        'catalogue-uatus.datalake.ihsmarkit.com': 's3-uatus.datalake.ihsmarkit.com',
        'client-uat.datalake.ihsmarkit.com': 's3-uat2.datalake.ihsmarkit.com',
        'catalogue-qa.udpmarkit.net': 's3-qa.udpmarkit.net',
        'catalogue-qa2.udpmarkit.net': 's3-qa2.udpmarkit.net',
        'catalogue-qa3.udpmarkit.net': 's3-qa3.udpmarkit.net',
        'catalogue-dev.udpmarkit.net': 's3-dev.udpmarkit.net',
    }

    _presto_environment_map = {
        'catalogue.datalake.ihsmarkit.com': 'sql.datalake.ihsmarkit.com',
        'catalogue-uat.datalake.ihsmarkit.com': 'presto-uat.datalake.ihsmarkit.com',
        'client-uat.datalake.ihsmarkit.com': 'sql-uat2.datalake.ihsmarkit.com',
        'catalogue-qa.udpmarkit.net': 'presto-qa.udpmarkit.net',
        'catalogue-qa2.udpmarkit.net': 'presto-qa2.udpmarkit.net',
        'catalogue-dev.udpmarkit.net': 'presto-dev.udpmarkit.net',
    }

    def __init__(self, api_root):
        """
        Class to manage the different endpoints

        :param str root_url: The root url of the catalogue
        """

        __catalogue_parse_result = urlparse(api_root)

        self.environment_name = self._catalogue_environment_name_map.get(
            __catalogue_parse_result.netloc, 'unknown'
        )

        # allow URLs to be overridden by ENV vars (SAM is fixed as Prod or Non-Prod, specific to env)
        # make sure to have the api_root of the SDK still set to the respective environment however

        if os.environ.get("DATA_LAKE_INTERFACE_URL"):
            self.catalogue = os.environ.get("DATA_LAKE_INTERFACE_URL")
        else:
            self.catalogue = ParseResult(
                __catalogue_parse_result.scheme, __catalogue_parse_result.netloc, '', '', '', ''
            ).geturl()

        if os.environ.get("DATA_LAKE_ACCOUNTS_URL"):
            self.accounts = os.environ.get("DATA_LAKE_ACCOUNTS_URL")
        else:
            __accounts_host = self._catalogue_accounts_environment_map.get(
                __catalogue_parse_result.netloc
            )

            self.accounts = ParseResult(
                __catalogue_parse_result.scheme, __accounts_host, '', '', '', ''
            ).geturl()

        if os.environ.get("CONSUMPTION_API_URL"):
            self.consumption = os.environ.get("CONSUMPTION_API_URL")
        else:
            __consumption_host = self._catalogue_consumption_environment_map.get(
                __catalogue_parse_result.netloc
            )

            self.consumption = ParseResult(
                __catalogue_parse_result.scheme, __consumption_host, '', '', '', ''
            ).geturl()

        if os.environ.get("S3_API_URL"):
            self.s3_proxy = os.environ.get("S3_API_URL")
        else:
            __s3_proxy_host = self._s3_proxy_environment_map.get(
                __catalogue_parse_result.netloc
            )

            self.s3_proxy = ParseResult(
                __catalogue_parse_result.scheme, __s3_proxy_host, '', '', '', ''
            ).geturl()

        if os.environ.get("SAM_URL"):
            self.sam = os.environ.get("SAM_URL")
        else:
            __sam_host = self._catalogue_sam_environment_map.get(
                __catalogue_parse_result.netloc
            )

            self.sam = ParseResult(
                'https', __sam_host, '', '', '', ''
            ).geturl()

        if os.environ.get("SAM_API_URL"):
            self.sam_api = os.environ.get("SAM_API_URL")
        else:
            __sam_api_host = self._catalogue_sam_api_environment_map.get(
                __catalogue_parse_result.netloc
            )

            self.sam_api = ParseResult(
                'https', __sam_api_host, '', '', '', ''
            ).geturl()

        if os.environ.get("SQL_URL"):
            self.sql = os.environ.get("SQL_URL")
        else:
            __presto_host = self._presto_environment_map.get(
                __catalogue_parse_result.netloc
            )

            self.sql = ParseResult(
                'https', __presto_host, '', '', '', ''
            ).geturl()