# Copyright 2017 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import json

from flask import Flask
from flask import request
from flask_wtf import CSRFProtect
from flask_login import LoginManager
from flask_security import Security
from flask_security import SQLAlchemyUserDatastore

from .models import db, User, Role
from .util.helpers import LogginMiddleware
from .util.filters import register_filters

ENV_PREFIXES = 'TASKMAN', 'FLASK', 'SQLALCHEMY', 'SECURITY', 'SECRET'

user_datastore = SQLAlchemyUserDatastore(db, User, Role)


def set_default_app_config_value(config, key, value, warning=None):
    if key not in config:
        if warning:
            print(warning)
        config[key] = value


def set_app_config_defaults(config):
    set_default_app_config_value(config, 'TASKMAN_CALLBACK_METHOD', 'local')


def load_app_config(app, test_config):
    # Set default config variables
    app.config.from_mapping({
        'SQLALCHEMY_TRACK_MODIFICATIONS': False
    })

    # Load config from environment using dotenv
    import dotenv
    dotenv.load_dotenv()

    environment_config = {key: value for key, value in os.environ.items() if key.startswith(ENV_PREFIXES)}
    app.config.update(environment_config)

    # Load test config last (it overrides everything)
    if test_config is None:
        test_config = {}

    app.config.update(test_config)

    # Set the default if they are not set
    set_app_config_defaults(app.config)


#TODO: make use_sentry False by default, probably use environment variables for this...
def create_app(test_config=None, use_sentry=True):
    app = Flask(__name__)

    # Load the configuration from the environment and from test_config
    load_app_config(app, test_config)

    # Put the logging middleware in place for debugging purposes when the
    # TASKMAN_LOG_REQUEST_HEADERS configuration value is set to True.
    if app.config.get('TASKMAN_LOG_REQUEST_HEADERS') == "True":
        app.wsgi_app = LogginMiddleware(app.wsgi_app)

    # Register all custom filters.
    register_filters(app)

    # Inject instance name in all request contexts.
    #TODO: This should inject a configurable variable
    @app.context_processor
    def inject_instance_name():
        return dict(instance_name="Population Imaging Database")

    # Try to load raven (for using Sentry.io)
    if use_sentry:
        try:
            from raven.contrib.flask import Sentry
            sentry = Sentry()
            sentry.init_app(app)
        except ImportError:
            print('[WARNING] Could not load raven flask plugins, not using Sentry!')

    # Load models and add sqlalchemy to app
    db.init_app(app)

    # Load blueprints
    from .views import bp
    app.register_blueprint(bp)

    app.config['SECURITY_USER_IDENTITY_ATTRIBUTES'] = 'username'
    #TODO: make a more thorough configuration checker.
    if 'SECURITY_PASSWORD_SALT' not in app.config:
        print("Please make sure to set the SECURITY_PASSWORD_SALT to something sensible.")

    # Setting up CSRF for a mixed situation: We don't want requests with token based 
    # authentication to deal with CSRF, but we do want that with session and basic auth.
    # Read: https://flask-security-too.readthedocs.io/en/latest/patterns.html#csrf-enable-protection-for-session-auth-but-not-token-auth
    
    # We do want to use CSRF...
    app.config['WTF_CSRF_ENABLED'] = True
    # But we don't want wtf.CSRFProtect to check for CSRF early on, but it should be defined with decorators in the code.
    app.config['WTF_CSRF_CHECK_DEFAULT'] = False
    # Enable the session and but not for token based authentication
    #TODO: protection on basic auth is not enabled, please make sure something safe will be implemented.
    app.config['SECURITY_CSRF_PROTECT_MECHANISMS'] = ["session"]
    # Have a cookie sent on requests, axios understands that we are dealing with CSRF Protection.
    app.config["SECURITY_CSRF_COOKIE"] = {"key": "XSRF-TOKEN"}
    # You can't get the cookie until you are logged in.
    app.config["SECURITY_CSRF_IGNORE_UNAUTH_ENDPOINTS"] = True
    #app.config['SECURITY_CSRF_PROTECT_MECHANISMS'] = ["session", "basic"]
    app.config['SECURITY_DEFAULT_HTTP_AUTH_REALM'] = "Taskmanager Login Required"

    # Prepare the SQLAlchemy user data store and initialize flask security.
    security = Security()
    security.init_app(app, user_datastore)

    # Add REST api and health endpoint
    from .api.health import blueprint as health_blueprint
    from .api.v1 import blueprint as v1_blueprint
    app.register_blueprint(v1_blueprint, url_prefix='/api/v1')
    app.register_blueprint(health_blueprint, url_prefix='/-')

    # Setup wtf.CSRFProtect
    csrf = CSRFProtect()
    csrf.init_app(app)
    csrf.exempt(v1_blueprint)

    return app
