try:
    from django.urls import include, path
except ImportError:
    from django.conf.urls import include, url as path

from rest_framework.routers import DefaultRouter

from whisperer.resources.views import WebhookEventViewSet, WebhookViewSet

router = DefaultRouter()
router.register(r'hooks', WebhookViewSet)
router.register(r'hook_events', WebhookEventViewSet)

app_name = 'whisperer'


urlpatterns = [path('', include(router.urls))]
