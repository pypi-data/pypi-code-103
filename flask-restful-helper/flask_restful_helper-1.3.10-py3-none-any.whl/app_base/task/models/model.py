from datetime import datetime

from main.extension import db


class Task(db.Model):
    """
    工作排程
    """
    __tablename__ = 'task_task'

    id = db.Column(db.Integer,autoincrement=True, primary_key=True, nullable=False)
    description = db.Column(db.String(100), nullable=True)
    task = db.Column(db.String(100), nullable=False)
    day_of_month = db.Column(db.String(10), nullable=True)
    day_of_week = db.Column(db.String(10), nullable=True)
    hour = db.Column(db.String(10), nullable=True)
    minute = db.Column(db.String(10), nullable=True)
    date_last_run = db.Column(db.DateTime, nullable=True, onupdate=datetime.now)
    state_last_run = db.Column(db.Boolean, nullable=True, default=False)
    is_running = db.Column(db.Boolean, nullable=True, default=False)


class TaskLog(db.Model):
    """
    工作排程log
    """
    __tablename__ = 'task_log'
    id = db.Column(db.Integer,autoincrement=True, primary_key=True, nullable=False)
    task_id = db.Column(db.ForeignKey('task_task.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    text = db.Column(db.Text, nullable=True)
