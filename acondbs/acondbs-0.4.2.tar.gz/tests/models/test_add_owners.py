"""Assert owners specified in the config file are added as admins in DB
"""

from pathlib import Path
import pytest

from acondbs import create_app
from acondbs.db.ops import define_tables
from acondbs.db.sa import sa
from acondbs.models import AccountAdmin

from ..constants import SAMPLE_DIR


##__________________________________________________________________||
def test_no_error_in_create_app():
    """Assert an error does not occur in create_app() when tables are not defined"""
    config_path = Path(SAMPLE_DIR, "config.py")
    kwargs = dict(
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        ACONDBS_OWNERS_GITHUB_LOGINS="octocat,dojocat",
    )
    app = create_app(config_path, **kwargs)  # noqa: F841


##__________________________________________________________________||
params = [
    [{"ACONDBS_OWNERS_GITHUB_LOGINS": ""}, {"octocat"}],
    [{"ACONDBS_OWNERS_GITHUB_LOGINS": ","}, {"octocat"}],
    [{"ACONDBS_OWNERS_GITHUB_LOGINS": "octocat"}, {"octocat"}],
    [{"ACONDBS_OWNERS_GITHUB_LOGINS": "octocat  "}, {"octocat"}],
    [{"ACONDBS_OWNERS_GITHUB_LOGINS": "dojocat"}, {"octocat", "dojocat"}],
    [
        {"ACONDBS_OWNERS_GITHUB_LOGINS": "octocat,dojocat"},
        {"octocat", "dojocat"},
    ],
    [
        {"ACONDBS_OWNERS_GITHUB_LOGINS": "octocat  ,  dojocat"},
        {"octocat", "dojocat"},
    ],
    [
        {"ACONDBS_OWNERS_GITHUB_LOGINS": "octocat  ,  dojocat,, ,  octocat  "},
        {"octocat", "dojocat"},
    ],
]


@pytest.mark.parametrize("kwargs, expected", params)
def test_add_owners_to_db_as_admins(kwargs, expected, tmpdir_factory):
    config_path = Path(SAMPLE_DIR, "config.py")

    # use a file because, with memory, a DB will be recreated in the
    # second create_app().
    tmpdir = str(tmpdir_factory.mktemp("models"))
    tmp_database_path = Path(tmpdir, "product.sqlite3")
    kwargs.update(
        dict(SQLALCHEMY_DATABASE_URI=f"sqlite:///{tmp_database_path}")
    )

    # define tables and add a admin
    app_ = create_app(config_path, **kwargs)
    with app_.app_context():
        define_tables()

        octocat = AccountAdmin(git_hub_login="octocat")
        sa.session.add(octocat)
        sa.session.commit()

    app = create_app(config_path, **kwargs)
    with app.app_context():
        assert expected == {e.git_hub_login for e in AccountAdmin.query.all()}


##__________________________________________________________________||
