from dataclasses import dataclass


__all__ = 'Settings',


@dataclass
class Settings:
    SOURCE_MERGE_CODE_SEEKER_REGISTRY: str = 'wcd_geo_db.modules.code_seeker.globals.registry'
