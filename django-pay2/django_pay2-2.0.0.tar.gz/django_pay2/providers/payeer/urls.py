from django.urls import path

from . import views

app_name = "payeer"

urlpatterns = [
    path("notify/", views.NotifyView.as_view(), name="notify"),
]
