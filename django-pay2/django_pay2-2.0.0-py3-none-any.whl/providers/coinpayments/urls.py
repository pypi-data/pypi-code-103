from django.urls import path

from . import views

app_name = "coinpayments"

urlpatterns = [
    path("notify/", views.CoinPaymentsNotifyView.as_view(), name="notify"),
]
