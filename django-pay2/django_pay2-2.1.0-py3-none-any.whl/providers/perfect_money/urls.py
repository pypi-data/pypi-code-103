from django.urls import path

from . import views

app_name = "perfect_money"

urlpatterns = [
    path("notify/", views.PerfectMoneyNotifyView.as_view(), name="notify"),
]
