from django.urls import path

from ..views.searchViews import *

urlpatterns = [
    path('', Search.as_view(), name='search'),
]