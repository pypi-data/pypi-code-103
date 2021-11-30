import os
from argparse import ArgumentParser
from typing import Dict

from flask import Flask, jsonify, request
from flask_cors import CORS
from k8kat.auth.kube_broker import BrokerConnException

from kama_sdk.cli import cli_helper
from kama_sdk.controllers import operations_controller, status_controller, \
  app_controller, variables_controller, releases_controller, \
  telem_controller, injections_controller, actions_controller, plugins_controller, view_specs_controller, \
  resources_controller, health_controller
from kama_sdk.core.core.config_man import coerce_ns
from kama_sdk.utils import env_utils


def get_meta() -> Dict:
  return {'name': MODE_NAME, 'info': 'Start the server'}


def register_arg_parser(parser: ArgumentParser):
  parser.add_argument(
    f"--{PORT_FLAG}",
    help=f"KAMA prototype server port, defaults to 5000"
  )


def run(options):
  cli_helper.start_engines()
  cli_helper.handle_ns(options, MODE_NAME, allow_empty=False)
  port = int(options.get(PORT_FLAG) or 5000)
  app.config["cmd"] = ["bash"]
  app.config['JSON_SORT_KEYS'] = False
  app.run(host='0.0.0.0', port=port, extra_files=['./**/*.yaml'])


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY')


controllers = [
  status_controller,
  operations_controller,
  app_controller,
  view_specs_controller,
  resources_controller,
  telem_controller,
  releases_controller,
  variables_controller,
  injections_controller,
  actions_controller,
  plugins_controller,
  health_controller
]

for controller in controllers:
  app.register_blueprint(controller.controller)


CORS(app)


@app.errorhandler(BrokerConnException)
def all_exception_handler(error):
  return jsonify(dict(
    error='could not connect to Kubernetes API',
    reason=str(error)
  )), 500


@app.before_request
def read_dev_ns():
  coerced_ns = request.headers.get('Appns')
  if coerced_ns:
    if env_utils.is_out_of_cluster():
      coerce_ns(coerced_ns)
    else:
      print(f"[kama_sdk::server] set-ns from header env={env_utils.run_env()}!")


MODE_NAME = "server"
PORT_FLAG = "port"