from enum import Enum
from typing import Optional, List
from datetime import datetime

import sqlalchemy

from pydantic import BaseModel 
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship

from poindexter.models import Base
from poindexter.models.CSE import CSE
from poindexter.models.APIKey import APIKey
from poindexter.models.Profile import Profile
from poindexter.models.Report import Report
from poindexter.models.Plugin import Plugin


Job_CSE_Table = Table(
  'job_cse_association',
  Base.metadata,
  Column('job_id', ForeignKey('jobs.id')),
  Column('cse_id', ForeignKey('cses.id'))
)

Job_Plugin_Table = Table(
  'job_plugin_association',
  Base.metadata,
  Column('job_id', ForeignKey('jobs.id')),
  Column('plugin_id', ForeignKey('plugins.id'))
)


class JobStatus(Enum):
  CREATED = "CREATED"
  RUNNING = "RUNNING"
  ERROR = "ERROR"
  FINISHED = "FINISHED"


class JobCreate(BaseModel):
  name: str
  profile_id: int
  key_id: int
  plugin_ids: List[int]
  plugin_urns: List[str]
  cse_ids: List[int]


class JobUpdate(BaseModel):
  status: JobStatus


class Job(BaseModel):
  id: int
  name: str
  status: JobStatus
  created: datetime
  profile_id: Optional[int]
  profile: Profile
  key_id: Optional[int]
  key: APIKey
  report_id: Optional[int]
  report: Optional[Report]
  plugins: List[Plugin]
  cses: List[CSE]
  class Config:
    orm_mode = True


class JobModel(Base):
  __tablename__ = 'jobs'
  id = Column(Integer, primary_key=True, index=True)
  name = Column(String)
  status = Column(sqlalchemy.Enum(JobStatus), default=JobStatus.CREATED)
  created = Column(DateTime, default=lambda: datetime.now())
  profile_id = Column(Integer, ForeignKey("profiles.id"))
  key_id = Column(Integer, ForeignKey("keys.id"))
  report_id = Column(Integer, ForeignKey("reports.id"), nullable=True)
  profile = relationship("ProfileModel")
  key = relationship("APIKeyModel")
  report = relationship("ReportModel")
  plugins = relationship("PluginModel", secondary=Job_Plugin_Table)
  cses = relationship("CSEModel", secondary=Job_CSE_Table)
