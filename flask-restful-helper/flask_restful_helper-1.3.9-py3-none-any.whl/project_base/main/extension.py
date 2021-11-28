from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_restful_helper import Api
from flask_sqlalchemy import SQLAlchemy
from flask_restful_helper import DBHelper
from flask_bcrypt import Bcrypt
from flask_restful_helper import Celery
db = SQLAlchemy()
api = Api()
ma = Marshmallow()
cors = CORS()
migrate = Migrate()
jwt = JWTManager()
bcrypt = Bcrypt()
db_helper = DBHelper()
celery = Celery()
