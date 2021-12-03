from django.db import models
from django.utils.translation import pgettext_lazy


__all__ = 'DivisionLevel', 'DivisionType'


class DivisionLevel(models.IntegerChoices):
    COUNTRY = 1200, pgettext_lazy('wcd_geo_db', 'Country')

    ADMINISTRATIVE_LEVEL_1 = 1410, pgettext_lazy('wcd_geo_db', 'Administrative division: Level 1')
    ADMINISTRATIVE_LEVEL_2 = 1420, pgettext_lazy('wcd_geo_db', 'Administrative division: Level 2')
    ADMINISTRATIVE_LEVEL_3 = 1430, pgettext_lazy('wcd_geo_db', 'Administrative division: Level 3')
    ADMINISTRATIVE_LEVEL_4 = 1440, pgettext_lazy('wcd_geo_db', 'Administrative division: Level 4')
    ADMINISTRATIVE_LEVEL_5 = 1450, pgettext_lazy('wcd_geo_db', 'Administrative division: Level 5')

    LOCALITY = 1600, pgettext_lazy('wcd_geo_db', 'Locality')

    SUBLOCALITY_LEVEL_1 = 1810, pgettext_lazy('wcd_geo_db', 'Locality division: Level 1')
    SUBLOCALITY_LEVEL_2 = 1820, pgettext_lazy('wcd_geo_db', 'Locality division: Level 2')
    SUBLOCALITY_LEVEL_3 = 1830, pgettext_lazy('wcd_geo_db', 'Locality division: Level 3')
    SUBLOCALITY_LEVEL_4 = 1840, pgettext_lazy('wcd_geo_db', 'Locality division: Level 4')
    SUBLOCALITY_LEVEL_5 = 1850, pgettext_lazy('wcd_geo_db', 'Locality division: Level 5')


class DivisionType(models.TextChoices):
    COUNTRY = 'country', pgettext_lazy('wcd_geo_db', 'Country')
    STATE = 'state', pgettext_lazy('wcd_geo_db', 'State')

    FEDERAL_STATE = 'federal_state', pgettext_lazy('wcd_geo_db', 'Federal state')
    REGION = 'region', pgettext_lazy('wcd_geo_db', 'Region')
    COUNTY = 'county', pgettext_lazy('wcd_geo_db', 'County')
    MUNICIPALITY = 'municipality', pgettext_lazy('wcd_geo_db', 'Municipality')
    PROVINCE = 'province', pgettext_lazy('wcd_geo_db', 'Province')
    DISTRICT = 'district', pgettext_lazy('wcd_geo_db', 'District')
    SUBDISTRICT = 'subdistrict', pgettext_lazy('wcd_geo_db', 'Subdistrict')
    TOWNSHIP = 'township', pgettext_lazy('wcd_geo_db', 'Township')
    DEPARTMENT = 'department', pgettext_lazy('wcd_geo_db', 'Department')
    COMMUNE = 'commune', pgettext_lazy('wcd_geo_db', 'Commune')
    COMMUNITY = 'community', pgettext_lazy('wcd_geo_db', 'Community')

    AUTONOMOUS_CITY = 'autonomous_city', pgettext_lazy('wcd_geo_db', 'Autonomous city')
    CITY = 'city', pgettext_lazy('wcd_geo_db', 'City')
    CITY_DISTRICT = 'city_district', pgettext_lazy('wcd_geo_db', 'City district')
    CITY_SUBDISTRICT = 'city_subdistrict', pgettext_lazy('wcd_geo_db', 'City subdistrict')
    TOWN = 'town', pgettext_lazy('wcd_geo_db', 'Town')
    LOCALITY = 'locality', pgettext_lazy('wcd_geo_db', 'Locality')
    VILLAGE = 'village', pgettext_lazy('wcd_geo_db', 'Village')
    HAMLET = 'hamlet', pgettext_lazy('wcd_geo_db', 'Hamlet')
    SETTLEMENT = 'settlement', pgettext_lazy('wcd_geo_db', 'Settlement')
