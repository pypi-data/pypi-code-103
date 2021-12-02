from acondbs import ops

from acondbs.models import ProductFilePath


def test_create(app):
    with app.app_context():
        count = ProductFilePath.query.count()
        model = ops.create_product_file_path(path="/new/path")
        assert model.path == "/new/path"
        ops.commit()
        path_id = model.path_id
        assert path_id

    with app.app_context():
        assert ProductFilePath.query.count() == (count + 1)
        model = ProductFilePath.query.filter_by(path_id=path_id).one()
        assert model.path == "/new/path"


def test_updated(app):
    with app.app_context():
        count = ProductFilePath.query.count()

        model = ProductFilePath.query.first()
        path_id = model.path_id
        assert model.path != "/new/path"

        model = ops.update_product_file_path(path_id=path_id, path="/new/path")
        assert model.path == "/new/path"

        ops.commit()

    with app.app_context():
        assert ProductFilePath.query.count() == count
        model = ProductFilePath.query.filter_by(path_id=path_id).one()
        assert model.path == "/new/path"


def test_delete(app):
    with app.app_context():
        model = ops.create_product_file_path(path="/to/delete")
        ops.commit()
        path_id = model.path_id

    with app.app_context():
        count = ProductFilePath.query.count()
        model = ops.delete_product_file_path(path_id=path_id)
        ops.commit()

    with app.app_context():
        assert ProductFilePath.query.count() == (count - 1)
        model = ProductFilePath.query.filter_by(path_id=path_id).one_or_none()
        assert model is None
