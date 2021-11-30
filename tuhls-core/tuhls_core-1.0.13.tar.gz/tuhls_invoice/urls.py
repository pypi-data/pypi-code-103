from django.urls import path

from . import views

urlpatterns = [
    path("overview/", views.invoice_overview, name="invoice_overview"),
    path("invoice_pdf/<uuid:invoice_gid>", views.invoice_pdf, name="invoice_pdf"),
    path("receipt_pdf/<uuid:invoice_gid>", views.receipt_pdf, name="receipt_pdf"),
]
