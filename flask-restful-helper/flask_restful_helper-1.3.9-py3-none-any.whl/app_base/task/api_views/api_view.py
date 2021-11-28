from apps.task.logics import logic

from flask_restful_helper import ApiView


class Task(ApiView):
    _logic = logic.Task


class TaskLog(ApiView):
    _logic = logic.TaskLog
