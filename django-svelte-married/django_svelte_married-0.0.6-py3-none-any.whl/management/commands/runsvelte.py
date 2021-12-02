import os
from subprocess import run
from sys import stdout, stderr

from django.core.management import BaseCommand

from django_svelte_married.settings import SVELTE_PROJECT_PATH, SVELTE_RELOADING_PORT


class Command(BaseCommand):
    def handle(self, *args, **options):
        # copy necessary environment from `settings.py` to be used in Node
        os.environ["SVELTE_RELOADING_PORT"] = str(SVELTE_RELOADING_PORT)
        # run npm that handles parallel procs
        run("npm run dev", cwd=SVELTE_PROJECT_PATH, stdout=stdout, stderr=stderr, shell=True)
