""" Test fixtures module """
#  Copyright (c) 2021 Roger Muñoz
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
from logging import getLogger
import pytest


@pytest.fixture
def tesla_ce_provider_conf():
    '''
    Fixture tesla_ce_provider_conf
    :return:
    '''
    return {
        'provider_class': 'tks.TKSProvider',
        'provider_desc_file': None,
        'instrument': None,
        'info': None
    }


@pytest.fixture
def tks_provider(tesla_ce_base_provider):
    '''
    Fixture tks_provider
    :param tesla_ce_base_provider:
    :return:
    '''
    from tks import TKSProvider
    assert isinstance(tesla_ce_base_provider, TKSProvider)

    logger = getLogger('tks Tests')
    tesla_ce_base_provider.set_logger(logger.debug)

    return tesla_ce_base_provider
