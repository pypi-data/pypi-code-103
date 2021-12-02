from ...db.sa import sa


##__________________________________________________________________||
class AccountAdmin(sa.Model):
    __tablename__ = "account_admins"
    admin_id = sa.Column(sa.Integer(), primary_key=True)
    git_hub_login = sa.Column(sa.Text(), unique=True, nullable=False)

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.git_hub_login!r}>"


##__________________________________________________________________||
