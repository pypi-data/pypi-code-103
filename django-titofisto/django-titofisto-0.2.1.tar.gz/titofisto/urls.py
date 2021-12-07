from django.urls import path

from .views import TitofistoMediaView

urlpatterns = [
    path("<path:name>", TitofistoMediaView.as_view()),
]
