from celery import Celery as BaseCelery, _state


class Celery(BaseCelery):
    def __init__(self, app=None):
        self.original_register_app = _state._register_app  # Backup Celery app registration function.
        _state._register_app = lambda _: None  # Upon Celery app registration attempt, do nothing.
        super(Celery, self).__init__()
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        _state._register_app = self.original_register_app  # Restore Celery app registration function.

        app.extensions['celery'] = _CeleryState(self, app)

        super(Celery, self).__init__(app.import_name, backend=app.config['RESULT_BACKEND'],
                                     broker=app.config['BROKER_URL'], )
        task_base = self.Task

        class ContextTask(task_base):
            def __call__(self, *_args, **_kwargs):
                with app.app_context():
                    return task_base.__call__(self, *_args, **_kwargs)

        setattr(self, 'Task', ContextTask)


class _CeleryState(object):
    """Remember the configuration for the (celery, app) tuple. Modeled from SQLAlchemy."""

    def __init__(self, celery, app):
        self.celery = celery
        self.app = app
