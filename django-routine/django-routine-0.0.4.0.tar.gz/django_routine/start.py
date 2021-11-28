import os
import sys
from pathlib import Path


class CreateFile:
    def __init__(self, path=None, name=None):
        self.path = path
        self.name = name

    def create_serializer(self):
        serializer = open(self.path.joinpath('serializers.py'), 'w+')
        serializer.write(f"from rest_framework import serializers\n"
                         f"from apps.{self.name}.models import *\n\n\n"
                         f"class {self.name.capitalize()}Serializer(serializers.ModelSerializer):\n"
                         f"    class Meta:\n"
                         f"        model = {self.name.capitalize()}\n"
                         f"        fields = '__all__'\n")

    def create_urls(self):
        urls = open(self.path.joinpath('urls.py'), 'w+')
        urls.write(f"from rest_framework import routers\n"
                   f"from apps.{self.name}.views import {self.name.capitalize()}ViewSet\n\n"
                   f"router = routers.SimpleRouter(trailing_slash=False)\n\n\n"
                   f"router.register(r'{self.name}', {self.name.capitalize()}ViewSet, basename='{self.name}')\n\n"
                   f"urlpatterns = [\n    *router.urls,\n]")

    def create_views(self):
        view = open(self.path.joinpath('views.py'), 'w+')
        view.write(f"from rest_framework.viewsets import GenericViewSet\n\n"
                   f"from apps.{self.name}.models import {self.name.capitalize()}\n"
                   f"from apps.{self.name}.serializers import {self.name.capitalize()}Serializer\n\n\n"
                   f"class {self.name.capitalize()}ViewSet(GenericViewSet):\n"
                   f"    serializer_class = {self.name.capitalize()}Serializer\n"
                   f"    queryset = {self.name.capitalize()}.objects.all()\n")

    def create_model(self):
        model = open(self.path.joinpath('models.py'), 'w+')
        model.write(f"from django.db import models\n\n\n"
                    f"class {self.name.capitalize()}(models.Model):\n"
                    f"    created_at = models.DateTimeField(auto_now_add=True)\n"
                    f"    updated_at = models.DateTimeField(auto_now=True)\n\n"
                    f"    class Meta:\n"
                    f"        abstract = True\n")

    def create_apps(self):
        os.mkdir(f"apps/{self.name}")
        os.system(f"django-admin startapp {self.name} apps/{self.name}")
        apps = open(self.path.joinpath("apps.py"), "w+")
        apps.write(f"from django.apps import AppConfig\n\n\n"
                   f"class {self.name.capitalize()}Config(AppConfig):\n"
                   f"    default_auto_field = 'django.db.models.BigAutoField'\n"
                   f"    name = 'apps.{self.name}'\n")

    def main(self):
        self.create_apps()
        self.create_serializer()
        self.create_model()
        self.create_views()
        self.create_urls()


def start():
    os.system('django-admin startproject config .')
    os.mkdir('apps')
    if len(sys.argv):
        for arg in sys.argv:
            if arg != sys.argv[0]:
                path = Path('apps').absolute().joinpath(arg)
                CreateFile(path=path, name=arg).main()
    os.system('echo All is done, my Captain!')
