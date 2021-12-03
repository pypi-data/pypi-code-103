from enum import Enum
from typing import List

import sqlalchemy

from pydantic import BaseModel 
from sqlalchemy import Column, String, Integer, ForeignKey, Table
from sqlalchemy.orm import relationship

from poindexter.models import Base
from poindexter.models.Tag import Tag


Plugin_Tag_Table = Table(
  'plugin_tag_association',
  Base.metadata,
  Column('plugin_id', ForeignKey('plugins.id')),
  Column('tag_id', ForeignKey('tags.id'))
)


class PluginStatus(Enum):
  ENABLED = "ENABLED"
  DISABLED = "DISABLED"


class PluginCreate(BaseModel):
  urn: str
  description: str
  author: str
  path: str
  status: PluginStatus


class PluginUpdate(BaseModel):
  status: PluginStatus


class Plugin(PluginCreate):
  id: int
  tags: List[Tag]
  class Config:
    orm_mode = True


class PluginModel(Base):
  __tablename__ = 'plugins'
  id = Column(Integer, primary_key=True, index=True)
  urn = Column(String)
  description = Column(String)
  author = Column(String)
  path = Column(String)
  status = Column(sqlalchemy.Enum(PluginStatus))
  tags = relationship("TagModel", secondary=Plugin_Tag_Table)
