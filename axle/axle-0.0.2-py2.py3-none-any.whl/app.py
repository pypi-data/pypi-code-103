import logging
import logging.config
import inspect

from flask import Flask

from .exception import CatchableException
#from .database import connect
from . import config
from . import blueprints
from . import repositories

from .util import CustomJSONEncoder

def create_app(name = None, cfg = None):
    if cfg is None:
        cfg = config.load_config()

    if name is None:
        name = __name__

    if 'logging' in cfg:
        logging.config.dictConfig(cfg['logging'])

    app = Flask(name, **cfg['flask'])
    app.config['RESTFUL_JSON'] = {
        'cls': CustomJSONEncoder
    }
    app.site_config = cfg

    app.repositories = []
    repo_config = cfg['repository']
    repo_class = repo_config['class']
    if repo_class.startswith("_"):
        raise ValueError("Repository class names cannot start with '_'")
    if not hasattr(repositories, repo_class):
        raise ValueError(f"Invalid repository class: {repo_class}")

    Repo = getattr(repositories, repo_class)

    if inspect.isabstract(Repo):
        raise ValueError(f"Cannot instantiate abstract repository class: {Repo}")

    repo_spec = repo_config.get('spec', {})
    print(repo_spec, repo_config)
    app.repositories.append(Repo(**repo_spec))

    app.jinja_options.update(cfg['jinja2'])
    #app.dbengine, app.dbsession_factory = connect(cfg['database'])
    #app.session = None

    app.register_blueprint(blueprints.Static.blueprint, url_prefix='/static')
    app.register_blueprint(blueprints.Index.blueprint, url_prefix='/simple')

    @app.before_request
    def log_request_info():
        from flask import request
        app.logger.debug(f'Got {request.method} request with mimetype: {request.mimetype} for {request.full_path}')
        headers = []
        for name, value in request.headers:
            headers.append((name, value))
        app.logger.debug(f'Header: {headers}')

#    app.json_encoder = CustomJSONEncoder

#    @app.errorhandler(CatchableException)
#    def exception_to_error_handler(e):
#        return render_template("pages/exception.html", error_message=repr(e))

    return app
