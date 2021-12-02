from acondbs.db.sa import sa
from acondbs.models import ProductType, Product

# These tests are written primarily for the developer to understand
# how models in flask_sqlalchemy work.


##__________________________________________________________________||
def test_simple(app):
    """A simple test of adding an object"""

    with app.app_context():

        # the number of the product types is zero initially
        assert 0 == len(ProductType.query.all())

    # this instantiation doesn't need be within a app context
    type1 = ProductType(name="type1")

    with app.app_context():
        sa.session.add(type1)
        sa.session.commit()

    with app.app_context():

        # the number of the product types is increased by one
        assert 1 == len(ProductType.query.all())

        # the new product type can be retrieved in a different app context
        type1_ = ProductType.query.filter_by(name="type1").one_or_none()
        assert isinstance(type1_, ProductType)


##__________________________________________________________________||
def test_python_object(app):
    """A simple test about Python object"""

    type1 = ProductType(name="type1")

    with app.app_context():
        sa.session.add(type1)
        sa.session.commit()

        type1_ = ProductType.query.filter_by(name="type1").first()

        # the query returns the same Python object
        assert type1 is type1_

    with app.app_context():
        type1_ = ProductType.query.filter_by(name="type1").first()

        # In a different app context, no longer the same Python object
        assert type1 is not type1_


##__________________________________________________________________||
def test_primary_key(app):
    """A simple test about the primary key"""

    type1 = ProductType(name="type1")

    # The primary key (type_id) is None at this point
    assert type1.type_id is None

    with app.app_context():
        sa.session.add(type1)
        sa.session.commit()

        # After the commit, type_id is automatically assigned
        type_id = type1.type_id
        assert type_id is not None

    with app.app_context():

        # The object can be retrived by the product_id in another context
        type1 = ProductType.query.filter_by(type_id=type_id).first()
        assert "type1" == type1.name


##__________________________________________________________________||
def test_relation(app):
    """A simple test of adding an object with relation"""

    type1 = ProductType(name="type1")
    product1 = Product(name="product1", type_=type1)

    # The relation has been already established
    assert type1 is product1.type_
    assert [product1] == type1.products

    # The primary and foreign keys are still None
    assert type1.type_id is None
    assert product1.product_id is None
    assert product1.type_id is None

    with app.app_context():
        sa.session.add(product1)
        sa.session.commit()

        # The primary keys are assigned
        assert type1.type_id is not None
        assert product1.product_id is not None

        # The foreign key is correctly set
        assert product1.type_id == type1.type_id

    with app.app_context():
        product1 = Product.query.filter_by(name="product1").first()

        # The relation is preserved in a different app context
        type1 = product1.type_
        assert "type1" == type1.name
        assert product1 is type1.products[0]
        assert product1.type_id == type1.type_id


##__________________________________________________________________||
