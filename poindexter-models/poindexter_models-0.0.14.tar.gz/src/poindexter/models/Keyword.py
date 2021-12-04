from pydantic import BaseModel 
from sqlalchemy import Column, String, Integer

from poindexter.models import Base


class KeywordCreate(BaseModel):
  value: str


class Keyword(KeywordCreate):
  id: int
  class Config:
    orm_mode = True


class KeywordModel(Base):
  __tablename__ = 'keywords'
  id = Column(Integer, primary_key=True, index=True)
  value = Column(String)
