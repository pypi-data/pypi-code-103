from django.urls import path, re_path

from . import views

app_name = "marketmanager"

urlpatterns = [
    path('', views.marketbrowser, name="index"),
    path('marketbrowser', views.marketbrowser, name="marketbrowser"),
    path('marketmanager', views.marketbrowser, name="marketmanager"),
    path('marketbrowser/ajax/search',  views.marketbrowser_autocomplete, name="marketbrowser_autocomplete"),
    path('char/add', views.add_char, name="add_char"),
    path('corp/add', views.add_corp, name="add_corp")
]
