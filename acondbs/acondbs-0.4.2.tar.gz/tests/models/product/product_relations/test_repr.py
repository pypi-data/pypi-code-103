from acondbs.models import ProductRelation


##__________________________________________________________________||
def test_repr(app):
    with app.app_context():
        model = ProductRelation.query.filter_by(relation_id=1).one()
        repr(model)


def test_transient(app):
    model = ProductRelation()
    repr(model)


##__________________________________________________________________||
