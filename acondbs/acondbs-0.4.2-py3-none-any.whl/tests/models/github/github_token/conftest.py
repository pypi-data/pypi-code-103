import pytest

from acondbs.db.sa import sa
from acondbs.models import GitHubToken, GitHubUser


##__________________________________________________________________||
@pytest.fixture
def app(app_empty):

    y = app_empty

    #
    #  +-------+        +--------+
    #  | user1 | --+--> | token1 |
    #  +-------+   |    +--------+
    #              |
    #              |    +--------+
    #              +--> | token2 |
    #                   +--------+
    #

    user1 = GitHubUser(login="octocat", git_hub_id="04:User583231")
    token1 = GitHubToken(  # noqa: F841
        token="token_001", scope="read:org", user=user1
    )
    token2 = GitHubToken(  # noqa: F841
        token="token_002", scope="read:org", user=user1
    )

    with y.app_context():
        sa.session.add(user1)
        sa.session.commit()
    yield y


##__________________________________________________________________||
