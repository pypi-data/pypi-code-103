import datetime

from acondbs.db.sa import sa
from acondbs.models import GitHubToken, GitHubUser


##__________________________________________________________________||
def test_query(app):

    with app.app_context():
        user1 = GitHubUser.query.filter_by(login="octocat").one()
        token1, token2 = user1.tokens

        assert token1.token == "token_001"
        assert token1.scope == "read:org"
        assert token1.user == user1

        assert token2.token == "token_002"
        assert token2.scope == "read:org"
        assert token2.user == user1


##__________________________________________________________________||
def test_add(app):

    with app.app_context():
        user1 = GitHubUser.query.filter_by(login="octocat").one()
        ntokens = len(user1.tokens)  # = 2
        token3 = GitHubToken(token="token_003", scope="read:org", user=user1)
        sa.session.commit()

    with app.app_context():
        token3 = (
            GitHubToken.query.join(GitHubUser)
            .filter(GitHubUser.login == "octocat")
            .filter(GitHubToken.token == "token_003")
            .one()
        )
        assert "token_003" == token3.token
        assert "read:org" == token3.scope
        assert (
            datetime.datetime(2021, 1, 4, 14, 32, 20) == token3.time_created
        )  # default value set in the fixture mock_datetime
        user1 = token3.user
        assert "octocat" == user1.login
        assert ntokens + 1 == len(user1.tokens)


##__________________________________________________________________||
def test_delete(app):

    with app.app_context():
        user1 = GitHubUser.query.filter_by(login="octocat").one()
        ntokens = len(user1.tokens)  # = 2
        token1 = user1.tokens[0]
        sa.session.delete(token1)
        sa.session.commit()

    with app.app_context():
        user1 = GitHubUser.query.filter_by(login="octocat").one()
        assert ntokens - 1 == len(user1.tokens)  # 1

    with app.app_context():
        user1 = GitHubUser.query.filter_by(login="octocat").one()
        token2 = user1.tokens[0]
        sa.session.delete(token2)
        sa.session.commit()

    with app.app_context():
        user1 = GitHubUser.query.filter_by(login="octocat").one()
        assert ntokens - 2 == len(user1.tokens)  # 0


##__________________________________________________________________||
def test_delete_cascade(app):

    with app.app_context():
        user1 = GitHubUser.query.filter_by(login="octocat").one()
        sa.session.delete(user1)
        sa.session.commit()

    with app.app_context():
        tokens = GitHubToken.query.all()
        assert 0 == len(tokens)


##__________________________________________________________________||
