from main.extension import db
from sqlalchemy.orm import backref


class Menu(db.Model):
    """左側清單"""
    __tablename__ = 'frontend_menu'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    parent_id = db.Column(db.ForeignKey('frontend_menu.id'), nullable=True)
    t_key = db.Column(db.String(50), nullable=False, comment='i18的key')
    name = db.Column(db.String(50), nullable=False, comment='名稱')
    children = db.relationship('Menu', backref=backref('parent', remote_side=[id]))
    allowed_roles = db.Column(db.Text, nullable=True, comment='權限群組')
    path = db.Column(db.String(100), nullable=True, comment='前端路由')
