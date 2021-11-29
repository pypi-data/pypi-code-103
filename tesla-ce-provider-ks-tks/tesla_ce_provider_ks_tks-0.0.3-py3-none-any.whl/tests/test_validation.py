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
''' TeSLA CE Keystroke Test Validation Module '''
import base64
from .tks_utils import get_sample, check_validation_result


def test_missing_mimetype(tks_provider):
    '''
    Test missing mimetype
    :param tks_provider:
    :return:
    '''
    sample = get_sample(sample_mimetype=None, data_mimetype=None)
    result_id = 1
    result = tks_provider.validate_sample(sample, validation_id=result_id)

    check_validation_result(result)

    assert result.contribution is None
    assert result.message_code_id == 'PROVIDER_MISSING_MIMETYPE'
    assert result.error_message == 'Missing mimetype.'
    assert result.status == 2


def test_different_mimetypes(tks_provider):
    '''
    Test different mimetypes
    :param tks_provider:
    :return:
    '''
    sample = get_sample(sample_mimetype='image/png')
    result_id = 1
    result = tks_provider.validate_sample(sample, validation_id=result_id)

    check_validation_result(result)

    assert result.contribution is None
    assert result.message_code_id == 'PROVIDER_INVALID_MIMETYPE'
    assert result.error_message == 'Mimetype in sample data differs from sample mimetype'
    assert result.status == 2


def test_unsuported_mimetypes(tks_provider):
    '''
    Test unsuported mimetypes
    :param tks_provider:
    :return:
    '''
    sample = get_sample(sample_mimetype='image/other', data_mimetype='image/other')
    result_id = 1
    result = tks_provider.validate_sample(sample, validation_id=result_id)

    check_validation_result(result)

    assert result.contribution is None
    assert result.message_code_id == 'PROVIDER_INVALID_MIMETYPE'
    assert result.error_message == \
           f"Invalid mimetype. Accepted types are: [{', '.join(tks_provider.accepted_mimetypes)}]"
    assert result.status == 2


def test_mimetype_both(tks_provider):
    '''
    Test mimetype both
    :param tks_provider:
    :return:
    '''
    sample = get_sample()
    result_id = 1
    result = tks_provider.validate_sample(sample, validation_id=result_id)

    check_validation_result(result)

    assert result.contribution > 0
    assert result.message_code_id is None
    assert result.error_message is None
    assert result.status == 1
    assert result.info is None


def test_mimetype_sample(tks_provider):
    '''
    Test mimetype sample
    :param tks_provider:
    :return:
    '''
    sample = get_sample(sample_mimetype=None)
    result_id = 1
    result = tks_provider.validate_sample(sample, validation_id=result_id)

    check_validation_result(result)

    assert result.contribution > 0
    assert result.message_code_id is None
    assert result.error_message is None
    assert result.status == 1
    assert result.info is None


def test_invalid_sample_datab64(tks_provider):
    '''
    Test invalid sample datab64
    :param tks_provider:
    :return:
    '''
    sample = get_sample(ks_data='this is not a b64')
    result_id = 1
    result = tks_provider.validate_sample(sample, validation_id=result_id)

    check_validation_result(result)

    assert result.contribution is None
    assert result.message_code_id == 'PROVIDER_INVALID_SAMPLE_DATA'
    assert result.error_message == 'Invalid image format in sample data.'
    assert result.status == 2


def test_invalid_sample_data(tks_provider):
    '''
    Test invalid sample data
    :param tks_provider:
    :return:
    '''
    sample = get_sample(ks_data=base64.b64encode(b'this is not a b64').decode())
    result_id = 1
    result = tks_provider.validate_sample(sample, validation_id=result_id)

    check_validation_result(result)

    assert result.contribution is None
    assert result.message_code_id == 'PROVIDER_INVALID_SAMPLE_DATA'
    assert result.error_message == 'Invalid image format in sample data.'
    assert result.status == 2
