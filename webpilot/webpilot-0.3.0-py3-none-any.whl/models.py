from typing import Optional, TypeVar
from pydantic import BaseModel

Model = TypeVar('Model')


class Target(BaseModel):
    targetId: Optional[str]
    sessionId: Optional[str]


class Page(BaseModel):
    target: Optional[Target]
    frameId: str
    errorText: Optional[str]


class Node(BaseModel):
    nodeId: int


class Document(BaseModel):
    root: Node


class OuterHTML(BaseModel):
    outerHTML: str
