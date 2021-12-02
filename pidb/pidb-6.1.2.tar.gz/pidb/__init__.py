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

__version__ = '6.1.2'
import base64
import os
from typing import Union

import bleach
from flask import Flask
from flask_babelex import Babel
from flask_mail import Mail
from flask import request
from flask_wtf import CSRFProtect
from flask_login import LoginManager
from flask_security import Security
from flask_security import SQLAlchemyUserDatastore
from flask_security import uia_email_mapper
from flask_security.signals import user_registered


from .models import db, User, Role
from .util.helpers import LogginMiddleware
from .util.filters import register_filters
from .auth.forms import AuthLoginForm, AuthRegisterForm

ENV_PREFIXES = 'PIDB_', 'FLASK_', 'SQLALCHEMY_', 'SECURITY_', 'SECRET_', 'MAIL_'

user_datastore = SQLAlchemyUserDatastore(db, User, Role)


def uia_username_mapper(identity: str) -> str:
    # we allow pretty much anything - but we bleach it.
    return bleach.clean(identity, strip=True)


def set_default_config_value(config, key, value, warning=None):
    if key not in config:
        if warning:
            print(warning)
        config[key] = value


def convert_to_bool(value: str) -> Union[str, bool]:
    if not isinstance(value, str):
        return value

    if value.lower() == 'true':
        return True
    elif value.lower() == 'false':
        return False
    else:
        return value


def set_app_config_defaults(config):
    # INSTANCE NAME
    set_default_config_value(config, 'PIDB_INSTANCE_NAME', 'Population Imaging Database')
    set_default_config_value(config, 'PIDB_PROJECT_NAME', 'default_project')

    # EMAIL RELATED PARAMETERS
    set_default_config_value(
        config, 'PIDB_EMAIL_FROM', 'pidb@localhost',
        '[WARNING] Could not find PIDB_EMAIL_FROM, assuming pidb@localhost'
    )
    set_default_config_value(
        config, 'PIDB_EMAIL_TO', '',
        '[WARNING] Could not find PIDB_EMAIL_TO, assuming ""'
    )
    set_default_config_value(config, 'PIDB_EMAIL_PREFIX', '[PIDB]')

    # Configurable security defaults
    set_default_config_value(config, "SECURITY_REGISTERABLE", True)
    set_default_config_value(config, "SECURITY_CHANGEABLE", True)
    set_default_config_value(config, "SECURITY_RECOVERABLE", True)
    set_default_config_value(config, "SECURITY_CONFIRMABLE", True)


def load_app_config(app, test_config):
    # Set default config variables
    app.config.from_mapping({
        'SQLALCHEMY_TRACK_MODIFICATIONS': False
    })

    # Load config from environment using dotenv
    import dotenv
    dotenv.load_dotenv()

    environment_config = {key: value for key, value in os.environ.items() if key.startswith(ENV_PREFIXES)}

    # Filter out TRUE and FALSE and convert them to booleans to allow for setting flags
    environment_config = {k: convert_to_bool(v) for k, v in environment_config.items()}
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
    # PIDB_LOG_REQUEST_HEADERS configuration value is set to True.
    if app.config.get('PIDB_LOG_REQUEST_HEADERS'):
        app.wsgi_app = LogginMiddleware(app.wsgi_app)

    # Register all custom filters.
    register_filters(app)

    with app.open_resource('static/img/logo.png') as fh:
        logo_data = {'base64': base64.b64encode(fh.read()).decode()}

    # Inject instance name in all request contexts.
    @app.context_processor
    def inject_instance_name():
        return dict(
            instance_name=app.config['PIDB_INSTANCE_NAME'],
            project_name=app.config['PIDB_PROJECT_NAME'],
            logo_data=logo_data,
        )

    # Try to load raven (for using Sentry.io)
    if use_sentry:
        try:
            import sentry_sdk
            from sentry_sdk.integrations.flask import FlaskIntegration
            sentry_sdk.init(release=__version__, integrations=[FlaskIntegration()])
        except ImportError:
            print('[WARNING] Could not load sentry_sdk plugins, not using Sentry!')
    # Load models and add sqlalchemy to app
    

    # Load models and add sqlalchemy to app
    db.init_app(app)

    # Load blueprints
    from .views import bp
    app.register_blueprint(bp)

    # Set the cookie name to something that is identifiable and does not mess up the sessions set by other flask apps.
    cookie_name = f"{app.config['PIDB_INSTANCE_NAME']}--{app.config['PIDB_PROJECT_NAME']}".replace(" ", "-").lower()
    app.config['SESSION_COOKIE_NAME'] = cookie_name

    app.config['SECURITY_USER_IDENTITY_ATTRIBUTES'] = [
        {"email": {"mapper": uia_email_mapper, "case_insensitive": True}},
        {"username": {"mapper": uia_username_mapper, "case_insensitive": False}},
    ]

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
    app.config['SECURITY_DEFAULT_HTTP_AUTH_REALM'] = f"{app.config['PIDB_INSTANCE_NAME']} {app.config['PIDB_PROJECT_NAME']}"

    # Prepare the SQLAlchemy user data store and initialize flask security.
    security = Security(
        login_form=AuthLoginForm,
        confirm_register_form=AuthRegisterForm
    )

    security.init_app(app, user_datastore)

    # Add handler for default user role
    @user_registered.connect_via(app)
    def user_registered_handler(app, user, confirm_token, form_data):
        # Give default user role but deactivate account for verification
        default_role = user_datastore.find_role('user')
        user.active = False
        user_datastore.add_role_to_user(user, default_role)
        db.session.commit()

    # Setup Flask Mai
    mail = Mail()
    mail.init_app(app)

    # Setup Flask Babel
    babel = Babel()
    babel.init_app(app)

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
