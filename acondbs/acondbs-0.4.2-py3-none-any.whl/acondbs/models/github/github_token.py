import datetime

from flask import current_app
from sqlalchemy_utils import EncryptedType

from ...db.sa import sa


def encription_key():
    return current_app.config["SECRET_KEY"]


##__________________________________________________________________||
class GitHubToken(sa.Model):
    __tablename__ = "github_tokens"
    token_id = sa.Column(sa.Integer(), primary_key=True)
    token = sa.Column(EncryptedType(sa.Text(), key=encription_key))
    scope = sa.Column(sa.Text())
    user_id = sa.Column(sa.ForeignKey("github_users.user_id"), nullable=False)
    user = sa.relationship(
        "GitHubUser",
        backref=sa.backref("tokens", cascade="all, delete-orphan"),
    )
    time_created = sa.Column(
        sa.DateTime(), default=lambda: datetime.datetime.now()
    )


##__________________________________________________________________||
