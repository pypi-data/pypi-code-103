import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List


flash_path = '/tmp/nmachine-telem-flash.json'


def prep_open_flash():
  filename = Path(flash_path)
  filename.touch(exist_ok=True)


def clear():
  prep_open_flash()
  os.remove(flash_path)


def write_collection(coll_id: str, records: List[Dict]):
  prep_open_flash()
  with open(flash_path, 'w+') as file:
    contents: Dict = json.loads(file.read() or '{}')
    contents[coll_id] = records
    file.write(json.dumps(contents))


def read_collection(coll_id: str) -> List[Dict]:
  prep_open_flash()
  with open(flash_path, 'r') as file:
    contents: Dict = json.loads(file.read() or '{}')
    return contents.get(coll_id, [])


def push_record(coll_id: str, record: Dict):
  collection = read_collection(coll_id)
  write_collection(coll_id, [
    *collection,
    sanitize_item(record)
  ])


def sanitize_item(record: Dict) -> Dict:
  new_record = {}
  for key, value in record.items():
    if isinstance(value, Dict):
      new_record[key] = json.dumps(value)
    elif isinstance(value, datetime):
      new_record[key] = str(value)
    else:
      new_record[key] = value
  return new_record
