from sqlalchemy import Column, String, PickleType, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class FileReports(Base):
    __tablename__ = "file_reports"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    reports = Column(PickleType)
