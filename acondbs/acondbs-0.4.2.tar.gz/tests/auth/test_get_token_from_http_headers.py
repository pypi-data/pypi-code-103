import pytest

from acondbs import auth

##__________________________________________________________________||
params = [
    pytest.param('Bearer {token}', id='no-quote'),
    pytest.param('Bearer "{token}"', id='double-quote'),
    pytest.param("Bearer '{token}'", id='single-quote'),
]

@pytest.mark.parametrize('format_', params)
def test_format(format_, app):
    token = '90b2ee5fed25506df04fd37343bb68d1803dd97f'
    environ_base = {'HTTP_AUTHORIZATION': format_.format(token=token)}
    with app.test_request_context(environ_base=environ_base):
        assert token == auth._get_token_from_http_headers()

##__________________________________________________________________||
