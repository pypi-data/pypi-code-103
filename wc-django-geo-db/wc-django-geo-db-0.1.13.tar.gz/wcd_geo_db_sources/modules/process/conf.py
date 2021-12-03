from dataclasses import dataclass
from typing import Sequence


__all__ = 'Settings',


@dataclass
class Settings:
    SOURCE_IMPORT_GLOBAL_REGISTRY: str = 'wcd_geo_db_sources.modules.process.globals.registry'
    SOURCE_IMPORT_RUNNERS: Sequence[str] = None
    SOURCE_IMPORT_DEBUG: bool = False
