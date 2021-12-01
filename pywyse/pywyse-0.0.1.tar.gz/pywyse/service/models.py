from dataclasses import asdict, dataclass, field
from typing import Dict, TypedDict
import json 
from typing import Optional
from pywyse.project import Project 
from typing import NamedTuple


@dataclass 
class PurchaseTicket:
    """Creating purchase tickets"""
    summary: str 
    project_description: str = None 
    project_id: str = None
    notes: str = None
    id: str = None
    recordType: str = 'ServiceTicket'
    board: Dict[str,str] = field(default_factory=lambda: ({'name':'Purchasing'}))
    company: Dict[str,str] = field(default_factory=lambda: ({'id':'2'}))
    status: Dict[str,str] = field(default_factory=lambda: ({'name':'New'}))

    def __post_init__(self): 
        if self.project_id is not None:
            r = Project().get_project(self.project_id, field='name')
            self.project_description = f"Project: [{self.project_id}] - {r.get('name','')}"
          
    def to_dict(self): 
        _data = asdict(self)
        return {k:v for k,v in _data.items() if v is not None and k is not 'project_id'}
