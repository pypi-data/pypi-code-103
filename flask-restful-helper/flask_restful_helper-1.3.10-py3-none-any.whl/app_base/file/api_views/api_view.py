from apps.file.logics import logic

from flask_restful_helper import ApiView


class FileVault(ApiView):
    _logic = logic.FileVault


class FileInfo(ApiView):
    _logic = logic.FileInfo
