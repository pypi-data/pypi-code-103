import os
import logging

import jinja2
from flask import g, Flask, request
from google.cloud.logging.client import Client
from google.cloud.logging.handlers.app_engine import AppEngineHandler
from gaelib.env import (is_dev,
                        get_env,
                        get_dashboard_url_prefix,
                        get_dashboard_assets_prefix,
                        get_sidebar_template,
                        get_app_or_default_prop,
                        get_twilio_account_sid,
                        get_twilio_auth_token,
                        get_twilio_verification_sid)
from gaelib import filters
from gaelib.urls import (auth_urls,
                         verification_urls,
                         dashboard_lib_urls,
                         dashboard_lib_template_dir,
                         client_logger_urls)

PARAMETER_LOGGING = get_app_or_default_prop('PARAMETER_LOGGING')

app_template_dir = os.path.abspath('./templates/')

app = Flask(__name__, template_folder=app_template_dir)

# Uncomment to debug template loading issues
# app.config['EXPLAIN_TEMPLATE_LOADING'] = True

app.jinja_loader.searchpath.append(dashboard_lib_template_dir)


@app.before_request
def log_request_info():
  """
      Logs request params before dispatching request
  """
  g.app = app

  if not PARAMETER_LOGGING:
    return

  request_data = None
  request_args = request.args.to_dict()
  request_form = request.form.to_dict()
  request_json = request.json

  if request_args:
    g.app.logger.info('Request args: ' + str(request_args))
  if request_form:
    g.app.logger.info('Request form: ' + str(request_form))
  if request_json:
    g.app.logger.info('Request json: ' + str(request_json))


@app.context_processor
def inject_global_template_vars():
  return dict(app_name=get_app_or_default_prop('APP_NAME'), dashboard_prefix=get_dashboard_url_prefix(),
              dashboard_assets_prefix=get_dashboard_assets_prefix(), env=get_env(), sidebar_template=get_sidebar_template())


def startup(auth=True, parameter_logging=False, client_logging=False, dashboard=True, verification=True):
  """The startup script to create flask app and check if
      the application is running on local server or production.
  """

  if is_dev():
    os.environ['DATASTORE_EMULATOR_HOST'] = 'localhost:8089'
    os.environ['DATASTORE_PROJECT_ID'] = 'codejedi-crypticcup-staging'
    os.environ['GOOGLE_CLOUD_PROJECT'] = 'codejedi-crypticcup-staging'
    # Dumb hack we need to run locally
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.getcwd() + \
        '/../fake_creds.json'

  gcp_client = Client(os.environ['GOOGLE_CLOUD_PROJECT'])
  gcph = AppEngineHandler(gcp_client)
  app.logger.setLevel(logging.DEBUG)
  app.logger.addHandler(gcph)

  if auth:
    app.register_blueprint(auth_urls)

  if dashboard:
    app.register_blueprint(dashboard_lib_urls)

  app.register_blueprint(filters.blueprint)

  app.secret_key = get_app_or_default_prop(
      'SESSION_SECRET')   # Used for session management

  if verification:
    app.register_blueprint(verification_urls)
    # Used for Twilio
    app.config['VERIFICATION_SID'] = get_twilio_verification_sid()
    app.config['ACCOUNT_SID'] = get_twilio_account_sid()
    app.config['AUTH_TOKEN'] = get_twilio_auth_token()

  if client_logging:
    app.register_blueprint(client_logger_urls)

  return app
