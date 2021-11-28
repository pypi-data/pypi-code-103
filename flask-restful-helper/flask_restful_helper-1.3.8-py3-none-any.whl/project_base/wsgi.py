import os

from main import create_app

app = create_app(config_type=os.getenv('config_type', 'dev'))
