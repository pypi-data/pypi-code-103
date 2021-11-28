from apps.file.logics import logic
from apps.file.managers import manager
from flask_restful_helper import DBHelper
import datetime
import hashlib
import pathlib
import random

db_helper = DBHelper()


def add_file(file, filename: str):
    file_vault_manager = manager.FileVault()
    file_info_manager = manager.FileInfo()

    # 先撈一個vault
    file_vaults = file_vault_manager.list(query_args={'active': True})
    # 隨機挑一個vault
    file_vault = random.choice(file_vaults)

    file_path = _build_path()
    full_path = pathlib.Path(file_vault.base_storage_dir, file_path)

    # 先存檔案
    try:
        with open(full_path, 'w') as f:
            f.write(file)
    except Exception as e:
        raise e

    with db_helper.auto_commit():
        obj_ = {
            'filename': filename,
            'encrypted_filename': _build_encrypted_filename(filename),
            'path': file_path,
            'file_vault_id': file_vault.id
        }
        file_info_manager.create(obj_)


def _build_path():
    today = datetime.datetime.today()
    paths = today.strftime('%Y-%m-%d').split('-')

    return pathlib.Path().joinpath(*paths)


def _build_encrypted_filename(filename):
    m = hashlib.sha256()
    m.update(filename.encode('utf-8'))

    return m.hexdigest()
