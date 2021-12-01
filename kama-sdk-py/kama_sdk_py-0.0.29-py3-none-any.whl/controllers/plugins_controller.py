from typing import Dict

from flask import Blueprint, jsonify

from kama_sdk.controllers import ctrl_utils
from kama_sdk.core.core.plugins_manager import plugins_manager
from kama_sdk.core.core.config_man import config_man, app_identifier_key, publisher_identifier_key, \
  KTEA_CONFIG_KEY, INSTALL_TOKEN_KEY, INSTALL_ID_KEY, SPACE_KW, RELOAD_KWARG
from kama_sdk.utils.logging import lwar

BASE = '/api/plugins'

controller = Blueprint('plugins_controller', __name__)


@controller.route(f"{BASE}/all")
def list_plugins():
  config_man.invalidate_cmap()
  serialized = list(map(serialize_config_space, plugins_manager.get_plugin_ids()))
  return jsonify(data=serialized)


@controller.route(f"{BASE}/all/<plugin_id>/initialize", methods=['POST'])
def initialize_plugin(plugin_id: str):
  if plugin_id in plugins_manager.get_plugin_ids():
    given_attrs = ctrl_utils.parse_json_body()

    raw_patch = {key: given_attrs.get(key) for key in auth_exp_keys}
    patch = {k: v for k, v in raw_patch.items() if v is not None}

    lwar(f"plugin init {raw_patch} -> {patch}")

    down_kwargs = {SPACE_KW: plugin_id}
    config_man.write_typed_entries(patch, **down_kwargs)
    return jsonify(data='success')
  else:
    return jsonify(error=f"no such plugin {plugin_id}"), 404


def serialize_config_space(plugin_id: str) -> Dict:
  kwargs = {SPACE_KW: plugin_id, RELOAD_KWARG: False}
  manifest = plugins_manager.get_manifest(plugin_id) or {}

  return {
    'id': plugin_id,
    'version':  manifest.get('version'),
    'app_identifier': manifest.get('app_identifier'),
    'publisher_identifier': manifest.get('publisher_identifier'),
    'install_id': config_man.get_install_id(**kwargs),
    'install_token': config_man.get_install_token(**kwargs),
    'status': config_man.get_status(**kwargs),
    'ktea': config_man.get_ktea_config(**kwargs),
  }


auth_exp_keys = [
  INSTALL_ID_KEY,
  INSTALL_TOKEN_KEY,
  KTEA_CONFIG_KEY,
  publisher_identifier_key,
  app_identifier_key
]
