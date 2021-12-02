from acondbs.db.sa import sa
from acondbs.models import GitHubUser


##__________________________________________________________________||
def test_entry(app_empty):
    app = app_empty

    user1 = GitHubUser(
        login="octocat",
        git_hub_id="04:User583231",
        name="The Octocat",
        avatar_url="https://avatars3.githubusercontent.com/u/583231?v=4",
    )

    with app.app_context():
        sa.session.add(user1)
        sa.session.commit()

    with app.app_context():
        user1 = GitHubUser.query.filter_by(login="octocat").one()
        assert "octocat" == user1.login


##__________________________________________________________________||
