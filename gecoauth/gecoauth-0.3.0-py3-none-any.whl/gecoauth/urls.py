from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from .views import (
                    GecoRegisterView, 
                    GecoLoginView)

from rest_auth.views import (
                            LogoutView,
                            PasswordResetConfirmView,
                            PasswordChangeView,
                            PasswordResetView,
                            UserDetailsView)

urlpatterns = [
    url(r'^rest-auth/login/', GecoLoginView.as_view()),
    url(r'^rest-auth/logout/', LogoutView.as_view()),
    url(r'^rest-auth/reset/', PasswordResetView.as_view()),
    url(r'^rest-auth/change/', PasswordChangeView.as_view()),
    url(r'^rest-auth/reset/confirm/', PasswordResetConfirmView.as_view()),
    url(r'^rest-auth/user/', UserDetailsView.as_view()),
    #url(r'^rest-auth/', include('rest_auth.urls')),
    url(r'^rest-auth/registration/', GecoRegisterView.as_view()),

]