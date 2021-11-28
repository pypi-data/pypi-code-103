"""Declares :mod:`pydantic` models for all exception classes."""
from typing import List
from typing import Optional

from pydantic import BaseModel


class CanonicalException(BaseModel):
    """Declares the :mod:`pydantic` schema for canonical exceptions."""

    code: str
    message: str
    detail: Optional[str]
    key: Optional[List]
