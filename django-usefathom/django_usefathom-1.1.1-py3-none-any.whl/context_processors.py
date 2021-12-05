from django.conf import settings

from .api import fetch_goals


def usefathom(request):
    return {
        "fathom_goals": fetch_goals(request),
        "FATHOM_SITE_ID": settings.FATHOM_SITE_ID,
        "FATHOM_SCRIPT_URL": getattr(
            settings, "FATHOM_SCRIPT_URL", "https://cdn.usefathom.com/script.js"
        ),
    }
