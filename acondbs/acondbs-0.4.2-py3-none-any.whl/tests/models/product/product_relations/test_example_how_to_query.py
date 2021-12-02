from acondbs.models import Product, ProductRelation, ProductRelationType


##__________________________________________________________________||
def test_example_how_to_query(app):

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

        # Product relations with the type name "child"
        relations = (
            ProductRelation.query.join(ProductRelationType)
            .filter(ProductRelationType.name == "child")
            .all()
        )
        assert ["child", "child"] == [r.type_.name for r in relations]

        # Products with "parent"
        products = (
            Product.query.join(
                ProductRelation,
                (Product.product_id == ProductRelation.self_product_id),
            )
            .join(ProductRelationType)
            .filter(ProductRelationType.name == "parent")
            .all()
        )
        assert [child1, child2] == products

        # Products with "child"
        products = (
            Product.query.join(
                ProductRelation,
                (Product.product_id == ProductRelation.self_product_id),
            )
            .join(ProductRelationType)
            .filter(ProductRelationType.name == "child")
            .all()
        )
        assert [parent1] == products


##__________________________________________________________________||
