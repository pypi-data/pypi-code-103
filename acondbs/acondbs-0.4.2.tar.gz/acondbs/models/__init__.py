"""Declare SQLAlchemy ORM models

In this package, ORM (Object-relational mapping) models are declared.
One model is mapped to one table in the DB. Models are declared as
Python classes inheriting the Model class in Flask-SQLAlchemy.

"Declaring Models" in Flask-SQLAlchemy doc:
https://flask-sqlalchemy.palletsprojects.com/en/2.x/models/

"Declare a Mapping" in SQLAlchemy doc:
https://docs.sqlalchemy.org/en/14/orm/tutorial.html#declare-a-mapping

"""

##__________________________________________________________________||
from .product import (  # noqa: F401
    ProductType,
    Product,
    ProductFilePath,
    ProductRelationType,
    ProductRelation,
    AttributeUnicodeText,
    AttributeBoolean,
    AttributeInteger,
    AttributeFloat,
    AttributeDate,
    AttributeDateTime,
    AttributeTime,
    FieldType,  # enum
    saEnumFieldType,  # SQLAlchemy Enum
    Field,
    TypeFieldAssociation,
)

from .github import (  # noqa: F401
    GitHubToken,
    GitHubOrg,
    GitHubUser,
    GitHubOrgMembership,
)

from .account import AccountAdmin  # noqa: F401

from .web import WebConfig  # noqa: F401

from .misc import Log  # noqa: F401


##__________________________________________________________________||
def init_app(app):
    """Initialize the Flask application object

    This function is called by `create_app()` of Flask

    Parameters
    ----------
    app : Flask
        The Flask application object, an instance of `Flask`
    """

    _add_owners_to_db_as_admins(app)
    # remove_git_hub_tokens_with_invalid_decryption_key(app)


##__________________________________________________________________||
def _add_owners_to_db_as_admins(app):
    import sqlalchemy
    from ..db.sa import sa

    # Test if tables are defined. For example, tables are not defined
    # when a migration version is being created.
    with app.app_context():
        try:
            _ = AccountAdmin.query.all()
        except sqlalchemy.exc.OperationalError:
            return

    with app.app_context():

        owners = app.config.get("ACONDBS_OWNERS_GITHUB_LOGINS", "")
        # e.g., "octocat,dojocat"

        owners = {e.strip() for e in owners.split(",")}
        # e.g., {"octocat", "dojocat"}

        # remove empty strings
        owners = {e for e in owners if e}

        # sort so that "admin_id" is deterministic in tests
        owners = sorted(owners)

        for owner in owners:
            if (
                admin := AccountAdmin.query.filter_by(
                    git_hub_login=owner
                ).one_or_none()
            ) is None:
                admin = AccountAdmin(git_hub_login=owner)
                sa.session.add(admin)
        sa.session.commit()


##__________________________________________________________________||
def remove_git_hub_tokens_with_invalid_decryption_key(app):
    from ..db.sa import sa

    with app.app_context():
        token_ids = [
            e[0] for e in sa.session.query(GitHubToken.token_id).all()
        ]
        for token_id in token_ids:
            try:
                token = GitHubToken.query.filter_by(  # noqa: F841
                    token_id=token_id
                ).one()
            except ValueError:
                sql = f"delete from {GitHubToken.__tablename__} where token_id={token_id};"
                sa.engine.execute(sql)


##__________________________________________________________________||
