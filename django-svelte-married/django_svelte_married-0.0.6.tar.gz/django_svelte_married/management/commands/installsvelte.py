import json
import os
import shutil
from sys import stdout, stderr
from subprocess import run

from django.core.management import BaseCommand
from django_svelte_married.settings import SVELTE_PROJECT_PATH
from django.conf import settings

SCRIPT_DIR = os.path.dirname(__file__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write(f"Install `django_svelte_married` runtime npm dependencies")
        with open(os.path.join(SVELTE_PROJECT_PATH, 'package.json'), 'r') as pkg_f:
            pkg_json = json.load(pkg_f)
            managepy_rel_path = os.path.relpath(settings.BASE_DIR, SVELTE_PROJECT_PATH)

            pkg_json['dependencies']['npm-run-all'] = "*"
            pkg_json['dependencies']['cross-env'] = "*"
            pkg_json['dependencies']['express'] = "*"
            pkg_json['dependencies']['body-parser'] = "*"

            if 'dev' in pkg_json['scripts'] and 'run-p' in pkg_json['scripts']['dev']:
                self.stdout.write("Looks like `package.json` is correctly provisioned.")
            else:
                pkg_json['scripts']['dev'] = "run-p -l dev:django dev:dom dev:ssr dev:renderer"
                pkg_json['scripts']['dev:django'] = f"cross-env python {managepy_rel_path}/manage.py runserver"
                pkg_json['scripts']['dev:dom'] = "cross-env BUILD_TYPE=DOM rollup -c -w"
                pkg_json['scripts']['dev:ssr'] = "cross-env BUILD_TYPE=RENDERER rollup ./src/exported.js -c -w"
                pkg_json['scripts']['dev:renderer'] = "cross-env node ./scripts/renderer.js"

            os.makedirs(os.path.join(SVELTE_PROJECT_PATH, "scripts"), exist_ok=True)
            os.makedirs(os.path.join(SVELTE_PROJECT_PATH, "src"), exist_ok=True)

            shutil.copy(os.path.join(SCRIPT_DIR, '../../js/renderer.js'),
                        os.path.join(SVELTE_PROJECT_PATH, "scripts/renderer.js"))
            shutil.copy(os.path.join(SCRIPT_DIR, '../../js/main.js'),
                        os.path.join(SVELTE_PROJECT_PATH, "src/main.js"))
            if not os.path.exists(os.path.join(SVELTE_PROJECT_PATH, "src/exported.js")):
                shutil.copy(os.path.join(SCRIPT_DIR, '../../js/exported.js'),
                            os.path.join(SVELTE_PROJECT_PATH, "src/exported.js"))

        with open(os.path.join(SVELTE_PROJECT_PATH, 'package.json'), 'w') as pkg_f:
            pkg_f.write(json.dumps(pkg_json, indent=4))

        self.stdout.write(f"Install npm dependencies in `{SVELTE_PROJECT_PATH}`...")
        run("npm install", cwd=SVELTE_PROJECT_PATH, stdout=stdout, stderr=stderr, shell=True)

        self.stdout.write("")
        self.stdout.write("")
        self.stdout.write("Congratulations. You can now run `python manage.py runsvelte`")
