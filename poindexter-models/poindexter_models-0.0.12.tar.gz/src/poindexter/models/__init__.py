from pydantic import BaseConfig
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
BaseConfig.arbitrary_types_allowed = True
