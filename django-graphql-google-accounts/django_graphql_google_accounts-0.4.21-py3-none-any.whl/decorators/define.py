from django.utils.decorators import method_decorator

from accounts.decorators.google import GoogleProviderCallback
from accounts.decorators.token import VerifyTokenAuthenticate

"""
    Google Accounts Class Based Decorator Defined
"""


def callback_google_provider(func):
    def wrapper(request, *args, **kwargs):
        g = GoogleProviderCallback(func)
        return g(request, *args, **kwargs)

    return wrapper


google_provider_callback_save = method_decorator(callback_google_provider, name='dispatch')
login_required = VerifyTokenAuthenticate
