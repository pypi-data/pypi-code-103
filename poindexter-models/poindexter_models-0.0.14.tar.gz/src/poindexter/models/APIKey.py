from pydantic import BaseModel 
from sqlalchemy import Column, String, Integer

from poindexter.models import Base


class APIKeyCreate(BaseModel):
  name: str
  value: str


class APIKey(APIKeyCreate):
  id: int
  class Config:
    orm_mode = True


class APIKeyModel(Base):
  __tablename__ = 'keys'
  id = Column(Integer, primary_key=True, index=True)
  name = Column(String)
  value = Column(String)
