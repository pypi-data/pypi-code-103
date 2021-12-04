from enum import Enum

import sqlalchemy

from pydantic import BaseModel
from sqlalchemy import Column, String, Integer

from poindexter.models import Base


class TagType(Enum):
  GOOD = "GOOD"
  BAD = "BAD"
  NEUTRAL = "NEUTRAL"


class TagCreate(BaseModel):
  name: str
  type: TagType
  description: str
  source: str


class Tag(TagCreate):
  id: int
  class Config:
    orm_mode = True


class TagModel(Base):
  __tablename__ = 'tags'
  id = Column(Integer, primary_key=True, index=True)
  name = Column(String)
  type = Column(sqlalchemy.Enum(TagType), default=TagType.NEUTRAL)
  description = Column(String)
  source = Column(String)
