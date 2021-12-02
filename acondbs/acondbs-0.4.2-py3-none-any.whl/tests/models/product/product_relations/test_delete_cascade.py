from acondbs.db.sa import sa
from acondbs.models import Product, ProductRelation


##__________________________________________________________________||
def test_cascade_delete_children(app):

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

    # delete child1
    with app.app_context():
        child1 = Product.query.filter_by(name="child1").one_or_none()
        sa.session.delete(child1)
        sa.session.commit()

    #
    #
    #
    #  +---------+
    #  |         |
    #  | parent1 |
    #  |         |                 +--------+
    #  +---------+  --(child)-->   |        |
    #                    |         | child2 |
    #               <-(parent)--   |        |
    #                              +--------+

    # assert
    with app.app_context():

        parent1 = Product.query.filter_by(name="parent1").one_or_none()
        child1 = Product.query.filter_by(name="child1").one_or_none()
        child2 = Product.query.filter_by(name="child2").one_or_none()

        assert parent1 is not None
        assert child1 is None
        assert child2 is not None

        relations = ProductRelation.query.all()
        assert 2 == len(relations)

        assert 1 == len(parent1.relations)
        assert child2 == parent1.relations[0].other
        assert parent1 == child2.relations[0].other
        assert parent1.relations[0].reverse == child2.relations[0]

    # delete child2
    with app.app_context():
        child2 = Product.query.filter_by(name="child2").one_or_none()
        sa.session.delete(child2)
        sa.session.commit()

    #
    #  +---------+
    #  |         |
    #  | parent1 |
    #  |         |
    #  +---------+
    #

    # assert
    with app.app_context():

        parent1 = Product.query.filter_by(name="parent1").one_or_none()
        child1 = Product.query.filter_by(name="child1").one_or_none()
        child2 = Product.query.filter_by(name="child2").one_or_none()

        assert parent1 is not None
        assert child1 is None
        assert child2 is None

        relations = ProductRelation.query.all()
        assert 0 == len(relations)

        assert 0 == len(parent1.relations)


##__________________________________________________________________||
def test_cascade_delete_parent(app):

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

    # delete parent1
    with app.app_context():
        parent1 = Product.query.filter_by(name="parent1").first()
        sa.session.delete(parent1)
        sa.session.commit()

    #                              +--------+
    #                              |        |
    #                              | child1 |
    #                              |        |
    #                              +--------+
    #
    #                              +--------+
    #                              |        |
    #                              | child2 |
    #                              |        |
    #                              +--------+

    # assert
    with app.app_context():

        parent1 = Product.query.filter_by(name="parent1").one_or_none()
        child1 = Product.query.filter_by(name="child1").one_or_none()
        child2 = Product.query.filter_by(name="child2").one_or_none()

        assert parent1 is None
        assert child1 is not None
        assert child2 is not None

        relations = ProductRelation.query.all()
        assert 0 == len(relations)


##__________________________________________________________________||
def test_cascade_delete_relations(app):

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

    # delete the relation from child1 to parent1
    with app.app_context():
        child1 = Product.query.filter_by(name="child1").one_or_none()
        sa.session.delete(child1.relations[0])
        sa.session.commit()

    #                              +--------+
    #                              |        |
    #                              | child1 |
    #  +---------+                 |        |
    #  |         |                 +--------+
    #  | parent1 |
    #  |         |                 +--------+
    #  +---------+  --(child)-->   |        |
    #                    |         | child2 |
    #               <-(parent)--   |        |
    #                              +--------+

    # assert
    with app.app_context():

        parent1 = Product.query.filter_by(name="parent1").one_or_none()
        child1 = Product.query.filter_by(name="child1").one_or_none()
        child2 = Product.query.filter_by(name="child2").one_or_none()

        assert parent1 is not None
        assert child1 is not None
        assert child2 is not None

        relations = ProductRelation.query.all()
        assert 2 == len(relations)

        assert 1 == len(parent1.relations)
        assert child2 == parent1.relations[0].other
        assert parent1 == child2.relations[0].other
        assert parent1.relations[0].reverse == child2.relations[0]

    # delete the relation from parent1 to child2
    with app.app_context():
        parent1 = Product.query.filter_by(name="parent1").one_or_none()
        sa.session.delete(parent1.relations[0])
        sa.session.commit()

    #                              +--------+
    #                              |        |
    #                              | child1 |
    #  +---------+                 |        |
    #  |         |                 +--------+
    #  | parent1 |
    #  |         |                 +--------+
    #  +---------+                 |        |
    #                              | child2 |
    #                              |        |
    #                              +--------+

    # assert
    with app.app_context():

        parent1 = Product.query.filter_by(name="parent1").one_or_none()
        child1 = Product.query.filter_by(name="child1").one_or_none()
        child2 = Product.query.filter_by(name="child2").one_or_none()

        assert parent1 is not None
        assert child1 is not None
        assert child2 is not None

        relations = ProductRelation.query.all()
        assert 0 == len(relations)


##__________________________________________________________________||
