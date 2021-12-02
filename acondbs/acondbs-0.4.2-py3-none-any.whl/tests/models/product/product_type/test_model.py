from acondbs.db.sa import sa
from acondbs.models import ProductType


##__________________________________________________________________||
def test_column(app_empty):
    app = app_empty

    with app.app_context():
        model = ProductType(
            name="map",
            order=2,
            indef_article="a",
            singular="map",
            plural="maps",
            icon="mdi-map",
        )
        sa.session.add(model)
        sa.session.commit()
        assert model.type_id
        type_id = model.type_id

    with app.app_context():
        model = ProductType.query.filter_by(type_id=type_id).one()
        assert model.type_id == type_id
        assert model.name == "map"
        assert model.order == 2
        assert model.indef_article == "a"
        assert model.singular == "map"
        assert model.plural == "maps"
        assert model.icon == "mdi-map"


def test_repr(app_empty):
    app = app_empty

    model = ProductType(name="map")
    repr(model)

    with app.app_context():
        sa.session.add(model)
        sa.session.commit()
        type_id = model.type_id

    with app.app_context():
        model = ProductType.query.filter_by(type_id=type_id).one()
        repr(model)


##__________________________________________________________________||
