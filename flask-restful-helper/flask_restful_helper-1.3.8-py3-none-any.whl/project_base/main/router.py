import importlib


def registry_router(app):
    for _ in app.config['INSTALLED_APPS']:
        router = importlib.import_module(f'apps.{_}.router')
        app.register_blueprint(router.blueprint)
