import importlib
import os

from celery.schedules import crontab

from apps.task.managers import manager
from main import create_app

config_type = os.getenv('CONFIG_TYPE', 'dev')
app = create_app(config_type=config_type)
celery = app.extensions['celery'].celery

# registry tasks

try:
    importlib.import_module('apps.task.schedules.schedule')
except ModuleNotFoundError:
    print('error')


@celery.on_after_configure.connect
def add_schedule(sender, **kwargs):

    with app.app_context():
        tasks = manager.Task().list()
        beat_schedule = {}
        for task in tasks:
            beat_schedule[str(task.id)] = {
                'task': task.task,
                'schedule': crontab(hour=task.hour, minute=task.minute, day_of_week=task.day_of_week,
                                    day_of_month=task.day_of_month)
            }
        celery.conf.beat_schedule = beat_schedule
