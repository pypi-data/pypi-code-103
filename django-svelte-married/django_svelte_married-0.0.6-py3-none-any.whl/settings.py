import os
from django.conf import settings
from django.utils.module_loading import import_string

SVELTE_PROJECT_PATH = getattr(settings, 'SVELTE_PROJECT_PATH', os.path.join(settings.BASE_DIR, 'svelte_project'))

SVELTE_RELOADING_ENABLED = getattr(settings, 'SVELTE_RELOADING_ENABLED', settings.DEBUG)
SVELTE_RELOADING_HOSTNAME = getattr(settings, 'SVELTE_RELOADING_HOSTNAME', "localhost")
SVELTE_RELOADING_PORT = getattr(settings, 'SVELTE_RELOADING_PORT', 5050)

SVELTE_RENDERER_ENABLED = getattr(settings, 'SVELTE_RENDERER_ENABLED', True)
SVELTE_RENDERER_HOSTNAME = getattr(settings, 'SVELTE_RENDERER_HOSTNAME', "localhost")
SVELTE_RENDERER_PORT = getattr(settings, 'SVELTE_RENDERER_PORT', 6060)
SVELTE_RENDERER = import_string(getattr(settings, 'SVELTE_RENDERER', 'django_svelte_married.renderers.local_renderer'))
