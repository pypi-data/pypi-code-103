from django.urls import path

from . import views

app_name = "qiwi"

urlpatterns = [
    path("notify/", views.QiwiKassaNotifyView.as_view(), name="notify"),
]
