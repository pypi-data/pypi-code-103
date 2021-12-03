from dataclasses import dataclass
from typing import List, Optional
from px_settings.contrib.django import settings as s


__all__ = 'Settings',


@s('WCD_GEO_DB')
@dataclass
class Settings:
    CODE_SEEKERS: Optional[List[str]] = None
    DB_NAME: str = 'default'
