from django.urls import path

from . import views

app_name = "free_kassa"

urlpatterns = [
    path("notify/", views.NotifyView.as_view(), name="notify"),
]
