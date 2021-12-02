import json

import pytest

from acondbs import ops


##__________________________________________________________________||
@pytest.fixture
def app(app_empty):

    y = app_empty

    config_json = json.dumps(
        {
            "headTitle": "Head Title",
            "toolbarTitle": "Toolbar Title",
            "devtoolLoadingstate": True,
            "productCreationDialog": False,
            "productUpdateDialog": True,
            "productDeletionDialog": True,
        },
        indent=2,
    )

    with y.app_context():
        ops.save_web_config(json=config_json)
        ops.commit()

    yield y


##__________________________________________________________________||
