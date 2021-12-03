from pydantic import BaseModel 
from sqlalchemy import Column, String, Integer, ForeignKey

from poindexter.models import Base


class PluginOutputCreate(BaseModel):
  path: str
  source: str


class PluginOutput(PluginOutputCreate):
  id: int
  path: str
  class Config:
    orm_mode = True


class PluginOutputModel(Base):
  __tablename__ = 'outputs'
  id = Column(Integer, primary_key=True, index=True)
  path = Column(String)
  source = Column(String)
