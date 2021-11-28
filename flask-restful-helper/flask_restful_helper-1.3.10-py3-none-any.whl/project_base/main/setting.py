from pathlib import Path

import yaml


class Setting(object):

    def __init__(self, config_type):
        with open(Path.cwd().joinpath('config', f'{config_type}.yaml'), 'r', encoding='utf-8') as f:
            env = yaml.safe_load(f.read())
        installed_apps_conf_path = Path.cwd().joinpath('config', 'installed_apps.yaml')
        if installed_apps_conf_path.exists():
            with open(installed_apps_conf_path, 'r', encoding='utf-8') as f:
                installed_apps = yaml.safe_load(f.read())
        else:
            print('無註冊任何app，請先創立app')
            exit(1)

        self.config = self._build_config(env, installed_apps)

    def _build_config(self, env, installed_apps):
        config = dict()
        config['DEBUG'] = env['DEBUG']
        # DB
        config['DB_TYPE'] = db_type = str(env['DB_TYPE'])
        config['DB_USERNAME'] = db_username = str(env['DB_USERNAME']) if env['DB_USERNAME'] is not None else None
        config['DB_PASSWORD'] = db_password = str(env['DB_PASSWORD']) if env['DB_PASSWORD'] is not None else None
        config['DB_HOST'] = db_host = str(env['DB_HOST']) if env['DB_HOST'] is not None else None
        config['DB_PORT'] = db_port = int(env['DB_PORT']) if env['DB_PORT'] is not None else None
        config['DB_DATABASE'] = db_database = str(env['DB_DATABASE']) if env['DB_DATABASE'] is not None else None
        if db_type == 'mysql':
            config['SQLALCHEMY_DATABASE_URI'] = \
                f"mysql+pymysql://{db_username}:{db_password}@{db_host}:{db_port}/{db_database}"
        elif db_type == 'sqlite':
            config['SQLALCHEMY_DATABASE_URI'] = \
                f"sqlite:///{Path.cwd().joinpath('sqlite.db')}"
        config['SQLALCHEMY_TRACK_MODIFICATIONS'] = env['SQLALCHEMY_TRACK_MODIFICATIONS']

        # JWT
        config['JWT_SECRET_KEY'] = env['JWT_SECRET_KEY']

        # TEST
        config['TEST_INIT_DB_ON_TEST'] = env['TEST_INIT_DB_ON_TEST']
        config['TEST_EXECUTE_ALL_TEST'] = env['TEST_EXECUTE_ALL_TEST']
        config['TEST_ACCOUNT'] = env['TEST_ACCOUNT']

        # CELERY
        config['BROKER_URL'] = env['CELERY_BROKER_URL']
        config['RESULT_BACKEND'] = env['CELERY_RESULT_BACKEND']

        # INSTALLED APPS
        config['INSTALLED_APPS'] = installed_apps

        # 固定參數
        config['BUNDLE_ERRORS'] = True

        return config

    def to_dict(self):
        return self.config
