
from apps.file.managers import manager
from apps.file.schemas import schema


from flask_restful_helper import Logic


class FileVault(Logic):
    _manager = manager.FileVault
    _schema = schema.FileVault


class FileInfo(Logic):
    _manager = manager.FileVault
    _schema = schema.FileVault
