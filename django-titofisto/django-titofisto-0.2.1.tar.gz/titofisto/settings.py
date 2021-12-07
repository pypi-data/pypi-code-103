from django.conf import settings

PARAM = getattr(settings, "TITOFISTO_PARAM", "titofisto_token")
TIMEOUT = getattr(settings, "TITOFISTO_TIMEOUT", 60 * 60)
USE_PUBLIC_NAMESPACE = getattr(settings, "TITOFISTO_USE_PUBLIC_NAMESPACE", True)
PUBLIC_NAMESPACE = getattr(settings, "TITOFISTO_PUBLIC_NAMESPACE", "public/")
