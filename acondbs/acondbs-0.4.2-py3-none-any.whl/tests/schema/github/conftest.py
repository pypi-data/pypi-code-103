import pytest

from acondbs import create_app
from acondbs.db.ops import define_tables
from acondbs.db.sa import sa
from acondbs.models import (
    GitHubOrg,
    GitHubUser,
    GitHubOrgMembership,
    GitHubToken,
    AccountAdmin,
)


##__________________________________________________________________||
@pytest.fixture
def app_empty():
    database_uri = "sqlite:///:memory:"
    y = create_app(
        SQLALCHEMY_DATABASE_URI=database_uri,
        GITHUB_AUTH_AUTHORIZE_URL="https://github.com/login/oauth/authorize",
        GITHUB_AUTH_TOKEN_URL="https://github.com/login/oauth/access_token",
        GITHUB_AUTH_CLIENT_ID="client_id_0123456789",
        GITHUB_AUTH_CLIENT_SECRET="client_secret_abcdefghijklmnupqrstuvwxyz",
        GITHUB_AUTH_REDIRECT_URI="http://localhost:8080/signin",
    )
    with y.app_context():
        define_tables()
    yield y


@pytest.fixture
def app(app_empty):

    y = app_empty

    #
    #  +------+
    #  |      |       +-------+       +--------+
    #  | org1 | ----- |       | --+-- | token1 |
    #  |      |       | user1 |   |   +--------+
    #  +------+   +-- |       |   |
    #             |   +-------+   |   +--------+
    #             |               +-- | token2 |
    #  +------+   |                   +--------+
    #  |      | --+   +-------+
    #  | org2 |       |       |       +--------+
    #  |      | ----- | user2 | ----- | token3 |
    #  +------+       |       |       +--------+
    #                 +-------+
    #
    #  +------+       +-------+
    #  |      |       |       |       +--------+
    #  | org3 |       | user3 | ----- | token4 |
    #  |      |       |       |       +--------+
    #  +------+       +-------+
    #
    #

    org1 = GitHubOrg(login="org1", git_hub_id="012:Organization1")
    org2 = GitHubOrg(login="org2", git_hub_id="012:Organization2")
    org3 = GitHubOrg(login="org3", git_hub_id="012:Organization3")

    user1 = GitHubUser(
        user_id=1,
        login="user1",
        git_hub_id="04:User1",
        name="User One",
        avatar_url="avatar.com/user1",
    )
    user2 = GitHubUser(
        user_id=2,
        login="user2",
        git_hub_id="04:User2",
        name="User Two",
        avatar_url="avatar.com/user2",
    )
    user3 = GitHubUser(
        user_id=3,
        login="user3",
        git_hub_id="04:User3",
        name="User Three",
        avatar_url="avatar.com/user3",
    )

    GitHubToken(token_id=1, token="token1", scope="read:org", user=user1)
    GitHubToken(token_id=2, token="token2", scope="", user=user1)
    GitHubToken(token_id=3, token="token3", scope="", user=user2)
    GitHubToken(token_id=4, token="token4", scope="", user=user3)

    GitHubOrgMembership(org=org1, member=user1)
    GitHubOrgMembership(org=org2, member=user1)
    GitHubOrgMembership(org=org2, member=user2)

    admin1 = AccountAdmin(git_hub_login="user1")
    admin2 = AccountAdmin(git_hub_login="user3")

    with y.app_context():
        sa.session.add(org1)
        sa.session.add(org2)
        sa.session.add(org3)
        sa.session.add(user1)
        sa.session.add(user2)
        sa.session.add(user3)
        sa.session.add(admin1)
        sa.session.add(admin2)
        sa.session.commit()
    yield y


##__________________________________________________________________||
