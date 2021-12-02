import pytest

from acondbs.db.sa import sa
from acondbs.models import ProductType, Product, ProductFilePath


##__________________________________________________________________||
@pytest.fixture
def app(app_empty):

    y = app_empty

    # product --- path1
    #          |
    #          +- path2
    type1 = ProductType(name="type1")
    product = Product(name="product", type_=type1)
    path1 = ProductFilePath(path="/path1")
    path2 = ProductFilePath(path="/path2")
    product.paths = [path1, path2]

    # commit
    with y.app_context():
        sa.session.add(product)
        sa.session.commit()
    yield y


##__________________________________________________________________||
def test_relations(app):

    with app.app_context():
        product = Product.query.filter_by(name="product").one_or_none()
        assert "product" == product.name
        assert 2 == len(product.paths)
        path1, path2 = product.paths
        assert "/path1" == path1.path
        assert "/path2" == path2.path
        assert product is path1.product
        assert product is path2.product


def test_delete_product(app):

    with app.app_context():
        product = Product.query.filter_by(name="product").one_or_none()
        sa.session.delete(product)
        sa.session.commit()

    with app.app_context():
        product = Product.query.filter_by(name="product").one_or_none()
        assert product is None
        assert [] == ProductFilePath.query.all()


def test_delete_path(app):

    with app.app_context():
        path1 = ProductFilePath.query.filter_by(path="/path1").one_or_none()
        sa.session.delete(path1)
        sa.session.commit()

    with app.app_context():
        product = Product.query.filter_by(name="product").one_or_none()
        assert product is not None
        path2 = ProductFilePath.query.filter_by(path="/path2").one_or_none()
        assert [path2] == ProductFilePath.query.all()

        sa.session.delete(path2)
        sa.session.commit()

    with app.app_context():
        product = Product.query.filter_by(name="product").one_or_none()
        assert product is not None
        assert [] == ProductFilePath.query.all()


##__________________________________________________________________||
def test_repr(app_empty):
    app = app_empty
    path = ProductFilePath(path="/abcdef/abcdef/abcdef/abcdef/abcdef/abcdef/path.txt")
    assert repr(path) == "<ProductFilePath '...f/abcdef/path.txt'>"
    path = ProductFilePath(path="path.txt")
    assert repr(path) == "<ProductFilePath 'path.txt'>"
    path = ProductFilePath()
    assert repr(path) == "<ProductFilePath None>"

##__________________________________________________________________||
