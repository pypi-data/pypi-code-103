from django.contrib.auth.views import LoginView
from django.views import View
from django.http import HttpResponse

from .forms import FireBasePhoneAuthFrom

from django.contrib.auth.views import LoginView


class FireBasePhoneAuthView(LoginView):
    template_name = 'fb_phoneauth/login.html'
    form_class = FireBasePhoneAuthFrom


class TestSuccessLogin(View):
    def get(self, request):
        return HttpResponse('Success')
