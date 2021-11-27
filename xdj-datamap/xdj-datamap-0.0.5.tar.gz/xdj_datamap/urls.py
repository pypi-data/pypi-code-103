# -*- coding: utf-8 -*-
from django.urls import re_path
from rest_framework import routers

from xdj_datamap.views.field import FieldsViewSet
from xdj_datamap.views.map import DataMapViewSet
from xdj_datamap.views.model import ModelViewSet

system_url = routers.SimpleRouter()
system_url.register(r'map', DataMapViewSet)
system_url.register(r'field', FieldsViewSet)
system_url.register(r'model', ModelViewSet)

urlpatterns = [
    re_path('map/get_data/(?P<datamap>.*?)/', DataMapViewSet.as_view({'get': 'get_data'})),
    re_path('map/get_model/(?P<datamap>.*?)/', DataMapViewSet.as_view({'get': 'get_model'})),
]
urlpatterns += system_url.urls
