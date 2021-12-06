# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from unittest import TestCase
from commonconf import override_settings
from uw_catalyst.dao import Catalyst_DAO
from uw_catalyst.util import fdao_catalyst_override
from restclients_core.dao import DAO
import mock


@fdao_catalyst_override
class CatalystTestDao(TestCase):
    @mock.patch.object(DAO, '_load_resource')
    def test_url(self, mock_load):
        r = Catalyst_DAO()._load_resource('GET', '/rest/v1/rest/123', {}, None)
        mock_load.assert_called_with('GET', '/rest/v1/rest/123', {}, None)

        with override_settings(
                RESTCLIENTS_CATALYST_SOL_AUTH_PRIVATE_KEY='token'):
            r = Catalyst_DAO()._load_resource(
                'GET', '/rest/v1/rest/123', {}, None)
            mock_load.assert_called_with(
                'GET', '/js_rest/v1/rest/123', {}, None)

    def test_custom_headers(self):
        headers = Catalyst_DAO()._custom_headers('GET', '/', {}, None)
        self.assertEquals(headers, None)

        with override_settings(
                RESTCLIENTS_CATALYST_SOL_AUTH_PRIVATE_KEY='token',
                RESTCLIENTS_CATALYST_SOL_AUTH_PUBLIC_KEY='testing'):

            headers = Catalyst_DAO()._custom_headers('GET', '/', {}, None)

            self.assertRegexpMatches(headers['Authorization'],
                                     r'^SolAuth testing:[a-f0-9]+$')
            self.assertRegexpMatches(headers['Date'], r'UTC')
