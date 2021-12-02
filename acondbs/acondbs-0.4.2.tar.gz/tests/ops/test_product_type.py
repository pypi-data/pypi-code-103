import pytest

from sqlalchemy import exc

from acondbs import ops
from acondbs.models import ProductType, TypeFieldAssociation


##__________________________________________________________________||
def test_fixture(app):
    with app.app_context():
        assert ProductType.query.count() == 2


##__________________________________________________________________||
params = [
    pytest.param(None, id="none"),
    pytest.param([], id="empty"),
    pytest.param([2], id="one"),
    pytest.param([1, 3, 4], id="multiple"),
    pytest.param([4, 1, 3], id="unsorted"),
    pytest.param([1, 3, 3, 4, 4, 4], id="duplicate"),
    pytest.param([4, 4, 3, 1, 3], id="unsorted-duplicate"),
]


@pytest.mark.parametrize("field_ids", params)
def test_create(app, field_ids):

    with app.app_context():
        count = ProductType.query.count()
        model = ops.create_product_type(
            name="derived_map",
            field_ids=field_ids,
        )
        assert model.name == "derived_map"
        ops.commit()
        type_id = model.type_id
        assert type_id

    with app.app_context():
        assert ProductType.query.count() == (count + 1)
        model = ProductType.query.filter_by(type_id=type_id).one()
        assert model.name == "derived_map"
        expected_field_ids = sorted(set(field_ids)) if field_ids else []
        actual_field_ids = [f.field.field_id for f in model.fields]
        assert actual_field_ids == expected_field_ids


params = [
    pytest.param([1, 3, 4, 88], id="non-existent"),
]


@pytest.mark.parametrize("field_ids", params)
def test_create_error(app, field_ids):

    with app.app_context():
        count = ProductType.query.count()
        with pytest.raises(exc.NoResultFound):
            model = ops.create_product_type(
                name="derived_map",
                field_ids=field_ids,
            )
            ops.commit()

    with app.app_context():
        assert ProductType.query.count() == count
        model = ProductType.query.filter_by(name="derived_map").one_or_none()
        assert model is None


##__________________________________________________________________||
params = [
    pytest.param(None, [1, 2, 3, 7, 9], id="none"),
    pytest.param([], [], id="empty"),
    pytest.param([2], [2], id="removed"),
    pytest.param([1, 2, 3, 4, 5], [1, 2, 3, 4, 5], id="added"),
    pytest.param([1, 4, 5], [1, 4, 5], id="removed-added"),
    pytest.param(
        [4, 5, 5, 5, 1, 4, 5, 1, 1],
        [1, 4, 5],
        id="removed-added-unsorted-duplicate",
    ),
]


@pytest.mark.parametrize("field_ids, expected_field_ids", params)
def test_update(app, field_ids, expected_field_ids):

    type_id = 2

    with app.app_context():
        count = TypeFieldAssociation.query.count()
        model = ProductType.query.filter_by(type_id=type_id).one()
        expected_len_change = len(model.fields) - len(expected_field_ids)

    with app.app_context():
        model = ops.update_product_type(
            type_id=type_id, name="compass", field_ids=field_ids
        )
        ops.commit()
        assert model.name == "compass"

    with app.app_context():
        model = ProductType.query.filter_by(type_id=type_id).one()
        assert model.name == "compass"
        actual_field_ids = [f.field.field_id for f in model.fields]
        assert actual_field_ids == expected_field_ids

        # assert unused TypeFieldAssociation is deleted
        actual_len_change = count - TypeFieldAssociation.query.count()
        assert expected_len_change == actual_len_change


params = [
    pytest.param([2, 4, 88], id="non-existent"),
]


@pytest.mark.parametrize("field_ids", params)
def test_update_error(app, field_ids):

    type_id = 2

    with app.app_context():
        count = TypeFieldAssociation.query.count()

    with app.app_context():
        with pytest.raises(exc.NoResultFound):
            model = ops.update_product_type(
                type_id=type_id,
                name="compass",
                field_ids=field_ids,
            )
            ops.commit()
            # commit() won't be called because of the exception

    with app.app_context():
        model = ProductType.query.filter_by(type_id=type_id).one()
        assert model.name == "beam"
        actual_field_ids = [f.field.field_id for f in model.fields]
        expected_field_ids = [1, 2, 3, 7, 9]
        assert actual_field_ids == expected_field_ids

        assert TypeFieldAssociation.query.count() == count


##__________________________________________________________________||
def test_delete(app):

    with app.app_context():
        model = ops.create_product_type(
            name="to_be_deleted",
            field_ids=[1, 4, 5],
        )
        ops.commit()
        type_id = model.type_id

    with app.app_context():
        count = ProductType.query.count()
        model = ops.delete_product_type(type_id=type_id)
        ops.commit()

    with app.app_context():
        model = ProductType.query.filter_by(type_id=type_id).one_or_none()
        assert model is None
        assert ProductType.query.count() == (count - 1)


##__________________________________________________________________||
