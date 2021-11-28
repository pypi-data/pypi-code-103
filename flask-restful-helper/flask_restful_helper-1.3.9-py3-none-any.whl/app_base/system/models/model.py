from datetime import datetime

from main.extension import db

from flask_restful_helper.restful_helper.utils import get_uuid


class User(db.Model):
    __tablename__ = 'system_user'
    id = db.Column(db.String(36), default=get_uuid, primary_key=True, nullable=False)
    username = db.Column(db.String(length=60), nullable=False)
    password = db.Column(db.String(length=60), nullable=False)
    email = db.Column(db.String(length=100), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.now)
    is_superuser = db.Column(db.Boolean, nullable=False, default=False)
    theme = db.Column(db.Text, nullable=True)
    locale = db.Column(db.String(length=5), nullable=False, default='zh-tw')

    role_id = db.Column(db.ForeignKey('system_role.id'), nullable=True)
    role = db.relationship('Role', back_populates='users')




class Role(db.Model):
    """
    角色模組
    """
    __tablename__ = 'system_role'
    id = db.Column(db.String(32), primary_key=True, default=get_uuid, nullable=False)
    name = db.Column(db.String(50), nullable=False, comment='名稱', unique=True)
    description = db.Column(db.String(30), nullable=True)

    users = db.relationship('User', back_populates='role', uselist=True)
    api_role_privileges = db.relationship('ApiRolePrivilege', back_populates='role', uselist=True)


class Api(db.Model):
    """
    API 列表
    """
    __tablename__ = 'system_api'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(50), nullable=False, comment='名稱', unique=True)
    ch_name = db.Column(db.String(50), nullable=False, comment='名稱', unique=True)

    api_role_privileges = db.relationship('ApiRolePrivilege', back_populates='api', uselist=True)


class ApiRolePrivilege(db.Model):
    """
    API 權限模組
    """
    __tablename__ = 'system_api_role_privilege'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    privilege = db.Column(db.Integer, nullable=False)

    role_id = db.Column(db.ForeignKey('system_role.id'), nullable=False)
    api_id = db.Column(db.ForeignKey('system_api.id'), nullable=False)

    role = db.relationship('Role', back_populates='api_role_privileges')
    api = db.relationship('Api', back_populates='api_role_privileges')


class Locale(db.Model):
    """語言"""

    __tablename__ = 'system_locale'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    key = db.Column(db.String(100), nullable=False)
    zh_tw = db.Column(db.String(100), nullable=False, index=True, default='')
    zh_cn = db.Column(db.String(100), nullable=False, index=True, default='')
    en_us = db.Column(db.String(100), nullable=False, index=True, default='')
