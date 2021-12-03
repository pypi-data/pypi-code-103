from django.utils.module_loading import import_string

from wcd_geo_db_sources.conf import settings

from .registry import ProcessRegistry, ProcessRegistryType


__all__ = 'registry', 'get_registry', 'autodiscover',


registry: ProcessRegistryType = ProcessRegistry()


def get_registry() -> ProcessRegistryType:
    if settings.SOURCE_IMPORT_GLOBAL_REGISTRY:
        return import_string(settings.SOURCE_IMPORT_GLOBAL_REGISTRY)

    return registry


def autodiscover():
    r = get_registry()

    for runner in settings.SOURCE_IMPORT_RUNNERS or []:
        r.register(import_string(runner))
