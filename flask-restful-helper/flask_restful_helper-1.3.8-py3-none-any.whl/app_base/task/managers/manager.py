from apps.task.models import model

from flask_restful_helper import Manager


class Task(Manager):
    _model = model.Task


class TaskLog(Manager):
    _model = model.TaskLog
