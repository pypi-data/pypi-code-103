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
''' TeSLA CE Keystroke TestVerificationMixtures '''
import pytest
from .tks_utils import get_sample, get_request, check_enrolment_result, check_verification_result


models = {}
@pytest.mark.dependency()
def test_progressive_enrolment_mixtures(tks_provider):
    '''
    Test progressive enrolment mixtures
    :param tks_provider:
    :return:
    '''
    tks_provider.set_options({'model': 'GaussianMixturesModel'})

    data = get_sample(filename='valid_user1')
    model = None
    for i in range(0, 15):
        result = tks_provider.enrol(samples=[data], model=model)
        model = result.model
        check_enrolment_result(result)

        assert result.valid
        assert result.error_message is None
        assert len(result.model['samples']) == (i+1)
        assert len(result.used_samples) == (i+1)
        assert result.percentage is not None

    assert result.percentage == 1
    models['user1'] = model

@pytest.mark.dependency(depends=["test_progressive_enrolment_mixtures"], scope='module')
def test_verification_mixtures(tks_provider):
    '''
    Test verification mixtures
    :param tks_provider:
    :return:
    '''
    test_progressive_enrolment_mixtures(tks_provider)
    tks_provider.set_options({'model': 'GaussianMixturesModel'})

    request = get_request(filename='valid_user1')
    result = tks_provider.verify(request, models['user1'])
    check_verification_result(result)

    assert result.status == 1
    assert result.code == result.AlertCode.OK
    assert result.result > 0.9


@pytest.mark.dependency(depends=["test_progressive_enrolment_mixtures"], scope='module')
def test_verification_mixtures_enrol_user1_verification_user2(tks_provider):
    '''
    Test verification mixtures enrol user1 and verification with user2
    :param tks_provider:
    :return:
    '''
    tks_provider.set_options({"failed_missing_data": True})
    test_progressive_enrolment_mixtures(tks_provider)
    tks_provider.set_options({'model': 'GaussianMixturesModel'})

    request = get_request(filename='valid_user2')
    result = tks_provider.verify(request, models['user1'])
    check_verification_result(result)

    assert result.status == 1
    assert result.code == result.AlertCode.ALERT
    assert result.result == 0
