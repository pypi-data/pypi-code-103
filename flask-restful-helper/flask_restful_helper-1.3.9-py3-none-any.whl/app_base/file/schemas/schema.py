

from apps.file.models import model
from main.extension import ma


class FileVault(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = model.FileVault


class FileInfo(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = model.FileInfo
