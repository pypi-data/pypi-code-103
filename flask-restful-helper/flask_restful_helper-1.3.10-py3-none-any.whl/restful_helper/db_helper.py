from contextlib import contextmanager



class _MetaSingleton(type):
    _instance = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instance:
            cls._instance[cls] = super(_MetaSingleton, cls).__call__(*args, **kwargs)
        return cls._instance[cls]


class _DBHelperConfig(object):
    def __init__(self, db_helper, db, **kwargs):
        self.db_helper = db_helper
        self.db = db
        self.configure_args = kwargs

    @property
    def metadata(self):
        return self.db.metadata


class DBHelper(metaclass=_MetaSingleton):

    def __init__(self, app=None, db=None, **kwargs):
        self.db = None
        if app is not None and db is not None:
            self.init_app(app, db)

    def init_app(self, app, db):
        self.db = db or self.db
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['db_helper'] = _DBHelperConfig(
            self, self.db)

    def add(self, instance):
        return self.db.session.add(instance)

    def delete(self, instance):
        return self.db.session.delete(instance)

    def flush(self):
        return self.db.session.flush()

    @contextmanager
    def auto_commit(self):
        try:
            yield self.db
        except Exception as e:
            self.db.session.rollback()
            raise e
        else:
            self.db.session.commit()
