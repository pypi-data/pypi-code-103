from acondbs.db.sa import sa
from acondbs.models import Log


##__________________________________________________________________||
def test_column(app_empty):
    app = app_empty

    with app.app_context():
        model = Log(level="ERROR", message="an exception occurred")
        sa.session.add(model)
        sa.session.commit()
        id_ = model.id_
        assert id_

    with app.app_context():
        model = Log.query.filter_by(id_=id_).one()
        assert model.level == "ERROR"


def test_repr(app_empty):
    app = app_empty

    model = Log(level="ERROR", message="an exception occurred")
    repr(model)

    with app.app_context():
        sa.session.add(model)
        sa.session.commit()
        id_ = model.id_

    with app.app_context():
        model = Log.query.filter_by(id_=id_).one()
        repr(model)


##__________________________________________________________________||
