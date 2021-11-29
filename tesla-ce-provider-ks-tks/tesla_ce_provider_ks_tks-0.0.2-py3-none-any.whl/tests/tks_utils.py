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
''' TeSLA CE Keystroke Test Utils Module'''
import os


def get_data(img='valid_user1'):
    '''
    Get data
    :param img:
    :return:
    '''
    with open(os.path.abspath(os.path.join(os.path.dirname(__file__), f'./data/{img}.b64')), 'r', encoding='utf-8') \
            as fd_ks:
        return fd_ks.read()


def get_sample(sample_mimetype='__default__', data_mimetype='__default__', ks_data=None, filename='valid_user1',
               sample_id=1, learner_id='9cfd197a-3b42-4361-841a-a45ef435b0e6', validations=None):
    '''
    Get sample
    :param sample_mimetype:
    :param data_mimetype:
    :param ks_data:
    :param filename:
    :param sample_id:
    :param learner_id:
    :param validations:
    :return:
    '''
    from tesla_ce_provider.models.base import Sample

    if ks_data is None:
        ks_filename = get_data(filename)
        assert ks_filename is not None and len(ks_filename)>0
        ks_data_parts = ks_filename.split(',')
        ks_data = ks_data_parts[1]
        if data_mimetype == '__default__':
            try:
                data_mimetype = ks_data_parts[0].split(':')[1].split(';')[0]
            except IndexError:
                # if the data mimetype is not found, assign None
                data_mimetype = None
    if data_mimetype == '__default__':
        data_mimetype = None
    if sample_mimetype == '__default__':
        if data_mimetype is None:
            sample_mimetype = 'text/plain'
        else:
            sample_mimetype = data_mimetype

    sample_data = {
        "learner_id": learner_id,
        "data": f"data:{data_mimetype};base64,{ks_data}",
        "instruments":[2],
        "metadata": {
            "context": {},
            "mimetype": sample_mimetype
        }
    }

    if data_mimetype is None:
        sample_data['data'] = f"data:;base64,{ks_data}"

    if sample_mimetype is None:
        del sample_data['metadata']['mimetype']

    return Sample({
        'id': sample_id,
        'learner_id': learner_id,
        'data': sample_data,
        'validations': validations
    })


def get_request(request_mimetype='__default__', data_mimetype='__default__', ks_data=None, filename='valid_user1',
                learner_id='9cfd197a-3b42-4361-841a-a45ef435b0e6', course_id=1, activity_id=1, session_id=1,
                request_id=1, ):
    '''
    Get request
    :param request_mimetype:
    :param data_mimetype:
    :param ks_data:
    :param filename:
    :param learner_id:
    :param course_id:
    :param activity_id:
    :param session_id:
    :param request_id:
    :return:
    '''
    from tesla_ce_provider.models.base import Request

    if ks_data is None:
        ks_filename = get_data(filename)
        assert ks_filename is not None and len(ks_filename) > 0
        ks_data_parts = ks_filename.split(',')
        ks_data = ks_data_parts[1]
        if data_mimetype == '__default__':
            try:
                data_mimetype = ks_data_parts[0].split(':')[1].split(';')[0]
            except IndexError:
                # if the data mimetype is not found, assign None
                data_mimetype = None
    if data_mimetype == '__default__':
        data_mimetype = None
    if request_mimetype == '__default__':
        if data_mimetype is None:
            request_mimetype = 'text/plain'
        else:
            request_mimetype = data_mimetype

    request_data = {
        "learner_id": learner_id,
        "course_id": course_id,
        "activity_id": activity_id,
        "session_id": session_id,
        "data": f"data:{data_mimetype};base64,{ks_data}",
        "instruments": [1],
        "metadata": {
            "filename": filename,
            "context": {},
            "mimetype": request_mimetype
        }
    }

    if data_mimetype is None:
        request_data['data'] = f"data:;base64,{ks_data}"

    if request_mimetype is None:
        del request_data['metadata']['mimetype']

    return Request({
        "id": request_id,
        "learner_id": learner_id,
        "data": request_data,
        "result": None,
        "audit": {}
    })


def check_validation_result(result):
    '''
    Check validtion result
    :param result:
    :return:
    '''
    import tesla_ce_provider
    assert isinstance(result, tesla_ce_provider.result.ValidationResult)


def check_enrolment_result(result):
    '''
    Check enrolment result
    :param result:
    :return:
    '''
    import tesla_ce_provider
    assert isinstance(result, tesla_ce_provider.result.EnrolmentResult)


def check_verification_result(result):
    '''
    Check verification result
    :param result:
    :return:
    '''
    import tesla_ce_provider
    assert isinstance(result, tesla_ce_provider.result.VerificationResult)
