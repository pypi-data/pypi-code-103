try:
    __import__('pkg_resources').declare_namespace(__name__)
except ImportError:
    __path__ = __import__('pkgutil').extend_path(__path__, __name__)

from .persistence import *  
from flask_sqlalchemy import SQLAlchemy


class NaverDB():

    def __init__(self, app, config):
        self.myApp = app
        self.myDb = SQLAlchemy(self.myApp)
        self.myConfig = config 
        self.persistence = Persistence(self.myConfig, self.myApp, self.myDb) 


if __name__ == '__main__':
    pass
