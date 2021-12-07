from django.conf.urls import url
from rest_framework.authtoken.views import obtain_auth_token

from ..views.authenticationViews import *

urlpatterns = [
    url(r'obtain/', obtain_auth_token, name='obtain'),
    url(r'register/', Register.as_view(), name='register'),
    url(r'login/', Login.as_view(), name='login'),
    url(r'logout/', Logout.as_view(), name='logout'),
    url(r'validate/', TokenValidation.as_view(), name='validate'),
]
