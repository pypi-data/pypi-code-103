from ...db.sa import sa


##__________________________________________________________________||
class ProductType(sa.Model):
    __tablename__ = "product_types"
    type_id = sa.Column(sa.Integer(), primary_key=True)
    name = sa.Column(sa.Text(), nullable=False, unique=True, index=True)
    order = sa.Column(sa.Integer())
    indef_article = sa.Column(sa.Text())
    singular = sa.Column(sa.Text())
    plural = sa.Column(sa.Text())
    icon = sa.Column(sa.Text())

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.name!r}>"


##__________________________________________________________________||
