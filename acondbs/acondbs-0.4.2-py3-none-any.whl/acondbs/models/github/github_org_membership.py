from ...db.sa import sa


##__________________________________________________________________||
class GitHubOrgMembership(sa.Model):
    __tablename__ = "github_org_memberships"
    entry_id = sa.Column(sa.Integer(), primary_key=True)
    org_id = sa.Column(sa.ForeignKey("github_orgs.org_id"), nullable=False)
    org = sa.relationship(
        "GitHubOrg",
        backref=sa.backref("memberships", cascade="all"),
    )
    member_id = sa.Column(
        sa.ForeignKey("github_users.user_id"), nullable=False
    )
    member = sa.relationship(
        "GitHubUser", backref=sa.backref("memberships", cascade="all")
    )


##__________________________________________________________________||
