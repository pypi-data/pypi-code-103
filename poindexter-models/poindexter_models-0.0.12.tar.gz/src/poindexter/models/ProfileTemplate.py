from typing import List

from pydantic import BaseModel 
from sqlalchemy import Column, String, Integer, Table, ForeignKey
from sqlalchemy.orm import relationship

from poindexter.models import Base
from poindexter.models.ProfileTemplateVariable import ProfileTemplateVariable


Template_Variable_Table = Table(
  'template_variable_association',
  Base.metadata,
  Column('template_id', ForeignKey('templates.id')),
  Column('variable_id', ForeignKey('template_variables.id'))
)


class ProfileTemplateCreate(BaseModel):
  name: str
  description: str
  version: str
  content: str


class ProfileTemplate(ProfileTemplateCreate):
  id: str
  variables: List[ProfileTemplateVariable]
  class Config:
    orm_mode = True


class ProfileTemplateModel(Base):
  __tablename__ = 'templates'
  id = Column(Integer, primary_key=True, index=True)
  name = Column(String)
  description = Column(String)
  version = Column(String)
  content = Column(String)
  variables = relationship("ProfileTemplateVariableModel", secondary=Template_Variable_Table)
