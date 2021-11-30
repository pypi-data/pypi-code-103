
from django.apps import AppConfig
from django.db.models.signals import post_migrate


class AdminInterfaceConfig(AppConfig):

    name = 'djangoadminkit'
    verbose_name = 'Admin Interface'
    default_auto_field = 'django.db.models.AutoField'

    # def ready(self):

    #     from admin_interface import settings
    #     settings.check_installed_apps()