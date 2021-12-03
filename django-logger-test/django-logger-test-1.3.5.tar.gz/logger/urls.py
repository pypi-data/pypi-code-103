from django.urls import path

from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('react', views.react_index, name="react_index")
]
