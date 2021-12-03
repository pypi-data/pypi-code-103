from dataclasses import dataclass
from typing import Optional


__all__ = 'Settings',


@dataclass
class Settings:
    CELERY_APP: Optional[str] = None
