from django.utils.module_loading import import_string


__all__ = 'get_celery',


def get_celery():
    from wcd_geo_db_sources.conf import settings

    if settings.CELERY_APP:
        return import_string(settings.CELERY_APP)

    return None
