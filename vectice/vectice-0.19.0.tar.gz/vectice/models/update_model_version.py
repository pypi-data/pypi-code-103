from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Optional, Union, List, Tuple

from .attachments import Attachments
from .with_tags import WithTags
from .with_properties import WithProperties
from ..entity.model_version import ModelVersionStatus


@dataclass
class UpdateModelVersion(dict):
    algorithmName: Optional[str] = None
    description: Optional[str] = None
    isStarred: Optional[bool] = False
    status: Optional[Union[ModelVersionStatus, str]] = "EXPERIMENTATION"
    tags: Optional[Union[List[Tuple[str, str]], Tuple[str, str]]] = None
    properties: Optional[Union[List[Tuple[str, str]], Tuple[str, str]]] = None
    """"""

    def __post_init__(self):
        self._assign_properties()
        self._assign_tags()
        if not self._check_status():
            raise ValueError(f"The status of {self.status} is not a valid option.")

    def as_dict(self):
        return asdict(self)

    @staticmethod
    def create_attachments(attachments: Optional[List[str]]):
        if attachments is not None and len(attachments) >= 1:
            return Attachments("modelversion").with_attachments(attachments)
        return None

    def _check_status(self) -> bool:
        try:
            ModelVersionStatus[str(self.status)]
            return True
        except KeyError:
            return False

    def _assign_properties(self) -> None:
        if isinstance(self.properties, list):
            self.properties = WithProperties().with_properties(self.properties).properties  # type: ignore
        if isinstance(self.properties, tuple):
            self.properties = WithProperties().with_property(*self.properties).properties  # type: ignore

    def _assign_tags(self) -> None:
        if isinstance(self.tags, list):
            self.tags = WithTags().with_tags(self.tags).tags  # type: ignore
        if isinstance(self.tags, tuple):
            self.tags = WithTags().with_tag(*self.tags).tags  # type: ignore
