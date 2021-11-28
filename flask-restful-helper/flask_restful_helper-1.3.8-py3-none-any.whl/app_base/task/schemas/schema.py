from apps.task.models import model
from main.extension import ma


class Task(ma.Schema):
    class Meta:
        model = model.Task


class TaskLog(ma.Schema):
    class Meta:
        model = model.TaskLog
