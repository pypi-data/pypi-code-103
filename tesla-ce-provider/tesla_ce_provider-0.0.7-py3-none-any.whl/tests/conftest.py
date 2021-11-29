#  Copyright (c) 2020 Xavier Baró
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU Affero General Public License as
#      published by the Free Software Foundation, either version 3 of the
#      License, or (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU Affero General Public License for more details.
#
#      You should have received a copy of the GNU Affero General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.
""" Test fixtures module """
import pytest

from tesla_ce_provider_fixtures.fixtures import *


@pytest.fixture
def tesla_ce_provider_conf():
    return {
        'provider_class': 'tesla_ce_provider_fixtures.utils.TestProvider',
        'provider_desc_file': None,
        'instrument': None,
        'info': None
    }


@pytest.fixture
def base_test_provider_class(mocker):
    # Disable automatic configuration
    mocker.patch('tesla_ce_client.connector.Connector.__init__', return_value=None)

    mock_config = {
        'CELERY_BROKER_URL': 'sqla+sqlite:///celerydb.sqlite',
        'CELERY_RESULT_BACKEND': 'rpc://',
        'CELERY_TASK_ALWAYS_EAGER': True,
        'CELERY_TASK_EAGER_PROPAGATES': True
    }

    mocker.patch('tesla_ce_client.connector.Connector.config', new_callable=mocker.PropertyMock,
                 return_value=mock_config)

    mock_module = {
        'provider_queue': 'pytest_queue'
    }
    mocker.patch('tesla_ce_client.connector.Connector.module', new_callable=mocker.PropertyMock,
                 return_value=mock_module)
    from tesla_ce_provider import BaseProvider

    return BaseProvider
