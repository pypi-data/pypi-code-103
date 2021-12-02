import json

from acondbs import ops
from acondbs.models import WebConfig


def test_new(app_empty):
    app = app_empty

    config_json = json.dumps(
        {
            "headTitle": "Head Title",
            "toolbarTitle": "Toolbar Title",
        },
        indent=2,
    )

    with app.app_context():
        ops.save_web_config(json=config_json)
        ops.commit()

    with app.app_context():
        model = WebConfig.query.one()
        assert model.json == config_json


def test_update(app_empty):
    app = app_empty

    config_json = json.dumps(
        {
            "headTitle": "Head Title",
            "toolbarTitle": "Toolbar Title",
        },
        indent=2,
    )

    with app.app_context():
        ops.save_web_config(json=config_json)
        ops.commit()

    config_json = json.dumps(
        {
            "headTitle": "Updated Head Title",
            "toolbarTitle": "Updated Toolbar Title",
        },
        indent=2,
    )

    with app.app_context():
        ops.save_web_config(json=config_json)
        ops.commit()

    with app.app_context():
        model = WebConfig.query.one()
        assert model.json == config_json
