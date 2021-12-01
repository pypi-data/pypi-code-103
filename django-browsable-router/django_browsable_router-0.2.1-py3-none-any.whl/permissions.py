from django.conf import settings
from rest_framework.permissions import BasePermission


__all__ = ["BlockSchemaAccess"]


class BlockSchemaAccess(BasePermission):
    """Block schema access from OPTIONS request when not in DEBUG mode."""

    def has_permission(self, request, view):
        return not (request.method == "OPTIONS" and not settings.DEBUG)
