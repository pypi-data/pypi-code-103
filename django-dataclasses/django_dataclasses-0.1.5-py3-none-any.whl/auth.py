import functools

from django import http


def login_required(func):
    """
    Require that the request be authenticated.

    Unlike Django's login_required, this does not redirect you to a login
    page because there is no person to login to API calls.
    """

    @functools.wraps(func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return func(request, *args, **kwargs)
        return http.HttpResponse(status=401)

    return wrapper
