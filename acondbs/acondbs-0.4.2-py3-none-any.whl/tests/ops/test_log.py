from acondbs import ops

from acondbs.models import Log


def test_create(app):
    with app.app_context():
        count = Log.query.count()
        model = ops.create_log(level="ERROR", message="An exception occurred")
        assert model.message == "An exception occurred"
        ops.commit()
        id_ = model.id_
        assert id_

    with app.app_context():
        assert Log.query.count() == (count + 1)
        model = Log.query.filter_by(id_=id_).one()
        assert model.message == "An exception occurred"


def test_delete(app):
    with app.app_context():
        model = ops.create_log(level="ERROR", message="To be deleted")
        ops.commit()
        id_ = model.id_

    with app.app_context():
        count = Log.query.count()
        ops.delete_log(id_=id_)
        ops.commit()

    with app.app_context():
        assert Log.query.count() == (count - 1)
        model = Log.query.filter_by(id_=id_).one_or_none()
        assert model is None
