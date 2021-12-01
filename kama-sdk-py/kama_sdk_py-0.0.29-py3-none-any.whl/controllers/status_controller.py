import json

from flask import Blueprint, jsonify, request
from k8kat.auth.kube_broker import broker

from kama_sdk.controllers import ctrl_utils
from kama_sdk.controllers.ctrl_utils import parse_json_body
from kama_sdk.core.core.config_man import config_man
from kama_sdk.utils import env_utils

controller = Blueprint('status_controller', __name__)


@controller.route('/api/ping')
def ping():
  return jsonify(ping='pong')

@controller.route('/api/echo', methods=['POST', 'PATCH'])
def echo_post():
  result = ctrl_utils.debug_parse_json_body()
  return jsonify(data=result)


@controller.route('/api/status')
def status():
  """
  Checks Wiz's status.
  :return: dict containing status details.
  """
  config_man.invalidate_cmap()

  if not is_healthy():
    broker.connect()

  return jsonify(
    sanity='2',
    app_id=config_man.get_app_id(),
    nectwiz_env=env_utils.run_env(),
    is_training_mode=config_man.is_training_mode(),
    is_healthy=is_healthy(),
    install_id=config_man.get_install_id(),
    install_token=config_man.get_install_token(),
    cluster_connection=dict(
      is_k8kat_connected=broker.is_connected,
      connect_config=broker.connect_config
    ),
    ns=config_man.get_ns(),
    ktea_config=config_man.get_ktea_config(),
    wiz_config=config_man.get_kama_config(),
    ktea_defaults=config_man.get_default_vars(),
    ktea_variables=config_man.get_user_vars()
  )


def is_healthy() -> bool:
  if broker.is_connected:
    return config_man.load_source_cmap() is not None
  else:
    return False
