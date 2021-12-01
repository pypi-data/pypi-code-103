from typing import Dict

from kama_sdk.core.core.types import KamafileBackup
from kama_sdk.utils.utils import deep_get


def poly_space_extract(root: Dict, key: str, bkp=None):
  try:
    return {k: deep_get(v, key) or bkp for k, v in root.items()}
  except:
    return {}

def ser_kamafile_backup(record: KamafileBackup) -> Dict:
  data: Dict = record.get('data', {})

  return dict(
    id=str(record.get('_id')),
    name=record.get('name'),
    trigger=record.get('trigger'),
    statuses=poly_space_extract(data, 'status'),
    ktea_versions=poly_space_extract(data, 'ktea.version'),
    kama_versions=poly_space_extract(data, 'kama.version'),
    timestamp=record.get('timestamp')
  )


def ser_kamafile_backup_full(record: Dict) -> Dict:
  return dict(
    **ser_kamafile_backup(record),
    config=record.get('config', {})
  )
