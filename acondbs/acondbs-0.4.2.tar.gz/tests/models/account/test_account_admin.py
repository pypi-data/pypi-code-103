from acondbs.db.sa import sa
from acondbs.models import AccountAdmin


##__________________________________________________________________||
def test_entry(app_empty):
    app = app_empty

    admin1 = AccountAdmin(git_hub_login="octocat")

    with app.app_context():
        sa.session.add(admin1)
        sa.session.commit()

    with app.app_context():
        admin1 = AccountAdmin.query.filter_by(git_hub_login="octocat").one()
        assert "octocat" == admin1.git_hub_login


##__________________________________________________________________||
