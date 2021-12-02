from acondbs.db.sa import sa
from acondbs.models import ProductRelationType


##__________________________________________________________________||
def test_column(app_empty):
    app = app_empty

    with app.app_context():
        model = ProductRelationType(
            name="parent",
            indef_article="a",
            singular="parent",
            plural="parents",
        )
        sa.session.add(model)
        sa.session.commit()
        assert model.type_id
        type_id = model.type_id

    with app.app_context():
        model = ProductRelationType.query.filter_by(type_id=type_id).one()
        assert model.type_id == type_id
        assert model.name == "parent"
        assert model.indef_article == "a"
        assert model.singular == "parent"
        assert model.plural == "parents"


##__________________________________________________________________||
