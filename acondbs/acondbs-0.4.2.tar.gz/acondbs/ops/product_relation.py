from ..models import (
    Product,
    ProductRelation,
    ProductRelationType,
)

from ..db.sa import sa


def create_product_relation(type_id, self_product_id, other_product_id, **kwargs):
    type_ = ProductRelationType.query.filter_by(type_id=type_id).one()
    self_ = Product.query.filter_by(product_id=self_product_id).one()
    other = Product.query.filter_by(product_id=other_product_id).one()
    model = ProductRelation(type_=type_, self_=self_, other=other, **kwargs)
    sa.session.add(model)
    return model


def delete_product_relation(relation_id):
    model = ProductRelation.query.filter_by(relation_id=relation_id).one()
    sa.session.delete(model)
    return
