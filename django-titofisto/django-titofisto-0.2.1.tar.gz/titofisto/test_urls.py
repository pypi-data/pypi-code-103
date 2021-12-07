from django.conf import settings
from django.urls import include, path

urlpatterns = [
    path(settings.MEDIA_URL.removeprefix("/"), include("titofisto.urls")),
]
