from ...db.sa import sa

from sqlalchemy.event import listens_for


##__________________________________________________________________||
class ProductRelationType(sa.Model):
    __tablename__ = "product_relation_types"
    type_id = sa.Column(sa.Integer(), primary_key=True)
    name = sa.Column(sa.Text(), nullable=False, unique=True, index=True)  # TODO: set unique False
    reverse_type_id = sa.Column(
        sa.ForeignKey("product_relation_types.type_id")
    )
    reverse = sa.relationship(
        lambda: ProductRelationType,
        uselist=False,
        foreign_keys=[reverse_type_id],
        remote_side="ProductRelationType.type_id",
        cascade="all",
        post_update=True,
    )
    indef_article = sa.Column(sa.Text())
    singular = sa.Column(sa.Text())
    plural = sa.Column(sa.Text())

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.name!r}>"


##__________________________________________________________________||
@listens_for(ProductRelationType.reverse, "set")
def set_reverse(target, value, oldvalue, initiator):
    """set the reciprocating reverse

    For example, if the reverse of the type1 is set type2,
       type1.reverse = type2
    this function sets the reverse of the type2 to type1,
       type2.reverse = type1

    """

    type1 = target
    type2 = value

    if type1 is type2:
        return

    try:
        if type1.__avoid_recursive:
            return
    except Exception:
        pass

    if not type2.reverse:
        type2.__avoid_recursive = True
        type2.reverse = type1
        del type2.__avoid_recursive


##__________________________________________________________________||
