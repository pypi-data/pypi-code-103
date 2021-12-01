from django.apps import apps
from django.urls import include, path
from django.conf import settings
from .views import FireBasePhoneAuthView, TestSuccessLogin

urlpatterns = [
    path("phone_login/", FireBasePhoneAuthView.as_view()),
    path("phone_login/__test__/", TestSuccessLogin.as_view()),
]
