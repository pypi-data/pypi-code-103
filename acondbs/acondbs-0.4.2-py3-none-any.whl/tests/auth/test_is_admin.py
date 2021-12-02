from acondbs import auth

##__________________________________________________________________||
def test_true(app):
    token = '90b2ee5fed25506df04fd37343bb68d1803dd97f' # octcat
    environ_base = {'HTTP_AUTHORIZATION': f'Bearer {token}'}
    with app.test_request_context(environ_base=environ_base):
        assert auth.is_signed_in()
        assert auth.is_admin()

##__________________________________________________________________||
def test_false_not_admin(app):
    token = '0fb8c9e16d6f7c4961c4c49212bf197d79f14080' # dojocat
    environ_base = {'HTTP_AUTHORIZATION': f'Bearer {token}'}
    with app.test_request_context(environ_base=environ_base):
        assert auth.is_signed_in()
        assert not auth.is_admin()

##__________________________________________________________________||
def test_false_wrong_token(app):
    token = '0000000000000000000000000000000000000000'
    environ_base = {'HTTP_AUTHORIZATION': f'Bearer {token}'}
    with app.test_request_context(environ_base=environ_base):
        assert not auth.is_admin()

##__________________________________________________________________||
def test_false_no_token(app):
    environ_base = {}
    with app.test_request_context(environ_base=environ_base):
        assert not auth.is_admin()

##__________________________________________________________________||
