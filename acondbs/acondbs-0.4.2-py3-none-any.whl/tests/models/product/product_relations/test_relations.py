from acondbs.models import Product


##__________________________________________________________________||
def test_relations(app):

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

    with app.app_context():
        parent1 = Product.query.filter_by(name="parent1").first()
        child1 = Product.query.filter_by(name="child1").first()
        child2 = Product.query.filter_by(name="child2").first()

        assert 2 == len(parent1.relations)
        assert 1 == len(child1.relations)
        assert 1 == len(child2.relations)

        assert "child" == parent1.relations[0].type_.name
        assert "child" == parent1.relations[1].type_.name
        assert "parent" == child1.relations[0].type_.name
        assert "parent" == child2.relations[0].type_.name

        assert child1 is parent1.relations[0].other
        assert child2 is parent1.relations[1].other

        assert parent1 is child1.relations[0].other
        assert parent1 is child2.relations[0].other

        assert parent1.relations[0] is child1.relations[0].reverse
        assert parent1.relations[0].reverse is child1.relations[0]

        assert parent1.relations[1] is child2.relations[0].reverse
        assert parent1.relations[1].reverse is child2.relations[0]


##__________________________________________________________________||
