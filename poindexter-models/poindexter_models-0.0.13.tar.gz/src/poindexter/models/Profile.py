from typing import List

from pydantic import BaseModel 
from sqlalchemy import Column, String, Integer, Table, ForeignKey
from sqlalchemy.orm import relationship

from poindexter.models import Base
from poindexter.models.Keyword import Keyword


Profile_Keyword_Table = Table(
  'profile_keyword_association',
  Base.metadata,
  Column('profile_id', ForeignKey('profiles.id')),
  Column('keyword_id', ForeignKey('keywords.id'))
)


class ProfileCreate(BaseModel):
  name: str
  keywords: List[int]

class ProfileUpdate(BaseModel):
  name: str
  keywords: List[int]

class Profile(BaseModel):
  id: int
  name: str
  keywords: List[Keyword]
  class Config:
    orm_mode = True


class ProfileModel(Base):
  __tablename__ = 'profiles'
  id = Column(Integer, primary_key=True, index=True)
  name = Column(String)
  keywords = relationship("KeywordModel", secondary=Profile_Keyword_Table)
