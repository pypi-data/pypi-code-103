from apps.file.models import model

from flask_restful_helper import Manager


class FileVault(Manager):
    _model = model.FileVault


class FileInfo(Manager):
    _model = model.FileInfo
