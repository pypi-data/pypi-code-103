from django.http.response import HttpResponseRedirect
from django.views.generic import View

from accounts.auth.google import GoogleProviderLogin
from accounts.decorators.define import google_provider_callback_save


# Create your views here.


class GoogleLoginView(GoogleProviderLogin, View):
    """
    [PROCESS]
    1. Front end -> Login URL Access
    2. Here! -> Redirect to Google
    """

    def dispatch(self, request, *args, **kwargs):
        return HttpResponseRedirect(self.get_redirect_url())


@google_provider_callback_save
class GoogleCallbackView(View):
    """
    [PROCESS]
    1. Google Redirect to Here!
    2. get request query string -> extract data
    3. save user info and refresh_token
    4. Redirect to Front-End Callback URL with url query string(
        userinfo,
        access_token,
        refresh_token
    )
    """

    def dispatch(self, request, *args, **kwargs):
        return HttpResponseRedirect(kwargs.get('redirect_url', '/'))
