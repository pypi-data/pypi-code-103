from ...db.sa import sa

from sqlalchemy.event import listens_for


##__________________________________________________________________||
class ProductRelation(sa.Model):
    __tablename__ = "product_relations"
    relation_id = sa.Column(sa.Integer(), primary_key=True)
    type_id = sa.Column(
        sa.Integer(),
        sa.ForeignKey("product_relation_types.type_id"),
        nullable=False,
    )
    type_ = sa.relationship(
        "ProductRelationType", backref=sa.backref("relations")
    )
    self_product_id = sa.Column(
        sa.Integer(), sa.ForeignKey("products.product_id"), nullable=False
    )
    self_ = sa.relationship(
        "Product",
        foreign_keys=[self_product_id],
        backref=sa.backref("relations", cascade="all, delete-orphan"),
    )
    other_product_id = sa.Column(
        sa.Integer(), sa.ForeignKey("products.product_id"), nullable=False
    )
    other = sa.relationship("Product", foreign_keys=[other_product_id])
    reverse_relation_id = sa.Column(
        sa.ForeignKey("product_relations.relation_id")
    )
    reverse = sa.relationship(
        lambda: ProductRelation,
        uselist=False,
        foreign_keys=[reverse_relation_id],
        remote_side="ProductRelation.relation_id",
        cascade="all",
        post_update=True,
    )
    __table_args__ = (
        sa.UniqueConstraint(
            "type_id",
            "self_product_id",
            "other_product_id",
            name="_type_id_self_product_id_other_product_id",
        ),
    )

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.type_name!r}>"

    @property
    def type_name(self):
        # used in __repr__()
        try:
            return self.type_.name
        except BaseException:
            return self.type_


##__________________________________________________________________||
@listens_for(ProductRelation.type_, "set")
def set_reverse_type(target, value, oldvalue, initiator):
    relation = target

    try:
        if relation.__avoid_recursive:
            return
    except Exception:
        pass

    if not value.reverse:
        return

    if not relation.reverse:
        reverse = ProductRelation()
        reverse.reverse = relation
        relation.reverse = reverse
        reverse.__avoid_recursive = True
        if relation.self_:
            reverse.other = relation.self_
        if relation.other:
            reverse.self_ = relation.other
        del reverse.__avoid_recursive
    if not relation.reverse.type_:
        relation.reverse.__avoid_recursive = True
        relation.reverse.type_ = value.reverse
        del relation.reverse.__avoid_recursive


@listens_for(ProductRelation.self_, "set")
def set_reverse_other(target, value, oldvalue, initiator):
    relation = target

    if not relation.reverse:
        return

    try:
        if relation.__avoid_recursive:
            return
    except Exception:
        pass

    if not relation.reverse.other:
        relation.reverse.__avoid_recursive = True
        relation.reverse.other = value
        del relation.reverse.__avoid_recursive


@listens_for(ProductRelation.other, "set")
def set_reverse_self(target, value, oldvalue, initiator):
    relation = target

    if not relation.reverse:
        return

    try:
        if relation.__avoid_recursive:
            return
    except Exception:
        pass

    if not relation.reverse.self_:
        relation.reverse.__avoid_recursive = True
        relation.reverse.self_ = value
        del relation.reverse.__avoid_recursive


##__________________________________________________________________||
