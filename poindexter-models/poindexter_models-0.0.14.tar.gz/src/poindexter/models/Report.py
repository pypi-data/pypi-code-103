from typing import List

from pydantic import BaseModel 
from sqlalchemy import Column, String, Integer, Table, ForeignKey
from sqlalchemy.orm import relationship

from poindexter.models import Base
from poindexter.models.Link import Link
from poindexter.models.PluginOutput import PluginOutput


Report_Link_Table = Table(
  'report_link_association',
  Base.metadata,
  Column('report_id', ForeignKey('reports.id')),
  Column('link_id', ForeignKey('links.id'))
)

Report_Output_Table = Table(
  'report_output_association',
  Base.metadata,
  Column('report_id', ForeignKey('reports.id')),
  Column('output_id', ForeignKey('outputs.id'))
)


class ReportCreate(BaseModel):
  name: str


class Report(ReportCreate):
  id: int
  links: List[Link]
  outputs: List[PluginOutput]
  class Config:
    orm_mode = True


class ReportModel(Base):
  __tablename__ = 'reports'
  id = Column(Integer, primary_key=True, index=True)
  name = Column(String)
  links = relationship("LinkModel", secondary=Report_Link_Table)
  outputs = relationship("PluginOutputModel", secondary=Report_Output_Table)
