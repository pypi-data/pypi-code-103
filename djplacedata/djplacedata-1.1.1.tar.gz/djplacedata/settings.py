from django.conf import settings


CENSUS_API_KEY = getattr(settings, 'CENSUS_API_KEY', None)
SODA_APP_TOKEN = getattr(settings, 'SODA_APP_TOKEN', None)
