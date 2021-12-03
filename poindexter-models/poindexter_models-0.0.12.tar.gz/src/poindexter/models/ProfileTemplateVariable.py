from pydantic import BaseModel 
from sqlalchemy import Column, String, Integer

from poindexter.models import Base


class ProfileTemplateVariableCreate(BaseModel):
  name: str


class ProfileTemplateVariable(ProfileTemplateVariableCreate):
  id: str
  class Config:
    orm_mode = True


class ProfileTemplateVariableModel(Base):
  __tablename__ = 'template_variables'
  id = Column(Integer, primary_key=True, index=True)
  name = Column(String)
