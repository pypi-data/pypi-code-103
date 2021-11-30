import os

import magic_import
import django
from django.template import Template
from django.template import Context
from django.conf import settings
from django.template.loader import get_template

def get_app_template_dir(app_name):
    mod = magic_import.import_from_string(app_name)
    if mod:
        return os.path.abspath(os.path.join(os.path.dirname(mod.__file__), "./templates/"))
    else:
        return None

def setup(template_dirs=None, apps=None):
    if settings.configured:
        return
    final_template_dirs = []
    # add extra template dirs
    template_dirs = template_dirs or []
    if isinstance(template_dirs, str):
        template_dirs = [template_dirs]
    final_template_dirs += template_dirs
    # add app template dirs
    apps = apps or []
    for app in apps:
        template_dir = get_app_template_dir(app)
        if template_dir:
            template_dirs.append(template_dir)
    # add workspace template dir
    workspace_template_dir = os.path.abspath(os.path.join(os.getcwd(), "./templates"))
    final_template_dirs.append(workspace_template_dir)
    # simple django template engine setup
    settings.configure(TEMPLATES=[{
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': final_template_dirs,
    }])
    django.setup()

def register_apps(*app_names):
    setup()
    for app_name in app_names:
        template_dir = get_app_template_dir(app_name)
        if template_dir and (not template_dir in settings.TEMPLATES[0]["DIRS"]):
            settings.TEMPLATES[0]["DIRS"].append(template_dir)

def register_dirs(*dirs):
    setup()
    for dir in dirs:
        dir = os.path.abspath(dir)
        if not dir in settings.TEMPLATES[0]["DIRS"]:
            settings.TEMPLATES[0]["DIRS"].append(dir)

def render_template(template_filename, context=None):
    context = context or {}
    setup()
    return get_template(template_filename).render(context)

def render(template_text, context=None):
    context = context or {}
    setup()
    return Template(template_text).render(Context(context))
