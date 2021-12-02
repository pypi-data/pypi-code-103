"""the instance of SQLAlchemy from Flask-SQLAlchemy

"""
from sqlalchemy import MetaData
from flask_sqlalchemy import SQLAlchemy

##__________________________________________________________________||
# https://flask-sqlalchemy.palletsprojects.com/en/2.x/config/#using-custom-metadata-and-naming-conventions
# https://stackoverflow.com/a/56000475/7309855
convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    # "ck": "ck_%(table_name)s_%(constraint_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
metadata = MetaData(naming_convention=convention)

##__________________________________________________________________||
sa = SQLAlchemy(metadata=metadata)
"""the instance of SQLAlchemy from Flask-SQLAlchemy

While the instance is named "sa" here, it is more commonly named "db"
in example code found online.

- API: https://flask-sqlalchemy.palletsprojects.com/en/2.x/api/#flask_sqlalchemy.SQLAlchemy
- The difference from the plain SQLAlchemy:
  https://flask-sqlalchemy.palletsprojects.com/en/2.x/api/#flask_sqlalchemy.SQLAlchemy

"""
##__________________________________________________________________||
