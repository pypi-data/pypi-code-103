from acondbs import ops

from acondbs.models import ProductRelation


def test_create(app):
    with app.app_context():
        count = ProductRelation.query.count()
        model = ops.create_product_relation(
            type_id=1, self_product_id=1, other_product_id=4
        )
        ops.commit()
        relation_id = model.relation_id
        assert relation_id

    with app.app_context():
        assert ProductRelation.query.count() == (count + 2)
        model = ProductRelation.query.filter_by(relation_id=relation_id).one()
        assert model.reverse


def test_delete(app):
    with app.app_context():
        count = ProductRelation.query.count()
        model = ProductRelation.query.first()
        relation_id = model.relation_id

        ops.delete_product_relation(relation_id=relation_id)
        ops.commit()

    with app.app_context():
        assert ProductRelation.query.count() == (count - 2)
        model = ProductRelation.query.filter_by(
            relation_id=relation_id
        ).one_or_none()
        assert model is None
