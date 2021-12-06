from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.urls import resolve
from expressmoney.utils import allowed_ip


class AllowedPathsMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if allowed_ip(request) or self._allow_path(request):
            return self.get_response(request)
        raise PermissionDenied

    @staticmethod
    def _allow_path(request):
        is_admin_app = (resolve(request.path_info).app_name == 'admin')
        if is_admin_app:
            return False

        path = request.path_info
        for allowed_path in settings.ALLOWED_PATHS:
            if path == allowed_path or path.startswith(allowed_path):
                return True
        return False
