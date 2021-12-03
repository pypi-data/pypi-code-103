from typing import List

from pydantic import BaseModel
from sqlalchemy import Column, String, Integer, Table, ForeignKey
from sqlalchemy.orm import relationship

from poindexter.models import Base
from poindexter.models.CSECX import CSECX
from poindexter.models.Domain import Domain


CSE_Domain_Table = Table(
  'cse_domain_association',
  Base.metadata,
  Column('cse_id', ForeignKey('cses.id')),
  Column('domain_id', ForeignKey('domains.id'))
)

CSE_CX_Table = Table(
  'cse_cx_association',
  Base.metadata,
  Column('cse_id', ForeignKey('cses.id')),
  Column('cx_id', ForeignKey('cxes.id'))
)


class CSECreate(BaseModel):
  name: str
  description: str
  cxes: List[int]
  domains: List[int]

class CSEUpdate(BaseModel):
  name: str
  description: str
  cxes: List[int]
  domains: List[int]

class CSE(BaseModel):
  id: int
  name: str
  description: str
  cxes: List[CSECX] = []
  domains: List[Domain] = []
  class Config:
    orm_mode = True


class CSEModel(Base):
  __tablename__ = 'cses'
  id = Column(Integer, primary_key=True, index=True)
  name = Column(String)
  description = Column(String)
  cxes = relationship("CSECXModel", secondary=CSE_CX_Table)
  domains = relationship("DomainModel", secondary=CSE_Domain_Table)
