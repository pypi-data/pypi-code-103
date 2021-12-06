from mad_notifications.api.views import DeviceViewSet, NotificationViewSet
from django.conf import settings
from django.urls import include, path
from rest_framework.routers import DefaultRouter, SimpleRouter


if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register('notification', NotificationViewSet)
router.register('device', DeviceViewSet)

urlpatterns = router.urls
urlpatterns += [
]
