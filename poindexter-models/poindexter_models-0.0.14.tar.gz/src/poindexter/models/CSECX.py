from pydantic import BaseModel
from sqlalchemy import Column, String, Integer

from poindexter.models import Base


class CSECXCreate(BaseModel):
  cx: str


class CSECX(CSECXCreate):
  id: int
  class Config:
    orm_mode = True


class CSECXModel(Base):
  __tablename__ = 'cxes'
  id = Column(Integer, primary_key=True, index=True)
  cx = Column(String, index=True)
