from dataclasses import dataclass
from px_settings.contrib.django import settings as s

from .modules.process.conf import Settings as ProcessSettings
from .modules.merger.conf import Settings as MergerSettings
from .modules.tasks.conf import Settings as TasksSettings


__all__ = 'Settings', 'settings'


@s('WCD_GEO_DBSOURCES')
@dataclass
class Settings(ProcessSettings, TasksSettings, MergerSettings):
    pass


settings = Settings()
