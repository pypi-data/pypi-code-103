from apps.task.managers import manager
from apps.task.schemas import schema

from flask_restful_helper import Logic


class Task(Logic):
    _manager = manager.Task
    _schema = schema.Task


class TaskLog(Logic):
    _manager = manager.TaskLog
    _schema = schema.TaskLog
