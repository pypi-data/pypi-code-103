import time, inspect, importlib, os
from .models import RequestLoggerModel
from django.conf import settings
from django.db.models import signals
from .signals import signal_list
from django.dispatch import receiver
from functools import wraps


def dispatch_general_receiver(sender, **kwargs):
    print('Managing a task')
    print(f'Sender: {sender}, Category: {kwargs["category"]}')
    print(f'Sender Keys: {", ".join(key for key in kwargs.keys())}')


class RequestMiddleware:
    """
    Middleware that intercepts every request and attach user information
    with response information and create its request model.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.url_prefixes = [
            '/admin/logger/testloggermodel'
        ]
        # TODO: Demo, AutoDiscover signals from APPS
        self.signals = []
        self.autodiscover_signal()
        # Take all django-apps

        for (name, method) in self.signals:
            self.connect(method, dispatch_general_receiver)

    def __str__(self):
        return f'M2D RequestMiddleware, signals loaded: {len(self.signals)}'

    def autodiscover_signal(self):
        for installed_app in [app for app in settings.INSTALLED_APPS if not app.startswith("django.")]:
            print(f'User Installed App: {installed_app}')
            # Find if there is some signals
            try:
                importer_module_name = f'{installed_app}.signals'
                module_ = importlib.import_module(importer_module_name)
                app_signal_list = module_.signal_list
                # Load all signals
                print(f'{self.__str__()}, loading {installed_app.upper()}')
                for (name, func) in app_signal_list.items():
                    self.signals.append((name, func))
                print(f'{self.__str__()}, loaded {installed_app.upper()}')

            except ModuleNotFoundError:
                print(f'Module not found for this app: {installed_app}')
            except AttributeError:
                print(f'This module has no attribute signal_list: {installed_app}')

    def connect(self, signal, func):

        @wraps(func)
        @receiver(signal)
        def wrapper(sender, **kwargs):
            return func(sender, **kwargs)

        signal.connect(wrapper)
        return wrapper

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        _t = time.time()
        response = self.get_response(request)
        _t = int((time.time() - _t) * 1000)

        # Code to be executed for each request/response after
        # the view is called.

        if not list(filter(request.get_full_path().startswith, self.url_prefixes)):
            print(f'Skipping request_log {request.get_full_path}')
            return response

            # Create instance of RequestLoggerModel
        request_log = LogModel(
            endpoint=request.get_full_path(),
            response_code=response.status_code,
            method=request.method,
            remote_address=self._get_client_ip(request),
            exec_time=_t,
            body_response=str(response.content),
            body_request=str(request.body)
        )

        # Assign user to log if it's not an anonymous user
        if not request.user.is_anonymous:
            request_log.user = request.user

        # Save log in db
        request_log.save()
        print(f'Request done, {request_log.method}, {request_log.endpoint}')
        return response

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            _ip = x_forwarded_for.split(',')[0]
        else:
            _ip = request.META.get('REMOTE_ADDR')
        return _ip
