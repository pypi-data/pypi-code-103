import pytest

from sqlalchemy import exc

from acondbs.db.sa import sa
from acondbs.models import ProductType, Product, GitHubUser


##__________________________________________________________________||
def test_product(app_empty):
    app = app_empty

    type_map = ProductType(name="map")
    map1 = Product(name="map1", type_=type_map)

    with app.app_context():
        sa.session.add(map1)
        sa.session.commit()

    with app.app_context():
        map1 = Product.query.filter_by(name="map1").one_or_none()
        assert map1 is not None
        type_map = map1.type_
        assert "map" == type_map.name
        assert [map1] == type_map.products


##__________________________________________________________________||
def test_constraint_type_required_add(app_empty):
    app = app_empty

    map1 = Product(name="map1")

    with app.app_context():
        sa.session.add(map1)
        with pytest.raises(exc.IntegrityError):
            sa.session.commit()

    with app.app_context():
        map1 = Product.query.filter_by(name="map1").one_or_none()
        assert map1 is None


##__________________________________________________________________||
def test_constraint_type_required_delete(app_empty):
    app = app_empty

    type_map = ProductType(name="map")
    map1 = Product(name="map1", type_=type_map)

    with app.app_context():
        sa.session.add(map1)
        sa.session.commit()

    # fail to delete a type with a product
    with app.app_context():
        type_map = ProductType.query.filter_by(name="map").one()
        sa.session.delete(type_map)
        with pytest.raises(exc.IntegrityError):
            sa.session.commit()

    # assert the type and the product are still there
    with app.app_context():
        map1 = Product.query.filter_by(name="map1").one()
        assert map1 is not None
        type_map = map1.type_
        assert "map" == type_map.name
        assert [map1] == type_map.products

    # delete the product
    with app.app_context():
        map1 = Product.query.filter_by(name="map1").one()
        sa.session.delete(map1)
        sa.session.commit()

    # assert the type still exists
    with app.app_context():
        type_map = ProductType.query.filter_by(name="map").one()
        assert type_map is not None
        assert [] == type_map.products

    # delete the type
    with app.app_context():
        type_map = ProductType.query.filter_by(name="map").one()
        sa.session.delete(type_map)
        sa.session.commit()


##__________________________________________________________________||
def test_git_hub_user(app_empty):
    app = app_empty

    user1 = GitHubUser(login="user1", git_hub_id="04:User1")
    user2 = GitHubUser(login="user2", git_hub_id="04:User2")

    type_map = ProductType(name="map")
    map1 = Product(name="map1", type_=type_map, posting_git_hub_user=user1)

    with app.app_context():
        sa.session.add(user1)
        sa.session.add(user2)
        sa.session.add(map1)
        sa.session.commit()

    with app.app_context():
        map1 = Product.query.filter_by(name="map1").one()
        user1 = GitHubUser.query.filter_by(login="user1").one()
        assert user1 == map1.posting_git_hub_user
        assert [map1] == user1.posted_products

    with app.app_context():
        map1 = Product.query.filter_by(name="map1").one()
        user2 = GitHubUser.query.filter_by(login="user2").one()
        map1.updating_git_hub_user = user2
        sa.session.commit()

    with app.app_context():
        map1 = Product.query.filter_by(name="map1").one()
        user2 = GitHubUser.query.filter_by(login="user2").one()
        assert user2 == map1.updating_git_hub_user
        assert [map1] == user2.updated_products


##__________________________________________________________________||
