from enum import Enum 
from typing import List

import sqlalchemy

from pydantic import BaseModel 
from sqlalchemy import Column, String, Integer, ForeignKey, Table
from sqlalchemy.orm import relationship

from poindexter.models import Base
from poindexter.models.Tag import Tag


Domain_Tag_Table = Table(
  'domain_tag_association',
  Base.metadata,
  Column('domain_id', ForeignKey('domains.id')),
  Column('tag_id', ForeignKey('tags.id'))
)

class DomainCategory(Enum):
  ANALYSIS = "ANALYSIS"
  CLOUD = "CLOUD"
  COMMUNICATION = "COMMUNICATION"
  DEVELOPMENT = "DEVELOPMENT"
  DOCUMENTATION = "DOCUMENTATION"
  EDUCATION = "EDUCATION"
  FINANCE = "FINANCE"
  FORMS = "FORMS"
  ORGANIZATION = "ORGANIZATION"
  OTHER = "OTHER"
  REMOTE = "REMOTE"
  SHORTNER = "SHORTNER"
  SOCIAL = "SOCIAL"
  STORAGE = "STORAGE"


class DomainCreate(BaseModel):
  name: str
  description: str
  category: DomainCategory
  tags: List[int]

class DomainUpdate(BaseModel):
  name: str
  description: str
  category: DomainCategory
  tags: List[int]

class Domain(BaseModel):
  id: int
  name: str
  description: str
  category: DomainCategory
  tags: List[Tag]
  class Config:
    orm_mode = True


class DomainModel(Base):
  __tablename__ = 'domains'
  id = Column(Integer, primary_key=True, index=True)
  name = Column(String)
  description = Column(String)
  category = Column(sqlalchemy.Enum(DomainCategory))
  tags = relationship("TagModel", secondary=Domain_Tag_Table)
