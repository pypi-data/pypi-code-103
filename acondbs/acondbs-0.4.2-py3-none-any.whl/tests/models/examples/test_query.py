import pytest

from flask_sqlalchemy import BaseQuery

from acondbs.db.sa import sa
from acondbs.models import ProductType, Product

# These tests are written primarily for the developer to understand
# how models in flask_sqlalchemy work.


##__________________________________________________________________||
@pytest.fixture
def app(app):
    y = app

    type_map = ProductType(name="map")
    map1 = Product(name="map1", type_=type_map)  # noqa: F841
    map2 = Product(name="map2", type_=type_map)  # noqa: F841
    map3 = Product(name="map3", type_=type_map)  # noqa: F841

    with y.app_context():
        sa.session.add(type_map)
        sa.session.commit()

    yield y


##__________________________________________________________________||
def test_context(app):

    # query cannot be accessed outside of the app context
    with pytest.raises(RuntimeError):
        Product.query

    with app.app_context():
        Product.query


def test_query_all(app):

    with app.app_context():

        # query is an instance of BaseQuery
        query = Product.query
        assert isinstance(query, BaseQuery)

        # query.all() returns a list of products
        results = query.all()
        # e.g., [<Product 1>, <Product 2>, <Product 3>]

        assert isinstance(results[0], Product)


def test_query_filter(app):

    with app.app_context():

        # filter_by() returns an instance of BaseQuery
        query = Product.query.filter_by(name="map1")
        assert isinstance(query, BaseQuery)

        # the results are a list with one element
        results = query.all()
        assert 1 == len(results)
        assert ["map1"] == [e.name for e in results]

        # first() returns a product
        product = query.first()
        assert isinstance(product, Product)
        assert "map1" == product.name


def test_query_filter_nonexistent(app):

    with app.app_context():

        query = Product.query.filter_by(name="no-such-product")
        assert isinstance(query, BaseQuery)

        # the results are an empty list
        results = query.all()
        assert [] == results

        # first() returns None
        product = query.first()
        assert product is None


##__________________________________________________________________||
