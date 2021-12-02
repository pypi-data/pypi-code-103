import pytest

from sqlalchemy import exc

from acondbs.db.sa import sa
from acondbs.models import Product, ProductRelationType


##__________________________________________________________________||
def test_delete_type(app):
    """assert ProductRelationType can only be deleted if relations of the
    type don't exist

    """

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

    # attempt to delete the relation type "parent"
    with app.app_context():
        relation_type_parent = ProductRelationType.query.filter_by(
            name="parent"
        ).one_or_none()
        sa.session.delete(relation_type_parent)
        with pytest.raises(exc.IntegrityError):
            sa.session.commit()

    # assert the relation type and the relations of this type still exist
    with app.app_context():
        relation_type_parent = ProductRelationType.query.filter_by(
            name="parent"
        ).one_or_none()
        assert relation_type_parent is not None
        assert 2 == len(relation_type_parent.relations)

    # delete the relations "parent"
    with app.app_context():
        relation_type_parent = ProductRelationType.query.filter_by(
            name="parent"
        ).one_or_none()
        for r in relation_type_parent.relations:
            sa.session.delete(r)
        sa.session.commit()

    # assert the relations "parent" and their reverse relations "child" are deleted.
    # assert the relation types still exist
    with app.app_context():
        relation_type_parent = ProductRelationType.query.filter_by(
            name="parent"
        ).one_or_none()
        assert relation_type_parent is not None
        assert 0 == len(relation_type_parent.relations)
        relation_type_child = ProductRelationType.query.filter_by(
            name="child"
        ).one_or_none()
        assert relation_type_child is not None
        assert 0 == len(relation_type_child.relations)

    # now, delete the relations type "parent"
    with app.app_context():
        relation_type_parent = ProductRelationType.query.filter_by(
            name="parent"
        ).one_or_none()
        sa.session.delete(relation_type_parent)
        sa.session.commit()

    # assert the relation types, both "parent" and its reverse "child", are deleted
    with app.app_context():
        relation_type_parent = ProductRelationType.query.filter_by(
            name="parent"
        ).one_or_none()
        assert relation_type_parent is None
        relation_type_child = ProductRelationType.query.filter_by(
            name="child"
        ).one_or_none()
        assert relation_type_child is None

    # assert Products still exist
    with app.app_context():
        parent1 = Product.query.filter_by(name="parent1").one_or_none()
        child1 = Product.query.filter_by(name="child1").one_or_none()
        child2 = Product.query.filter_by(name="child2").one_or_none()

        assert parent1 is not None
        assert child1 is not None
        assert child2 is not None


##__________________________________________________________________||
