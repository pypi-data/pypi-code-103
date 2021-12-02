from pathlib import Path

from flask import Flask
from flask_cors import CORS

# This import prevents the error, ImportError: cannot import name
# 'attach_enctype_error_multidict' from partially initialized module
# 'flask.debughelpers' (most likely due to a circular import)
from flask import debughelpers  # noqa: F401

from . import _warnings  # noqa: F401
from . import _logging

##__________________________________________________________________||
DEFAULT_CONFIG_DICT = dict(
    SECRET_KEY="dev",
    SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)


##__________________________________________________________________||
def create_app(config_path=None, **kwargs):

    _logging.configure_logging()

    app = Flask(__name__, instance_relative_config=False)
    app.config.from_mapping(**DEFAULT_CONFIG_DICT)

    if config_path is not None:
        config_path = Path(config_path)
        if not config_path.is_absolute():
            # If `config_path` is relative, it is considered relative
            # to the current working directory.
            config_path = Path.cwd().joinpath(config_path)

            # Note: `app.config.from_pyfile()` treats a relative path
            # either a) relative to the top directory of the app,
            # i.e., the directory in which this file is, if
            # `instance_relative_config` is `False`, or b) relative to
            # the "instance folder", a specific directory described in
            # https://flask.palletsprojects.com/en/1.1.x/config/#instance-folders),
            # if `instance_relative_config` is `True`.

        app.config.from_pyfile(config_path, silent=False)

    if kwargs:
        app.config.from_mapping(**kwargs)

    from . import db

    db.init_app(app)

    from . import blueprint

    blueprint.init_app(app)

    from . import models

    models.init_app(app)

    CORS(app, resources={r"/*": {"origins": "*"}})

    app.logger.info('"app" initialized')
    return app


##__________________________________________________________________||

from ._version import get_versions  # noqa: E402

__version__ = get_versions()["version"]
"""str: version

The version string, e.g., "0.1.2", "0.1.2+83.ga093a20.dirty".
generated from git tags by versioneer.

Versioneer: https://github.com/warner/python-versioneer

"""

del get_versions

##__________________________________________________________________||
