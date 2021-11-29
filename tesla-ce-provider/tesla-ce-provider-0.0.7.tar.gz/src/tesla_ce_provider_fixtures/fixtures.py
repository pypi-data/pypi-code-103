#  Copyright (c) 2020 Xavier Baró / Roger Muñoz Bernaus
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
import warnings
import os
import glob
import simplejson


@pytest.fixture(scope='session')
def celery_config():
    return {
        'broker_url': 'sqla+sqlite:///celerydb.sqlite',
        'result_backend': 'rpc://',
        'task_always_eager': True,
        'task_eager_propagates': True
    }


def _fr_info():
    return {
        "id": 1,
        "options_schema": {
            "type": "object",
            "properties": {
                "online": {
                    "type": "boolean",
                    "title": "Analyze learner identity during the assessment",
                    "default": True
                },
                "offline": {
                    "type": "boolean",
                    "title": "Analyze learner identity on the delivered assessment",
                    "default": False
                }
            }
        },
        "name": "Face Recognition",
        "acronym": "fr",
        "queue": "tesla_fr",
        "enabled": True,
        "requires_enrolment": True,
        "description": "Verify learner identity by means of face attributes.",
        "identity": True,
        "originality": False,
        "authorship": False,
        "integrity": False
    }


def _ks_info():
    return {
        "id": 2,
        "options_schema": None,
        "name": "Keystroke Dynamics Recognition",
        "acronym": "ks",
        "queue": "tesla_ks",
        "enabled": True,
        "requires_enrolment": True,
        "description": "Verify learner identity by means of keystroke patterns.",
        "identity": True,
        "originality": False,
        "authorship": False,
        "integrity": False
    }


def _vr_info():
    return {
        "id": 3,
        "options_schema": {
            "type": "object",
            "properties": {
                "online": {
                    "type": "boolean",
                    "title": "Analyze learner identity during the assessment",
                    "default": True
                },
                "offline": {
                    "type": "boolean",
                    "title": "Analyze learner identity on the delivered assessment",
                    "default": False
                }
            }
        },
        "name": "Voice Recognition",
        "acronym": "vr",
        "queue": "tesla_vr",
        "enabled": True,
        "requires_enrolment": True,
        "description": "Verify learner identity by means of voice attributes.",
        "identity": True,
        "originality": False,
        "authorship": False,
        "integrity": False
    }


def _fa_info():
    return {
        "id": 4,
        "options_schema": None,
        "name": "Forensic Analysis",
        "acronym": "fa",
        "queue": "tesla_fa",
        "enabled": True,
        "requires_enrolment": True,
        "description": "Verify learner identity by means of writing style patterns.",
        "identity": True,
        "originality": False,
        "authorship": True,
        "integrity": False
    }


def _plag_info():
    return {
        "id": 5,
        "options_schema": None,
        "name": "Plagiarism Detection",
        "acronym": "plag",
        "queue": "tesla_plag",
        "enabled": True,
        "requires_enrolment": False,
        "description": "Verify the originality of an assessment.",
        "identity": False,
        "originality": True,
        "authorship": False,
        "integrity": False
    }


def get_instrument_info(instrument_id):

    if instrument_id == 1:
        instrument = _fr_info()
    elif instrument_id == 2:
        instrument = _ks_info()
    elif instrument_id == 3:
        instrument = _vr_info()
    elif instrument_id == 4:
        instrument = _fa_info()
    elif instrument_id == 5:
        instrument = _plag_info()
    else:
        pytest.fail('Invalid instrument id on provider information.')

    return instrument


@pytest.fixture
def tesla_ce_provider_conf():
    return {
        'provider_class': os.getenv('PROVIDER_CLASS', None),
        'provider_desc_file': None,
        'instrument': None,
        'info': None
    }


@pytest.fixture
def tesla_ce_base_provider(mocker, celery_session_app, celery_session_worker, tesla_ce_provider_conf):
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

    # Load arguments
    if 'provider_class' not in tesla_ce_provider_conf or tesla_ce_provider_conf['provider_class'] is None:
        raise ModuleNotFoundError(
            'Provider implementation class is not provider. ' 
            'Set PROVIDER_CLASS or reimplement tesla_ce_provider_conf fixture.')

    components = tesla_ce_provider_conf['provider_class'].split('.')
    mod = __import__(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)
    provider_obj = mod()

    # Load provider options file
    desc_file = None
    if 'provider_desc_file' in tesla_ce_provider_conf and tesla_ce_provider_conf['provider_desc_file'] is not None:
        if not os.path.exists(tesla_ce_provider_conf['provider_desc_file']):
            raise FileNotFoundError('Cannot find provider description file at {}'.format(
                tesla_ce_provider_conf['provider_desc_file'])
            )
        desc_file = tesla_ce_provider_conf['provider_desc_file']

    if desc_file is None:
        options_file = glob.glob('*.info.json')
        if len(options_file) == 0:
            options_file = glob.glob('../*.info.json')
        if len(options_file) > 1:
            warnings.warn('Multiple provider info files found', RuntimeWarning)
        if len(options_file) > 0:
            desc_file = os.path.abspath(options_file[0])

    if desc_file is None:
        warnings.warn('No provider description file was provided.', RuntimeWarning)
    else:
        with open(desc_file, 'r') as dh_options:
            provider_obj.info = simplejson.load(dh_options)
        assert 'instrument' in provider_obj.info
        assert isinstance(provider_obj.info['instrument'], int)
        provider_obj.instrument = get_instrument_info(provider_obj.info['instrument'])

    provider_obj.provider_id = 15

    return provider_obj
