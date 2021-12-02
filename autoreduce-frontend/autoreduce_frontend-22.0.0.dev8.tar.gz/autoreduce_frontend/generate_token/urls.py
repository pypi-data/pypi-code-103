from django.urls import path

from autoreduce_frontend.generate_token import views

app_name = "token"

urlpatterns = [
    path("", views.ShowToken.as_view(), name="list"),
    path("generate", views.GenerateTokenFormView.as_view(), name="generate"),
    path("delete/<str:pk>", views.DeleteToken.as_view(), name="delete"),
]
