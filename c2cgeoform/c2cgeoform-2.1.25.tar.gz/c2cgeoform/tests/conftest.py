import pytest
import transaction
from pyramid import testing
from pyramid.paster import bootstrap
from webtest import TestApp

from getitfixed.models import (
    get_engine,
    get_session_factory,
    get_tm_session,
)


@pytest.fixture(scope="session")
def app_env():
    with bootstrap('tests.ini') as env:
        yield env


@pytest.fixture(scope='session')
@pytest.mark.usefixtures("settings")
def dbsession(settings):
    engine = get_engine(settings)
    session_factory = get_session_factory(engine)
    session = get_tm_session(session_factory, transaction.manager)
    return session


@pytest.fixture(scope="session")
@pytest.mark.usefixtures("app_env")
def settings(app_env):
    yield app_env.get('registry').settings


@pytest.fixture()  # noqa: F811
@pytest.mark.usefixtures("dbsession", "app_env")
def test_app(request, dbsession, settings, app_env):
    config = testing.setUp(registry=app_env['registry'])
    config.add_request_method(lambda request: dbsession, 'dbsession', reify=True)
    app = config.make_wsgi_app()
    testapp = TestApp(app)
    yield testapp
