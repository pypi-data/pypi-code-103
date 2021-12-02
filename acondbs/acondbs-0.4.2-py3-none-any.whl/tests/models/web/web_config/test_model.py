import json

from acondbs.db.sa import sa
from acondbs.models import WebConfig


SAMPLE_CONFIG_JSON = json.dumps(
    {
        "head_title": "Head Title",
        "toolbar_title": "Toolbar Title",
    },
    indent=2,
)


##__________________________________________________________________||
def test_column(app_empty):
    app = app_empty

    with app.app_context():
        model = WebConfig(json=SAMPLE_CONFIG_JSON)
        sa.session.add(model)
        sa.session.commit()
        id_ = model.id_
        assert id_

    with app.app_context():
        model = WebConfig.query.filter_by(id_=id_).one()
        assert model.json == SAMPLE_CONFIG_JSON


def test_repr(app_empty):
    app = app_empty

    model = WebConfig(json=SAMPLE_CONFIG_JSON)
    repr(model)

    with app.app_context():
        sa.session.add(model)
        sa.session.commit()
        id_ = model.id_

    with app.app_context():
        model = WebConfig.query.filter_by(id_=id_).one()
        repr(model)


##__________________________________________________________________||
