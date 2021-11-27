from django.urls import path

from . import views

app_name = "qiwi"

urlpatterns = [
    path("notify/", views.QiwiNotifyView.as_view(), name="notify"),
]
