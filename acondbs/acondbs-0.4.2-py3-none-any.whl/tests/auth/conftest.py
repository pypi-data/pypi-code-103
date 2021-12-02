import pytest

from acondbs import create_app
from acondbs.db.ops import define_tables

from acondbs.db.sa import sa
from acondbs.models import (
    GitHubToken,
    GitHubUser,
    AccountAdmin
    )

##__________________________________________________________________||
@pytest.fixture
def app_empty():
    database_uri ="sqlite:///:memory:"
    y = create_app(SQLALCHEMY_DATABASE_URI=database_uri)
    with y.app_context():
        define_tables()
    yield y

##__________________________________________________________________||
@pytest.fixture
def app(app_empty):
    y = app_empty

    # user1: octocat - admin
    user1 = GitHubUser(login="octocat", git_hub_id="04:User583231")
    token1 = GitHubToken(token="90b2ee5fed25506df04fd37343bb68d1803dd97f", scope="", user=user1)
    admin1 = AccountAdmin(git_hub_login="octocat")

    # user2: dojocat - not admin
    user2 = GitHubUser(login="dojocat", git_hub_id="04:User9758946")
    token2 = GitHubToken(token="0fb8c9e16d6f7c4961c4c49212bf197d79f14080", scope="", user=user2)

    with y.app_context():
        sa.session.add(user1)
        sa.session.add(admin1)
        sa.session.add(user2)
        sa.session.commit()
    yield y

##__________________________________________________________________||
