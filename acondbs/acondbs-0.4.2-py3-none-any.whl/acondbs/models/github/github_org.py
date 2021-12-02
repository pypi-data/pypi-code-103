from ...db.sa import sa


##__________________________________________________________________||
class GitHubOrg(sa.Model):
    __tablename__ = "github_orgs"
    org_id = sa.Column(sa.Integer(), primary_key=True)
    git_hub_id = sa.Column(sa.Text(), unique=True, nullable=False)
    login = sa.Column(sa.Text(), nullable=False)
    avatar_url = sa.Column(sa.Text())
    url = sa.Column(sa.Text())

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.login!r}>"


##__________________________________________________________________||
