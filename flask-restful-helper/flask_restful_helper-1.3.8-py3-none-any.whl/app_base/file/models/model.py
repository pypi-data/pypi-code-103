from datetime import datetime

from flask_restful_helper.restful_helper.utils import get_uuid

from main.extension import db


class FileVault(db.Model):
    __tablename__ = 'file_vault'
    id = db.Column(db.Integer, default=get_uuid, primary_key=True, nullable=False)
    base_storage_dir = db.Column(db.String(30), commnet='資料夾')
    active = db.Column(db.Boolean, nullable=False, default=True)


class FileInfo(db.Model):
    __tablename__ = 'file_info'
    id = db.Column(db.String(36), default=get_uuid, primary_key=True, nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    path = db.Column(db.String(36), nullable=False)
    encrypted_filename = db.Column(db.String(36), nullable=False)

    file_vault_id = db.Column(db.ForeignKey('file_vault.id'), nullable=False)
