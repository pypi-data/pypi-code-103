import pytest

from sqlalchemy import exc

from acondbs.models import Product, ProductRelation, ProductRelationType

from acondbs.db.sa import sa


##__________________________________________________________________||
def test_constraint(app):

    #                              +--------+
    #               --(child)-->   |        |
    #                    |         | child1 |
    #  +---------+  <-(parent)--   |        |
    #  |         |                 +--------+
    #  | parent1 |
    #  |         |                 +--------+
    #  +---------+  --(child)-->   |        |
    #                    |         | child2 |
    #               <-(parent)--   |        |
    #                              +--------+

    # try to duplicate relation
    with app.app_context():
        parent1 = Product.query.filter_by(name="parent1").first()
        child1 = Product.query.filter_by(name="child1").first()
        type_ = ProductRelationType.query.filter_by(name="child").first()

        relation = ProductRelation()
        relation.type_ = type_
        relation.self_ = parent1
        relation.other = child1

        with pytest.raises(exc.IntegrityError):
            sa.session.commit()


##__________________________________________________________________||
