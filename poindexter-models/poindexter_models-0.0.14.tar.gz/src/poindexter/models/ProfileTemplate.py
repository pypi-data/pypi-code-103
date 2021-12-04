from pydantic import BaseModel 
from sqlalchemy import Column, String, Integer

from poindexter.models import Base


class ProfileTemplateCreate(BaseModel):
  name: str
  description: str
  version: str
  content: str


class ProfileTemplate(ProfileTemplateCreate):
  id: str
  class Config:
    orm_mode = True


class ProfileTemplateModel(Base):
  __tablename__ = 'templates'
  id = Column(Integer, primary_key=True, index=True)
  name = Column(String)
  description = Column(String)
  version = Column(String)
  content = Column(String)
