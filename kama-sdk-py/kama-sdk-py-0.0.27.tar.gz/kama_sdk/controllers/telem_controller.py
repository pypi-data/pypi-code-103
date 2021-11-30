from datetime import datetime

from flask import Blueprint, jsonify

from kama_sdk.controllers.ctrl_utils import parse_json_body
from kama_sdk.core.core.config_man import config_man
from kama_sdk.core.core.types import KamafileBackup
from kama_sdk.core.telem import backups_manager
from kama_sdk.core.telem.backups_manager import TRIGGER_USER
from kama_sdk.serializers.telem_serializers import ser_kamafile_backup, ser_kamafile_backup_full

controller = Blueprint('telem_controller', __name__)

BASE = '/api/telem'


@controller.route(f'{BASE}/config_backups/index')
def config_backups_index():
  records = backups_manager.get_all() or []
  return jsonify(data=list(map(ser_kamafile_backup, records)))


@controller.route(f'{BASE}/config_backups/detail/<config_id>')
def get_config_backups(config_id: str):
  if record := backups_manager.find_by_id(config_id):
    return jsonify(data=ser_kamafile_backup_full(record))
  else:
    return jsonify(error='dne'), 404


@controller.route(f'{BASE}/config_backups/new', methods=['POST'])
def create_config_backup():
  attrs = parse_json_body()
  backup_data = config_man.read_spaces()
  config_backup = KamafileBackup(
    name=attrs.get('name') or '',
    trigger=TRIGGER_USER,
    data=backup_data,
    timestamp=str(datetime.now())
  )

  backups_manager.create(config_backup)
  return jsonify(status='success', record=config_backup)
